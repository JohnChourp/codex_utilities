---
name: crp-audit-refresh-playbooks-refs
description: Combine frontend-lambda refs audit, playbooks/refs coverage audit, and playbooks/refs refresh after infra changes into one CRP workflow for cloud-repos-panel and crp_all.
---

# crp-audit-refresh-playbooks-refs

## Overview
Unified workflow for CRP documentation integrity:
- map frontend-called lambdas from `cloud-repos-panel` `*.service.ts` files into `.codex/refs`
- audit coverage gaps for canonical CRP playbooks/refs
- refresh `.codex/playbooks` and `.codex/refs` after verified infra changes

Write playbook/ref content in English.

## Modes
1. Audit-only mode (no edits)
- Inventory current CRP playbooks/refs.
- Scan `cloud-repos-panel` and `crp_all` for contracts and integrations.
- Report missing/stale docs with evidence.

2. Refresh mode (edits expected)
- Apply verified updates to `.codex/playbooks` and `.codex/refs`.
- Keep changes minimal and scoped to observed code/IaC deltas.

## Workflow
1. Collect baseline docs.
- List `.codex/playbooks/crp-*.md`.
- List `.codex/refs/crp-*.md`, `cloud-repos-panel-lambdas*.md`, and the CRP generated frontend index.
- Avoid duplicate docs; update canonical files only.

2. Scan frontend callers (services only).
- Restrict frontend lambda discovery to:
  - `projects/cloud-repos-panel/src/app/**/*.service.ts`
- Capture HTTP method, route/path, request payload shape, and observed response shape if present.

3. Map to normalized lambda paths.
- Use `.codex/playbooks/crp-api-gateways.md` for `apiId -> apiName` mapping when available.
- Normalize as `{api}/{stage}/{lambda}` when resolvable.

4. Scan infra and contracts.
- Lambdas/IaC:
  - `rg -n "httpApi|httpApiEvent|events:|path:|method:|handler:" /Users/john/Downloads/lambdas/crp_all`
  - `rg -n "SQS|SNS|EventBridge|DynamoDB|S3|CloudFront|API Gateway" /Users/john/Downloads/lambdas/crp_all`
- Frontend services only:
  - `rg -n "HttpClient|fetch\\(|/api/|/v1/" /Users/john/Downloads/projects/cloud-repos-panel -g "*.service.ts"`

5. Decide updates.
- If no verified gap: produce audit findings only.
- If verified gap exists: update the matching canonical CRP playbook/ref.

6. Update refs for frontend lambda usage (when requested).
For each lambda section include:
- Normalized path `{api}/{stage}/{lambda}`
- HTTP method and route
- Observed request payload example (sanitized)
- Observed response example (sanitized), or
  - `Response example not observed in service code`
- Source `cloud-repos-panel` `*.service.ts` path

7. Validate consistency.
- Re-check referenced resources/contracts against code/IaC.
- Keep refs as usage maps and playbooks as contract sources.
- Keep CRP generated outputs in CRP-specific filenames so they do not collide with CodeDeliver outputs.

## Resources
### scripts/collect_doc_inventory.py
List current CRP playbooks/refs.

Usage:
- `python scripts/collect_doc_inventory.py`
- `python scripts/collect_doc_inventory.py --root /Users/john`

### scripts/extract_frontend_http_calls.py
Extract frontend HTTP calls from `cloud-repos-panel` and optionally generate reviewable ref markdown.

Usage:
- `python scripts/extract_frontend_http_calls.py`
- `python scripts/extract_frontend_http_calls.py --format md`
- `python scripts/extract_frontend_http_calls.py --write`

### scripts/scan_infra_keywords.py
Scan `crp_all` lambdas for infra keyword hints and optionally output markdown.

Usage:
- `python scripts/scan_infra_keywords.py`
- `python scripts/scan_infra_keywords.py --format md`
- `python scripts/scan_infra_keywords.py --format md --out`

## Guardrails
- Do not search outside `cloud-repos-panel` `*.service.ts` files for frontend-called lambda mapping unless explicitly requested.
- Never guess resource names, schemas, payloads, or contracts.
- Do not duplicate playbooks/refs inside repos.
- Keep edits minimal and grounded in verified code/IaC evidence.
- Keep generated filenames CRP-specific to avoid overwriting CodeDeliver-generated refs.
