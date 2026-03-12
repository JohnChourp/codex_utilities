# Current Auth-Drift Findings Baseline (CodeDeliver)

This file captures the current static-audit baseline and should be treated as a starting point, not as live-log proof by itself.

## Remediation Matrix Snapshot

| product | login_lambda | renew_lambda | authorizer | frontend_auth_entry | identity_source_table | late_failure_signatures | risk_level | recommended_fix_wave |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `codeliver-pos` | `codeliver-pos-login` | `codeliver-pos-renew-token` | `codeliver-pos-authorizer` | `projects/codeliver/codeliver-pos/src/app/shared/auth/auth.service.ts` | `codeliver-pos-users` | `user_does_not_exist`, `no_user_found` | `confirmed systemic risk` | `baseline` |
| `codeliver-panel` | `codeliver-panel-login` | `codeliver-panel-renew-token` | `codeliver-panel-authorizer` | `projects/codeliver/codeliver-panel/src/app/shared/auth/auth.service.ts` | `codeliver-panel-users` | `user_does_not_exist`, `no_user_found` | `confirmed systemic risk` | `wave_1` |
| `codeliver-sap` | `codeliver-sap-login` | `codeliver-sap-renew-token` | `codeliver-sap-authorizer` | `projects/codeliver/codeliver-sap/src/app/shared/auth/auth.service.ts` | `codeliver-sap-users` | `user_does_not_exist`, `user_not_found`, `no_user_found` | `likely risk` | `wave_2` |
| `codeliver-app` | `codeliver-app-device-login`, `codeliver-app-login-mobile-pin` | `codeliver-app-renew-device-token` | `codeliver-app-authorizer` | `projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts` | `codeliver-devices`, `codeliver-delivery-guys` | `delivery_guy_does_not_exist`, `device_does_not_exist`, `no_device_found` | `likely risk` | `wave_3` |

## Key static evidence

### POS baseline
- POS already produced a confirmed stale-session incident where valid authorizer context reached a protected lambda and failed late on `codeliver-pos-users`.
- This product is the reference implementation for remediation, not just another audit target.

### Panel
- `codeliver-panel-login` still does blind selection with `users[0]`.
  - Evidence: `codeliver-panel-login/index.js:92-100`
- `codeliver-panel-renew-token` still issues long-lived tokens with `expiresIn: 2000000`.
  - Evidence: `codeliver-panel-renew-token/index.js:61-71`, `:140-142`
- `codeliver-panel-authorizer` does JWT verify and returns `Allow`, but there is no current-user existence check against `codeliver-panel-users`.
  - Evidence: `codeliver-panel-authorizer/index.js:279-306`
- Many protected panel lambdas still fail late with `user_does_not_exist`.
  - Evidence examples: `codeliver-panel-fetch-group-stores`, `codeliver-panel-fetch-localservers`, `codeliver-panel-search-group-delivery-requests`

### SAP
- `codeliver-sap-login` issues long-lived tokens with `expiresIn: 1209600`.
  - Evidence: `codeliver-sap-login/index.js:52-60`
- `codeliver-sap-renew-token` also uses `expiresIn: 1209600`.
  - Evidence: `codeliver-sap-renew-token/index.js:44-52`, `:116-123`
- `codeliver-sap-authorizer` is verify-only and does not check that the current `superadmin_id` still exists in `codeliver-sap-users`.
  - Evidence: `codeliver-sap-authorizer/index.js:45-105`
- Multiple protected SAP lambdas do late `get_sap_user_by_superadmin_id(...)` lookups and fail with `user_does_not_exist` / `user_not_found`.
  - Evidence examples: `codeliver-sap-fetch-delivery-requests`, `codeliver-sap-fetch-routes`, `codeliver-sap-fetch-zones`, `codeliver-sap-fetch-groups`

### App
- `codeliver-app-authorizer` is verify-only and returns `Allow` without validating the current device/delivery-guy relationship.
  - Evidence: `codeliver-app-authorizer/index.js:258-309`
- `codeliver-app-renew-device-token` still uses `expiresIn: 2000000`.
  - Evidence: `codeliver-app-renew-device-token/index.js:94-104`
- Core protected app lambdas still fail late with `delivery_guy_does_not_exist` / `device_does_not_exist`.
  - Evidence examples: `codeliver-app-fetch-delivery-requests`, `codeliver-app-fetch-notifications`, `codeliver-app-fetch-routes`
- App frontend renew flow is less obviously fail-open than POS/Panel, so this is currently `likely risk`, not `confirmed systemic risk`.

## Suggested rollout
- Wave 1: `codeliver-panel`
- Wave 2: `codeliver-sap`
- Wave 3: `codeliver-app`

## Important note
Upgrade any `likely risk` product to `confirmed systemic risk` only after live log correlation proves that stale claims are reaching protected lambdas in production.
