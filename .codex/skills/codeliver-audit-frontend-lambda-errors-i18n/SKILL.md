---
name: codeliver-audit-frontend-lambda-errors-i18n
description: Audit and autofix frontend-visible CodeDeliver lambda CustomError translation coverage gaps.
---

# codeliver-audit-frontend-lambda-errors-i18n

## Overview
Use this skill to enforce translation coverage for frontend-visible lambda error codes (`comment_id` / `comments`) in CodeDeliver.

The skill scans frontend->lambda refs, resolves local lambdas, expands one-hop downstream lambda invokes, extracts error codes from lambda code, checks impacted frontend i18n files, and can autofix missing keys with deterministic fallback translations.

## Workflow (edits expected)
1. Collect frontend-reachable entry lambdas from refs.
2. Resolve entry lambda names to local lambda folders.
3. Analyze entry lambdas (+ one-hop downstream) for error codes and response fields.
4. Detect caller-based translation path policy per frontend project:
- nested path when caller usage is `presentPostFailureAlert(..., "<lambda>")` or `lambdas_responses.<lambda>.`
- root path when caller usage translates `res.comment_id` / `res?.comment_id` directly
5. Check translation coverage only in impacted frontend `el.json` and `en.json` i18n files.
6. Autofix missing keys with production-ready translations when mode is `autofix` (default):
- first prefer a valid translation from another locale (if available),
- otherwise generate natural language text per locale (not raw error-code text),
- treat placeholder values like `TODO(...)` as **missing** and replace them.
7. Write JSON + Markdown reports.

## Resources
### scripts/collect_frontend_reachable_lambdas.py
Collects entry lambdas from `.codex/refs/codeliver-*-lambdas.md` and resolves local lambda paths.

Usage:
- `python scripts/collect_frontend_reachable_lambdas.py`
- `python scripts/collect_frontend_reachable_lambdas.py --output /home/dm-soft-1/.codex/tmp/frontend-reachable-lambdas.json`

### scripts/audit_frontend_lambda_errors_i18n.py
Main analyzer and autofix engine.

Usage:
- `python scripts/audit_frontend_lambda_errors_i18n.py --mode audit`
- `python scripts/audit_frontend_lambda_errors_i18n.py` (default `--mode autofix --languages el,en`)
- `python scripts/audit_frontend_lambda_errors_i18n.py --languages el,en`

### scripts/check_frontend_lambda_errors_el_en.py
Fast helper check for `el.json` and `en.json` using the already generated JSON report.

Usage:
- `python scripts/check_frontend_lambda_errors_el_en.py`
- `python scripts/check_frontend_lambda_errors_el_en.py --report-json /home/dm-soft-1/.codex/tmp/frontend-lambda-errors-i18n-report.json`

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
