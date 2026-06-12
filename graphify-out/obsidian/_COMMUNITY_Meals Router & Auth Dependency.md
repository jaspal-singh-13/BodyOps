---
type: community
cohesion: 0.12
members: 19
---

# Meals Router & Auth Dependency

**Cohesion:** 0.12 - loosely connected
**Members:** 19 nodes

## Members
- [[ConfirmMealRequest_1]] - code - api/routers/meals.py
- [[DailyNutrition_1]] - code - api/routers/meals.py
- [[FastAPI dependency that extracts and verifies the bearer token.      Inject th]] - rationale - api/auth.py
- [[Fire-and-forget wrapper so nutrition target checks never delay the response.]] - rationale - api/routers/meals.py
- [[HTTPAuthorizationCredentials]] - code - api/auth.py
- [[MealHistoryDay_1]] - code - api/routers/meals.py
- [[Meals router — meal photo analysis, confirmation, and history.  Endpoints]] - rationale - api/routers/meals.py
- [[Return per-day nutrition summaries for the last 30 days.      Days with no mea]] - rationale - api/routers/meals.py
- [[Return today's nutrition totals and targets for the authenticated user.      R]] - rationale - api/routers/meals.py
- [[Run a coroutine as a background task that survives garbage collection.]] - rationale - api/routers/meals.py
- [[Save a confirmed meal (and its items) to the Sheets.      The ``items`` list s]] - rationale - api/routers/meals.py
- [[SavedMealResponse_1]] - code - api/routers/meals.py
- [[_bg_check_nutrition()]] - code - api/routers/meals.py
- [[_spawn_bg()]] - code - api/routers/meals.py
- [[get_current_user()]] - code - api/auth.py
- [[get_history_endpoint()]] - code - api/routers/meals.py
- [[get_today_endpoint()]] - code - api/routers/meals.py
- [[meals.py]] - code - api/routers/meals.py
- [[save_meal_endpoint()]] - code - api/routers/meals.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meals_Router__Auth_Dependency
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_App Entry & Login]]
- 5 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 5 edges to [[_COMMUNITY_Meal Service Logic]]
- 3 edges to [[_COMMUNITY_Drive Photo Upload]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 2 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 1 edge to [[_COMMUNITY_Auth & JWT Tests]]
- 1 edge to [[_COMMUNITY_Agent Router & Chat History]]
- 1 edge to [[_COMMUNITY_Settings Service & Router]]
- 1 edge to [[_COMMUNITY_Weight REST Endpoints]]
- 1 edge to [[_COMMUNITY_Workout REST Endpoints]]
- 1 edge to [[_COMMUNITY_Meal Macro Schemas]]
- 1 edge to [[_COMMUNITY_Meal Vision Service]]
- 1 edge to [[_COMMUNITY_Daily Task Service]]

## Top bridge nodes
- [[meals.py]] - degree 30, connects to 9 communities
- [[get_current_user()]] - degree 10, connects to 6 communities