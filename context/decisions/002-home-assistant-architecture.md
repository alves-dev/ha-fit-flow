# Decision: Home Assistant Integration Architecture

## Context

FitFlow needs one shared domain state for the admin UI, sensors, actions, persistence, recommendation calculations, and repair diagnostics. It also needs to be safe to expose in a Home Assistant instance.

## Decision

Use a single `FitFlowCoordinator` per config entry as the runtime façade. Register a single config entry, one administrator-only custom panel, WebSocket commands for panel operations, sensors for observable state, and Home Assistant actions for automation entry points. Publish coordinator changes through a dispatcher signal so entities refresh without polling.

## Rationale

The coordinator centralizes state, validation, mutations, persistence, and domain calls. Home Assistant’s config-entry lifecycle provides setup/unload/remove boundaries. The administrator-only panel limits configuration access, while native sensors and actions integrate with existing Home Assistant features. Dispatcher notifications provide immediate updates after mutations.

## Alternatives Considered

Alternatives are not documented in the existing codebase. No separate API server, polling loop, or multi-entry architecture is implemented.

## Outcomes

The current implementation supports the panel, five sensor categories (next, alternate, last activity, workout counts, and activity counts), two actions, and repair updates from the same coordinator state.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Workout Configuration and Catalog Management](../intent/feature-workout-configuration.md)
- [Feature: Home Assistant Integration Surfaces](../intent/feature-home-assistant-surfaces.md)
- [Feature: Data-Quality Repair Guidance](../intent/feature-data-quality-repairs.md)
- [Pattern: Validated Coordinator Mutations](../knowledge/patterns/validated-coordinator-mutations.md)
- [Pattern: Dispatcher-Driven Entity Refresh](../knowledge/patterns/dispatcher-driven-entity-refresh.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.

