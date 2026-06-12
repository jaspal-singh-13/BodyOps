---
type: community
cohesion: 0.13
members: 26
---

# App Entry & Login

**Cohesion:** 0.13 - loosely connected
**Members:** 26 nodes

## Members
- [[Authenticate the user and return a signed JWT.      Delegates to ``api.auth.lo]] - rationale - api/main.py
- [[FastAPI]] - code - api/main.py
- [[FastAPI application entry point.  Registers all routers, configures CORS, and]] - rationale - api/main.py
- [[FastAPI lifespan hook — runs startup checks then yields to serve requests.]] - rationale - api/main.py
- [[JWT creationverification and login endpoint.  Auth flow     1. Client POSTs]] - rationale - api/auth.py
- [[Liveness probe — returns immediately without any IO.      Google Sheets conne]] - rationale - api/main.py
- [[Log every HTTP request with method, path, status, and elapsed time.      Each]] - rationale - api/main.py
- [[LoginRequest]] - code - api/auth.py
- [[LoginRequest_1]] - code - api/main.py
- [[Request]] - code - api/main.py
- [[Request body for ``POST authlogin``.]] - rationale - api/auth.py
- [[Response body returned on successful login.]] - rationale - api/auth.py
- [[Root endpoint — returns a friendly API info payload.      Useful when browsing]] - rationale - api/main.py
- [[Tasks router — daily missions  task tracking.  Endpoints     GET  taskstoday]] - rationale - api/routers/tasks.py
- [[TokenResponse]] - code - api/auth.py
- [[TokenResponse_1]] - code - api/main.py
- [[Validate credentials against the Auth Sheet and return a JWT on success.]] - rationale - api/auth.py
- [[auth.py]] - code - api/auth.py
- [[health()]] - code - api/main.py
- [[lifespan()]] - code - api/main.py
- [[log_requests()]] - code - api/main.py
- [[login()]] - code - api/auth.py
- [[login_endpoint()]] - code - api/main.py
- [[main.py]] - code - api/main.py
- [[root()]] - code - api/main.py
- [[tasks.py]] - code - api/routers/tasks.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/App_Entry__Login
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Auth Sheet Credentials Cache]]
- 5 edges to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 4 edges to [[_COMMUNITY_Logging Configuration]]
- 4 edges to [[_COMMUNITY_Daily Task Service]]
- 3 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 3 edges to [[_COMMUNITY_Settings Service & Router]]
- 3 edges to [[_COMMUNITY_Weight REST Endpoints]]
- 3 edges to [[_COMMUNITY_Workout REST Endpoints]]
- 3 edges to [[_COMMUNITY_Sheets Client Singleton]]
- 3 edges to [[_COMMUNITY_Task Models & Router Tests]]
- 3 edges to [[_COMMUNITY_Tasks REST Endpoints]]
- 2 edges to [[_COMMUNITY_Shared Test Fixtures]]
- 2 edges to [[_COMMUNITY_Auth & JWT Tests]]
- 2 edges to [[_COMMUNITY_Workout Models & Router Tests]]

## Top bridge nodes
- [[auth.py]] - degree 19, connects to 9 communities
- [[main.py]] - degree 24, connects to 8 communities
- [[FastAPI]] - degree 12, connects to 6 communities
- [[tasks.py]] - degree 15, connects to 4 communities
- [[login()]] - degree 8, connects to 2 communities