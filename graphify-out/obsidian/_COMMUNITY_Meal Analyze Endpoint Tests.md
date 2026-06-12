---
type: community
cohesion: 0.33
members: 6
---

# Meal Analyze Endpoint Tests

**Cohesion:** 0.33 - loosely connected
**Members:** 6 nodes

## Members
- [[.test_analyze_empty_file_returns_400()]] - code - tests/test_meal_router.py
- [[.test_analyze_no_auth_returns_401()]] - code - tests/test_meal_router.py
- [[.test_analyze_success()]] - code - tests/test_meal_router.py
- [[.test_analyze_unsupported_mime_returns_400()]] - code - tests/test_meal_router.py
- [[.test_analyze_value_error_returns_422()]] - code - tests/test_meal_router.py
- [[TestPostMealsAnalyze]] - code - tests/test_meal_router.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meal_Analyze_Endpoint_Tests
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 2 edges to [[_COMMUNITY_Auth & JWT Tests]]
- 1 edge to [[_COMMUNITY_Meal Macro Schemas]]
- 1 edge to [[_COMMUNITY_Nutrition Target Checks]]

## Top bridge nodes
- [[TestPostMealsAnalyze]] - degree 15, connects to 4 communities