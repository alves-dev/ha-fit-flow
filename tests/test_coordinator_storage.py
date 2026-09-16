from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from custom_components.fit_flow.coordinator import FitFlowCoordinator
from custom_components.fit_flow.models import FitFlowData
from custom_components.fit_flow.storage import FitFlowStorage


class FakeBus:
    def __init__(self):
        self.events = []

    def async_fire(self, event, data):
        self.events.append((event, data))


class FakeHass:
    def __init__(self):
        self.bus = FakeBus()


class FakeStore:
    payload = None

    def __init__(self, *_args, **_kwargs):
        self.saved = None
        self.removed = False

    async def async_load(self):
        return self.payload

    async def async_save(self, payload):
        self.saved = payload

    async def async_remove(self):
        self.removed = True


@pytest.fixture(autouse=True)
def mock_repairs():
    with patch("custom_components.fit_flow.coordinator.async_update_repairs") as update:
        yield update


@pytest.fixture(autouse=True)
def mock_dispatcher():
    with patch("custom_components.fit_flow.coordinator.async_dispatcher_send") as send:
        yield send


def coordinator_with_data():
    hass = FakeHass()
    storage = SimpleNamespace(
        async_load=AsyncMock(return_value=FitFlowData()),
        async_save=AsyncMock(),
        async_remove=AsyncMock(),
    )
    with patch(
        "custom_components.fit_flow.coordinator.FitFlowStorage", return_value=storage
    ):
        coordinator = FitFlowCoordinator(hass, "entry")
    coordinator.storage = storage
    coordinator.data = FitFlowData(
        muscle_groups=[{"id": "chest", "name": "Peito"}],
        exercises=[
            {"id": "press", "name": "Supino", "muscle_group_id": "chest"},
            {"id": "fly", "name": "Crucifixo", "muscle_group_id": "chest"},
        ],
        workouts=[
            {
                "id": "upper",
                "name": "Superior",
                "requirements": [{"muscle_group_id": "chest", "exercise_count": 1}],
            },
            {"id": "lower", "name": "Inferior", "requirements": []},
        ],
        activities=[{"id": "run", "name": "Corrida"}],
    )
    return coordinator, storage


@pytest.mark.asyncio
async def test_storage_loads_defaults_and_round_trips_data():
    data = FitFlowData(activities=[{"id": "run", "name": "Corrida"}])
    FakeStore.payload = None
    with patch("custom_components.fit_flow.storage.Store", FakeStore):
        storage = FitFlowStorage(SimpleNamespace(), "entry")
        assert await storage.async_load() == FitFlowData()
        await storage.async_save(data)
        assert storage._store.saved == data.as_dict()
        await storage.async_remove()
        assert storage._store.removed

        FakeStore.payload = {"version": 1, "activities": data.activities}
        assert await storage.async_load() == data


@pytest.mark.asyncio
async def test_storage_rejects_unknown_payload_versions():
    FakeStore.payload = {"version": 99}
    with (
        patch("custom_components.fit_flow.storage.Store", FakeStore),
        pytest.raises(ValueError, match="Unsupported"),
    ):
        await FitFlowStorage(SimpleNamespace(), "entry").async_load()

    FakeStore.payload = ["not a mapping"]
    with (
        patch("custom_components.fit_flow.storage.Store", FakeStore),
        pytest.raises(ValueError, match="Unsupported"),
    ):
        await FitFlowStorage(SimpleNamespace(), "entry").async_load()


@pytest.mark.asyncio
async def test_coordinator_setup_snapshot_and_notifications():
    coordinator, storage = coordinator_with_data()
    storage.async_load.return_value = coordinator.data
    await coordinator.async_setup()
    storage.async_load.assert_awaited_once()

    with (
        patch("custom_components.fit_flow.coordinator.async_update_repairs") as repairs,
        patch(
            "custom_components.fit_flow.coordinator.async_dispatcher_send"
        ) as dispatch,
    ):
        await coordinator.save()
        repairs.assert_called_once()
        dispatch.assert_called_once()

    snapshot = coordinator.snapshot()
    assert snapshot["recommendation"]["workout_id"] == "lower"
    assert snapshot["exercise_recommendations"]["upper"] == {"chest": ["fly"]}

    with patch(
        "custom_components.fit_flow.coordinator.async_dispatcher_send"
    ) as dispatch:
        coordinator.async_check_recommendation()
        assert coordinator.hass.bus.events[-1][1] == {"workout_id": "lower"}
        assert dispatch.call_count == 1


