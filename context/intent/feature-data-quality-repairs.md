# Feature: Data-Quality Repair Guidance

## What

FitFlow identifies configuration and history conditions that can make the routine confusing or incomplete, including unused or empty muscle groups, duplicate exercise names, and duplicate recent activity records. It presents these findings as actionable Home Assistant repair issues.

## Why

Recommendations depend on coherent catalog and history data. Early visibility into stale, duplicated, or disconnected data helps the user correct the routine before it produces misleading results.

## Acceptance Criteria

- [ ] Empty and unused muscle groups are identified.
- [ ] Duplicate exercise names are identified case-insensitively.
- [ ] Exercises without an image link are identified.
- [ ] Duplicate recent activity records are identified.
- [ ] Repair issues are refreshed after data changes and removed when no longer applicable.

## Related

- [Project Intent](project-intent.md)
- [Decision: Home Assistant Integration Architecture](../decisions/002-home-assistant-architecture.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Active (already implemented)
