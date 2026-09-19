# Decision: Recommendation and Recovery Model

## Context

FitFlow must choose a useful next workout from history while respecting recovery constraints caused by both workouts and other activities. The specification requires directional conflicts and an explanation of blocked choices.

## Decision

Represent recovery as directional rules from a source activity/workout to a target workout. Calculate active blocks from history timestamps, merge multiple active rules by the latest expiration for each target, prioritize never-completed eligible workouts, then rank remaining workouts by oldest completion with stable ID tie-breaking. Recommend exercises per muscle-group requirement using least-recent use ordering.

## Rationale

Directional rules model asymmetric recovery needs. Separating blocked, eligible, and next-available results lets the UI explain the recommendation. A deterministic ordering makes behavior predictable and testable, while recent-use ordering provides rotation without requiring a more complex scheduling engine.

## Alternatives Considered

Alternatives are not documented in the existing codebase. A calendar-based scheduler or symmetric conflict graph is not present.

## Outcomes

Tests cover never-performed priority, directional conflicts, all-blocked availability, timezone normalization, and exercise rotation.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Recovery-Aware Recommendations](../intent/feature-recommendations.md)
- [Pattern: Pure Recommendation Calculation](../knowledge/patterns/pure-recommendation-calculation.md)

## Status

- **Created**: 2026-09-19 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.

