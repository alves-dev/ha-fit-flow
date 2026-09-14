"""Dynamic workout and exercise recommendation engines."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .models import Recommendation


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = dt_util.parse_datetime(value)
    return dt_util.as_utc(parsed) if parsed else None


def latest_workout(history: list[dict[str, Any]], workout_id: str) -> datetime | None:
    values = [
        _parse(item.get("finished_at"))
        for item in history
        if item.get("kind") == "workout" and item.get("workout_id") == workout_id
    ]
    return max((value for value in values if value), default=None)


def recommend(
    workouts: list[dict[str, Any]],
    activities: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    history: list[dict[str, Any]],
    now: datetime,
) -> Recommendation:
    now = dt_util.as_utc(now)
    blocked: dict[str, dict[str, Any]] = {}
    for rule in rules:
        target = rule.get("target_workout_id")
        source_id = rule.get("source_id")
        source_type = rule.get("source_type")
        if not target or not source_id or source_type not in ("workout", "activity"):
            continue
        occurrences = []
        for item in history:
            if (
                source_type == "workout"
                and item.get("kind") == "workout"
                and item.get("workout_id") == source_id
            ):
                occurrences.append(_parse(item.get("finished_at")))
            if (
                source_type == "activity"
                and item.get("kind") == "activity"
                and item.get("activity_id") == source_id
            ):
                occurrences.append(_parse(item.get("performed_at")))
        for occurrence in (value for value in occurrences if value):
            until = occurrence + timedelta(hours=float(rule.get("recovery_hours", 0)))
            if until > now and (
                target not in blocked or until > _parse(blocked[target]["until"])
            ):
                blocked[target] = {
                    "source": source_id,
                    "source_type": source_type,
                    "until": until.isoformat(),
                }
    eligible = [item["id"] for item in workouts if item.get("id") not in blocked]
    eligible.sort(
        key=lambda item: (
            latest_workout(history, item) is not None,
            latest_workout(history, item) or datetime.min,
            item,
        )
    )
    next_available = min(
        (_parse(item["until"]) for item in blocked.values()), default=None
    )
    return Recommendation(
        eligible[0] if eligible else None,
        eligible,
        blocked,
        next_available,
        eligible[1] if len(eligible) > 1 else None,
    )


def recommend_exercises(
    workout: dict[str, Any],
    exercises: list[dict[str, Any]],
    history: list[dict[str, Any]],
) -> dict[str, list[str]]:
    last: dict[str, datetime] = {}
    for item in history:
        if item.get("kind") != "workout":
            continue
        when = _parse(item.get("finished_at"))
        for exercise in item.get("exercises", []):
            if when and (
                exercise.get("exercise_id") not in last
                or when > last[exercise["exercise_id"]]
            ):
                last[exercise["exercise_id"]] = when
    result = {}
    for requirement in workout.get("requirements", []):
        group = requirement["muscle_group_id"]
        candidates = [
            item for item in exercises if item.get("muscle_group_id") == group
        ]
        candidates.sort(
            key=lambda item: (
                item["id"] in last,
                last.get(item["id"], datetime.min.replace(tzinfo=dt_util.UTC)),
                item.get("name", ""),
                item["id"],
            )
        )
        requested = requirement.get("exercise_count") or 1
        result[group] = [item["id"] for item in candidates[: int(requested)]]
    return result
