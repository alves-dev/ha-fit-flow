"""Pure domain models and serialization helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


def new_id() -> str:
    return uuid4().hex


@dataclass
class Recommendation:
    workout_id: str | None
    eligible_workouts: list[str] = field(default_factory=list)
    blocked_workouts: dict[str, dict[str, Any]] = field(default_factory=dict)
    next_available_at: datetime | None = None
    alternate_workout_id: str | None = None


@dataclass
class FitFlowData:
    muscle_groups: list[dict[str, Any]] = field(default_factory=list)
    exercises: list[dict[str, Any]] = field(default_factory=list)
    workouts: list[dict[str, Any]] = field(default_factory=list)
    activities: list[dict[str, Any]] = field(default_factory=list)
    conflict_rules: list[dict[str, Any]] = field(default_factory=list)
    active_session: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"version": 1, **self.__dict__}
