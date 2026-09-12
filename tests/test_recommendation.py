from datetime import UTC, datetime, timedelta

from custom_components.fit_flow.recommendation import recommend, recommend_exercises

NOW = datetime(2026, 9, 12, 12, tzinfo=UTC)


def test_never_performed_wins_and_conflicts_are_directional():
    workouts = [
        {"id": "a", "name": "A"},
        {"id": "b", "name": "B"},
        {"id": "d", "name": "D"},
    ]
    history = [
        {
            "kind": "workout",
            "workout_id": "b",
                "finished_at": (NOW - timedelta(hours=24)).isoformat(),
        }
    ]
    result = recommend(
        workouts,
        [],
        [
            {
                "source_type": "workout",
                "source_id": "b",
                "target_workout_id": "d",
                "recovery_hours": 48,
            }
        ],
        history,
        NOW,
    )
    assert result.workout_id == "a"
    assert "d" in result.blocked_workouts
    assert "b" in result.eligible_workouts


def test_all_blocked_reports_next_expiration():
    workouts = [{"id": "a"}]
    history = [
        {
            "kind": "activity",
            "activity_id": "run",
            "performed_at": (NOW - timedelta(hours=1)).isoformat(),
        }
    ]
    result = recommend(
        workouts,
        [],
        [
            {
                "source_type": "activity",
                "source_id": "run",
                "target_workout_id": "a",
                "recovery_hours": 4,
            }
        ],
        history,
        NOW,
    )
    assert result.workout_id is None
    assert result.next_available_at == NOW + timedelta(hours=3)


def test_exercises_never_used_are_recommended_first():
    workout = {
        "id": "a",
        "requirements": [{"muscle_group_id": "chest", "exercise_count": 2}],
    }
    exercises = [
        {"id": "old", "name": "Old", "muscle_group_id": "chest"},
        {"id": "new", "name": "New", "muscle_group_id": "chest"},
    ]
    history = [
        {
            "kind": "workout",
            "finished_at": NOW.isoformat(),
            "exercises": [{"exercise_id": "old"}],
        }
    ]
    assert recommend_exercises(workout, exercises, history)["chest"] == ["new", "old"]
