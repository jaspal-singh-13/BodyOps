---
type: community
cohesion: 0.09
members: 27
---

# Auth & JWT Tests

**Cohesion:** 0.09 - loosely connected
**Members:** 27 nodes

## Members
- [[.test_analyze_drive_error_still_returns_200()]] - code - tests/test_meal_router.py
- [[.test_analyze_vision_error_returns_500()]] - code - tests/test_meal_router.py
- [[.test_bad_token_returns_401()]] - code - tests/test_auth.py
- [[.test_create_and_verify_jwt_returns_user_id()]] - code - tests/test_auth.py
- [[.test_login_email_case_insensitive()]] - code - tests/test_auth.py
- [[.test_login_second_user()]] - code - tests/test_auth.py
- [[.test_login_sheet_error()]] - code - tests/test_auth.py
- [[.test_login_success()]] - code - tests/test_auth.py
- [[.test_login_success_token_contains_user_id()]] - code - tests/test_auth.py
- [[.test_login_wrong_email()]] - code - tests/test_auth.py
- [[.test_login_wrong_password()]] - code - tests/test_auth.py
- [[.test_no_auth_header_returns_401()]] - code - tests/test_auth.py
- [[.test_verify_jwt_invalid_token_raises_401()]] - code - tests/test_auth.py
- [[.test_verify_jwt_missing_user_id_claim_raises_401()]] - code - tests/test_auth.py
- [[.test_verify_jwt_non_numeric_user_id_raises_401()]] - code - tests/test_auth.py
- [[A correctly-signed token without a user_id claim is rejected with 401, not 500.]] - rationale - tests/test_auth.py
- [[A user_id claim that cannot be coerced to int is rejected with 401.]] - rationale - tests/test_auth.py
- [[Decode and verify a JWT, returning the ``user_id`` claim.      Args]] - rationale - api/auth.py
- [[Drive upload failure is non-fatal — analysis proceeds with empty drive_url.]] - rationale - tests/test_meal_router.py
- [[Exception]] - code
- [[TestJWTUtilities]] - code - tests/test_auth.py
- [[TestLoginEndpoint]] - code - tests/test_auth.py
- [[TestProtectedRoute]] - code - tests/test_auth.py
- [[Tests for POST authlogin, JWT utilities, and get_current_user dependency.]] - rationale - tests/test_auth.py
- [[_find_user()]] - code - tests/test_auth.py
- [[test_auth.py]] - code - tests/test_auth.py
- [[verify_jwt()]] - code - api/auth.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Auth__JWT_Tests
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_App Entry & Login]]
- 2 edges to [[_COMMUNITY_Shared Test Fixtures]]
- 2 edges to [[_COMMUNITY_Meal Analyze Endpoint Tests]]
- 1 edge to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 1 edge to [[_COMMUNITY_Workout Models & Router Tests]]

## Top bridge nodes
- [[verify_jwt()]] - degree 10, connects to 2 communities
- [[test_auth.py]] - degree 8, connects to 2 communities
- [[Exception]] - degree 4, connects to 1 community
- [[.test_create_and_verify_jwt_returns_user_id()]] - degree 3, connects to 1 community
- [[.test_analyze_drive_error_still_returns_200()]] - degree 3, connects to 1 community