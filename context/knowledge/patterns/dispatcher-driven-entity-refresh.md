# Pattern: Dispatcher-Driven Entity Refresh

## Description

After a successful state save, send a dispatcher signal containing the config-entry identifier. Entities subscribe when added to Home Assistant and write their state only when the signal belongs to their coordinator.

## When to Use

Use this pattern when several entities share mutable integration state and should update immediately without polling.

## Pattern

```python
# coordinator.py
await self.storage.async_save(self.data)
async_dispatcher_send(self.hass, SIGNAL_UPDATE, self.entry_id)

# sensor.py
async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self._updated)

def _updated(self, entry_id):
    if entry_id == self.coordinator.entry_id:
        self.hass.loop.call_soon_threadsafe(self.async_write_ha_state)
```

## Example

All FitFlow sensors inherit `FitFlowSensor`, which subscribes to `SIGNAL_UPDATE`; coordinator `save()` emits the signal after persistence.

## Files Using This Pattern

- `custom_components/fit_flow/coordinator.py` — emits updates.
- `custom_components/fit_flow/sensor.py` — subscribes and refreshes entities.

## Related

- [Decision: Home Assistant Integration Architecture](../../decisions/002-home-assistant-architecture.md)
- [Feature: Home Assistant Integration Surfaces](../../intent/feature-home-assistant-surfaces.md)

## Status

- **Created**: 2026-09-19
- **Status**: Active

