---
name: crp-repos-harden-deploy
description: >-
  Runbook + execution workflow for CRP hardening flows that auto-merge + deploy
  (`crp repos harden-deploy`). Use when you need to explain what the deploy flow
  does, choose safe flags (debug, handoff), infer deploy target (`AWS_PROFILE`),
  or execute the flow with post-deploy verification (CloudWatch scan + smoke
  invoke), including preflight (npm auth, `whc` updates before `la`), embedded
  ACTION:SLACK_COMMENT error-context rules, and troubleshooting. For PR-only,
  use `crp-repos-harden-pr`.
---

# CRP repos harden-deploy

## Goal

Explain and/or run the end-to-end “harden” pipeline that CRP orchestrates for a single repo:
- `la run harden`
- `la run handled-errors-policy`
- (deploy flow only) auto-merge + `npm run deploy:prod` + post-deploy checks

## Choose the right command (safety first)

- Default to PR-only:
  - Use `crp repos harden-pr <repo> [debug]` unless the user explicitly wants AWS mutations.
- Deploy flow (AWS-mutating):
  - Use `crp repos harden-deploy <repo> [debug]` only when the user explicitly asks for merge+deploy or when you have clear approval to deploy.

## Debug vs auto flow (non-interactive gotcha)

`crp repos harden-deploy <repo> debug` **pauses between phases** for human verification. In non-interactive agent sessions this can easily “hang” waiting for input.

- Prefer **auto** flow (default) + inspect artifacts/PR/deploy results.
- If you *must* use debug, be ready to actively continue each phase (and always include `--yes`).

## Important: “agent-mode” vs `la run ...` (nested Codex)

`crp repos harden-pr` / `crp repos harden-deploy` normally run `la run harden` and `la run handled-errors-policy`.

`la run ...` is a *prompt runner* that may invoke an external Codex CLI execution (nested run). If you want the work to happen **as the current agent** (this session) instead of spawning a nested Codex terminal, use **handoff + agent execution**:

1) Generate a handoff plan with `--la-mode handoff --no-autopilot-run` (this does **not** run `la`/Codex).
2) Apply the code changes yourself as the agent (using the policies/prompts as reference).
3) Resume the CRP pipeline with `--continue` (commit/push/open PR, and optionally merge+deploy) without any `la` execution.

Notes:
- `--no-autopilot-run` is important: autopilot may try to run an inline `codex exec` (nested) depending on environment.
- If you’re iterating on the same repo multiple times in the same day, pass an explicit `--branch <name>` so you don’t collide with an existing harden branch.

## Preflight checklist (before any `la ...` OR any deploy flow)

1) Verify binaries + versions:
   - `which crp && crp --version` (or `crp --help` if `--version` is not supported)
   - `which la && la --version`

2) Verify npm auth (mandatory for the flow):
   - Preferred (when `whc` exists): `whc npm-automation verify`
   - Fallback: `npm whoami`

3) Mandatory update-check before running any `la ...` command:
   - `whc updates --non-interactive`
   - If updates exist: `whc u`
   - Verify: `la --version`

Tip: run `scripts/crp_harden_preflight.sh` from this skill folder to print a compact preflight report.

## Agent-mode execution (no nested Codex CLI)

Use this workflow when you want *this agent* to do the edits, while CRP handles the orchestration bits.

### A) PR-only (`harden-pr`) agent-mode

1) Create handoff (no Codex run):
   - Prefer auto flow:
     - `crp repos harden-pr <repo> --la-mode handoff --no-autopilot-run --yes`
   - If you truly need debug flow (interactive pauses):
     - `crp repos harden-pr <repo> debug --la-mode handoff --no-autopilot-run --yes`
2) Go to the cloned repo directory that CRP created and apply changes as the agent:
   - Follow the harden policy + handled-errors policy references.
3) Resume orchestration (no `la` execution):
   - `crp repos harden-pr <repo> --continue --yes`

