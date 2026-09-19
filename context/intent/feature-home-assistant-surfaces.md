# Feature: Home Assistant Integration Surfaces

## What

FitFlow is available inside Home Assistant through a setup flow, an administrator-only sidebar panel, sensors, and actions that can be used by automations or scripts. The integration exposes the next workout, alternate workout, last activity, and lifetime workout/activity counts.

## Why

People should be able to manage and observe their routine where the rest of their home automation lives. Home Assistant entities and actions make FitFlow useful both interactively and as part of automations.

## Acceptance Criteria

- [ ] FitFlow can be configured as a single Home Assistant instance.
- [ ] The management panel is restricted to administrators.
- [ ] Recommendation and activity state is reflected in Home Assistant sensors.
- [ ] Users can log an activity and request a recommendation refresh through actions.
- [ ] State changes update exposed entities.

## Related

- [Project Intent](project-intent.md)
- [Decision: Technology Stack](../decisions/001-tech-stack.md)
- [Decision: Home Assistant Integration Architecture](../decisions/002-home-assistant-architecture.md)
- [Pattern: Dispatcher-Driven Entity Refresh](../knowledge/patterns/dispatcher-driven-entity-refresh.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Active (already implemented)

