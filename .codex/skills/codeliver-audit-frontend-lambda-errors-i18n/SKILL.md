---
name: codeliver-audit-frontend-lambda-errors-i18n
description: Audit and autofix frontend-visible lambda CustomError translation coverage across impacted CodeDeliver frontends using caller-based translation paths.
---

# codeliver-audit-frontend-lambda-errors-i18n

## Overview
Use this skill to enforce translation coverage for frontend-visible lambda error codes (`comment_id` / `comments`) in CodeDeliver.

The skill scans frontend->lambda refs, resolves local lambdas, expands one-hop downstream lambda invokes, extracts error codes from lambda code, checks impacted frontend i18n files, and can autofix missing keys with deterministic placeholders.

## Workflow (edits expected)
1. Collect frontend-reachable entry lambdas from refs.
2. Resolve entry lambda names to local lambda folders.
3. Analyze entry lambdas (+ one-hop downstream) for error codes and response fields.
4. Detect caller-based translation path policy per frontend project:
- nested path when caller usage is `presentPostFailureAlert(..., "<lambda>")` or `lambdas_responses.<lambda>.`
- root path when caller usage translates `res.comment_id` / `res?.comment_id` directly
5. Check translation coverage in impacted frontend i18n files.
6. Autofix missing keys with `TODO(<error_code>)` when mode is `autofix` (default).
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
- `python scripts/audit_frontend_lambda_errors_i18n.py` (default `--mode autofix`)
- `python scripts/audit_frontend_lambda_errors_i18n.py --languages el,en`

### scripts/check_frontend_lambda_errors_el_en.py
Fast helper check for `el.json` and `en.json` using the already generated JSON report.

Usage:
- `python scripts/check_frontend_lambda_errors_el_en.py`
- `python scripts/check_frontend_lambda_errors_el_en.py --report-json /home/dm-soft-1/.codex/tmp/frontend-lambda-errors-i18n-report.json`

## Guardrails
- Use refs as source-of-truth for frontend-called entry lambdas.
- One-hop downstream only.
- Frontend-visible fields are limited to `comment_id` and `comments`.
- Caller-based path policy is mandatory.
- Unresolved lambda mappings are warn+skip and must be included in report output.
