"""FitFlow runtime and mutation API."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_util

from .const import SIGNAL_UPDATE
from .models import FitFlowData, Recommendation, new_id
from .recommendation import recommend, recommend_exercises
from .storage import FitFlowStorage


def resolve_activity(
    activities: list[dict[str, Any]], value: str
) -> dict[str, Any] | None:
    """Resolve an activity by stable ID or user-facing name."""
    normalized = value.strip().casefold()
    return next(
        (
            item
            for item in activities
            if item.get("id") == value
            or str(item.get("name", "")).strip().casefold() == normalized
        ),
        None,
    )


class FitFlowCoordinator:
    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self.hass, self.entry_id = hass, entry_id
        self.storage = FitFlowStorage(hass, entry_id)
        self.data = FitFlowData()
        self._lock = asyncio.Lock()

    async def async_setup(self) -> None:
        self.data = await self.storage.async_load()

    @property
    def recommendation(self) -> Recommendation:
        return recommend(
            self.data.workouts,
            self.data.activities,
            self.data.conflict_rules,
            self.data.history,
            dt_util.now(),
        )

    def snapshot(self) -> dict[str, Any]:
        recommendation = self.recommendation
        return {
            **self.data.as_dict(),
            "recommendation": {
                "workout_id": recommendation.workout_id,
                "eligible_workouts": recommendation.eligible_workouts,
                "blocked_workouts": recommendation.blocked_workouts,
                "next_available_at": recommendation.next_available_at.isoformat()
                if recommendation.next_available_at
                else None,
            },
            "exercise_recommendations": {
                item["id"]: recommend_exercises(
                    item, self.data.exercises, self.data.history
                )
                for item in self.data.workouts
            },
        }

    async def save(self) -> None:
        await self.storage.async_save(self.data)
        async_dispatcher_send(self.hass, SIGNAL_UPDATE, self.entry_id)

    async def mutate(
        self, collection: str, value: dict[str, Any], item_id: str | None = None
    ) -> dict[str, Any]:
        async with self._lock:
            values = getattr(self.data, collection)
            value = {**value, "id": item_id or value.get("id") or new_id()}
            self._validate_item(collection, value, item_id)
            if item_id:
                for index, item in enumerate(values):
                    if item.get("id") == item_id:
                        values[index] = value
                        break
                else:
                    raise ValueError("Not found")
            else:
                if any(item.get("id") == value["id"] for item in values):
                    raise ValueError("Duplicate id")
                values.append(value)
            await self.save()
            return value

    def _validate_item(
        self, collection: str, value: dict[str, Any], item_id: str | None
    ) -> None:
        if (
            collection
            in {
                "muscle_groups",
                "exercises",
                "workouts",
                "activities",
            }
            and not str(value.get("name", "")).strip()
        ):
            raise ValueError("Name is required")
        if collection == "exercises" and not any(
            item.get("id") == value.get("muscle_group_id")
            for item in self.data.muscle_groups
        ):
            raise ValueError("Unknown muscle group")
        if collection == "workouts":
            requirements = value.get("requirements")
            if not isinstance(requirements, list) or not requirements:
                raise ValueError("At least one muscle group is required")
            groups = [item.get("muscle_group_id") for item in requirements]
            if len(groups) != len(set(groups)):
                raise ValueError("A muscle group can only appear once per workout")
            known = {item.get("id") for item in self.data.muscle_groups}
            if any(item.get("muscle_group_id") not in known for item in requirements):
                raise ValueError("Unknown muscle group in workout")
            if any(int(item.get("exercise_count") or 0) < 1 for item in requirements):
                raise ValueError("Exercise quantity must be at least one")
        if collection == "conflict_rules":
            source_type = value.get("source_type")
            source_items = (
                self.data.activities
                if source_type == "activity"
                else self.data.workouts
            )
            if source_type not in {"activity", "workout"} or not any(
                item.get("id") == value.get("source_id") for item in source_items
            ):
                raise ValueError("Unknown conflict source")
            if not any(
                item.get("id") == value.get("target_workout_id")
                for item in self.data.workouts
            ):
                raise ValueError("Unknown target workout")
            if float(value.get("recovery_hours") or 0) <= 0:
                raise ValueError("Recovery must be greater than zero")
            duplicate = any(
                item.get("id") != item_id
                and item.get("source_type") == source_type
                and item.get("source_id") == value.get("source_id")
                and item.get("target_workout_id") == value.get("target_workout_id")
                for item in self.data.conflict_rules
            )
            if duplicate:
                raise ValueError("This conflict rule already exists")

    async def delete(self, collection: str, item_id: str) -> None:
        async with self._lock:
            if collection == "muscle_groups" and (
                any(x.get("muscle_group_id") == item_id for x in self.data.exercises)
                or any(
                    item_id
                    in [r.get("muscle_group_id") for r in x.get("requirements", [])]
                    for x in self.data.workouts
                )
            ):
                raise ValueError("Item is still referenced")
            if (
                collection == "workouts"
                and self.data.active_session
                and self.data.active_session.get("workout_id") == item_id
            ):
                raise ValueError("Active workout is using this item")
            setattr(
                self.data,
                collection,
                [x for x in getattr(self.data, collection) if x.get("id") != item_id],
            )
            await self.save()

    async def start(self, workout_id: str) -> dict[str, Any]:
        if self.data.active_session:
            raise ValueError("A workout is already active")
        if not any(x.get("id") == workout_id for x in self.data.workouts):
            raise ValueError("Unknown workout")
        self.data.active_session = {
            "workout_id": workout_id,
            "started_at": dt_util.now().isoformat(),
            "selected_exercise_ids": [],
        }
        await self.save()
        return self.data.active_session

    async def update_session(self, selected: list[str]) -> dict[str, Any]:
        if not self.data.active_session:
            raise ValueError("No active workout")
        self.data.active_session["selected_exercise_ids"] = selected
        await self.save()
        return self.data.active_session

    async def finish(self) -> dict[str, Any]:
        session = self.data.active_session
        if not session:
            raise ValueError("No active workout")
        workout = next(
            x for x in self.data.workouts if x["id"] == session["workout_id"]
        )
        selected = set(session["selected_exercise_ids"])
        exercises = [x for x in self.data.exercises if x.get("id") in selected]
        now = dt_util.now()
        entry = {
            "id": new_id(),
            "kind": "workout",
            "workout_id": workout["id"],
            "workout_name": workout.get("name", workout["id"]),
            "started_at": session["started_at"],
            "finished_at": now.isoformat(),
            "exercises": [
                {
                    "exercise_id": x["id"],
                    "exercise_name": x.get("name", x["id"]),
                    "muscle_group_id": x.get("muscle_group_id"),
                }
                for x in exercises
            ],
        }
        self.data.history.append(entry)
        self.data.active_session = None
        await self.save()
        return entry

    async def cancel(self) -> None:
        self.data.active_session = None
        await self.save()

    async def log_activity(
        self,
        activity_id: str,
        when: datetime | None = None,
        duration_minutes: int | None = None,
    ) -> dict[str, Any]:
        activity = resolve_activity(self.data.activities, activity_id)
        if not activity:
            available = ", ".join(
                str(item.get("name", item.get("id"))) for item in self.data.activities
            )
            suffix = f" Available activities: {available}." if available else "."
            raise ValueError(f"Unknown activity '{activity_id}'.{suffix}")
        if duration_minutes is not None and duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        entry = {
            "id": new_id(),
            "kind": "activity",
            "activity_id": activity_id,
            "activity_name": activity.get("name", activity_id),
            "performed_at": (when or dt_util.now()).isoformat(),
        }
        if duration_minutes is not None:
            entry["duration_minutes"] = duration_minutes
        self.data.history.append(entry)
        await self.save()
        return entry
