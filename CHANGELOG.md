# Changelog

All user-relevant changes are documented in this file.

## [2026.9.3] - 2026-09-19

### Added

- Added a Home Assistant Repair warning for exercises without an image link.
- Added an in-panel image/GIF preview modal for exercise media during workouts, configuration, and history.

## [2026.9.2] - 2026-09-16

### Added

- Added readable unlock dates and workout completion counts with compact bars to the panel cards.
- Added inline editing for muscle-group names while preserving their stable IDs and existing references.
- Added the ability to remove a muscle-group requirement while editing a workout.
- Improved panel loading feedback and theme-variable compatibility.

## [2026.9.1] - 2026-09-13

### Added

- Added duplicate external-activity detection for the last five days in Repairs.
- Added history deletion with confirmation, recommendation refresh action/button, and an alternate workout sensor.

### Fixed

- Fixed activity IDs being stored from user input instead of the configured activity ID, keeping counters consistent with history.

## [2026.9.0] - 2026-09-13

### Added

- Added the FitFlow Home Assistant integration with configurable workout data, history, recommendations, sessions, sensors, action, and sidebar panel.
- Added Home Assistant Repairs warnings for unused or empty muscle groups and duplicate exercise names.

### Changed

- Reorganized the configuration page into sequential sections and added exercise search and muscle-group filtering.
