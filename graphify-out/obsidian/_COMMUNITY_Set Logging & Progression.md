---
type: community
cohesion: 0.17
members: 16
---

# Set Logging & Progression

**Cohesion:** 0.17 - loosely connected
**Members:** 16 nodes

## Members
- [[Any_1]] - code - api/services/workout_service.py
- [[ExerciseProgressionResponse_2]] - code - api/services/workout_service.py
- [[Filter rows by user_id and optionally by plan_id.      When plan_id is None (l]] - rationale - api/services/workout_service.py
- [[LogSetRequest_2]] - code - api/services/workout_service.py
- [[LogSetResponse_2]] - code - api/services/workout_service.py
- [[Look up rep_minrep_max from pre-loaded WorkoutPrograms rows; fall back to (8, 1]] - rationale - api/services/workout_service.py
- [[Look up rep_minrep_max from the active plan's WorkoutPrograms; fall back to (8,]] - rationale - api/services/workout_service.py
- [[Return (weight_kg, reps) from the final set of the most recent session.      O]] - rationale - api/services/workout_service.py
- [[Return the plan_id of the user's currently active plan, or None.      None mea]] - rationale - api/services/workout_service.py
- [[_filter_by_plan()]] - code - api/services/workout_service.py
- [[_get_last_set_from_rows()]] - code - api/services/workout_service.py
- [[_get_program_rep_range()]] - code - api/services/workout_service.py
- [[_get_program_rep_range_from_rows()]] - code - api/services/workout_service.py
- [[get_active_plan_id()]] - code - api/services/workout_service.py
- [[get_progression()]] - code - api/services/workout_service.py
- [[log_set()]] - code - api/services/workout_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Set_Logging__Progression
SORT file.name ASC
```

## Connections to other communities
- 19 edges to [[_COMMUNITY_Workout Plan Management]]
- 9 edges to [[_COMMUNITY_Workout Service Queries]]
- 4 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 2 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 2 edges to [[_COMMUNITY_Workout REST Endpoints]]
- 2 edges to [[_COMMUNITY_Daily Task Service]]
- 2 edges to [[_COMMUNITY_Progression Suggestion Tests]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]
- 1 edge to [[_COMMUNITY_Meal Service Logic]]

## Top bridge nodes
- [[get_progression()]] - degree 14, connects to 6 communities
- [[log_set()]] - degree 14, connects to 6 communities
- [[get_active_plan_id()]] - degree 15, connects to 3 communities
- [[_filter_by_plan()]] - degree 9, connects to 2 communities
- [[_get_last_set_from_rows()]] - degree 7, connects to 2 communities