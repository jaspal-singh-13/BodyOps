---
type: community
cohesion: 0.07
members: 29
---

# Workout REST Endpoints

**Cohesion:** 0.07 - loosely connected
**Members:** 29 nodes

## Members
- [[CompleteSessionRequest_1]] - code - api/routers/workouts.py
- [[ExerciseProgressionResponse_1]] - code - api/routers/workouts.py
- [[Fire-and-forget wrapper so task completion never delays the response._1]] - rationale - api/routers/workouts.py
- [[LogSetRequest_1]] - code - api/routers/workouts.py
- [[LogSetResponse_1]] - code - api/routers/workouts.py
- [[RenamePlanRequest_1]] - code - api/routers/workouts.py
- [[Run a coroutine as a background task that survives garbage collection._2]] - rationale - api/routers/workouts.py
- [[TodayWorkoutResponse_1]] - code - api/routers/workouts.py
- [[UpdateDayRequest_1]] - code - api/routers/workouts.py
- [[UpdateScheduleWeekdayRequest_1]] - code - api/routers/workouts.py
- [[Workout system API routes.  Endpoints     POST   workoutsimport]] - rationale - api/routers/workouts.py
- [[WorkoutHistoryResponse_1]] - code - api/routers/workouts.py
- [[WorkoutPlansResponse_1]] - code - api/routers/workouts.py
- [[WorkoutScheduleResponse_1]] - code - api/routers/workouts.py
- [[_bg_auto_complete()_1]] - code - api/routers/workouts.py
- [[_spawn_bg()_2]] - code - api/routers/workouts.py
- [[activate_plan_endpoint()]] - code - api/routers/workouts.py
- [[complete_session_endpoint()]] - code - api/routers/workouts.py
- [[delete_plan_endpoint()]] - code - api/routers/workouts.py
- [[get_history_endpoint()_2]] - code - api/routers/workouts.py
- [[get_progression_endpoint()]] - code - api/routers/workouts.py
- [[get_schedule_endpoint()]] - code - api/routers/workouts.py
- [[get_today_endpoint()_1]] - code - api/routers/workouts.py
- [[list_plans_endpoint()]] - code - api/routers/workouts.py
- [[log_set_endpoint()]] - code - api/routers/workouts.py
- [[rename_plan_endpoint()]] - code - api/routers/workouts.py
- [[update_day_exercises_endpoint()]] - code - api/routers/workouts.py
- [[update_schedule_weekday_endpoint()]] - code - api/routers/workouts.py
- [[workouts.py]] - code - api/routers/workouts.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workout_REST_Endpoints
SORT file.name ASC
```

## Connections to other communities
- 15 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 9 edges to [[_COMMUNITY_Workout Plan Management]]
- 4 edges to [[_COMMUNITY_Workout Text Parser]]
- 3 edges to [[_COMMUNITY_App Entry & Login]]
- 3 edges to [[_COMMUNITY_Workout Service Queries]]
- 2 edges to [[_COMMUNITY_Daily Task Service]]
- 2 edges to [[_COMMUNITY_Set Logging & Progression]]
- 1 edge to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 1 edge to [[_COMMUNITY_Agent Router & Chat History]]
- 1 edge to [[_COMMUNITY_AI Workout Import]]

## Top bridge nodes
- [[workouts.py]] - degree 56, connects to 10 communities