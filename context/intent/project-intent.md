# Project Intent: FitFlow

## What

FitFlow is a Home Assistant integration for managing flexible gym routines. It helps a person configure workouts, exercises, muscle groups, activities, and recovery conflicts; recommends what to do next; supports an active workout; and records completed workouts and activities.

## Why

People need a workout routine that adapts to what they have recently done instead of requiring a fixed calendar. FitFlow makes recovery-aware choices visible in Home Assistant and keeps workout history and counts available for ongoing use.

## Current State

The integration is implemented as a local Home Assistant custom component, version `2026.9.2`, supporting Home Assistant `2026.8+`. It has a single-instance setup flow, an administrator panel, sensors, actions, persistent storage, data-quality repairs, automated tests, CI validation, HACS metadata, and release workflows.

The repository includes the domain specification in `FITFLOW_SPEC.md`, user and contributor documentation in `README.md` and `docs/`, Python integration code under `custom_components/fit_flow/`, and tests under `tests/`.

## Project Structure and Tooling

- `custom_components/fit_flow/` — Home Assistant integration, domain logic, frontend panel, translations, services, and branding.
- `tests/` — unit and integration-module tests for storage, coordination, recommendation, sensors, services, config flow, and repairs.
- `dev/` — scripts for managing and deploying to the shared local Home Assistant instance.
- `docs/` — compatibility and development guidance.
- `.github/workflows/` — tests, Hassfest, HACS, SonarQube, and release automation.
- `pyproject.toml` and `uv.lock` — Python and dependency configuration.
- `hacs.json`, `manifest.json`, and `sonar-project.properties` — distribution, Home Assistant, and quality-analysis metadata.

## Current Features

- [Workout configuration and catalog management](feature-workout-configuration.md)
- [Recovery-aware workout and exercise recommendations](feature-recommendations.md)
- [Active sessions, activity logging, and history](feature-sessions-and-history.md)
- [Home Assistant integration surfaces](feature-home-assistant-surfaces.md)
- [Data-quality repair guidance](feature-data-quality-repairs.md)

## Related Technical Context

- [Decision: Technology Stack](../decisions/001-tech-stack.md)
- [Decision: Home Assistant Integration Architecture](../decisions/002-home-assistant-architecture.md)
- [Decision: Recommendation and Recovery Model](../decisions/003-recommendation-approach.md)
- [Decision: Local Persistence and Versioning](../decisions/004-persistence-approach.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Active
- **Note**: Generated from existing codebase analysis.

