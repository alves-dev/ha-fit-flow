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

The current implementation supports the panel, five sensor categories (next, alternate, last activity, workout counts, and activity counts), two actions, and repair updates from the same coordinator state. Repairs include missing exercise image links and multiple recent workout or activity records on a local calendar day. Each completed workout counts as one history record even when it contains several exercises. The panel renders valid image URLs as in-place preview buttons and opens images or GIFs in a larger modal during workouts, configuration, and history views. During an active workout, it tags exercises that were used in the most recently completed session of that same workout and provides collapsible exercise groups with right-aligned progress icons.

The panel persists the expanded/collapsed state of active-workout exercise groups in browser storage, keyed by workout and muscle group, so navigating away does not reset the user's view. Exercise descriptions remain part of the exercise catalog and are editable from both configuration and the active-workout view; completed workout history stores the description snapshot used at completion.

The main recommendation card uses action hierarchy to reflect the user's likely next step: starting the recommended workout is primary, choosing an alternate workout is secondary, and manually checking for a fresh recommendation is a compact supporting action aligned to the card's lower edge.

The panel keeps the original chronological history view and adds a separate calendar history view. The calendar defaults to the current month, supports previous/next month navigation, renders past empty days with a neutral symbol, marks the current day with a theme-colored pulsing dot, shows only the time for records, and places workout or activity records inside their local calendar day without introducing fixed state colors.

Workout requirements may optionally carry a unique sequential order. The coordinator validates that order when supplied, while the configuration summary and active-workout panel use it to present muscle groups consistently.

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