### B) Merge + deploy (`harden-deploy`) agent-mode (AWS-mutating)

Only when you have explicit approval to merge+deploy.

1) Create handoff (no Codex run):
   - Prefer auto flow:
     - `crp repos harden-deploy <repo> --la-mode handoff --no-autopilot-run --yes --aws-profile <p> --region <r>`
   - If you truly need debug flow (interactive pauses):
     - `crp repos harden-deploy <repo> debug --la-mode handoff --no-autopilot-run --yes --aws-profile <p> --region <r>`
2) Apply changes in the cloned repo as the agent (same as PR-only).
3) Resume orchestration (no `la` execution):
   - `crp repos harden-deploy <repo> --continue --yes --aws-profile <p> --region <r>`

Notes:
- If you need to pass the exact session file explicitly, use `--session <path>` (see the `crp ... --help` text; the handoff JSON lives under `./.codecheck/output/`).
- In agent-mode, do **not** call `la run harden` / `la run handled-errors-policy`. Use the policy references directly (below).

### Embedded ACTION:SLACK_COMMENT workflow (mandatory in harden runs)

When the harden scope touches Node.js lambda error handling, apply this within the same run:
- Keep business behavior stable. Do not change success/failure payload shapes or handled-error branching.
- Preserve existing `ACTION:SLACK_HANDLED_ERROR_HE1=...` and `RequestId SUCCESS` behavior.
- Add/extend reusable helpers in `index.js` (before handler export) to:
  - parse optional `event.body` safely (JSON when possible),
  - collect high-signal IDs from existing inputs only (no extra fetches),
  - sanitize values (`|` replacement, whitespace normalization, length cap).
- Build `ACTION:SLACK_COMMENT=...` from available fields only, preferred order:
  - `group`, `delivery_guy_id`, `store_id`, `request_id`, `path_id`, `route_id`, `device_id`, `batch_id`, `customer_id`, `timestamp`, `day`, `zone_id`, `server_id`, `connection`, `notification_id`, `user_id`, `calculation_id`, `apikey_date`, `comment_id`.
- Resolve key fallbacks in this order where applicable:
  - `event.<key>`
  - parsed `event.body.<key>`
  - `event.pathParameters.<key>`
  - `event.queryStringParameters.<key>`
  - `event.requestContext.authorizer.<key>`
  - `event.requestContext.authorizer.claims.<key>`
  - request id: `event.requestContext.requestId` then `context.awsRequestId`
  - connection: `connection`, `connection_id`, `connectionId`, `requestContext.connectionId`
  - apikey date: `apikey-date`, `apikey_date`, and lowercase header variants
- Emit the marker in `catch` before handled/unhandled branch decisions:
  - log only if payload is non-empty,
  - always append `comment_id` in marker payload.
- Sensitive-data rule:
  - never include passwords/tokens/cookies/raw secrets,
  - never dump full bodies into `ACTION:SLACK_COMMENT`.
- Marker format must stay single-token:
  - `ACTION:SLACK_COMMENT=key1:value1|key2:value2|...|comment_id:<code>`

## Post-deploy verification (log scan pitfalls + recommended queries)

CRP’s post-deploy check scans CloudWatch for common failure patterns. When you do manual verification:

- Prefer searching for stable tokens (single “words”) like `SLACK_CTX_V1` / `SLACK_HANDLED_ERROR_HE1`.
- Avoid filter patterns that include `:` (e.g. `ACTION:...`) because CloudWatch filter pattern parsing can be surprising; use the token part instead.

Example (replace `<fn>`):
- `aws logs filter-log-events --log-group-name "/aws/lambda/<fn>" --filter-pattern "SLACK_CTX_V1" --start-time $(( ($(date +%s) - 86400) * 1000 ))`

## Explain what `crp repos harden-deploy` does (no execution)

Use this when the user’s request is “τι τρέχει αυτό το command;” / “what does it do?”.

