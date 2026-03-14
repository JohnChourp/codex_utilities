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

## Fast path defaults
- Default behavior is `audit-only` with a compact `audit-fast` path.
- Prefer macOS-first root resolution, then Linux/Windows fallback.
- Accept optional OS hint from the prompt or command line: `macos`, `ubuntu`, `linux`, `windows`.
- Keep user-facing chat quiet:
  - one short start update
  - one blocker/fallback update only if needed
  - one finish update
- Do not narrate every command or paste intermediate command output unless the user explicitly asks.

## Modes
1. Audit-only mode (no edits)
- Resolve canonical roots first.
- Run compact frontend summary first.
- Report only verified missing/stale docs with evidence.
- Run DynamoDB index audit in `code-only` mode only when the request asks for it or when the frontend evidence alone is insufficient.
- Run infra scan only when there is still an unresolved verified gap.

2. Refresh mode (edits expected)
- Apply verified updates to `.codex/playbooks` and `.codex/refs`.
- Keep changes minimal and scoped to observed code/IaC deltas.
- When requested, run DynamoDB index audit in `live` mode and refresh the canonical ref/playbook only if the audit proves a mismatch.

## Workflow
1. Resolve canonical roots before scanning.
- Resolve canonical `.codex`, `projects`, and `lambdas/codeliver_all` roots.
- macOS-first defaults usually resolve to:
  - `~/Downloads/projects/codex_utilities/.codex`
  - `~/Downloads/projects`
  - `~/Downloads/lambdas/codeliver_all`
- On Linux/Windows, use the same relative layout from the detected home directory when present.
- If the user supplies `macos`, `ubuntu`, or `windows`, honor that hint before auto-detection.

2. Collect baseline docs only when needed.
- Prefer compact inventory summary first.
- Skip full file listings when canonical `.codex` is already resolved.
- Avoid duplicate docs; update canonical files only.

3. Scan frontend callers (services only).
- Restrict frontend lambda discovery to:
  - `projects/codeliver/codeliver-app/src/app/**/*.service.ts`
  - `projects/codeliver/codeliver-pos/src/app/**/*.service.ts`
  - `projects/codeliver/codeliver-panel/src/app/**/*.service.ts`
  - `projects/codeliver/codeliver-sap/src/app/**/*.service.ts`
- Capture HTTP method, route/path, request payload shape, and observed response shape if present.
- The extractor must handle:
  - `this.http.post<any>(...)`
  - multiline `this.http` newline `.post(...)`
  - `CapacitorHttp.get/post/...`
  - concatenated base URLs such as `this.url + "route"`

4. Map to normalized lambda paths.
- Use `.codex/playbooks/codeliver-api-gateways.md` for `apiId -> apiName` mapping.
- Normalize as `{api}/{stage}/{lambda}` when resolvable.

5. Scan infra and contracts only on evidence-driven escalation.
- Lambdas/IaC fast path:
  - scan code/IaC files first (`.js`, `.ts`, `.json`, `.yaml`, `.yml`)
  - ignore README/ROADMAP/docs by default
- Enable noisy infra/doc scans only when the request explicitly asks for broad infra coverage or when a verified gap remains unresolved.

6. Audit DynamoDB table/index usage only when requested.
- Scan all lambdas under the resolved `lambdas/codeliver_all` root.
- Extract DynamoDB `TableName` + `IndexName` pairs from JS lambda files.
- Resolve literal values and simple same-file constant indirection.
- Treat unresolved dynamic expressions such as `params.IndexName` as manual-review evidence, never as missing indexes.
- Default to `code-only`.
- In `live` mode, verify every resolved pair against the currently authenticated AWS CLI account/profile using `aws dynamodb describe-table`.
- Compare against both `GlobalSecondaryIndexes` and `LocalSecondaryIndexes`.
- Produce these result buckets:
  - `confirmed-present`
  - `missing-in-dynamodb`
  - `unresolved-needs-manual-review`
  - `table-errors` (for `describe-table` failures such as missing tables or auth problems)

7. Decide updates.
- If no verified gap: produce audit findings only.
- If verified gap exists: update the matching canonical playbook/ref.

8. Update refs for frontend lambda usage (when requested).
For each lambda section include:
- Normalized path `{api}/{stage}/{lambda}`
- HTTP method and route
- Observed request payload example (sanitized)
- Observed response example (sanitized), or
  - `Response example not observed in service code`
- Source `*.service.ts` path

9. Validate consistency.
- Re-check referenced resources/contracts against code/IaC.
- Keep refs as usage maps and playbooks as contract sources.
- For DynamoDB audit findings, prefer live `describe-table` verification over lambda-local CloudFormation, because the lambda-local templates are deployment templates and are not the table/index source of truth.
- In audit-only mode, skip temp regenerate/diff of `.generated.md` files unless the summary points to a mismatch or the user explicitly requests that deeper check.

## Resources
### scripts/collect_doc_inventory.py
List current playbooks/refs from the resolved canonical `.codex`.

Usage:
- `python3 scripts/collect_doc_inventory.py`
- `python3 scripts/collect_doc_inventory.py --verbose`
- `python3 scripts/collect_doc_inventory.py --codex-root ~/Downloads/projects/codex_utilities/.codex`

### scripts/extract_frontend_http_calls.py
Extract frontend HTTP calls and optionally generate reviewable ref markdown.

Usage:
- `python3 scripts/extract_frontend_http_calls.py --summary`
- `python3 scripts/extract_frontend_http_calls.py --format md`
- `python3 scripts/extract_frontend_http_calls.py --write`
- `python3 scripts/extract_frontend_http_calls.py --projects-root ~/Downloads/projects --codex-root ~/Downloads/projects/codex_utilities/.codex`

### scripts/scan_infra_keywords.py
Scan lambdas for infra keyword hints and optionally output markdown.

Usage:
- `python3 scripts/scan_infra_keywords.py`
- `python3 scripts/scan_infra_keywords.py --include-docs`
- `python3 scripts/scan_infra_keywords.py --format md --out`

### scripts/audit_dynamodb_indexes.py
Audit DynamoDB `TableName` + `IndexName` usage across `codeliver_all` lambdas.

Usage:
- `python3 scripts/audit_dynamodb_indexes.py`
- `python3 scripts/audit_dynamodb_indexes.py --mode live`
- `python3 scripts/audit_dynamodb_indexes.py --mode live --format md --out`
- `python3 scripts/audit_dynamodb_indexes.py --mode live --profile <aws-profile> --region eu-west-1`

### scripts/audit_fast.py
Run the compact default audit path with root resolution and minimal output.

Usage:
- `python3 scripts/audit_fast.py`
- `python3 scripts/audit_fast.py --os macos`
- `python3 scripts/audit_fast.py --include-dynamodb`
- `python3 scripts/audit_fast.py --include-dynamodb --dynamodb-mode live --include-infra`

Output includes:
- compact frontend summary by default
- canonical resolved roots
- optional DynamoDB and infra details when explicitly enabled

## Guardrails
- Do not search outside `*.service.ts` for frontend-called lambda mapping unless explicitly requested.
- Never guess resource names, schemas, payloads, or contracts.
- Do not duplicate playbooks/refs inside repos.
- Keep edits minimal and grounded in verified code/IaC evidence.
- Do not use AWS write actions for DynamoDB index auditing; this skill only inventories and verifies reads against live schema.
- If live AWS auth fails, report it clearly and fall back to `code-only` guidance instead of guessing the schema.
- Do not start with broad infra scans, temp generated-ref diffs, or live AWS checks in audit-only mode unless the request explicitly requires them.
