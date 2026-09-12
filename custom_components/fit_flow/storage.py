"""Versioned integration-owned persistence."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_VERSION
from .models import FitFlowData


class FitFlowStorage:
    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._store = Store(hass, 1, f"{DOMAIN}.{entry_id}", atomic_writes=True)

    async def async_load(self) -> FitFlowData:
        payload = await self._store.async_load()
        if payload is None:
            return FitFlowData()
        if not isinstance(payload, dict) or payload.get("version") != STORAGE_VERSION:
            raise ValueError("Unsupported FitFlow storage version")
        values = {
            key: payload.get(key, default)
            for key, default in FitFlowData().__dict__.items()
        }
        return FitFlowData(**values)

    async def async_save(self, data: FitFlowData) -> None:
        await self._store.async_save(data.as_dict())

    async def async_remove(self) -> None:
        await self._store.async_remove()
