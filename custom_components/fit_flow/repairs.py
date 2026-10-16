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
    "duplicate_record_",
    "missing_exercise_image_",
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


def _missing_exercise_image_issues(data: FitFlowData) -> list[RepairIssue]:
    issues: list[RepairIssue] = []
    for exercise in data.exercises:
        if _name(exercise.get("image_url")):
            continue
        exercise_id = str(exercise.get("id") or "unknown")
        issues.append(
            RepairIssue(
                f"missing_exercise_image_{exercise_id}",
                "missing_exercise_image",
                {"exercise_name": _name(exercise.get("name")) or exercise_id},
            )
        )
    return issues


def _recent_day(
    timestamp_value: Any, recent_start: object, today: object
) -> object | None:
    timestamp = dt_util.parse_datetime(timestamp_value or "")
    if not timestamp:
        return None
    day = dt_util.as_local(timestamp).date()
    return day if recent_start <= day <= today else None


def _recent_record_day(
    entry: dict[str, Any], recent_start: object, today: object
) -> object | None:
    timestamp_key = "performed_at" if entry.get("kind") == "activity" else "finished_at"
    return _recent_day(entry.get(timestamp_key), recent_start, today)


def _duplicate_record_issue(day: object, entries: list[dict[str, Any]]) -> RepairIssue:
    digest = hashlib.sha256(f"{day}".encode()).hexdigest()[:16]
    return RepairIssue(
        f"duplicate_record_{digest}",
        "duplicate_record",
        {
            "record_type": "treinos e atividades",
            "record_name": "histórico do FitFlow",
            "date": day.isoformat(),
            "count": str(len(entries)),
        },
    )


def _duplicate_record_issues(data: FitFlowData) -> list[RepairIssue]:
    issues: list[RepairIssue] = []
    today = dt_util.as_local(dt_util.now()).date()
    recent_start = today - timedelta(days=4)
    records_by_day: defaultdict[object, list[dict[str, Any]]] = defaultdict(list)
    for entry in data.history:
        day = _recent_record_day(entry, recent_start, today)
        if day is not None:
            records_by_day[day].append(entry)
    for day, entries in records_by_day.items():
        if len(entries) < 2:
            continue
        issues.append(_duplicate_record_issue(day, entries))
    return issues


def get_repair_issues(data: FitFlowData) -> list[RepairIssue]:
    """Return the current data-quality issues for a FitFlow data set."""
    return [
        *_muscle_group_issues(data),
        *_duplicate_exercise_issues(data),
        *_missing_exercise_image_issues(data),
        *_duplicate_record_issues(data),
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
