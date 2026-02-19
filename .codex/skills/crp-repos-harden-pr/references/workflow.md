# CRP `repos harden-pr` workflow (reference)

Authoritative source is always:
- `crp repos harden-pr --help`

This doc is a compact checklist for **PR-only** hardening:
- `crp repos harden-pr <repo> [debug]`

## Phase-by-phase checklist

1) **Preflight**
   - Verify tools: `crp --version`, `la --version`
   - NPM auth (mandatory): `whc npm-automation verify` (fallback: `npm whoami`)
   - Mandatory before running any `la ...`: `whc updates --non-interactive` → if updates: `whc u` → `la --version`

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
   - Open PR and stop (no merge, no deploy).

7) **Sync**
   - Optional post-run git sync commit (CloudFormation/lockfile drift): disable via `--no-post-git-sync`

## Safe command templates

- PR-only, step-by-step:
  - `crp repos harden-pr <repo> debug --yes`

- Agent-mode (no nested Codex exec):
  - `crp repos harden-pr <repo> debug --la-mode handoff --no-autopilot-run --yes`
  - apply changes as the agent
  - `crp repos harden-pr <repo> debug --continue --yes`

