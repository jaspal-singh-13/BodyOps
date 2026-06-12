---
type: community
cohesion: 0.22
members: 11
---

# Logging Configuration

**Cohesion:** 0.22 - loosely connected
**Members:** 11 nodes

## Members
- [[.filter()]] - code - api/logger.py
- [[Centralized logging configuration for the BodyOps backend.  All loggers are na]] - rationale - api/logger.py
- [[Initialize ``logging.basicConfig`` once per process and apply fine-grained]] - rationale - api/logger.py
- [[Inject the current ``request_id`` into every log record.]] - rationale - api/logger.py
- [[LogRecord]] - code - api/logger.py
- [[Logger]] - code - api/logger.py
- [[Return a namespaced logger, configuring the root handler on first call.      A]] - rationale - api/logger.py
- [[_RequestIdFilter]] - code - api/logger.py
- [[_configure()]] - code - api/logger.py
- [[get_logger()]] - code - api/logger.py
- [[logger.py]] - code - api/logger.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Logging_Configuration
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 4 edges to [[_COMMUNITY_App Entry & Login]]
- 4 edges to [[_COMMUNITY_Sheets Repo Helpers]]
- 2 edges to [[_COMMUNITY_Pydantic AI Agent Core]]
- 2 edges to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 2 edges to [[_COMMUNITY_Drive Photo Upload]]
- 2 edges to [[_COMMUNITY_Meal Service Logic]]
- 2 edges to [[_COMMUNITY_Meal Macro Schemas]]
- 2 edges to [[_COMMUNITY_Settings Service & Router]]
- 2 edges to [[_COMMUNITY_Daily Task Service]]
- 2 edges to [[_COMMUNITY_Workout Plan Management]]
- 2 edges to [[_COMMUNITY_Auth Sheet Credentials Cache]]
- 2 edges to [[_COMMUNITY_Sheets Client Singleton]]

## Top bridge nodes
- [[logger.py]] - degree 20, connects to 13 communities
- [[get_logger()]] - degree 20, connects to 13 communities