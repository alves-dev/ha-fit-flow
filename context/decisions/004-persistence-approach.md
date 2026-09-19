# Decision: Local Persistence and Versioning

## Context

Workout sessions and history must survive Home Assistant restarts without an external database, and invalid or unknown data versions must not be silently interpreted.

## Decision

Use Home Assistant’s integration-owned `Store` with atomic writes, one storage key per config entry, and an explicit payload version. Serialize the `FitFlowData` aggregate as a dictionary and reject unsupported versions during load.

## Rationale

The data is local to the Home Assistant integration and small enough for the built-in storage facility. Atomic writes reduce the risk of partial payloads. An explicit version check prevents accidental data-shape interpretation when the schema changes.

## Alternatives Considered

Alternatives are not documented in the existing codebase. No external database, migration framework, or unversioned file format is used.

## Outcomes

Storage round-trip and unsupported-version behavior are covered by tests. Integration removal deletes the associated stored data.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Active Sessions, Activity Logging, and History](../intent/feature-sessions-and-history.md)
- [Pattern: Versioned Home Assistant Storage](../knowledge/patterns/versioned-home-assistant-storage.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.

