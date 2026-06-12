---
type: community
cohesion: 0.20
members: 10
---

# Meal Macro Schemas

**Cohesion:** 0.20 - loosely connected
**Members:** 10 nodes

## Members
- [[._calories_non_negative()]] - code - api/models/meal.py
- [[._macros_non_negative()]] - code - api/models/meal.py
- [[.test_save_meal_empty_items_accepted()]] - code - tests/test_meal_router.py
- [[AI vision service for meal photo analysis.  Sends a meal photo URL to Azure Op]] - rationale - api/services/meal_vision.py
- [[Combined macro totals for a meal or day.]] - rationale - api/models/meal.py
- [[Empty items list is valid — user manually deleted all items.]] - rationale - tests/test_meal_router.py
- [[MacroTotal]] - code - api/models/meal.py
- [[_ItemSchema]] - code - api/services/meal_vision.py
- [[_MealAnalysisSchema]] - code - api/services/meal_vision.py
- [[meal_vision.py]] - code - api/services/meal_vision.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meal_Macro_Schemas
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 4 edges to [[_COMMUNITY_Meal Vision Service]]
- 3 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 3 edges to [[_COMMUNITY_Meal Service Logic]]
- 2 edges to [[_COMMUNITY_Pydantic AI Agent Core]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 1 edge to [[_COMMUNITY_Meal Analyzer Factory Tests]]
- 1 edge to [[_COMMUNITY_Meal Analyze Endpoint Tests]]
- 1 edge to [[_COMMUNITY_Agent Router & Chat History]]
- 1 edge to [[_COMMUNITY_Meals Router & Auth Dependency]]

## Top bridge nodes
- [[MacroTotal]] - degree 22, connects to 6 communities
- [[meal_vision.py]] - degree 14, connects to 6 communities
- [[.test_save_meal_empty_items_accepted()]] - degree 4, connects to 1 community
- [[_ItemSchema]] - degree 2, connects to 1 community
- [[_MealAnalysisSchema]] - degree 2, connects to 1 community