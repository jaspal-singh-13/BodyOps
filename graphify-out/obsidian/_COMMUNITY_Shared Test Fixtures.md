---
type: community
cohesion: 0.29
members: 8
---

# Shared Test Fixtures

**Cohesion:** 0.29 - loosely connected
**Members:** 8 nodes

## Members
- [[Create a signed JWT containing the user's email and integer ID.      The token]] - rationale - api/auth.py
- [[Session-scoped FastAPI test client with ``get_main_sheet`` mocked.      Mockin]] - rationale - tests/conftest.py
- [[Session-scoped bearer token headers for ``user_id=1``.      Creates a real JWT]] - rationale - tests/conftest.py
- [[Shared pytest fixtures for all test modules.  Sets required environment variab]] - rationale - tests/conftest.py
- [[auth_headers()]] - code - tests/conftest.py
- [[client()]] - code - tests/conftest.py
- [[conftest.py]] - code - tests/conftest.py
- [[create_jwt()]] - code - api/auth.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Shared_Test_Fixtures
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_App Entry & Login]]
- 2 edges to [[_COMMUNITY_Agent Router Tests]]
- 2 edges to [[_COMMUNITY_Auth & JWT Tests]]

## Top bridge nodes
- [[create_jwt()]] - degree 9, connects to 3 communities