@pytest.mark.asyncio
async def test_coordinator_mutations_and_validation():
    coordinator, storage = coordinator_with_data()
    created = await coordinator.mutate("activities", {"name": "Caminhada"})
    assert created["name"] == "Caminhada"
    assert storage.async_save.await_count == 1
    updated = await coordinator.mutate("activities", {"name": "Corrida leve"}, "run")
    assert updated == {"id": "run", "name": "Corrida leve"}

    renamed_group = await coordinator.mutate(
        "muscle_groups", {"name": "Peitoral"}, "chest"
    )
    assert renamed_group == {"id": "chest", "name": "Peitoral"}
    assert coordinator.data.exercises[0]["muscle_group_id"] == "chest"
    assert coordinator.data.workouts[0]["requirements"][0]["muscle_group_id"] == "chest"

    invalid_items = [
        ("activities", {}, "Name is required"),
        (
            "exercises",
            {"name": "X", "muscle_group_id": "missing"},
            "Unknown muscle group",
        ),
        (
            "exercises",
            {"name": "X", "muscle_group_id": "chest", "image_url": "ftp://x"},
            "Image URL",
        ),
        ("workouts", {"name": "X", "requirements": []}, "At least one"),
        (
            "workouts",
            {
                "name": "X",
                "requirements": [
                    {"muscle_group_id": "chest", "exercise_count": 1},
                    {"muscle_group_id": "chest", "exercise_count": 1},
                ],
            },
            "only appear once",
        ),
        (
            "workouts",
            {
                "name": "X",
                "requirements": [{"muscle_group_id": "chest", "exercise_count": 0}],
            },
            "Exercise quantity",
        ),
        (
            "conflict_rules",
            {
                "source_type": "other",
                "source_id": "x",
                "target_workout_id": "upper",
                "recovery_hours": 1,
            },
            "Unknown conflict source",
        ),
        (
            "conflict_rules",
            {
                "source_type": "workout",
                "source_id": "upper",
                "target_workout_id": "missing",
                "recovery_hours": 1,
            },
            "Unknown target",
        ),
        (
            "conflict_rules",
            {
                "source_type": "workout",
                "source_id": "upper",
                "target_workout_id": "lower",
                "recovery_hours": 0,
            },
            "Recovery",
        ),
    ]
    for collection, value, message in invalid_items:
        with pytest.raises(ValueError, match=message):
            await coordinator.mutate(collection, value)

    rule = {
        "source_type": "workout",
        "source_id": "upper",
        "target_workout_id": "lower",
        "recovery_hours": 2,
    }
    await coordinator.mutate("conflict_rules", rule)
    with pytest.raises(ValueError, match="already exists"):
        await coordinator.mutate("conflict_rules", rule)
    await coordinator.mutate(
        "conflict_rules",
        {**rule, "recovery_hours": 3},
        coordinator.data.conflict_rules[0]["id"],
    )


@pytest.mark.asyncio
async def test_coordinator_sessions_and_activity_logging():
    coordinator, _storage = coordinator_with_data()
    with pytest.raises(ValueError, match="Unknown workout"):
        await coordinator.start("missing")
    session = await coordinator.start("upper")
    assert session["workout_id"] == "upper"
    with pytest.raises(ValueError, match="already active"):
        await coordinator.start("upper")
    other, _storage = coordinator_with_data()
    with pytest.raises(ValueError, match="No active"):
        await other.update_session([])
    await coordinator.update_session(["press"])
    entry = await coordinator.finish()
    assert entry["exercises"][0]["exercise_id"] == "press"
    assert coordinator.data.active_session is None

    with pytest.raises(ValueError, match="No active"):
        await coordinator.finish()
    await coordinator.start("upper")
    await coordinator.cancel()
    with pytest.raises(ValueError, match="Unknown activity"):
        await coordinator.log_activity("missing")
    with pytest.raises(ValueError, match="positive"):
        await coordinator.log_activity("run", duration_minutes=0)
    activity = await coordinator.log_activity(
        " corrida ", datetime(2026, 9, 16, 10, tzinfo=UTC), 30
    )
    assert activity["activity_id"] == "run"
    assert activity["duration_minutes"] == 30


@pytest.mark.asyncio
async def test_coordinator_delete_rejects_references_and_removes_items():
    coordinator, _storage = coordinator_with_data()
    with pytest.raises(ValueError, match="History entry"):
        await coordinator.delete("history", "missing")
    coordinator.data.history = [{"id": "history"}]
    await coordinator.delete("history", "history")

    with pytest.raises(ValueError, match="still referenced"):
        await coordinator.delete("muscle_groups", "chest")
    with pytest.raises(ValueError, match="using"):
        coordinator.data.active_session = {"workout_id": "upper"}
        await coordinator.delete("workouts", "upper")
    coordinator.data.active_session = None
    await coordinator.delete("activities", "run")
    assert coordinator.data.activities == []
