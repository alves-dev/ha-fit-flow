# Pattern: Pure Recommendation Calculation

## Description

Keep recommendation logic in functions that accept workouts, rules, history, and a timestamp, then return a structured result without mutating Home Assistant state.

## When to Use

Use this pattern for domain decisions that need deterministic tests, can be recalculated from stored data, and should be consumed by multiple surfaces.

## Pattern

```python
result = recommend(workouts, conflict_rules, history, now)
eligible = [item["id"] for item in workouts if item.get("id") not in blocked]
return Recommendation(
    eligible[0] if eligible else None,
    eligible,
    blocked,
    next_available,
    eligible[1] if len(eligible) > 1 else None,
)
```

## Example

`FitFlowCoordinator.recommendation` calls `recommend(...)`, and sensors/panel snapshots consume the resulting `Recommendation` rather than implementing ranking themselves.

## Files Using This Pattern

- `custom_components/fit_flow/recommendation.py` — workout and exercise ranking.
- `custom_components/fit_flow/coordinator.py` — domain result exposed to integration surfaces.
- `tests/test_recommendation.py` — deterministic edge-case coverage.

## Related

- [Decision: Recommendation and Recovery Model](../../decisions/003-recommendation-approach.md)
- [Feature: Recovery-Aware Recommendations](../../intent/feature-recommendations.md)

## Status

- **Created**: 2026-09-19
- **Status**: Active

