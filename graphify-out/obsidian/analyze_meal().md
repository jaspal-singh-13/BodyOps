---
source_file: "api/services/meal_vision.py"
type: "code"
community: "Meal Vision Service"
location: "L93"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Meal_Vision_Service
---

# analyze_meal()

## Connections
- [[.test_analyze_kurkure_drive_url_passed_through()]] - `calls` [EXTRACTED]
- [[.test_analyze_kurkure_returns_snack_items()]] - `calls` [EXTRACTED]
- [[.test_analyze_kurkure_totals_match_items()]] - `calls` [EXTRACTED]
- [[.test_base64_data_url_sent_to_openai()]] - `calls` [EXTRACTED]
- [[.test_confidence_levels_mapped_per_item()]] - `calls` [EXTRACTED]
- [[.test_drive_url_defaults_to_empty_string()]] - `calls` [EXTRACTED]
- [[.test_drive_url_preserved()]] - `calls` [EXTRACTED]
- [[.test_empty_items_returns_valid_response()]] - `calls` [EXTRACTED]
- [[.test_none_parsed_raises_value_error()]] - `calls` [EXTRACTED]
- [[.test_png_mime_type_used_in_data_url()]] - `calls` [EXTRACTED]
- [[.test_totals_computed_from_items()]] - `calls` [EXTRACTED]
- [[.test_valid_response_parses_correctly()]] - `calls` [EXTRACTED]
- [[Analyse a meal photo and return a structured macro breakdown.      Encodes the]] - `rationale_for` [EXTRACTED]
- [[AnalyzeMealResponse_2]] - `references` [EXTRACTED]
- [[AnalyzeMealResponse]] - `calls` [EXTRACTED]
- [[DetectedItem]] - `calls` [EXTRACTED]
- [[MacroTotal]] - `calls` [EXTRACTED]
- [[_make_meal_analyzer()]] - `calls` [EXTRACTED]
- [[agent.py_1]] - `imports` [EXTRACTED]
- [[analyze_meal_endpoint()]] - `calls` [EXTRACTED]
- [[get_async_client()]] - `calls` [EXTRACTED]
- [[meal_vision.py]] - `contains` [EXTRACTED]
- [[meals.py]] - `imports` [EXTRACTED]
- [[test_meal_integration.py]] - `imports` [EXTRACTED]
- [[test_meal_vision.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Meal_Vision_Service