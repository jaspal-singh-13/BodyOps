---
type: community
cohesion: 0.14
members: 28
---

# Meal Vision Service

**Cohesion:** 0.14 - loosely connected
**Members:** 28 nodes

## Members
- [[.test_base64_data_url_sent_to_openai()]] - code - tests/test_meal_vision.py
- [[.test_confidence_levels_mapped_per_item()]] - code - tests/test_meal_vision.py
- [[.test_drive_url_defaults_to_empty_string()]] - code - tests/test_meal_vision.py
- [[.test_drive_url_preserved()]] - code - tests/test_meal_vision.py
- [[.test_empty_items_returns_valid_response()]] - code - tests/test_meal_vision.py
- [[.test_none_parsed_raises_value_error()]] - code - tests/test_meal_vision.py
- [[.test_png_mime_type_used_in_data_url()]] - code - tests/test_meal_vision.py
- [[.test_totals_computed_from_items()]] - code - tests/test_meal_vision.py
- [[.test_valid_response_parses_correctly()]] - code - tests/test_meal_vision.py
- [[All three confidence levels are preserved per item.]] - rationale - tests/test_meal_vision.py
- [[Analyse a meal photo and return a structured macro breakdown.      Encodes the]] - rationale - api/services/meal_vision.py
- [[AnalyzeMealResponse_2]] - code - api/services/meal_vision.py
- [[Build a mock structured-output parse result from raw dicts.]] - rationale - tests/test_meal_vision.py
- [[Empty items list (unrecognisable image) returns valid zero-total response.]] - rationale - tests/test_meal_vision.py
- [[Full valid response is parsed into AnalyzeMealResponse.]] - rationale - tests/test_meal_vision.py
- [[If structured output returns None, ValueError is raised.]] - rationale - tests/test_meal_vision.py
- [[OpenAI receives a base64 data URL built from the raw bytes.]] - rationale - tests/test_meal_vision.py
- [[PNG bytes produce a dataimagepng;base64,… URL.]] - rationale - tests/test_meal_vision.py
- [[Return a mock AsyncAzureOpenAI whose beta.chat.completions.parse returns the com]] - rationale - tests/test_meal_vision.py
- [[TestAnalyzeMeal]] - code - tests/test_meal_vision.py
- [[Tests for the meal vision service (apiservicesmeal_vision.py).  Covers   -]] - rationale - tests/test_meal_vision.py
- [[Total macros are summed from items, not trusted directly from model output.]] - rationale - tests/test_meal_vision.py
- [[_make_parse_result()]] - code - tests/test_meal_vision.py
- [[_mock_client()]] - code - tests/test_meal_vision.py
- [[analyze_meal()]] - code - api/services/meal_vision.py
- [[drive_url defaults to '' when not supplied.]] - rationale - tests/test_meal_vision.py
- [[drive_url passed in is stored unchanged on the response.]] - rationale - tests/test_meal_vision.py
- [[test_meal_vision.py]] - code - tests/test_meal_vision.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meal_Vision_Service
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 4 edges to [[_COMMUNITY_Meal Macro Schemas]]
- 3 edges to [[_COMMUNITY_Meal Vision Integration Tests]]
- 1 edge to [[_COMMUNITY_Pydantic AI Agent Core]]
- 1 edge to [[_COMMUNITY_Agent Router & Chat History]]
- 1 edge to [[_COMMUNITY_Meal Analyzer Factory Tests]]
- 1 edge to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 1 edge to [[_COMMUNITY_Drive Photo Upload]]
- 1 edge to [[_COMMUNITY_Meal Integration Tests]]

## Top bridge nodes
- [[analyze_meal()]] - degree 25, connects to 9 communities
- [[TestAnalyzeMeal]] - degree 13, connects to 2 communities
- [[test_meal_vision.py]] - degree 8, connects to 2 communities