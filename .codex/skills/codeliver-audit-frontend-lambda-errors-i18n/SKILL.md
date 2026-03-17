---
name: codeliver-audit-frontend-lambda-errors-i18n
description: Audit and autofix frontend-visible CodeDeliver lambda CustomError translation coverage gaps.
---

# codeliver-audit-frontend-lambda-errors-i18n

## Overview
Use this skill to enforce translation coverage for frontend-visible lambda error codes (`comment_id` / `comments`) in CodeDeliver.

The skill scans frontend->lambda refs, resolves local lambdas, expands one-hop downstream lambda invokes, extracts error codes from lambda code, checks impacted frontend i18n files, and can autofix missing keys with deterministic fallback translations.

## Fast path
- Default to the main script only. Do not run helper scripts unless there is a blocker, mismatch, or the user explicitly asks for debug detail.
- If the user provides an OS hint such as `macos`, `ubuntu`, or `windows`, trust it and skip extra environment probing.
- Prefer runtime-detected user roots:
  - refs: `~/.codex/refs`
  - projects: `~/Downloads/projects`
  - lambdas: `~/Downloads/lambdas`
- On Windows prefer the same relative layout under the user profile and use the runtime launcher from `skill.runtime.json`.
- Keep chat output minimal:
  - one short start update
  - one short completion update if the run is long
  - one concise final result
  - no step-by-step narration unless blocked or explicitly requested
- Read only the summary from the main script first. Open the JSON/Markdown report only if you need the exact missing/unresolved rows.
- If autofix changes files under `projects/`, run `ionic build` only in the touched frontend repos, not in untouched repos.

## Workflow (edits expected)
1. Run `scripts/audit_frontend_lambda_errors_i18n.py` directly in `autofix` mode with explicit `--projects-root`, `--lambdas-root`, `--refs-dir`, `--report-json`, and `--report-md`.
2. Analyze entry lambdas (+ one-hop downstream) for error codes and response fields.
3. Detect caller-based translation path policy per frontend project:
- nested path when caller usage is `presentPostFailureAlert(..., "<lambda>")` or `lambdas_responses.<lambda>.`
- root path when caller usage translates `res.comment_id` / `res?.comment_id` directly
4. Check translation coverage only in impacted frontend `el.json` and `en.json` i18n files.
5. Autofix missing keys with production-ready translations when mode is `autofix` (default):
- first prefer a valid translation from another locale (if available),
- otherwise generate natural language text per locale (not raw error-code text),
- treat placeholder values like `TODO(...)` as **missing** and replace them.
6. If the generated fallback is not production-ready, replace it with a natural user-facing message and write the improved mapping back into `ERROR_CODE_TRANSLATIONS`.
7. If the installed skill gained a proven translation mapping, keep it in the local preserve-skills mechanism so sync does not overwrite it.
8. Write JSON + Markdown reports.

## Resources
### scripts/collect_frontend_reachable_lambdas.py
Collects entry lambdas from `.codex/refs/codeliver-*-lambdas.md` and resolves local lambda paths.
Use only for debugging, path validation, or when the main audit result looks inconsistent.

Usage:
- `python scripts/collect_frontend_reachable_lambdas.py`
- `python scripts/collect_frontend_reachable_lambdas.py --output ~/.codex/tmp/frontend-reachable-lambdas.json`

### scripts/audit_frontend_lambda_errors_i18n.py
Main analyzer and autofix engine.
This is the default and usually the only script you should run.

Usage:
- `python scripts/audit_frontend_lambda_errors_i18n.py --mode audit`
- `python scripts/audit_frontend_lambda_errors_i18n.py` (default `--mode autofix --languages el,en`)
- `python scripts/audit_frontend_lambda_errors_i18n.py --languages el,en`

### scripts/check_frontend_lambda_errors_el_en.py
Fast helper check for `el.json` and `en.json` using the already generated JSON report.
Use only as a post-run spot check when the user explicitly asks for extra verification or when the main report path/output seems inconsistent.

Usage:
- `python scripts/check_frontend_lambda_errors_el_en.py`
- `python scripts/check_frontend_lambda_errors_el_en.py --report-json ~/.codex/tmp/frontend-lambda-errors-i18n-report.json`

## Guardrails
- Use refs as source-of-truth for frontend-called entry lambdas.
- One-hop downstream only.
- Locale scope is strict: only `el.json` and `en.json`.
- Never create/update any other i18n locale file (for example `ej.json`).
- Frontend-visible fields are limited to `comment_id` and `comments`.
- Caller-based path policy is mandatory.
- Unresolved lambda mappings are warn+skip and must be included in report output.
- Never write `TODO(...)` placeholders in i18n autofix output.
- Never keep raw placeholder-like values (e.g. `TODO(...)` or unchanged error codes) as final translations.
- Every created/updated value must read as a real user-facing message in the target locale.
