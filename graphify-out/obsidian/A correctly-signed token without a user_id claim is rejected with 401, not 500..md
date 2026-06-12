---
source_file: "tests/test_auth.py"
type: "rationale"
community: "Auth & JWT Tests"
location: "L80"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Auth__JWT_Tests
---

# A correctly-signed token without a user_id claim is rejected with 401, not 500.

## Connections
- [[.test_verify_jwt_missing_user_id_claim_raises_401()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/Auth__JWT_Tests