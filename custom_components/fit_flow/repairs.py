"""FitFlow data-quality issues shown in Home Assistant Repairs."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN
from .models import FitFlowData

_ISSUE_PREFIXES = (
    "unused_muscle_group_",
    "empty_muscle_group_",
    "duplicate_exercise_name_",
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


def get_repair_issues(data: FitFlowData) -> list[RepairIssue]:
    """Return the current data-quality issues for a FitFlow data set."""
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

    exercises_by_name: defaultdict[str, list[str]] = defaultdict(list)
    for exercise in data.exercises:
        normalized = _normalized_name(exercise.get("name"))
        if normalized:
            exercises_by_name[normalized].append(_name(exercise.get("name")))

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
