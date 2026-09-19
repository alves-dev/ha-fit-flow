# Changelog

## [2026.9.3] - 2026-09-19

### Added

- Added a Home Assistant Repair for exercises without an image link.
- Added an in-panel image/GIF preview modal for exercise media.

### Changed

- Updated the integration version to `2026.9.3`.

## [Current State] - Context Mesh Added

### Existing Features (documented)

- Workout catalog management for muscle groups, exercises, workouts, activities, and directional recovery rules.
- Recovery-aware workout and exercise recommendations.
- Persisted active sessions, activity logging, workout/activity history, and lifetime counters.
- Home Assistant config flow, administrator panel, WebSocket API, sensors, actions, and Repairs issues.

### Tech Stack (documented)

- Python 3.14 and Home Assistant 2026.8.0+.
- Home Assistant custom integration APIs with a vanilla JavaScript panel.
- `uv`, pytest/pytest-asyncio, Ruff, GitHub Actions, HACS validation, Hassfest, and SonarQube.

### Patterns Identified

- Validated coordinator mutations with serialized state changes.
- Pure recommendation calculation from stored inputs.
- Versioned atomic Home Assistant storage.
- Dispatcher-driven entity refresh.

---

*Context Mesh added: 2026-09-19*
*This changelog documents the state when Context Mesh was added.*
*Future changes will be tracked below.*
