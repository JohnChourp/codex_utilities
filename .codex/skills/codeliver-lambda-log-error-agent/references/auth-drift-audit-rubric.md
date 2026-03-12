# Auth-Drift Audit Rubric (CodeDeliver)

Use this rubric when the goal is to find stale-session or invalid-auth-context risk across products, not just to triage one failing request.

## Products
- `codeliver-pos`
- `codeliver-panel`
- `codeliver-sap`
- `codeliver-app`

## Required inventory per product
- `login_lambda`
- `renew_lambda`
- `authorizer`
- `frontend_auth_entry`
- `identity_source_table`
- `late_failure_signatures`
- `risk_level`
- `recommended_fix_wave`

## Auth surfaces to inspect
### Login issuance contract
- Token TTL value
- Whether login does blind selection such as `users[0]`
- Whether login verifies only existence or also permissions / current identity context
- Whether login response contains enough state for frontend gating

### Renew-token contract
- Token TTL value
- Whether renew re-checks the same canonical identity source used by protected lambdas
- Whether renew returns controlled auth failures (`401` / `Unauthorized`) or generic failures
- Whether renew path can keep stale session state alive on the client

### Authorizer depth
- JWT verify only
- JWT verify + canonical identity existence check
- JWT verify + existence + relationship check
- Failure mapping quality (`Unauthorized` vs custom string errors that leak into transport failures)

### Downstream protected-lambda checks
- Repeated identity lookups after the authorizer
- Error codes such as:
  - `no_user_found`
  - `user_not_found`
  - `user_does_not_exist`
  - `delivery_guy_does_not_exist`
  - `device_does_not_exist`
- Whether downstream identity failure suggests the authorizer should have denied earlier

### Frontend fail-close behavior
- Does renew retry restore `login_completed` or equivalent auth-complete state?
- Does the frontend log out on auth-like terminal failures?
- Does the UI continue to call protected endpoints while the session is stale?

## High-signal discovery signatures
- `users[0]`
- `expiresIn: 2000000`
- `expiresIn: 1209600`
- `jwt.verify`
- `authorizationToken`
- `principalId`
- `login_completed`
- `no_user_found`
- `user_does_not_exist`
- `delivery_guy_does_not_exist`
- `device_does_not_exist`

## Risk classification
### `confirmed systemic risk`
Use only when at least one of these is true:
- live logs confirm auth-like failures reaching protected lambdas after a valid authorizer context
- multiple protected lambdas in the same product repeat the same late identity failure pattern
- static audit shows both:
  - verify-only authorizer or inconsistent login/renew contract
  - repeated downstream identity failures tied to the same canonical identity table

### `likely risk`
Use when:
- static audit shows one or more strong smells, but live logs are not yet correlated
- only one late-failure path is confirmed and the rest is inferred from adjacent code

### `monitor-only`
Use when:
- auth boundaries appear aligned
- frontend fail-close behavior is already in place
- downstream missing-identity failures do not indicate authorizer drift

## Recommended remediation waves
- Wave 1: product with confirmed stale-session or fail-open frontend behavior plus verify-only authorizer
- Wave 2: product with verify-only authorizer and many repeated late identity failures
- Wave 3: product with dual-identity or more complex relationship checks that need design clarification before hardening