1) Read the authoritative CLI help:
   - `crp repos harden-deploy --help`
   - `crp repos harden-pr --help`

2) Summarize the phases in order (use the template below):
   - **Repo setup**: clone into `--dest` (fresh/reuse), choose `--base`, create `--branch`
   - **Repo hygiene**: ensure `.codecheck/` is gitignored (unless `--no-ensure-gitignore`)
   - **Deploy safety**: ensure safe/gated `deploy:prod` exists (unless `--no-ensure-deploy-prod`)
   - **Preflight scan**: BigInt-unsafe `JSON.stringify(...)` scan (unless `--no-bigint-json-check`)
   - **AI hardening**: run `la run harden` (timeout via `--timeout-min`)
   - **Handled errors wiring**: run `la run handled-errors-policy` (unless `--no-handled-errors-action-log`)
   - **PR**:
     - harden-pr: open PR and stop
     - harden-deploy: open PR → auto-merge
   - **Deploy (harden-deploy only)**: run `npm run deploy:prod` (sets `AWS_PROFILE`/`AWS_REGION`)
     - default includes runtime/arch upgrade config unless `--no-upgrade-config`
   - **Post-deploy verification (harden-deploy only)**:
     - CloudWatch scan (unless `--no-post-deploy-check`)
     - smoke invoke (unless `--no-post-deploy-smoke`; force via `--post-deploy-smoke-force`)
   - **Cleanup/sync**:
     - optional post-run git sync commit unless `--no-post-git-sync`
     - optional local branch cleanup unless `--no-cleanup-branches`

3) If the user wants *the exact machine plan without running Codex*:
   - Use `--la-mode handoff` and disable autopilot:
     - `crp repos harden-deploy <repo> debug --la-mode handoff --no-autopilot-run --yes`
   - Then explain what the emitted handoff JSON(s) would do.

## Execute `crp repos harden-deploy` safely

When actually executing, prefer `debug` flow unless the user explicitly wants full automation.

1) Confirm inputs (do not assume) — but infer when possible:
   - `repo` (name or `owner/repo`)
   - `--org` (if not encoded in `owner/repo`)
   - `--aws-profile` and `--region` for deploy (recommended for safety)
   - whether this is single-account or multi-account deploy (`--deploy-prod-use-alias` / `--deploy-prod-use-aliases`)

   If the user didn’t tell you `--aws-profile`, infer it automatically (do not ask by default):
   - Preferred: parse the repo’s `package.json` deploy scripts and extract the alias from `lambda-upload deploy-prod <alias>` (most repos pin this explicitly, e.g. `dm`).
     - Example: `scripts.deploy:prod:upgrade = "lambda-upload deploy-prod dm --upgrade-config …"` ⇒ `--aws-profile dm`
   - Secondary: read `package.json:lambda_upload.deployed_accounts[-1]` (alias/region from the last deploy).
   - Best-effort sanity (no AWS calls): run `npm run deploy:prod:check` and use the printed `Account: <alias> (region: <r>)`.
   - CRP-based fallback (when the alias is not pinned in the repo scripts): use the CRP Lambda inventory probe (local AWS CLI across profiles) and pick the matching profile:
     - `crp repos lambda-inventory --profiles <csv> --region <r> --out /tmp/lambda-inventory.json`
     - Then find the function row: `functionName == <repoName>` and read `accounts[0].profile` (this is your `--aws-profile`).

2) Recommended baseline command (deploy flow):
   - `crp repos harden-deploy <repo> debug --yes --aws-profile <p> --region <r>`

3) If you need the repo to keep legacy deploy scripts but still proceed, use the explicit flag:
   - `--fix-deploy-prod` rewrites unsafe/legacy deploy scripts to canonical `lambda-upload deploy-prod` scripts.

4) Post-deploy verification (do not skip by default):
   - Keep CloudWatch scan enabled (`--no-post-deploy-check` is an exception)
   - Keep smoke invoke enabled (`--no-post-deploy-smoke` is an exception)

