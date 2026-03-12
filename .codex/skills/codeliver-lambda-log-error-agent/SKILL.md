---
name: codeliver-lambda-log-error-agent
description: Investigate CodeDeliver lambda errors end-to-end for single incidents or batch local triage.
---

# CodeDeliver Lambda Log Error Agent

## Overview
Run complete Lambda error investigation for CodeDeliver as an agent, without manual copy/paste. Start from the error URL or request id, build a local investigation workspace, correlate lambda/resources/frontends, and return an actionable root-cause report with deterministic preflight checks and health verdict filtering.

The skill supports:
- Single incident mode (one function/request id)
- Batch mode (all local CodeDeliver lambda repos under `/home/dm-soft-1/Downloads/lambdas/codeliver_all`)
- Cross-product auth-drift audit mode (`codeliver-pos`, `codeliver-panel`, `codeliver-sap`, `codeliver-app`)

## Required Input
Collect at least one entry input:
- CloudWatch `logEventViewer` URL (preferred)
- Function name + request id (+ region/time window)
- Existing lambda-error workspace path

For batch mode (all CodeDeliver lambdas), collect:
- Region
- Time window (for example last 24h)
- Optional limit for max lambdas to inspect

For auth-drift audit mode, collect:
- Region for optional live log sweep
- Time window (for example last 24h or last 7d)
- Optional product subset (`pos`, `panel`, `sap`, `app`)
- Optional live-sweep toggle (`static-only` or `static + logs`)

Use `--dest` when the user asks for a specific workspace location.

## Workflow

### 1. Run deterministic preflight gate
Run and record these checks before doing analysis:

```bash
aws sts get-caller-identity > /tmp/aws.sts.json
test -d /home/dm-soft-1/Downloads/lambdas/codeliver_all
test -d /home/dm-soft-1/Downloads/projects/codeliver
```

When function and region are known, also capture runtime/arch:

```bash
aws lambda get-function-configuration --function-name <fn> --region <region> --output json | jq '{Runtime,Architectures,LastModified,RevisionId}'
```

Preflight result must be explicit:
- `aws_auth`: `pass` or `fail`
- `local_codeliver_all_present`: `yes` or `no`
- `local_projects_present`: `yes` or `no`
- `lambda_runtime_checked`: `yes` or `no` (required once `<fn>/<region>` are known)
- `preflight_status`: `pass` only if all required checks passed

Failure actions:
- If AWS auth fails, stop and ask user to authenticate AWS CLI before continuing.
- If `codeliver_all` path is missing, stop and ask user to sync repos first.
- If `/home/dm-soft-1/Downloads/projects/codeliver` is missing, continue with lambda-only analysis and mark completeness as partial.

### 2. Choose the right execution command
Prefer request-id-based collection when function and request id are known:

```bash
workspace="/tmp/codeliver-lambda-error-$(date +%Y%m%d%H%M%S)-<fn>-<request_id>"
mkdir -p "$workspace/logs"

aws logs filter-log-events \
  --log-group-name "/aws/lambda/<fn>" \
  --region <region> \
  --filter-pattern '"<request_id>"' \
  --output json > "$workspace/logs/request-events.json"
```

If only CloudWatch URL is available and parser tooling exists, use it to resolve function/request id first. Otherwise parse them manually from URL query params, then run the command above.

### 3. Batch mode for all CodeDeliver lambdas in `codeliver_all`
When the user asks to run for all downloaded CodeDeliver lambdas, discover function candidates from local repo folders and inspect recent failing request ids.

```bash
find /home/dm-soft-1/Downloads/lambdas/codeliver_all -mindepth 1 -maxdepth 1 -type d | sort > /tmp/codeliver_all.repos.txt
awk -F/ '{print $NF}' /tmp/codeliver_all.repos.txt > /tmp/codeliver_all.lambda_candidates.txt
```

Validate each candidate against AWS and keep existing functions only:

```bash
while read -r fn; do
  aws lambda get-function --function-name "$fn" --region <region> --output json >/dev/null 2>&1 && echo "$fn"
done < /tmp/codeliver_all.lambda_candidates.txt > /tmp/codeliver_all.lambda_functions.txt
```

For each valid function, scan latest failures and persist per-function logs:

