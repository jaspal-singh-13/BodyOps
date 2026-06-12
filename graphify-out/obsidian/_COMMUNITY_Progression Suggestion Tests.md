---
type: community
cohesion: 0.25
members: 14
---

# Progression Suggestion Tests

**Cohesion:** 0.25 - loosely connected
**Members:** 14 nodes

## Members
- [[ProgressionSuggestion_1]] - code - api/services/workout_service.py
- [[Unit tests for compute_suggestion() in apiservicesworkout_service.py. Pure fun]] - rationale - tests/test_progression.py
- [[compute_suggestion()]] - code - api/services/workout_service.py
- [[test_below_middle_reduces_weight()]] - code - tests/test_progression.py
- [[test_exceeds_upper_range_still_increases_weight()]] - code - tests/test_progression.py
- [[test_first_session_returns_null_suggestion()]] - code - tests/test_progression.py
- [[test_hit_upper_range_increases_weight()]] - code - tests/test_progression.py
- [[test_just_below_upper_range_adds_rep()]] - code - tests/test_progression.py
- [[test_middle_of_range_adds_rep()]] - code - tests/test_progression.py
- [[test_progression.py]] - code - tests/test_progression.py
- [[test_single_rep_target_hit_increases_weight()]] - code - tests/test_progression.py
- [[test_single_rep_target_miss_reduces_weight()]] - code - tests/test_progression.py
- [[test_weight_floor_at_zero()]] - code - tests/test_progression.py
- [[test_weight_increment_rounds_correctly()]] - code - tests/test_progression.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Progression_Suggestion_Tests
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Set Logging & Progression]]
- 1 edge to [[_COMMUNITY_Workout Models & Router Tests]]
- 1 edge to [[_COMMUNITY_Workout Plan Management]]
- 1 edge to [[_COMMUNITY_Workout Service Queries]]

## Top bridge nodes
- [[compute_suggestion()]] - degree 17, connects to 4 communities