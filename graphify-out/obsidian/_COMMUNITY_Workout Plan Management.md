---
type: community
cohesion: 0.10
members: 41
---

# Workout Plan Management

**Cohesion:** 0.10 - loosely connected
**Members:** 41 nodes

## Members
- [[Delete a saved plan and all its programsschedules.      If the plan is curren]] - rationale - api/services/workout_service.py
- [[Delete all rows belonging to user_id in the given tab.      Groups contiguous]] - rationale - api/services/workout_service.py
- [[Delete all rows matching (user_id, plan_id) in the given tab.]] - rationale - api/services/workout_service.py
- [[Delete all rows matching (user_id, plan_id, day_name) in the given tab.]] - rationale - api/services/workout_service.py
- [[Group a sorted list of 1-based row indices into contiguous (start, end) ranges.]] - rationale - api/services/workout_service.py
- [[Make the given plan the active one for the user.      Deactivates the current]] - rationale - api/services/workout_service.py
- [[Mark the current active plan as inactive (called before activating a new import)]] - rationale - api/services/workout_service.py
- [[Overwrite an existing row by 1-based row index.      Row 1 is the header row,]] - rationale - api/sheets/sheets_repo.py
- [[Read all rows from a tab, returning  if the tab doesn't exist.]] - rationale - api/services/workout_service.py
- [[Reassign a weekday to a different day_name within a plan.      Raises ValueErr]] - rationale - api/services/workout_service.py
- [[Rename a saved plan. Raises ValueError if the plan is not found.]] - rationale - api/services/workout_service.py
- [[Replace all exercises for a day within a plan.      Existing WorkoutPrograms r]] - rationale - api/services/workout_service.py
- [[Resolve plan_name → plan_id case-insensitively and activate it.      Returns a]] - rationale - api/services/workout_service.py
- [[Return (weight_kg, reps) from the final set of the most recent session.]] - rationale - api/services/workout_service.py
- [[Return ``value`` as int, or ``default`` if it cannot be converted.      ``get_]] - rationale - api/sheets/sheets_repo.py
- [[Return a cached ``Worksheet`` handle for the given tab name.      On the first]] - rationale - api/sheets/sheets_client.py
- [[Workout service — business logic for Phase 3 + plan library.  Tabs used]] - rationale - api/services/workout_service.py
- [[WorkoutDaySummary_2]] - code - api/services/workout_service.py
- [[WorkoutHistoryResponse_2]] - code - api/services/workout_service.py
- [[Worksheet]] - code - api/sheets/sheets_client.py
- [[_deactivate_current_plan()]] - code - api/services/workout_service.py
- [[_delete_day_rows()]] - code - api/services/workout_service.py
- [[_delete_plan_rows()]] - code - api/services/workout_service.py
- [[_delete_user_rows()]] - code - api/services/workout_service.py
- [[_get_last_set()]] - code - api/services/workout_service.py
- [[_group_contiguous()]] - code - api/services/workout_service.py
- [[_now_utc()]] - code - api/services/workout_service.py
- [[_safe_read_rows()]] - code - api/services/workout_service.py
- [[activate_plan()]] - code - api/services/workout_service.py
- [[complete_session()]] - code - api/services/workout_service.py
- [[delete_plan()]] - code - api/services/workout_service.py
- [[get_history()_1]] - code - api/services/workout_service.py
- [[get_worksheet()]] - code - api/sheets/sheets_client.py
- [[import_workout()]] - code - api/services/workout_service.py
- [[rename_plan()]] - code - api/services/workout_service.py
- [[switch_plan_by_name()]] - code - api/services/workout_service.py
- [[to_int()]] - code - api/sheets/sheets_repo.py
- [[update_day_exercises()]] - code - api/services/workout_service.py
- [[update_row()]] - code - api/sheets/sheets_repo.py
- [[update_schedule_weekday()]] - code - api/services/workout_service.py
- [[workout_service.py]] - code - api/services/workout_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workout_Plan_Management
SORT file.name ASC
```

## Connections to other communities
- 19 edges to [[_COMMUNITY_Set Logging & Progression]]
- 18 edges to [[_COMMUNITY_Workout Service Queries]]
- 15 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 15 edges to [[_COMMUNITY_Sheets Repo Helpers]]
- 14 edges to [[_COMMUNITY_Daily Task Service]]
- 9 edges to [[_COMMUNITY_Workout REST Endpoints]]
- 7 edges to [[_COMMUNITY_Meal Service Logic]]
- 6 edges to [[_COMMUNITY_Settings Service & Router]]
- 4 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 3 edges to [[_COMMUNITY_AI Workout Import]]
- 3 edges to [[_COMMUNITY_Sheets Client Singleton]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 2 edges to [[_COMMUNITY_Weight Logging]]
- 2 edges to [[_COMMUNITY_Auth Sheet Credentials Cache]]
- 1 edge to [[_COMMUNITY_Pydantic AI Agent Core]]
- 1 edge to [[_COMMUNITY_Weight History Logic]]
- 1 edge to [[_COMMUNITY_Weight Trend Computation]]
- 1 edge to [[_COMMUNITY_Workout Text Parser]]
- 1 edge to [[_COMMUNITY_Progression Suggestion Tests]]
- 1 edge to [[_COMMUNITY_Non-Destructive Import Tests]]

## Top bridge nodes
- [[workout_service.py]] - degree 60, connects to 14 communities
- [[to_int()]] - degree 44, connects to 10 communities
- [[import_workout()]] - degree 11, connects to 6 communities
- [[update_row()]] - degree 20, connects to 5 communities
- [[get_worksheet()]] - degree 15, connects to 4 communities