```bash
start_ms=$(date -d '24 hours ago' +%s000)

while read -r fn; do
  workspace="/tmp/codeliver-lambda-error-$(date +%Y%m%d%H%M%S)-$fn"
  mkdir -p "$workspace/logs"

  aws logs filter-log-events \
    --log-group-name "/aws/lambda/$fn" \
    --region <region> \
    --start-time "$start_ms" \
    --filter-pattern '"ERROR" || "Task timed out" || "Runtime.ImportModuleError" || "RequestId:"' \
    --output json > "$workspace/logs/logscan.json"

  rid=$(jq -r '.events[].message' "$workspace/logs/logscan.json" | rg -o 'RequestId:\s*[0-9a-f-]+' -m1 | awk '{print $2}')
  if [ -n "$rid" ]; then
    aws logs filter-log-events \
      --log-group-name "/aws/lambda/$fn" \
      --region <region> \
      --filter-pattern "\"$rid\"" \
      --output json > "$workspace/logs/request-${rid}.json"
  fi
done < /tmp/codeliver_all.lambda_functions.txt
```

Batch report requirements:
- `scanned_functions_count`
- `functions_with_failures_count`
- per-function latest `request_id`
- per-function top hypothesis + fix + verify step
- global health verdict split (production vs smoke/test)

### 3b. Cross-product auth-drift audit mode
Use this mode when the user asks whether stale/invalid auth-context failures can happen across products, not just in one lambda.

Audit products:
- `codeliver-pos`
- `codeliver-panel`
- `codeliver-sap`
- `codeliver-app`

Static inventory commands:

```bash
rg -n "authorizer|renew-token|login|jwt.verify|expiresIn|users\\[0\\]|no_user_found|user_does_not_exist|delivery_guy_does_not_exist|device_does_not_exist|login_completed" \
  /home/dm-soft-1/Downloads/lambdas/codeliver_all \
  /home/dm-soft-1/Downloads/projects/codeliver
```

Per-product inventory requirements:
- `login_lambda`
- `renew_lambda`
- `authorizer`
- `frontend_auth_entry`
- `identity_source_table`
- `late_failure_signatures`
- `risk_level`
- `recommended_fix_wave`

High-signal discovery signatures:
- blind selection such as `users[0]`
- long-lived token TTLs such as `expiresIn: 2000000` or `1209600`
- authorizers that only do JWT verify and do not check the canonical identity table
- protected lambdas that re-check the same identity and fail late with `no_user_found`, `user_does_not_exist`, `delivery_guy_does_not_exist`, `device_does_not_exist`
- frontend renew/retry flows that restore `login_completed` or otherwise keep stale sessions alive

Optional live log sweep for auth-drift signatures:

```bash
start_ms=$(date -d '24 hours ago' +%s000)

while read -r fn; do
  aws logs filter-log-events \
    --log-group-name "/aws/lambda/$fn" \
    --region <region> \
    --start-time "$start_ms" \
    --filter-pattern '"user_does_not_exist" || "user_not_found" || "no_user_found" || "delivery_guy_does_not_exist" || "device_does_not_exist" || "Unauthorized" || "502"' \
    --output json > "/tmp/${fn}.auth-drift.json"
done < /tmp/codeliver_all.lambda_functions.txt
```

Auth-drift deliverable requirements:
- `auth_surface_inventory`
- `suspected_fail_open_paths`
- `late_identity_failure_signatures`
- `ttl_mismatches`
- `frontend_fail_close_gaps`
- `recommended_remediation_waves`
- remediation matrix with one row per product

### 4. Capture investigation artifacts
Capture and normalize:
- workspace root path
- logs JSON path(s)
- failing request id
- exception type/message/stack
- resource identifiers (table/queue/topic/bucket/host/path)
- business identifiers (`group`, `store`, `store_id`, `store_name`, user/order ids)

When `group` and `store_id` are available, enrich `store_name` from DynamoDB:

```bash
aws dynamodb get-item --table-name storeAccounts --key '{"group":{"S":"<group>"},"store_id":{"S":"<store_id>"}}' --region <region> --output json
```

Preferred `store_name` extraction order from the item:
- `name`
- `store_name`
- `title`
- `shop_name`

### 5. Smart context enrichment (lambda + frontend + downstream 1-hop)
Build context from local repos:

```bash
rg -n "<function_name>|<api_path>|<event_name>|<table_name>|<queue_name>" /home/dm-soft-1/Downloads/lambdas/codeliver_all
rg -n "<function_name>|<api_path>" /home/dm-soft-1/Downloads/projects/codeliver
```

Mandatory context mapping:
- primary lambda repo (folder under `codeliver_all`)
- direct callers (API Gateway/frontends/other lambdas)
- one-hop downstream consumers (queues/topics/events/tables)
- frontend references from `.codex/refs/codeliver-*-lambdas.md` first, then `*.service.ts` when needed
- consult playbooks when DynamoDB keys/indexes/item shapes are involved:
  - `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md`
  - `.codex/playbooks/codeliver-dynamodb-item-examples.md`

