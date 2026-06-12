---
type: community
cohesion: 0.28
members: 9
---

# Meal Analyzer Factory Tests

**Cohesion:** 0.28 - loosely connected
**Members:** 9 nodes

## Members
- [[.test_analyze_photo_downloads_bytes_and_runs_vision()]] - code - tests/test_meal_router.py
- [[.test_analyze_photo_fetch_failure_returns_error_dict()]] - code - tests/test_meal_router.py
- [[A download failure returns an error dict instead of raising.]] - rationale - tests/test_meal_router.py
- [[Return a patch for httpx.AsyncClient whose ``get`` resolves to the given mock re]] - rationale - tests/test_meal_router.py
- [[Return an async callable that runs vision analysis on a meal photo URL.      `]] - rationale - api/routers/agent.py
- [[TestAgentAnalyzeMealPhoto]] - code - tests/test_meal_router.py
- [[The meal_analyzer factory downloads the image and passes bytes + mime to vision.]] - rationale - tests/test_meal_router.py
- [[_make_meal_analyzer()]] - code - api/routers/agent.py
- [[_mock_httpx_async_client()]] - code - tests/test_meal_router.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meal_Analyzer_Factory_Tests
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 2 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 1 edge to [[_COMMUNITY_Meal Macro Schemas]]
- 1 edge to [[_COMMUNITY_Nutrition Target Checks]]
- 1 edge to [[_COMMUNITY_Meal Vision Service]]

## Top bridge nodes
- [[TestAgentAnalyzeMealPhoto]] - degree 10, connects to 3 communities
- [[_make_meal_analyzer()]] - degree 7, connects to 3 communities
- [[_mock_httpx_async_client()]] - degree 4, connects to 1 community