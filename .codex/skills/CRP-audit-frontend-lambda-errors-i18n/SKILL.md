---
name: "CRP Audit Frontend Lambda Errors i18n"
description: Audit and autofix frontend-visible CRP lambda error translation coverage for cloud-repos-panel using one-hop lambda expansion and OpenAI auto-translation.
---

# CRP Audit Frontend Lambda Errors i18n

## Overview
Use this skill to enforce translation coverage for frontend-visible CRP lambda error codes (`comment_id` / `comments`) in `cloud-repos-panel`.

The skill discovers frontend entry lambdas from `cloud-repos-panel` service files, resolves local lambdas under `crp_all`, expands one-hop downstream lambda invokes, extracts error codes from lambda code, checks i18n coverage, and can autofix missing keys with high-quality auto-translation.

## Workflow (edits expected)
1. Collect frontend-reachable entry lambdas from:
- `cloud-repos-panel/src/app/shared/data-storage.service.ts`
- `cloud-repos-panel/src/app/shared/auth/auth.service.ts`
2. Resolve entry lambda names to local lambda folders in `/Users/john/Downloads/lambdas/crp_all`.
3. Analyze entry lambdas (+ one-hop downstream) for error codes and frontend-visible response fields (`comment_id`, `comments`).
4. Detect translation path policy per project:
- default root path (CRP primary pattern: `translate.instant(response.comment_id)`)
- optional nested path only when detected from code patterns
5. Check translation coverage only across `src/assets/i18n/el.json` and `src/assets/i18n/en.json`.
6. Autofix missing keys with full auto-translation (default provider `openai`) and strict placeholder cleanup:
- values like `TODO(...)` are treated as **missing** and replaced,
- prefer high-quality translated text for the target locale,
- use fallback copy/generation only when provider translation is unavailable, while keeping output user-facing and readable.
7. Write JSON + Markdown reports.

## Resources
### scripts/collect_frontend_reachable_lambdas.py
Collects CRP frontend entry lambdas from code and resolves local lambda paths.

Usage:
- `python scripts/collect_frontend_reachable_lambdas.py`
- `python scripts/collect_frontend_reachable_lambdas.py --output /Users/john/.codex/tmp/crp-frontend-reachable-lambdas.json`

### scripts/audit_frontend_lambda_errors_i18n.py
Main analyzer and autofix engine.

Usage:
- `python scripts/audit_frontend_lambda_errors_i18n.py --mode audit`
- `python scripts/audit_frontend_lambda_errors_i18n.py` (default `--mode autofix --languages el,en`)
- `python scripts/audit_frontend_lambda_errors_i18n.py --languages el,en`
- `python scripts/audit_frontend_lambda_errors_i18n.py --translation-provider none`

OpenAI translation requirements:
- Set `OPENAI_API_KEY` in the environment.
- Optional overrides:
  - `OPENAI_BASE_URL` (default `https://api.openai.com/v1`)
  - `--translation-model` (default `gpt-4.1-mini`)

### scripts/check_frontend_lambda_errors_locales.py
Fast report validator for missing/created/found/skipped coverage status.

Usage:
- `python scripts/check_frontend_lambda_errors_locales.py`
- `python scripts/check_frontend_lambda_errors_locales.py --report-json /Users/john/.codex/tmp/crp-frontend-lambda-errors-i18n-report.json`

## Guardrails
- Frontend scope is `cloud-repos-panel` only.
- Lambda scope is `/Users/john/Downloads/lambdas/crp_all`.
- One-hop downstream only.
- Locale scope is strict: only `el.json` and `en.json`.
- Never create/update any other i18n locale file (for example `ej.json`).
- Frontend-visible fields are limited to `comment_id` and `comments`.
- Unresolved lambda mappings are warn+skip and are included in report output.
- Translation fallback must never write `TODO(...)`.
- Placeholder-like values (`TODO(...)`, raw error-code text) are not acceptable final translations.
- Every created/updated translation must be a natural, user-facing message in the target locale.