### 6. Enforce data completeness gate
Before root-cause analysis, ensure this minimum dataset exists:
- deterministic preflight object with `preflight_status=pass`
- `function`, `region`, `request_id`
- normalized error signature (`error type`, `error message`, key stack frame)
- at least 1 shared resource id tied to the failing flow
- business context object with:
  - `group`
  - `store_id`
  - `store_name` (or explicit `unknown` with source checked)
- mapping across lambda callers + one-hop downstream resources
- at least 2 code evidence points from relevant repos

If any required item is missing:
- run extra collection commands first (do not jump to conclusions)
- list exactly what is missing and why
- return a blocked/partial status only when collection cannot continue

### 7. Correlate behavior across lambdas/projects
Search across local CodeDeliver lambdas and projects using extracted ids/resources:

```bash
rg -n "<resource-or-id>" /home/dm-soft-1/Downloads/lambdas/codeliver_all /home/dm-soft-1/Downloads/projects/codeliver
```

Prioritize paths that:
- write into shared resources that fail downstream
- transform payloads before publish/emit
- recently changed in commits affecting contracts/schemas

### 8. Build and test hypotheses
Form 1-3 ranked hypotheses.
For each hypothesis, attach:
- evidence from logs
- evidence from code path(s)
- cross-lambda/project interaction that explains the failure
- concrete fix step
- concrete verification step

Prefer verifiable claims over generic speculation.
If confidence is low, state the exact missing evidence that would raise confidence.

### 9. Run safe smoke verification profile (only when needed)
Use smoke invoke only when it adds evidence and the event shape is known.
Pick profile by trigger type using `<skill-root>/references/smoke-profiles.md`.

Rules:
- prefer replaying a sanitized real event shape from recent logs over invented payloads
- include smoke markers (for example `source="codex-smoke"`) so logs can be filtered later
- if trigger type is unknown, skip invoke and rely on logs + metrics
- never treat malformed smoke payload failures as production regressions

### 10. Compute health verdict with noise filters
Use `<skill-root>/references/health-verdict-filters.md` to classify results:
- `production_failures`
- `smoke_or_test_failures`
- `critical_signatures`

Health verdict must:
- filter out smoke/test-marked request ids from regression status
- report counts for production vs smoke/test failures separately
- report critical signature matches (runtime/import/timeouts + critical business signatures discovered in logs)
- mark status `healthy_after_fix` only when production failures and critical signatures are both zero in the checked window

### 11. Return a structured report
Use `<skill-root>/references/report-template.md` for the response layout.
Keep the report concise but complete enough to execute the fix.
Always include:
- data completeness status (`complete` / `partial`)
- business context block (`group`, `store`, `store_id`, `store_name`)
- confidence score per main hypothesis (0.0-1.0)
- minimal, testable fix steps
- preflight gate outcome
- health verdict split (production vs smoke/test)
- final conclusion section at the end with exactly:
  - where the problem is
  - why it happens
  - impact/what happens next

For cross-product auth-drift audit mode, use `<skill-root>/references/auth-drift-report-template.md` instead and include:
- remediation matrix row for each product
- explicit classification per product: `confirmed systemic risk`, `likely risk`, or `monitor-only`
- rollout order and why
- clear split between static findings and live-log-confirmed findings

## Guardrails
- Do not rely on lambda-ai-tools output.
- Do not ask the user to manually copy logs when AWS CLI can fetch them.
- Do not conclude root cause from one stack trace line without cross-repo/resource correlation.
- Do not skip prerequisite checks for AWS auth and local clone context.
- Do not run smoke invokes with arbitrary payload shape.
- Do not classify smoke/test-only failures as production regressions.
- Do not provide final fix recommendations when the completeness gate fails.
- Do not stop at findings only; always propose fix + verification commands.
- Do not omit `group`, `store`, `store_id`, `store_name` in the final report; if unavailable, state `unknown` and the data source checked.
- Do not end the report without an explicit final conclusion.
- Do not treat auth-drift audit as a single-incident triage. It must inventory all auth surfaces for the selected products before ranking risk.
- Do not classify a product as `confirmed systemic risk` from static code smell alone; require either repeated late-failure paths across multiple lambdas or live log confirmation.

## References
Load these only when needed:
- `<skill-root>/references/report-template.md`
- `<skill-root>/references/search-patterns.md`
- `<skill-root>/references/smoke-profiles.md`
- `<skill-root>/references/health-verdict-filters.md`
- `<skill-root>/references/auth-drift-audit-rubric.md`
- `<skill-root>/references/auth-drift-search-patterns.md`
- `<skill-root>/references/auth-drift-report-template.md`
- `<skill-root>/references/auth-drift-current-findings.md`
