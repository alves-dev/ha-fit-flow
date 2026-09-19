# Feature: Workout Configuration and Catalog Management

## What

Administrators can maintain the workout catalog used by FitFlow, including muscle groups, exercises, workouts, activities, and recovery conflict rules. The catalog supports named exercises grouped by muscle group and workouts that require one or more muscle groups and exercise quantities.

## Why

Flexible routines need to reflect a person’s available exercises, preferred workout structure, and other physical activities. Managing this catalog lets recommendations match the person’s real routine instead of a fixed, generic plan.

## Acceptance Criteria

- [ ] An administrator can create, update, and delete supported catalog items.
- [ ] Workouts can require muscle groups and exercise quantities.
- [ ] Recovery conflict rules can relate an activity or workout to a target workout.
- [ ] Invalid names, references, quantities, URLs, and duplicate rules are rejected.
- [ ] Referenced muscle groups and active workouts cannot be removed in ways that would break existing data.

## Related

- [Project Intent](project-intent.md)
- [Decision: Home Assistant Integration Architecture](../decisions/002-home-assistant-architecture.md)
- [Pattern: Validated Coordinator Mutations](../knowledge/patterns/validated-coordinator-mutations.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Active (already implemented)

