---
type: community
cohesion: 0.13
members: 29
---

# Daily Task Service

**Cohesion:** 0.13 - loosely connected
**Members:** 29 nodes

## Members
- [[Alias for ``get_today_tasks`` — returns today's mission summary.]] - rationale - api/services/task_service.py
- [[Business logic for daily missions  tasks.  Tabs used     Tasks           —]] - rationale - api/services/task_service.py
- [[Combine task definitions with daily status rows into a response object.]] - rationale - api/services/task_service.py
- [[Count consecutive fully-complete days ending on or before ``today``.      Scan]] - rationale - api/services/task_service.py
- [[Create DailyTaskStatus rows for ``date`` if they don't already exist.      Ide]] - rationale - api/services/task_service.py
- [[DailyStatusResponse_2]] - code - api/services/task_service.py
- [[Mark a specific task complete for a given date.      Finds the ``DailyTaskStat]] - rationale - api/services/task_service.py
- [[Mark a task complete by its type rather than its ID.      Called automatically]] - rationale - api/services/task_service.py
- [[Return DailyTaskStatus rows for this user and date.]] - rationale - api/services/task_service.py
- [[Return True if the given date has no workout scheduled (rest day or no schedule)]] - rationale - api/services/task_service.py
- [[Return all data rows from a tab as a list of header-keyed dicts.      Delegate]] - rationale - api/sheets/sheets_repo.py
- [[Return existing task definition rows for this user, seeding defaults if none exi]] - rationale - api/services/task_service.py
- [[Return today's date in ``YYYY-MM-DD`` format for the given timezone.]] - rationale - api/services/task_service.py
- [[Return today's mission list, generating it if it doesn't exist yet.      Resol]] - rationale - api/services/task_service.py
- [[Write default task definitions for a new user and return them.]] - rationale - api/services/task_service.py
- [[_build_response()]] - code - api/services/task_service.py
- [[_compute_streak()]] - code - api/services/task_service.py
- [[_ensure_daily_status()]] - code - api/services/task_service.py
- [[_get_task_definitions()]] - code - api/services/task_service.py
- [[_is_rest_day()]] - code - api/services/task_service.py
- [[_read_daily_status()]] - code - api/services/task_service.py
- [[_resolve_today()]] - code - api/services/task_service.py
- [[_seed_tasks()]] - code - api/services/task_service.py
- [[auto_complete_task()]] - code - api/services/task_service.py
- [[complete_task()_1]] - code - api/services/task_service.py
- [[get_status()]] - code - api/services/task_service.py
- [[get_today_tasks()]] - code - api/services/task_service.py
- [[read_rows()]] - code - api/sheets/sheets_repo.py
- [[task_service.py]] - code - api/services/task_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Daily_Task_Service
SORT file.name ASC
```

## Connections to other communities
- 14 edges to [[_COMMUNITY_Workout Plan Management]]
- 12 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 7 edges to [[_COMMUNITY_Sheets Repo Helpers]]
- 6 edges to [[_COMMUNITY_Task Models & Router Tests]]
- 6 edges to [[_COMMUNITY_Meal Service Logic]]
- 5 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 4 edges to [[_COMMUNITY_App Entry & Login]]
- 4 edges to [[_COMMUNITY_Streak Computation Tests]]
- 3 edges to [[_COMMUNITY_Settings Service & Router]]
- 3 edges to [[_COMMUNITY_Complete Task Tests]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 2 edges to [[_COMMUNITY_Weight REST Endpoints]]
- 2 edges to [[_COMMUNITY_Workout REST Endpoints]]
- 2 edges to [[_COMMUNITY_Set Logging & Progression]]
- 1 edge to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 1 edge to [[_COMMUNITY_Rest Day Tasks Test]]
- 1 edge to [[_COMMUNITY_Completion Percentage Test]]
- 1 edge to [[_COMMUNITY_Workout Day Tasks Test]]
- 1 edge to [[_COMMUNITY_Auto-Complete Write Test]]
- 1 edge to [[_COMMUNITY_Auto-Complete No-Op Test]]
- 1 edge to [[_COMMUNITY_Status Totals Test]]
- 1 edge to [[_COMMUNITY_Weight Logging]]
- 1 edge to [[_COMMUNITY_Weight History Logic]]
- 1 edge to [[_COMMUNITY_Weight Trend Computation]]

## Top bridge nodes
- [[task_service.py]] - degree 34, connects to 13 communities
- [[read_rows()]] - degree 24, connects to 7 communities
- [[get_today_tasks()]] - degree 16, connects to 6 communities
- [[auto_complete_task()]] - degree 14, connects to 6 communities
- [[complete_task()_1]] - degree 17, connects to 5 communities