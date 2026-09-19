# Pattern: Versioned Home Assistant Storage

## Description

Persist the complete integration aggregate through Home Assistant `Store`, include a version field, reconstruct defaults for missing keys, and reject unsupported versions.

## When to Use

Use this pattern for small, integration-owned state that must survive restarts without a separate database.

## Pattern

```python
payload = await self._store.async_load()
if payload is None:
    return FitFlowData()
if not isinstance(payload, dict) or payload.get("version") != STORAGE_VERSION:
    raise ValueError("Unsupported FitFlow storage version")
values = {key: payload.get(key, default)
          for key, default in FitFlowData().__dict__.items()}
return FitFlowData(**values)
```

## Example

`FitFlowStorage` uses `Store(hass, 1, f"{DOMAIN}.{entry_id}", atomic_writes=True)` and writes `FitFlowData.as_dict()`.

## Files Using This Pattern

- `custom_components/fit_flow/storage.py` — load/save/remove behavior.
- `custom_components/fit_flow/models.py` — aggregate defaults and serialization.
- `tests/test_coordinator_storage.py` — round-trip and version rejection tests.

## Related

- [Decision: Local Persistence and Versioning](../../decisions/004-persistence-approach.md)
- [Feature: Active Sessions, Activity Logging, and History](../../intent/feature-sessions-and-history.md)

## Status

- **Created**: 2026-09-19
- **Status**: Active

