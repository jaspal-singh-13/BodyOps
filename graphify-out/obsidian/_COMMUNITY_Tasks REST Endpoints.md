---
type: community
cohesion: 0.25
members: 8
---

# Tasks REST Endpoints

**Cohesion:** 0.25 - loosely connected
**Members:** 8 nodes

## Members
- [[CompleteTaskRequest_1]] - code - api/routers/tasks.py
- [[DailyStatusResponse_1]] - code - api/routers/tasks.py
- [[Mark a task complete by its task_id and date.      Idempotent — marking an alrea]] - rationale - api/routers/tasks.py
- [[Return today's mission list for the authenticated user.      Generates the daily]] - rationale - api/routers/tasks.py
- [[Return today's mission summary (total, completed, percentage).      Equivalent t]] - rationale - api/routers/tasks.py
- [[complete_task_endpoint()]] - code - api/routers/tasks.py
- [[get_status_endpoint()]] - code - api/routers/tasks.py
- [[get_today_tasks_endpoint()]] - code - api/routers/tasks.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tasks_REST_Endpoints
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_App Entry & Login]]

## Top bridge nodes
- [[complete_task_endpoint()]] - degree 4, connects to 1 community
- [[get_status_endpoint()]] - degree 3, connects to 1 community
- [[get_today_tasks_endpoint()]] - degree 3, connects to 1 community