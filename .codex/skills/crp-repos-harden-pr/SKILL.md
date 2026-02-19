---
name: crp-repos-harden-pr
description: >-
  Runbook + agent-mode execution workflow for `crp repos harden-pr` (PR-only
  hardening in Lambda repos: `la run harden` + `la run handled-errors-policy` +
  open PR; no merge, no deploy, no AWS mutations), with embedded
  ACTION:SLACK_COMMENT error-context rules. Use when you want to
  harden/upgrade a Lambda repo safely via PR review, avoid nested `codex exec`
  terminals, or when a legacy runtime/arch/SDK migration is needed but
  merge+deploy must stay out of scope.
---

# CRP repos harden-pr

## Goal

Run the PR-only harden pipeline for a single repo via CRP, while keeping execution **in this agent session** (handoff mode), so no nested Codex CLI terminal is spawned.

## What `harden-pr` is (and isn’t)

- `crp repos harden-pr <repo>`:
  - clones repo + creates a harden branch
  - ensures `.codecheck/` is gitignored (unless disabled)
  - ensures a safe/gated `deploy:prod` script exists (unless disabled)
  - runs `la run harden` + `la run handled-errors-policy` (unless disabled)
  - opens a PR and stops
- It does **not** merge, deploy, or change AWS resources.

For merge+deploy automation, use `crp repos harden-deploy` (separate skill: `crp-repos-harden-deploy`).

## How to use this skill (in practice)

In the Codex app, you typically trigger it by asking something like:
- “Τρέξε `crp repos harden-pr` για το repo `<repo_id>` σε agent-mode (handoff), PR-only.”
- “Explain what `crp repos harden-pr` does and generate the exact handoff commands.”

The agent should then follow the workflow below (without spawning nested Codex).

## Preflight (before you start)

- Verify tools exist: `crp`, `la`, `gh` (recommended).
- Verify npm auth (mandatory): `whc npm-automation verify` (fallback: `npm whoami`).
- Mandatory update-check **before running any `la ...`**:
  - `whc updates --non-interactive`
  - if updates exist: `whc u`
  - `la --version`

Tip: run `scripts/crp_harden_preflight.sh` inside the target repo to print a compact report (and infer the deploy alias/AWS profile for later, if needed).

## Execute in agent-mode (no nested Codex CLI)

Prefer `debug` while iterating (pauses between phases for verification).

### 1) Generate handoff (no `codex exec`, no autopilot)

Run:
- `crp repos harden-pr <repo> debug --la-mode handoff --no-autopilot-run --yes`

CRP will:
- clone the repo and create the harden branch
- run the analysis steps in handoff mode (emits plans + artifacts under `./.codecheck/output/`)
- print the generated handoff JSON path(s)

### 2) Apply changes as the current agent

In the cloned repo directory:
- Read the latest harden artifacts under `./.codecheck/output/` (especially the extracted apply prompt / `lambda_fix_prompt`).
- Implement the changes yourself (minimal diffs, behavior-preserving).
- Use `dmngr/lambda-policies` as source of truth for phases/checkpoints and handled-errors wiring (see `references/lambda-policies.md`).

Important constraints:
- Do not “upgrade/deploy ad-hoc”. If a fix requires runtime/arch/deploy wiring changes, express it by updating the repo’s `package.json` scripts (the harden policy expects “run the scripts”, not random commands).
- Do not merge or deploy in this flow.

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

### 3) Resume orchestration (`--continue`) to push + open PR

Run:
- `crp repos harden-pr <repo> debug --continue --yes`

If CRP refuses to continue due to missing checkpoint artifacts:
- Preferred: re-run step (1) to regenerate artifacts and ensure they exist.
- Escape hatch (use sparingly): add `--no-require-checkpoint-artifacts`.

## Troubleshooting quick hits

- Unsafe/legacy deploy scripts detected:
  - re-run with `--fix-deploy-prod` (still PR-only; this just standardizes `deploy:prod` scripts).
- You must avoid nested execution:
  - keep `--la-mode handoff --no-autopilot-run` (do not use `--autopilot-run-mode inline`).
- Want the authoritative list of flags/phases:
  - `crp repos harden-pr --help`

## References

- `references/workflow.md` for a compact PR-only checklist.
- `references/lambda-policies.md` for source-of-truth pointers + common mistakes.
