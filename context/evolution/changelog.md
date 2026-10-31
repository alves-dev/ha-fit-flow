# Changelog

## [Unreleased]

### Added

- Added optional sequential ordering for workout muscle groups, validated by the coordinator and applied in configuration and active-workout views.

## [2026.10.1] - 2026-10-16

### Added

- Added duplicate-history Repairs for multiple workout or activity records on a recent local calendar day.
- Updated the calendar history view to show only record times and mark past empty days with a neutral symbol.
- Added a pulsing theme-colored dot to identify the current day in the calendar.
- Added a separate “Histórico v2” monthly calendar view while keeping the original chronological history view available.

### Changed

- Reordered and restyled the main recommendation card actions so starting the recommended workout is the primary action, choosing an alternative is secondary, and checking the recommendation is less prominent.
- Updated the integration version to `2026.10.1`.
- Aligned the development-release cleanup workflow with the shared GitHub Actions baseline: daily scheduling, retention of the newest five prereleases, and explicit repository scoping for GitHub CLI operations.

## [2026.9.5] - 2026-09-30

### Added

- Added optional exercise descriptions, editable in configuration and during an active workout.
- Added browser persistence for expanded/collapsed exercise groups during active workouts.

## [2026.9.4] - 2026-09-21

### Added

- Added collapsible exercise groups with right-aligned progress icons.
- Added a “Treino anterior” tag to exercises used in the most recently completed session of the active workout.

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
