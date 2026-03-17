# CodeDeliver Lambda Hardening Policy (On-Demand)

Load this policy when a task changes lambda code, lambda contracts, or lambda deployment/hardening behavior.

## Lambda-first safety rules

- Before changing any lambda, review `.codex/AGENTS.md` and the relevant `.codex/refs/codeliver-*-lambdas.md` reference files to confirm required inputs/examples so the flow does not break.
- CustomError translation coverage (frontend-facing): when adding/changing any `CustomError` code in a lambda that is frontend-reachable (directly called by frontend, or one-hop downstream from a frontend-called lambda and its result is returned to frontend), you MUST ensure translation coverage in impacted frontend project(s) for **all** `src/assets/i18n/*.json` files.
  - Frontend-visible error fields are `comment_id` and `comments`.
  - Caller-based path policy:
    - Use nested keys `lambdas_responses.<caller_lambda>.<error_code>` when the frontend caller path uses `presentPostFailureAlert(..., "<caller_lambda>")` or `lambdas_responses.<caller_lambda>.`.
    - Use root key `<error_code>` when the frontend caller path translates `res.comment_id` / `res?.comment_id` directly.
  - For unresolved lambda mapping from refs, treat as warn+skip (do not block unrelated work), but report them explicitly.

## Node.js Lambda rules (always)

- **Null-safe optional fields:** when reading fields from DynamoDB/API results that may be missing, always use optional chaining or explicit guards (e.g. `request?.readyToPickUp`, `request?.status`) to prevent runtime `TypeError` from `undefined` values.
- **AWS SDK v3 deps in Lambdas**: never add `@aws-sdk/*` to a Node.js Lambda `package.json`. If they already exist, remove them from `package.json` and update `package-lock.json`, even when the code imports them, because the Lambda execution environment provides AWS SDK v3 at runtime.
  - This rule also applies to local compile/test convenience: do **not** add `@aws-sdk/*` just to satisfy editor or local `npm install` resolution in Lambda repos.
  - If a repo still contains `@aws-sdk/*` for non-Lambda reasons, do **not** version-pin them in `package.json` (prefer semver ranges like `^`) and remove any unused ones.
- **Deploy scripts must be canonical**: ensure scripts exist (rewrite legacy `zsh -ic 'lu'` wrappers to these):
  - `deploy:prod`: `lambda-upload deploy-prod df`
  - `deploy:prod:check`: `lambda-upload deploy-prod df --check --force --assume-runtime nodejs24.x`
  - `deploy:prod:upgrade`: `lambda-upload deploy-prod df --upgrade-config`
- **Legacy callback handlers must be removed**: migrate handlers from the legacy callback style (`(event, context, callback)` + `callback(...)`) to `async`/`await` with `return`/`throw`.
  - Do **not** keep mixed signatures like `async (event, context, callback)`; treat this as a harden failure.
  - Preserve behavior: keep the same returned payload shape and the same error message strings (e.g. authorizers must still fail with `"Unauthorized"` when expected).
  - Quick self-check: `rg -n "\\bcallback\\b|context\\.succeed\\b|context\\.fail\\b" -S .`
- **Client retry overrides must be stripped**: keep existing behavior and do NOT set `maxAttempts` / `retryMode` when creating AWS SDK clients in code (unless explicitly requested):
  - `new DynamoDBClient({ ... })` -> remove `maxAttempts` / `retryMode`
  - `new LambdaClient({ ... })` -> remove `maxAttempts` / `retryMode`
- **Handled errors policy must be present when applicable**: if the harden prompt/run mentions `handled-errors-policy` (or the lambda uses `CustomError`), ensure the repo includes the policy wiring and do not rely on harden flows to add it later:
  - A `custom_errors.policy.json` (v1) in the lambda root and an implementation module (commonly `handled_errors.js`) that reads it.
  - Policy schema requirement: `defaults` must include both `emit_requestid_success` and `log_event` (safe defaults: both `false`).
  - Add/merge string-literal `CustomError` codes into the policy under `errors.<code>` and keep both toggles policy-driven:
    - `emit_requestid_success`: controls `RequestId SUCCESS` emission for that code.
    - `log_event`: controls whether the redacted incoming event is logged for that code.
  - Add explicit entries for known handled codes (do not rely only on defaults). For auth flows, include `Unauthorized` explicitly so event logging can be controlled independently for JWT-verify failures.
  - For every lambda execution completion path (all terminal branches: early return, success return, handled error return, catch/failure return, and any other final outcome), always add distinct policy-controlled keys in `custom_errors.policy.json` (prefer `flags.*`) so each terminal path can independently control `RequestId SUCCESS` emission.
  - Event logging must remain policy-driven by `log_event`; when enabled, log the incoming event once (redacted, keep `event.body` intact).
  - Quick self-check: `rg -n "custom_errors\\.policy\\.json|handled_errors\\.js" -S .`
- **Harden skill composition (mandatory):** when the active run uses `crp-repos-harden-pr` or `crp-repos-harden-deploy`, apply the embedded `ACTION:SLACK_COMMENT` error-context workflow in the same harden flow (combined execution).
  - During those harden runs, perform full-lambda handled-error coverage (entire lambda, not partial): inspect all terminal paths and all handled `CustomError` branches and synchronize `custom_errors.policy.json` accordingly.
  - In those harden runs, `custom_errors.policy.json` must contain explicit per-entry booleans for `log_event` (`true` or `false`) across policy-controlled entries (`errors.<code>` and `flags.<path_or_outcome>`); do not leave per-entry logging behavior implicit.
  - In those harden runs, keep `emit_requestid_success` policy-controlled per terminal outcome as already required.
  - In those harden runs, always stamp `package.json` `version` to show the latest harden timestamp. Keep the SemVer core (`X.Y.Z`) unchanged and set/replace build metadata to `+harden.YYYYMMDDHHmm` (Europe/Athens), e.g. `1.4.2+harden.20260218.1540`.
  - In those harden-pr runs, update/create top-level `package.json.harden_pr_timestamp` as a string with format `YYYYMMDDHHmm` (Europe/Athens), e.g. `202602181540`.
  - In those harden-deploy runs, update/create top-level `package.json.harden_deploy_timestamp` as a string with format `YYYYMMDDHHmm` (Europe/Athens), e.g. `202602181540`.
  - Update only the timestamp key that corresponds to the active harden flow (`harden_pr_timestamp` for harden-pr, `harden_deploy_timestamp` for harden-deploy`) and never delete the other key when present.
  - Keep the Slack action marker implementation (`ACTION:SLACK_HANDLED_ERROR_HE1=...`) and encoding rules under that combined harden flow.
  - Outside those harden skills, do not add or modify Slack action marker behavior unless the user explicitly requests it.
