"""FitFlow data-quality issues shown in Home Assistant Repairs."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .models import FitFlowData

_ISSUE_PREFIXES = (
    "unused_muscle_group_",
    "empty_muscle_group_",
    "duplicate_exercise_name_",
    "duplicate_activity_",
)


@dataclass(frozen=True)
class RepairIssue:
    """The translated details needed to create a Repairs issue."""

    issue_id: str
    translation_key: str
    placeholders: dict[str, str]


def _name(value: Any) -> str:
    return str(value or "").strip()


def _normalized_name(value: Any) -> str:
    return _name(value).casefold()


def _muscle_group_issues(data: FitFlowData) -> list[RepairIssue]:
    issues: list[RepairIssue] = []
    workout_groups = {
        requirement.get("muscle_group_id")
        for workout in data.workouts
        for requirement in workout.get("requirements", [])
    }
    exercise_groups = {exercise.get("muscle_group_id") for exercise in data.exercises}

    for group in data.muscle_groups:
        group_id = group.get("id")
        group_name = _name(group.get("name")) or str(group_id)
        if group_id not in workout_groups:
            issues.append(
                RepairIssue(
                    f"unused_muscle_group_{group_id}",
                    "unused_muscle_group",
                    {"muscle_group": group_name},
                )
            )
        if group_id not in exercise_groups:
            issues.append(
                RepairIssue(
                    f"empty_muscle_group_{group_id}",
                    "empty_muscle_group",
                    {"muscle_group": group_name},
                )
            )

    return issues


def _duplicate_exercise_issues(data: FitFlowData) -> list[RepairIssue]:
    exercises_by_name: defaultdict[str, list[str]] = defaultdict(list)
    for exercise in data.exercises:
        normalized = _normalized_name(exercise.get("name"))
        if normalized:
            exercises_by_name[normalized].append(_name(exercise.get("name")))

    issues: list[RepairIssue] = []
    for normalized, names in exercises_by_name.items():
        if len(names) < 2:
            continue
        issue_id = hashlib.sha256(normalized.encode()).hexdigest()[:16]
        issues.append(
            RepairIssue(
                f"duplicate_exercise_name_{issue_id}",
                "duplicate_exercise_name",
                {"exercise_name": names[0], "count": str(len(names))},
            )
        )

    return issues


def _recent_activity_key(
    entry: dict[str, Any],
    activities: dict[str, dict[str, Any]],
    configured_activities: list[dict[str, Any]],
    recent_start: object,
    today: object,
) -> tuple[str, object] | None:
    if entry.get("kind") != "activity":
        return None
    timestamp = dt_util.parse_datetime(entry.get("performed_at", ""))
    if not timestamp:
        return None
    day = dt_util.as_local(timestamp).date()
    if not recent_start <= day <= today:
        return None
    activity_id = entry.get("activity_id")
    activity = activities.get(activity_id) or next(
        (
            item
            for item in configured_activities
            if _normalized_name(item.get("name"))
            == _normalized_name(entry.get("activity_name"))
        ),
        None,
    )
    canonical_id = activity.get("id") if activity else activity_id
    return str(canonical_id or entry.get("activity_name", "")), day


def _duplicate_activity_issue(
    activity_id: str,
    day: object,
    entries: list[dict[str, Any]],
    activities: dict[str, dict[str, Any]],
) -> RepairIssue:
    activity = activities.get(activity_id)
    name = (
        _name(activity.get("name") if activity else None)
        or _name(entries[0].get("activity_name"))
        or activity_id
    )
    digest = hashlib.sha256(f"{activity_id}:{day}".encode()).hexdigest()[:16]
    return RepairIssue(
        f"duplicate_activity_{digest}",
        "duplicate_activity",
        {"activity": name, "date": day.isoformat(), "count": str(len(entries))},
    )


def _duplicate_activity_issues(data: FitFlowData) -> list[RepairIssue]:
    issues: list[RepairIssue] = []
    activities = {item.get("id"): item for item in data.activities}
    today = dt_util.as_local(dt_util.now()).date()
    recent_start = today - timedelta(days=4)
    activity_days: defaultdict[tuple[str, object], list[dict[str, Any]]] = defaultdict(
        list
    )
    for entry in data.history:
        key = _recent_activity_key(
            entry, activities, data.activities, recent_start, today
        )
        if key:
            activity_days[key].append(entry)
    for (activity_id, day), entries in activity_days.items():
        if len(entries) < 2:
            continue
        issues.append(_duplicate_activity_issue(activity_id, day, entries, activities))
    return issues


def get_repair_issues(data: FitFlowData) -> list[RepairIssue]:
    """Return the current data-quality issues for a FitFlow data set."""
    return [
        *_muscle_group_issues(data),
        *_duplicate_exercise_issues(data),
        *_duplicate_activity_issues(data),
    ]


@callback
def async_update_repairs(hass: HomeAssistant, data: FitFlowData) -> None:
    """Synchronize FitFlow's current data-quality issues with HA Repairs."""
    issues = get_repair_issues(data)
    current = {issue.issue_id for issue in issues}
    registry = ir.async_get(hass)
    for issue in issues:
        ir.async_create_issue(
            hass,
            DOMAIN,
            issue.issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=issue.translation_key,
            translation_placeholders=issue.placeholders,
        )
    for domain, issue_id in tuple(registry.issues):
        if (
            domain == DOMAIN
            and issue_id.startswith(_ISSUE_PREFIXES)
            and issue_id not in current
        ):
            ir.async_delete_issue(hass, DOMAIN, issue_id)


@callback
def async_clear_repairs(hass: HomeAssistant) -> None:
    """Remove FitFlow data-quality issues when the integration is removed."""
    registry = ir.async_get(hass)
    for domain, issue_id in tuple(registry.issues):
        if domain == DOMAIN and issue_id.startswith(_ISSUE_PREFIXES):
            ir.async_delete_issue(hass, DOMAIN, issue_id)
