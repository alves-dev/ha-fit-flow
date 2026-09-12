"""Public FitFlow Home Assistant actions."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("activity"): cv.string,
        vol.Optional("datetime"): cv.datetime,
        vol.Optional("duration_minutes"): vol.All(vol.Coerce(int), vol.Range(min=1)),
    }
)


async def async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, "log_activity"):
        return

    async def handle(call: ServiceCall) -> None:
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("FitFlow is not configured")
        coordinator = hass.data[DOMAIN][entries[0].entry_id]
        try:
            await coordinator.log_activity(
                call.data["activity"],
                call.data.get("datetime"),
                call.data.get("duration_minutes"),
            )
        except ValueError as error:
            raise HomeAssistantError(str(error)) from error

    hass.services.async_register(DOMAIN, "log_activity", handle, schema=SERVICE_SCHEMA)
