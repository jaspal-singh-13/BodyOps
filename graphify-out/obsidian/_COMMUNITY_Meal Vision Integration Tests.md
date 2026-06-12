---
type: community
cohesion: 0.29
members: 7
---

# Meal Vision Integration Tests

**Cohesion:** 0.29 - loosely connected
**Members:** 7 nodes

## Members
- [[.test_analyze_kurkure_drive_url_passed_through()]] - code - tests/test_meal_integration.py
- [[.test_analyze_kurkure_returns_snack_items()]] - code - tests/test_meal_integration.py
- [[.test_analyze_kurkure_totals_match_items()]] - code - tests/test_meal_integration.py
- [[Real OpenAI call kurkure.jpg should be identified as a snackchips.         As]] - rationale - tests/test_meal_integration.py
- [[TestMealVisionIntegration]] - code - tests/test_meal_integration.py
- [[Totals are computed by summing items — verify they match within rounding.]] - rationale - tests/test_meal_integration.py
- [[drive_url arg is stored on result even when Drive upload is skipped.]] - rationale - tests/test_meal_integration.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meal_Vision_Integration_Tests
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Meal Vision Service]]
- 1 edge to [[_COMMUNITY_Meal Integration Tests]]

## Top bridge nodes
- [[TestMealVisionIntegration]] - degree 4, connects to 1 community
- [[.test_analyze_kurkure_drive_url_passed_through()]] - degree 3, connects to 1 community
- [[.test_analyze_kurkure_returns_snack_items()]] - degree 3, connects to 1 community
- [[.test_analyze_kurkure_totals_match_items()]] - degree 3, connects to 1 community