---
source_file: "tests/test_auth.py"
type: "rationale"
community: "Auth & JWT Tests"
location: "L93"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Auth__JWT_Tests
---

# A user_id claim that cannot be coerced to int is rejected with 401.

## Connections
- [[.test_verify_jwt_non_numeric_user_id_raises_401()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/Auth__JWT_Tests