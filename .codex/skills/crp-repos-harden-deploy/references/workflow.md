# CRP `repos harden-deploy` workflow (reference)

This file is a compact checklist for explaining/executing:
- `crp repos harden-pr <repo> [debug]` (PR-only)
- `crp repos harden-deploy <repo> [debug]` (PR → auto-merge → deploy)

Authoritative source is always `crp repos harden-deploy --help` / `crp repos harden-pr --help`.

## Phase-by-phase checklist

1) **Preflight**
   - Verify binaries: `crp --version`, `la --version`
   - NPM auth: `whc npm-automation verify` (fallback: `npm whoami`)
   - Mandatory before any `la ...`: `whc updates --non-interactive` → if updates: `whc u` → `la --version`

2) **Repo setup**
   - Resolve org (`--org`) and clone root (`--dest`)
   - Clone mode: `--dest-mode fresh|reuse`
   - Choose base: `--base` (default `origin/HEAD`)
   - Create branch: `--branch` (default `chore/harden-<repo>-<yyyymmdd>`)

3) **Repo guardrails**
   - Ensure `.codecheck/` is in `.gitignore` (unless `--no-ensure-gitignore`)
   - Ensure safe/gated `deploy:prod` exists (unless `--no-ensure-deploy-prod`)
   - Optional: rewrite unsafe deploy scripts to canonical `lambda-upload` entrypoints via `--fix-deploy-prod`

4) **Preflight scan**
   - BigInt-unsafe `JSON.stringify(...)` scan (unless `--no-bigint-json-check`)

5) **AI hardening**
   - Run `la run harden` (timeout via `--timeout-min`)
   - Run `la run handled-errors-policy` unless disabled by `--no-handled-errors-action-log`

6) **PR**
   - `harden-pr`: open PR and stop
   - `harden-deploy`: open PR → auto-merge (unless you are in a handoff/continue workflow)

7) **Deploy (harden-deploy only)**
   - Run `npm run deploy:prod`
   - Pass safety context:
     - `--aws-profile <p>` (sets `AWS_PROFILE`)
     - `--region <r>` (sets `AWS_REGION`, default `eu-west-1`)
   - Default behavior deploys with runtime/arch upgrade config; disable via `--no-upgrade-config`.

8) **Post-deploy verification (harden-deploy only)**
   - CloudWatch scan for `ImportModuleError` / `unhandled_error`
     - Disable: `--no-post-deploy-check`
     - Tune: `--post-deploy-check-lookback-sec <n>`
   - Smoke invoke (best-effort, safe-only by default)
     - Disable: `--no-post-deploy-smoke`
     - Tune payload discovery: `--post-deploy-smoke-lookback-sec <n>`
     - Force risky/unknown smoke: `--post-deploy-smoke-force` (use sparingly)

9) **Sync & cleanup**
   - Optional post-run git sync commit (CloudFormation/lockfile drift): disable via `--no-post-git-sync`
   - Optional local branch cleanup after successful merge+deploy: disable via `--no-cleanup-branches`

## Safe command templates

- PR-only (recommended default):
  - `crp repos harden-pr <repo> debug --yes`

- Deploy (explicit approval required):
  - `crp repos harden-deploy <repo> debug --yes --aws-profile <p> --region <r>`

- Inspect the exact handoff plan without running Codex:
  - `crp repos harden-deploy <repo> debug --la-mode handoff --no-autopilot-run --yes`
  - Then either:
    - run the emitted handoff JSON(s) manually, or
    - resume with `--continue` when you are ready to commit/push/open PR/merge/deploy (no `la` execution).

