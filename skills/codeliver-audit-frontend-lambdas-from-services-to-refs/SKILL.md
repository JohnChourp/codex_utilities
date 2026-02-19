---
name: codeliver-audit-frontend-lambdas-from-services-to-refs
description: Scan CodeDeliver frontends (app/pos/panel/sap) to find frontend-called lambdas and update `.codex/refs/codeliver-*-lambdas.md` with normalized paths plus observed payload and response examples. Use when endpoints change or new services are added.
---

# codeliver-audit-frontend-lambdas-from-services-to-refs

## Overview
Sync frontend-called lambda usage into `.codex/refs/codeliver-*-lambdas.md` with normalized paths and observed request/response examples. Write ref content in English.

## Workflow (edits expected)
1. Scan frontend services (only `*.service.ts`).
- `projects/codeliver/codeliver-app/src/app/**/*.service.ts`
- `projects/codeliver/codeliver-pos/src/app/**/*.service.ts`
- `projects/codeliver/codeliver-panel/src/app/**/*.service.ts`
- `projects/codeliver/codeliver-sap/src/app/**/*.service.ts`

2. Extract endpoints and payloads.
- Capture HTTP method, path, and request body shape from the service method.
- Capture observed response shapes from typed interfaces or inline handling.
- Sanitize secrets/tokens; keep real field names.

3. Map endpoints to normalized paths.
- Use `.codex/playbooks/codeliver-api-gateways.md` to map `apiId -> apiName`.
- Normalize to `{api}/{stage}/{lambda}`.
- Add a small `apiId -> apiName` table at the top of each ref file.

4. Update refs.
- Update the matching file in `.codex/refs/codeliver-*-lambdas.md`.
- For each lambda section include:
  - Normalized path: `{api}/{stage}/{lambda}`
  - HTTP method and route
  - Observed request payload example (sanitized)
  - Observed response example (sanitized)
  - Source `*.service.ts` path
- If a response example is not observed, state "Response example not observed in service code".

## Resources
### scripts/extract_frontend_http_calls.py
Extract raw HTTP calls and optionally write ready-to-review markdown into `.codex/refs` using `*-lambdas.generated.md` suffix, plus an index file.

Usage:
- `python scripts/extract_frontend_http_calls.py` (json)
- `python scripts/extract_frontend_http_calls.py --format md` (table)
- `python scripts/extract_frontend_http_calls.py --write` (write `*-lambdas.generated.md` and `refs-frontend-index.generated.md`)

## Guardrails
- Do not search outside `*.service.ts` for frontend-called lambdas.
- Do not invent payloads; use observed examples only.
- Do not edit `.codex/playbooks` unless a contract is missing.
