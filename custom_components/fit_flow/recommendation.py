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


def _rule_occurrences(
    rule: dict[str, Any], history: list[dict[str, Any]]
) -> list[datetime]:
    source_type = rule.get("source_type")
    source_id = rule.get("source_id")
    date_key = "finished_at" if source_type == "workout" else "performed_at"
    return [
        occurrence
        for item in history
        if item.get("kind") == source_type
        and item.get(f"{source_type}_id") == source_id
        for occurrence in [_parse(item.get(date_key))]
        if occurrence
    ]


def _blocked_workout(
    rule: dict[str, Any], history: list[dict[str, Any]], now: datetime
) -> dict[str, Any] | None:
    target = rule.get("target_workout_id")
    source_id = rule.get("source_id")
    source_type = rule.get("source_type")
    if not target or not source_id or source_type not in ("workout", "activity"):
        return None
    recovery = timedelta(hours=float(rule.get("recovery_hours", 0)))
    until = max(
        (occurrence + recovery for occurrence in _rule_occurrences(rule, history)),
        default=None,
    )
    if until is None or until <= now:
        return None
    return {"source": source_id, "source_type": source_type, "until": until.isoformat()}


def recommend(
    workouts: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    history: list[dict[str, Any]],
    now: datetime,
) -> Recommendation:
    now = dt_util.as_utc(now)
    blocked: dict[str, dict[str, Any]] = {}
    for rule in rules:
        blocked_workout = _blocked_workout(rule, history, now)
        target = rule.get("target_workout_id")
        if blocked_workout and target:
            current = blocked.get(target)
            if not current or _parse(blocked_workout["until"]) > _parse(
                current["until"]
            ):
                blocked[target] = blocked_workout
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
