# `dmngr/lambda-policies` notes (source-of-truth + common mistakes)

Source of truth: `dmngr/lambda-policies` (GitHub repo).

Preferred for day-to-day use: keep a **local clone** so you can read files fast/offline and so the agent can grep across the policies without relying on network.

Typical local location (example only; do not hardcode): `~/repos/lambda-policies`

## Ensure local clone (recommended)

If the local clone is missing, create it:

- Preferred (if you have `gh` auth):
  - `mkdir -p ~/repos && cd ~/repos`
  - `gh repo clone dmngr/lambda-policies`
- Fallback (plain git):
  - `mkdir -p ~/repos && cd ~/repos`
  - `git clone git@github.com:dmngr/lambda-policies.git`

Treat this repo as **source of truth** for:
- handled-errors logging contract + `custom_errors.policy.json` semantics
- harden policy/phases (Node LTS/Node 24 + `arm64`)

If anything here conflicts with other docs/prompts, prefer `dmngr/lambda-policies`.

Canonical ownership map (quick):
- General Lambda logging baseline: `printed-logs/printed-logs-policy.md`
- Handled-errors contract (`ACTION:...` + `RequestId SUCCESS` suppression): `handled-errors/handled-error-policy.md`
- Handled-errors automation behavior: `handled-errors/handled-errors-policy-tooling.md`
- Hardening flow/phases/checkpoints: `harden/README.md` + `harden/harden-policy.md`

Scope note:
- For policy/docs-only edits in `dmngr/lambda-policies`, do not run harden flows.
- For Lambda repo runtime/arch hardening, default to PR-first (`crp repos harden-pr`) and use deploy flow (`crp repos harden-deploy`) only with explicit deploy intent.

## Key docs to read (only when needed)

- Handled errors contract:
  - `handled-errors/handled-error-policy.md`
  - `handled-errors/handled-errors-policy-tooling.md`
- Harden policy:
  - `harden/harden-policy.md` (and linked phase docs under `harden/`)

## Common mistakes (high-signal)

### ACTION marker parsing breaks (whitespace)

The ingestor expects the `ACTION:SLACK_HANDLED_ERROR_HE1=...` marker to be a **single whitespace-delimited token**.

Avoid:
- spaces around `=` or `|`
- multi-line logs that split the token
- printing the JSON payload with spaces *inside the token*

Prefer the canonical shape:
- `ACTION:SLACK_HANDLED_ERROR_HE1=<error_code>|<base64url(json)>`

### Wrong `RequestId SUCCESS` placement

Never add `console.log("RequestId SUCCESS")` inside:
- `catch` blocks
- generic error middleware/handlers

Only emit it when the handled-error policy says to suppress legacy Slack alerting for a specific `error_code`.

### Policy defaults are safety-critical

`custom_errors.policy.json` should default to **no suppression**:
- `defaults.emit_requestid_success: false`
- unknown/missing error codes must **not** crash and must fallback to “no suppression”.

### Logging sensitive data

If you log invocation events for debugging/replay:
- keep full schema (same keys/arrays)
- deep-redact secrets/PII (`authorization`, cookies, tokens, passwords, etc.)
- avoid duplicate event logs (one per catch)

### Non-literal error codes

If `CustomError` uses a variable/expression error code:
- do not guess a policy entry or refactor semantics
- leave it as-is and surface as TODO for a developer decision