5) Report back with a concrete run summary:
   - exact `crp ...` command you ran (including flags)
   - local clone path + branch name
   - PR URL + merge status (if deploy flow)
   - deploy command executed + target account/region
   - post-deploy findings (log scan + smoke result)

## Troubleshooting quick hits

- NPM auth blocks the run:
  - `whc npm-automation verify` → if needed: `whc npm-automation repair`
  - fallback sanity: `npm whoami`
- Git clone fails with `Permission denied (publickey)`:
  - re-run with `--prefer https` (CRP option), and ensure GitHub host protocol is HTTPS:
    - `gh config set git_protocol https --host github.com`
- `la run harden` fails unexpectedly:
  - re-run the mandatory update-check sequence (`whc updates …`, `whc u`, `la --version`) and retry
- `--continue` fails because checkpoint artifacts are missing:
  - Symptom: `crp ... --continue` complains about missing CHECKPOINT artifacts / analysis JSON / extracted `lambda_fix_prompt`.
  - Preferred: re-run the handoff generation step and execute the apply-phase prompts so the artifacts exist.
  - Escape hatch (use sparingly): add `--no-require-checkpoint-artifacts` to proceed when you are intentionally skipping the AI apply phase (e.g., no code changes, or already applied manually).
- `--continue` fails due to AWS SDK v2 policy checks:
  - Symptom: harden refuses because it detects `require("aws-sdk")` (v2) in code, or legacy DM deps that rely on it (e.g. `@deliverymanager/s3_fns`).
  - Fix:
    - Replace `require("aws-sdk")` callsites with AWS SDK v3 clients (e.g. DynamoDB via `@aws-sdk/client-dynamodb` + `@aws-sdk/lib-dynamodb`, SES via `@aws-sdk/client-ses`).
    - Replace legacy DM deps with their v3 variants (common examples: `@deliverymanager/s3_fns` → `@deliverymanager/s3_fns_v3`).
  - Packaging note (important): for Node.js 18+ managed Lambda runtimes, AWS SDK v3 (`@aws-sdk/*`) is runtime-included. Harden policy may prefer **not** pinning `@aws-sdk/*` in `package.json` (remove them from deps + lockfile), while still using `require("@aws-sdk/...")` at runtime.
- Deploy risk too high / unclear:
  - stop and switch to PR-only: `crp repos harden-pr …`
  - or run deploy with upgrades disabled: `crp repos harden-deploy … --no-upgrade-config`
- `deploy:prod:upgrade` fails verifying `arm64` (stuck on `x86_64` even after retries):
  - Symptom: `lambda-upload ... --upgrade-config` (or `--update-arch-arm64-only`) returns success / HTTP 200 but `Architectures` remains `x86_64` even after polling.
  - Fix (preferred): apply `arm64` **during a code upload** using `--ensure-arch-arm64` (aka `--update-arch-arm64`) instead of relying on the config-only arch update.
    - Via repo scripts (preferred; makes the “arch update” auditable and repeatable): `npm run deploy:prod -- --skip-bump --ensure-arch-arm64`
    - Direct form (only if the repo has no deploy scripts): `lambda-upload deploy-prod <alias> --skip-bump --ensure-arch-arm64` (add `--s3` if that repo uses S3 deploy)
  - If this still fails: check if the repo/Lambda must deploy via CloudFormation and whether `cloudformation/stack.json` is stale.
    - Fallback: `lambda-upload deploy-prod <alias> --cloudformation`
  - After manual recovery, avoid looping CRP deploy attempts; finish with explicit verification (CloudWatch scan + `GetFunctionConfiguration` for `Architectures=["arm64"]`).

## References

- `references/workflow.md` for a compact phase-by-phase checklist and option notes.
- `references/lambda-policies.md` for source-of-truth pointers + high-signal common mistakes from `dmngr/lambda-policies` (aka “dm-lambdas-policies”).
