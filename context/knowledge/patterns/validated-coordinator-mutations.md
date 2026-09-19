# Pattern: Validated Coordinator Mutations

## Description

Route catalog and session changes through one coordinator method that serializes mutations, validates references and invariants, persists the aggregate, and notifies consumers.

## When to Use

Use this pattern when multiple Home Assistant surfaces can change the same integration-owned state and every mutation must have consistent validation and persistence behavior.

## Pattern

```python
async def mutate(self, collection, value, item_id=None):
    async with self._lock:
        values = getattr(self.data, collection)
        value = {**value, "id": item_id or value.get("id") or new_id()}
        self._validate_item(collection, value, item_id)
        # replace an existing item or append a new one
        await self.save()
        return value
```

The coordinator uses the same save path for session start/update/finish/cancel and activity logging. Deletion checks references before changing the collection.

## Example

From `custom_components/fit_flow/coordinator.py`:

```python
async with self._lock:
    values = getattr(self.data, collection)
    value = {**value, "id": item_id or value.get("id") or new_id()}
    self._validate_item(collection, value, item_id)
    values.append(value)
    await self.save()
```

## Files Using This Pattern

- `custom_components/fit_flow/coordinator.py` — catalog CRUD, sessions, and activity logging.
- `custom_components/fit_flow/panel.py` — WebSocket commands delegate mutations to the coordinator.
- `tests/test_coordinator_storage.py` — validates serialization, errors, references, and lifecycle behavior.

## Related

- [Decision: Home Assistant Integration Architecture](../../decisions/002-home-assistant-architecture.md)
- [Feature: Workout Configuration and Catalog Management](../../intent/feature-workout-configuration.md)
- [Feature: Active Sessions, Activity Logging, and History](../../intent/feature-sessions-and-history.md)

## Status

- **Created**: 2026-09-19
- **Status**: Active

