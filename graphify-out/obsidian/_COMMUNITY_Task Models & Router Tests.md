---
type: community
cohesion: 0.11
members: 24
---

# Task Models & Router Tests

**Cohesion:** 0.11 - loosely connected
**Members:** 24 nodes

## Members
- [[._validate_date()_2]] - code - api/models/task.py
- [[.test_returns_200_with_summary_fields()]] - code - tests/test_tasks_router.py
- [[.test_returns_200_with_task_list()]] - code - tests/test_tasks_router.py
- [[.test_returns_200_with_updated_status()]] - code - tests/test_tasks_router.py
- [[.test_returns_401_without_auth()_1]] - code - tests/test_tasks_router.py
- [[.test_returns_401_without_auth()_2]] - code - tests/test_tasks_router.py
- [[.test_returns_401_without_auth()]] - code - tests/test_tasks_router.py
- [[.test_returns_422_invalid_date_format()]] - code - tests/test_tasks_router.py
- [[.test_returns_422_missing_date()]] - code - tests/test_tasks_router.py
- [[.test_returns_422_missing_task_id()]] - code - tests/test_tasks_router.py
- [[.test_task_fields_present()]] - code - tests/test_tasks_router.py
- [[A single task with its completion state for a specific day.      Attributes]] - rationale - api/models/task.py
- [[CompleteTaskRequest]] - code - api/models/task.py
- [[DailyStatusResponse]] - code - api/models/task.py
- [[Integration tests for GET taskstoday, POST taskscomplete, GET tasksstatus.]] - rationale - tests/test_tasks_router.py
- [[Pydantic models for daily missions  tasks.  Tasks are stored in two sheet tabs]] - rationale - api/models/task.py
- [[Request body for ``POST taskscomplete``.      Attributes         task_id The]] - rationale - api/models/task.py
- [[TaskResponse]] - code - api/models/task.py
- [[TestCompleteTask_1]] - code - tests/test_tasks_router.py
- [[TestGetStatus_1]] - code - tests/test_tasks_router.py
- [[TestGetTodayTasks_1]] - code - tests/test_tasks_router.py
- [[The full daily mission list for a user on a given date.      Attributes]] - rationale - api/models/task.py
- [[task.py]] - code - api/models/task.py
- [[test_tasks_router.py]] - code - tests/test_tasks_router.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Task_Models__Router_Tests
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Daily Task Service]]
- 3 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 3 edges to [[_COMMUNITY_App Entry & Login]]

## Top bridge nodes
- [[DailyStatusResponse]] - degree 10, connects to 3 communities
- [[CompleteTaskRequest]] - degree 6, connects to 3 communities
- [[TaskResponse]] - degree 9, connects to 2 communities
- [[task.py]] - degree 6, connects to 2 communities