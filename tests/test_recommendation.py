from datetime import UTC, datetime, timedelta

from custom_components.fit_flow.coordinator import resolve_activity
from custom_components.fit_flow.models import FitFlowData
from custom_components.fit_flow.recommendation import recommend, recommend_exercises
from custom_components.fit_flow.repairs import get_repair_issues

NOW = datetime(2026, 9, 12, 12, tzinfo=UTC)


def test_activity_can_be_resolved_by_display_name():
    activities = [{"id": "running", "name": "Corrida"}]

    assert resolve_activity(activities, " corrida ") == activities[0]


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
    assert result.alternate_workout_id == "b"


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


def test_recommendation_accepts_history_dates_without_timezone():
    result = recommend(
        [{"id": "a"}],
        [
            {
                "source_type": "activity",
                "source_id": "run",
                "target_workout_id": "a",
                "recovery_hours": 4,
            }
        ],
        [
            {
                "kind": "activity",
                "activity_id": "run",
                "performed_at": "2026-09-12T07:00:00",
            }
        ],
        NOW,
    )

    assert result.workout_id == "a"


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


def test_repairs_report_unlinked_and_empty_muscle_groups():
    issues = get_repair_issues(
        FitFlowData(
            muscle_groups=[
                {"id": "chest", "name": "Peito"},
                {"id": "back", "name": "Costas"},
                {"id": "legs", "name": "Pernas"},
            ],
            exercises=[
                {
                    "id": "row",
                    "name": "Remada",
                    "muscle_group_id": "back",
                    "image_url": "https://example.com/row.jpg",
                }
            ],
            workouts=[
                {
                    "id": "upper",
                    "requirements": [{"muscle_group_id": "chest", "exercise_count": 1}],
                }
            ],
        )
    )

    actual = {
        (issue.translation_key, issue.placeholders["muscle_group"])
        for issue in issues
    }
    assert actual == {
        ("empty_muscle_group", "Peito"),
        ("unused_muscle_group", "Costas"),
        ("unused_muscle_group", "Pernas"),
        ("empty_muscle_group", "Pernas"),
    }


def test_repairs_group_duplicate_exercise_names_case_insensitively():
    issues = get_repair_issues(
        FitFlowData(
            exercises=[
                {
                    "id": "one",
                    "name": "Supino Reto",
                    "image_url": "https://example.com/one.jpg",
                },
                {
                    "id": "two",
                    "name": " supino reto ",
                    "image_url": "https://example.com/two.jpg",
                },
                {
                    "id": "three",
                    "name": "Agachamento",
                    "image_url": "https://example.com/three.jpg",
                },
            ]
        )
    )

    assert [(issue.translation_key, issue.placeholders) for issue in issues] == [
        (
            "duplicate_exercise_name",
            {"exercise_name": "Supino Reto", "count": "2"},
        )
    ]


def test_repairs_find_duplicate_activity_records_in_recent_five_days():
    issues = get_repair_issues(
        FitFlowData(
            activities=[{"id": "volleyball", "name": "Vôlei"}],
            history=[
                {
                    "id": "one",
                    "kind": "activity",
                    "activity_id": "Vôlei",
                    "activity_name": "Vôlei",
                    "performed_at": "2026-09-17T18:00:00+00:00",
                },
                {
                    "id": "two",
                    "kind": "activity",
                    "activity_id": "volleyball",
                    "activity_name": "Vôlei",
                    "performed_at": "2026-09-17T20:00:00+00:00",
                },
            ],
        )
    )

    assert any(
        issue.translation_key == "duplicate_activity"
        and issue.placeholders["count"] == "2"
        for issue in issues
    )
