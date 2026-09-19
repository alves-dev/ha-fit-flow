# Decision: Technology Stack

## Context

FitFlow is a Home Assistant custom integration that must run inside the Home Assistant runtime, expose native entities/actions, and remain distributable through HACS. The repository is Python-based and pins the tested Home Assistant version.

## Decision

- Use Python with Home Assistant `2026.8.0` as the runtime dependency and support Home Assistant `2026.8+`.
- Use `uv` with `pyproject.toml` and `uv.lock` for reproducible dependency and development-environment management.
- Use Home Assistant’s native integration APIs, `voluptuous` validation, and a small vanilla JavaScript custom panel.
- Use pytest/pytest-asyncio for tests and Ruff for linting; use SonarQube for coverage/quality reporting.

## Rationale

The integration must use Home Assistant-native lifecycle, entity, service, storage, panel, and repair APIs. The repository already pins the platform and locks dependencies, while the test and lint configuration matches the project’s asynchronous Python code. The panel has limited scope and is implemented without a separate frontend framework.

## Alternatives Considered

Alternatives are not documented in the existing codebase. A separate backend service, database, or frontend framework is not present in the implementation.

## Outcomes

Outcomes to be documented as the project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Home Assistant Integration Surfaces](../intent/feature-home-assistant-surfaces.md)
- [Decision: Home Assistant Integration Architecture](002-home-assistant-architecture.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.

