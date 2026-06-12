---
type: community
cohesion: 0.11
members: 19
---

# Meal Integration Tests

**Cohesion:** 0.11 - loosely connected
**Members:** 19 nodes

## Members
- [[.test_post_analyze_empty_file_returns_400()]] - code - tests/test_meal_integration.py
- [[.test_post_analyze_kurkure_full_pipeline()]] - code - tests/test_meal_integration.py
- [[.test_post_analyze_kurkure_via_http()]] - code - tests/test_meal_integration.py
- [[.test_post_analyze_no_auth_returns_401()]] - code - tests/test_meal_integration.py
- [[.test_post_analyze_wrong_mime_returns_400()]] - code - tests/test_meal_integration.py
- [[.test_upload_kurkure_to_shared_drive()]] - code - tests/test_meal_integration.py
- [[Empty file body is rejected before any API call.]] - rationale - tests/test_meal_integration.py
- [[Full end-to-end real OpenAI vision + real Google Drive upload.         Only ru]] - rationale - tests/test_meal_integration.py
- [[Integration tests for the meal photo analysis pipeline.  These tests use the r]] - rationale - tests/test_meal_integration.py
- [[Non-image MIME type is rejected before any API call.]] - rationale - tests/test_meal_integration.py
- [[POST mealsanalyze with the real kurkure.jpg through the FastAPI test]] - rationale - tests/test_meal_integration.py
- [[Real Drive upload kurkure.jpg should be uploaded to the Shared Drive         f]] - rationale - tests/test_meal_integration.py
- [[TestDriveServiceIntegration]] - code - tests/test_meal_integration.py
- [[TestMealRouterIntegration]] - code - tests/test_meal_integration.py
- [[Unauthenticated request is rejected before any processing.]] - rationale - tests/test_meal_integration.py
- [[_has_real_drive()]] - code - tests/test_meal_integration.py
- [[_has_real_openai()]] - code - tests/test_meal_integration.py
- [[kurkure_bytes()]] - code - tests/test_meal_integration.py
- [[test_meal_integration.py]] - code - tests/test_meal_integration.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meal_Integration_Tests
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Drive Photo Upload]]
- 1 edge to [[_COMMUNITY_Meal Vision Service]]
- 1 edge to [[_COMMUNITY_Meal Vision Integration Tests]]

## Top bridge nodes
- [[test_meal_integration.py]] - degree 9, connects to 3 communities
- [[.test_upload_kurkure_to_shared_drive()]] - degree 3, connects to 1 community