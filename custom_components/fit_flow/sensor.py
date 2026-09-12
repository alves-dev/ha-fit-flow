"""FitFlow recommendation and lifetime counter sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, INTEGRATION_NAME, SIGNAL_UPDATE
from .coordinator import FitFlowCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback
) -> None:
    coordinator: FitFlowCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        LastActivitySensor(coordinator),
        NextWorkoutSensor(coordinator),
    ]
    entities.extend(
        CountSensor(coordinator, "workout", item) for item in coordinator.data.workouts
    )
    entities.extend(
        CountSensor(coordinator, "activity", item)
        for item in coordinator.data.activities
    )
    add(entities)


class FitFlowSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: FitFlowCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name=INTEGRATION_NAME,
            manufacturer=INTEGRATION_NAME,
            model="Workout manager",
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self._updated)
        )

    def _updated(self, entry_id: str) -> None:
        if entry_id == self.coordinator.entry_id:
            self.hass.loop.call_soon_threadsafe(self.async_write_ha_state)


class NextWorkoutSensor(FitFlowSensor):
    _attr_icon = "mdi:arm-flex"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_next_workout"
        self._attr_name = "Next Workout"

    @property
    def native_value(self):
        recommendation = self.coordinator.recommendation
        return next(
            (
                x.get("name", x["id"])
                for x in self.coordinator.data.workouts
                if x["id"] == recommendation.workout_id
            ),
            None,
        )

    @property
    def extra_state_attributes(self):
        recommendation = self.coordinator.recommendation
        return {
            "workout_id": recommendation.workout_id,
            "eligible_workouts": recommendation.eligible_workouts,
            "blocked_workouts": list(recommendation.blocked_workouts),
            "next_available_at": recommendation.next_available_at,
        }


class LastActivitySensor(FitFlowSensor):
    _attr_icon = "mdi:history"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_last_activity"
        self._attr_name = "Last Activity"

    @property
    def _last(self):
        return max(
            self.coordinator.data.history,
            key=lambda x: x.get("finished_at", x.get("performed_at", "")),
            default=None,
        )

    @property
    def native_value(self):
        item = self._last
        return item.get("workout_name", item.get("activity_name")) if item else None

    @property
    def extra_state_attributes(self):
        item = self._last
        if not item:
            return {}
        return {
            key: value for key, value in item.items() if key not in ("id", "exercises")
        }


class CountSensor(FitFlowSensor):
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, kind, item):
        super().__init__(coordinator)
        self.kind, self.item = kind, item
        self._attr_unique_id = f"{coordinator.entry_id}_{kind}_{item['id']}_count"
        self._attr_name = f"{item.get('name', item['id'])} Count"
        self._attr_icon = "mdi:counter"

    @property
    def native_value(self):
        return sum(
            1
            for x in self.coordinator.data.history
            if x.get("kind") == self.kind
            and x.get(f"{self.kind}_id") == self.item["id"]
        )
