from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from custom_components.fit_flow import (
    async_remove_entry,
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.fit_flow.config_flow import FitFlowConfigFlow
from custom_components.fit_flow.models import FitFlowData, Recommendation
from custom_components.fit_flow.panel import _coordinator
from custom_components.fit_flow.repairs import get_repair_issues
from custom_components.fit_flow.sensor import (
    AlternateWorkoutSensor,
    CountSensor,
    LastActivitySensor,
    NextWorkoutSensor,
)
from custom_components.fit_flow.sensor import (
    async_setup_entry as async_setup_sensor_entry,
)
from custom_components.fit_flow.services import async_register_services


class FakeServices:
    def __init__(self):
        self.handlers = {}

    def has_service(self, domain, service):
        return (domain, service) in self.handlers

    def async_register(self, domain, service, handler, **_kwargs):
        self.handlers[(domain, service)] = handler


class FakeConfigEntries:
    def __init__(self, entries=None):
        self.entries = entries or []
        self.forwarded = []

    def async_entries(self, _domain):
        return self.entries

    async def async_forward_entry_setups(self, entry, platforms):
        self.forwarded.append((entry, platforms))

    async def async_unload_platforms(self, entry, platforms):
        return True


class FakeHass:
    def __init__(self, entries=None):
        self.config_entries = FakeConfigEntries(entries)
        self.services = FakeServices()
        self.data = {}


@pytest.mark.asyncio
async def test_integration_setup_and_entry_lifecycle():
    hass = FakeHass()
    with (
        patch(
            "custom_components.fit_flow.async_register_panel", new_callable=AsyncMock
        ) as panel,
        patch(
            "custom_components.fit_flow.async_register_services", new_callable=AsyncMock
        ) as services,
    ):
        assert await async_setup(hass, {})
        panel.assert_awaited_once_with(hass)
        services.assert_awaited_once_with(hass)

    entry = SimpleNamespace(entry_id="entry")
    coordinator = SimpleNamespace(
        async_setup=AsyncMock(),
        data=FitFlowData(),
        storage=SimpleNamespace(async_remove=AsyncMock()),
    )
    with (
        patch(
            "custom_components.fit_flow.FitFlowCoordinator", return_value=coordinator
        ),
        patch("custom_components.fit_flow.async_update_repairs") as repairs,
    ):
        assert await async_setup_entry(hass, entry)
    assert hass.data["fit_flow"]["entry"] is coordinator
    coordinator.async_setup.assert_awaited_once()
    repairs.assert_called_once_with(hass, coordinator.data)
    assert hass.config_entries.forwarded == [(entry, ("sensor",))]

    with patch("custom_components.fit_flow.async_clear_repairs") as clear:
        await async_remove_entry(hass, entry)
        clear.assert_called_once_with(hass)
    coordinator.storage.async_remove = AsyncMock()
    hass.data["fit_flow"]["entry"] = coordinator
    with patch("custom_components.fit_flow.async_clear_repairs"):
        await async_remove_entry(hass, entry)
    coordinator.storage.async_remove.assert_awaited_once()

    hass.data["fit_flow"] = {"entry": coordinator}
    with patch.object(
        hass.config_entries, "async_unload_platforms", new=AsyncMock(return_value=True)
    ) as unload:
        assert await async_unload_entry(hass, entry)
    unload.assert_awaited_once()
    assert "entry" not in hass.data["fit_flow"]


@pytest.mark.asyncio
async def test_config_flow_shows_form_creates_entry_and_blocks_duplicates():
    flow = FitFlowConfigFlow()
    flow._async_current_entries = lambda: []
    form = await flow.async_step_user()
    assert form["type"] == "form"
    flow._async_current_entries = lambda: [object()]
    assert (await flow.async_step_user())["reason"] == "single_instance_allowed"

    flow = FitFlowConfigFlow()
    flow._async_current_entries = lambda: []
    result = await flow.async_step_user({})
    assert result["type"] == "create_entry"
    assert result["title"] == "FitFlow"


def sensor_coordinator():
    return SimpleNamespace(
        entry_id="entry",
        data=FitFlowData(
            workouts=[{"id": "upper", "name": "Superior"}],
            activities=[{"id": "run", "name": "Corrida"}],
            history=[
                {
                    "kind": "workout",
                    "workout_id": "upper",
                    "workout_name": "Superior",
                    "finished_at": "2026-09-16T10:00:00+00:00",
                },
                {
                    "kind": "activity",
                    "activity_id": "run",
                    "activity_name": "Corrida",
                    "performed_at": "2026-09-17T10:00:00+00:00",
                },
            ],
        ),
        recommendation=Recommendation(
            "upper", ["upper"], {}, alternate_workout_id=None
        ),
    )


def test_sensor_entities_expose_values_attributes_and_counts():
    coordinator = sensor_coordinator()
    assert NextWorkoutSensor(coordinator).native_value == "Superior"
    assert (
        NextWorkoutSensor(coordinator).extra_state_attributes["workout_id"] == "upper"
    )
    assert AlternateWorkoutSensor(coordinator).native_value is None
    assert AlternateWorkoutSensor(coordinator).extra_state_attributes == {
        "workout_id": None
    }
    last = LastActivitySensor(coordinator)
    assert last.native_value == "Corrida"
    assert last.extra_state_attributes["activity_id"] == "run"
    assert (
        LastActivitySensor(
            SimpleNamespace(entry_id="empty", data=FitFlowData())
        ).native_value
        is None
    )
    assert (
        CountSensor(
            coordinator, "workout", {"id": "upper", "name": "Superior"}
        ).native_value
        == 1
    )
    assert (
        CountSensor(
            coordinator, "activity", {"id": "run", "name": "Corrida"}
        ).native_value
        == 1
    )


@pytest.mark.asyncio
async def test_sensor_setup_creates_recommendation_and_counter_entities():
    coordinator = sensor_coordinator()
    hass = FakeHass()
    hass.data["fit_flow"] = {"entry": coordinator}
    entry = SimpleNamespace(entry_id="entry")
    added = []
    await async_setup_sensor_entry(hass, entry, added.extend)
    assert len(added) == 5
    assert {entity._attr_unique_id for entity in added} == {
        "entry_next_workout",
        "entry_alternate_workout",
        "entry_last_activity",
        "entry_workout_upper_count",
        "entry_activity_run_count",
    }


@pytest.mark.asyncio
async def test_services_register_and_dispatch_calls():
    entry = SimpleNamespace(entry_id="entry")
    hass = FakeHass([entry])
    coordinator = SimpleNamespace(
        log_activity=AsyncMock(), async_check_recommendation=Mock()
    )
    hass.data["fit_flow"] = {"entry": coordinator}
    await async_register_services(hass)
    await hass.services.handlers[("fit_flow", "log_activity")](
        SimpleNamespace(data={"activity": "run", "duration_minutes": 20})
    )
    coordinator.log_activity.assert_awaited_once_with("run", None, 20)
    await hass.services.handlers[("fit_flow", "check_next_workout")](None)
    coordinator.async_check_recommendation.assert_called_once()

    empty = FakeHass()
    await async_register_services(empty)
    with pytest.raises(Exception, match="not configured"):
        await empty.services.handlers[("fit_flow", "log_activity")](
            SimpleNamespace(data={"activity": "run"})
        )


def test_panel_coordinator_requires_configuration():
    hass = FakeHass()
    with pytest.raises(Exception, match="not configured"):
        _coordinator(hass)
    coordinator = object()
    hass.data["fit_flow"] = {"entry": coordinator}
    hass.config_entries.entries = [SimpleNamespace(entry_id="entry")]
    assert _coordinator(hass) is coordinator


def test_repairs_identify_exercises_without_image_links():
    issues = get_repair_issues(
        FitFlowData(
            exercises=[
                {"id": "squat", "name": "Agachamento", "image_url": ""},
                {
                    "id": "press",
                    "name": "Supino",
                    "image_url": "https://example.com/press.gif",
                },
            ]
        )
    )

    assert [(issue.issue_id, issue.translation_key) for issue in issues] == [
        ("missing_exercise_image_squat", "missing_exercise_image")
    ]
