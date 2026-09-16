"""FitFlow sidebar panel and websocket API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.components import panel_custom, websocket_api
from homeassistant.components.frontend import async_panel_exists
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, INTEGRATION_VERSION

PANEL_PATH = "fit-flow"
STATIC_PATH = "/fit_flow_panel"
PANEL_ASSET_REVISION = "9"


async def async_register_panel(hass: HomeAssistant) -> None:
    if async_panel_exists(hass, PANEL_PATH):
        return
    frontend = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_PATH, str(frontend), cache_headers=False)]
    )
    websocket_api.async_register_command(hass, websocket_get)
    websocket_api.async_register_command(hass, websocket_mutate)
    websocket_api.async_register_command(hass, websocket_session)
    websocket_api.async_register_command(hass, websocket_check_recommendation)
    await panel_custom.async_register_panel(
        hass=hass,
        frontend_url_path=PANEL_PATH,
        webcomponent_name="fit-flow-panel",
        sidebar_title="FitFlow",
        sidebar_icon="mdi:arm-flex",
        module_url=(
            f"{STATIC_PATH}/fit-flow-panel.js?"
            f"v={INTEGRATION_VERSION}-{PANEL_ASSET_REVISION}"
        ),
        require_admin=True,
    )


def _coordinator(hass: HomeAssistant):
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        raise HomeAssistantError("FitFlow is not configured")
    return hass.data[DOMAIN][entries[0].entry_id]


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "fit_flow/config/get"})
@websocket_api.async_response
async def websocket_get(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    connection.send_result(msg["id"], _coordinator(hass).snapshot())


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "fit_flow/mutate",
        vol.Required("collection"): vol.In(
            [
                "muscle_groups",
                "exercises",
                "workouts",
                "activities",
                "conflict_rules",
                "history",
            ]
        ),
        vol.Optional("item"): dict,
        vol.Optional("item_id"): str,
        vol.Optional("delete"): bool,
    }
)
@websocket_api.async_response
async def websocket_mutate(
    hass: HomeAssistant, connection, msg: dict[str, Any]
) -> None:
    try:
        coordinator = _coordinator(hass)
        if msg.get("delete"):
            await coordinator.delete(msg["collection"], msg["item_id"])
            result = {}
        else:
            result = await coordinator.mutate(
                msg["collection"], msg.get("item", {}), msg.get("item_id")
            )
        connection.send_result(msg["id"], {"success": True, "item": result})
    except (ValueError, HomeAssistantError) as error:
        connection.send_error(msg["id"], "invalid", str(error))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "fit_flow/session",
        vol.Required("operation"): vol.In(["start", "update", "finish", "cancel"]),
        vol.Optional("workout_id"): str,
        vol.Optional("selected_exercise_ids"): [str],
    }
)
@websocket_api.async_response
async def websocket_session(
    hass: HomeAssistant, connection, msg: dict[str, Any]
) -> None:
    try:
        coordinator = _coordinator(hass)
        operation = msg["operation"]
        result = await {
            "start": lambda: coordinator.start(msg["workout_id"]),
            "update": lambda: coordinator.update_session(
                msg.get("selected_exercise_ids", [])
            ),
            "finish": coordinator.finish,
            "cancel": coordinator.cancel,
        }[operation]()
        connection.send_result(msg["id"], {"success": True, "result": result})
    except ValueError as error:
        connection.send_error(msg["id"], "invalid", str(error))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "fit_flow/recommendation/check"}
)
@websocket_api.async_response
async def websocket_check_recommendation(
    hass: HomeAssistant, connection, msg: dict[str, Any]
) -> None:
    _coordinator(hass).async_check_recommendation()
    connection.send_result(msg["id"], {"success": True})
