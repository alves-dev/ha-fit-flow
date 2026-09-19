# Feature: Active Sessions, Activity Logging, and History

## What

FitFlow lets a user start one workout, keep track of selected exercises, finish or cancel it, and retain the resulting workout history. Users can also record other activities, optionally with a duration and time. History supports recent-activity visibility and lifetime counts.

## Why

A routine is useful only when completed work is captured reliably. Persisted sessions protect progress across restarts, while activity history provides the information needed for recovery decisions and long-term tracking.

## Acceptance Criteria

- [ ] At most one workout session is active at a time.
- [ ] A session can be started, updated, finished, or cancelled.
- [ ] Finishing a session records the workout, times, and selected exercises.
- [ ] Activities can be logged by configured identifier or display name.
- [ ] Invalid activities and non-positive durations are rejected.
- [ ] Data survives Home Assistant restarts and can be removed with the integration entry.

## Related

- [Project Intent](project-intent.md)
- [Decision: Local Persistence and Versioning](../decisions/004-persistence-approach.md)
- [Pattern: Versioned Home Assistant Storage](../knowledge/patterns/versioned-home-assistant-storage.md)
- [Pattern: Validated Coordinator Mutations](../knowledge/patterns/validated-coordinator-mutations.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Active (already implemented)

