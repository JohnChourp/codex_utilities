---
name: codeliver-audit-refresh-playbooks-refs
description: Audit and refresh CodeDeliver frontend refs, playbooks, and infra-derived reference files.
---

# codeliver-audit-refresh-playbooks-refs

## Overview
Unified workflow for CodeDeliver documentation integrity:
- map frontend-called lambdas from `*.service.ts` into `.codex/refs`
- audit coverage gaps for canonical playbooks/refs
- audit DynamoDB `TableName` + `IndexName` usage across all CodeDeliver lambdas
- refresh `.codex/playbooks` and `.codex/refs` after verified infra changes

Write playbook/ref content in English.

## Modes
1. Audit-only mode (no edits)
- Inventory current playbooks/refs.
- Scan lambdas/projects for contracts and integrations.
- Report missing/stale docs with evidence.
- Optionally run DynamoDB index audit in `code-only` mode when live AWS verification is not requested.

2. Refresh mode (edits expected)
- Apply verified updates to `.codex/playbooks` and `.codex/refs`.
- Keep changes minimal and scoped to observed code/IaC deltas.
- When requested, run DynamoDB index audit in `live` mode and refresh the canonical ref/playbook only if the audit proves a mismatch.

## Workflow
1. Collect baseline docs.
- List `.codex/playbooks/*.md` and `.codex/refs/*.md`.
- Avoid duplicate docs; update canonical files only.

2. Scan frontend callers (services only).
- Restrict frontend lambda discovery to:
  - `projects/codeliver/codeliver-app/src/app/**/*.service.ts`
  - `projects/codeliver/codeliver-pos/src/app/**/*.service.ts`
  - `projects/codeliver/codeliver-panel/src/app/**/*.service.ts`
  - `projects/codeliver/codeliver-sap/src/app/**/*.service.ts`
- Capture HTTP method, route/path, request payload shape, and observed response shape if present.

3. Map to normalized lambda paths.
- Use `.codex/playbooks/codeliver-api-gateways.md` for `apiId -> apiName` mapping.
- Normalize as `{api}/{stage}/{lambda}` when resolvable.

4. Scan infra and contracts.
- Lambdas/IaC:
  - `rg -n "httpApi|httpApiEvent|events:|path:|method:|handler:" /home/dm-soft-1/Downloads/lambdas`
  - `rg -n "SQS|SNS|EventBridge|DynamoDB|S3|CloudFront|API Gateway" /home/dm-soft-1/Downloads/lambdas`
- Frontend services only:
  - `rg -n "HttpClient|fetch\(|/api/|/v1/" /home/dm-soft-1/Downloads/projects -g "*.service.ts"`

5. Audit DynamoDB table/index usage (when requested).
- Scan all lambdas under `/home/dm-soft-1/Downloads/lambdas/codeliver_all`.
- Extract DynamoDB `TableName` + `IndexName` pairs from JS lambda files.
- Resolve literal values and simple same-file constant indirection.
- Treat unresolved dynamic expressions such as `params.IndexName` as manual-review evidence, never as missing indexes.
- In `live` mode, verify every resolved pair against the currently authenticated AWS CLI account/profile using `aws dynamodb describe-table`.
- Compare against both `GlobalSecondaryIndexes` and `LocalSecondaryIndexes`.
- Produce these result buckets:
  - `confirmed-present`
  - `missing-in-dynamodb`
  - `unresolved-needs-manual-review`
  - `table-errors` (for `describe-table` failures such as missing tables or auth problems)

6. Decide updates.
- If no verified gap: produce audit findings only.
- If verified gap exists: update the matching canonical playbook/ref.

7. Update refs for frontend lambda usage (when requested).
For each lambda section include:
- Normalized path `{api}/{stage}/{lambda}`
- HTTP method and route
- Observed request payload example (sanitized)
- Observed response example (sanitized), or
  - `Response example not observed in service code`
- Source `*.service.ts` path

8. Validate consistency.
- Re-check referenced resources/contracts against code/IaC.
- Keep refs as usage maps and playbooks as contract sources.
- For DynamoDB audit findings, prefer live `describe-table` verification over lambda-local CloudFormation, because the lambda-local templates are deployment templates and are not the table/index source of truth.

## Resources
### scripts/collect_doc_inventory.py
List current playbooks/refs.

Usage:
- `python scripts/collect_doc_inventory.py`
- `python scripts/collect_doc_inventory.py --root /home/dm-soft-1`

### scripts/extract_frontend_http_calls.py
Extract frontend HTTP calls and optionally generate reviewable ref markdown.

Usage:
- `python scripts/extract_frontend_http_calls.py`
- `python scripts/extract_frontend_http_calls.py --format md`
- `python scripts/extract_frontend_http_calls.py --write`

### scripts/scan_infra_keywords.py
Scan lambdas for infra keyword hints and optionally output markdown.

Usage:
- `python scripts/scan_infra_keywords.py`
- `python scripts/scan_infra_keywords.py --format md`
- `python scripts/scan_infra_keywords.py --format md --out`

### scripts/audit_dynamodb_indexes.py
Audit DynamoDB `TableName` + `IndexName` usage across `codeliver_all` lambdas.

Usage:
- `python scripts/audit_dynamodb_indexes.py --root /home/dm-soft-1/Downloads/lambdas/codeliver_all --mode code-only`
- `python scripts/audit_dynamodb_indexes.py --root /home/dm-soft-1/Downloads/lambdas/codeliver_all --mode live`
- `python scripts/audit_dynamodb_indexes.py --mode live --format md --out`
- `python scripts/audit_dynamodb_indexes.py --mode live --profile <aws-profile> --region eu-west-1`

Output includes:
- active AWS account id in `live` mode
- scanned lambda count and JS file count
- unique tables and resolved `table/index` pairs
- `confirmed-present`
- `missing-in-dynamodb`
- `unresolved-needs-manual-review`
- `table-errors`

## Guardrails
- Do not search outside `*.service.ts` for frontend-called lambda mapping unless explicitly requested.
- Never guess resource names, schemas, payloads, or contracts.
- Do not duplicate playbooks/refs inside repos.
- Keep edits minimal and grounded in verified code/IaC evidence.
- Do not use AWS write actions for DynamoDB index auditing; this skill only inventories and verifies reads against live schema.
- If live AWS auth fails, report it clearly and fall back to `code-only` guidance instead of guessing the schema.
