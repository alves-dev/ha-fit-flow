# Feature: Recovery-Aware Recommendations

## What

FitFlow recommends the workout that has gone longest without being completed, while excluding workouts that are still in a configured recovery period. It can show eligible and blocked choices, the next time a blocked choice becomes available, an alternate workout, and exercise suggestions that rotate toward exercises used less recently.

## Why

The user needs a useful next workout without manually tracking rest periods or repeating the same exercises too frequently. Showing why a workout is unavailable makes the recommendation understandable and actionable.

## Acceptance Criteria

- [ ] Never-completed eligible workouts are prioritized.
- [ ] Otherwise, the workout with the oldest completion is prioritized.
- [ ] Activity and workout recovery rules can block a target workout directionally.
- [ ] Multiple rules for one target use the most restrictive active block.
- [ ] When all workouts are blocked, the next availability is reported.
- [ ] Exercise suggestions satisfy workout muscle-group quantities and favor less-recently-used exercises.

## Related

- [Project Intent](project-intent.md)
- [Decision: Recommendation and Recovery Model](../decisions/003-recommendation-approach.md)
- [Pattern: Pure Recommendation Calculation](../knowledge/patterns/pure-recommendation-calculation.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Active (already implemented)

