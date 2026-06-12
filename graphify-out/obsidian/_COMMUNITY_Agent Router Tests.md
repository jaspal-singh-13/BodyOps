---
type: community
cohesion: 0.11
members: 18
---

# Agent Router Tests

**Cohesion:** 0.11 - loosely connected
**Members:** 18 nodes

## Members
- [[.test_requires_auth()]] - code - tests/test_agent_router.py
- [[.test_requires_auth()_1]] - code - tests/test_agent_router.py
- [[.test_returns_204_with_auth()]] - code - tests/test_agent_router.py
- [[.test_returns_422_for_missing_fields()]] - code - tests/test_agent_router.py
- [[.test_returns_422_for_missing_message()]] - code - tests/test_agent_router.py
- [[.test_returns_422_for_missing_session_id()]] - code - tests/test_agent_router.py
- [[.test_returns_event_stream_with_auth()]] - code - tests/test_agent_router.py
- [[.test_sse_body_contains_events()]] - code - tests/test_agent_router.py
- [[HTTP-layer tests for the agent router — SSE endpoint and history clear.  Tests]] - rationale - tests/test_agent_router.py
- [[Minimal SSE generator that yields one text event and a done sentinel.      Use]] - rationale - tests/test_agent_router.py
- [[Module-scoped bearer token headers for user_id=1.]] - rationale - tests/test_agent_router.py
- [[Module-scoped test client with Sheets mocked.]] - rationale - tests/test_agent_router.py
- [[TestChatEndpoint]] - code - tests/test_agent_router.py
- [[TestClearHistoryEndpoint]] - code - tests/test_agent_router.py
- [[_fake_sse_gen()]] - code - tests/test_agent_router.py
- [[auth_headers()_1]] - code - tests/test_agent_router.py
- [[client()_1]] - code - tests/test_agent_router.py
- [[test_agent_router.py]] - code - tests/test_agent_router.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Agent_Router_Tests
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Shared Test Fixtures]]

## Top bridge nodes
- [[test_agent_router.py]] - degree 7, connects to 1 community
- [[auth_headers()_1]] - degree 3, connects to 1 community