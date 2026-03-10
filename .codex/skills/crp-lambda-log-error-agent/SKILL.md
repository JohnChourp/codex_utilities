---
name: "CRP Lambda Log Error Agent"
description: "Agent-native runbook for end-to-end Lambda error investigation through CRP CLI without lambda-ai-tools dependency. Supports single incident triage and batch triage for all locally downloaded CRP lambdas under /home/dm-soft-1/Downloads/lambdas/crp_all."
---

# CRP Lambda Log Error Agent

## Overview
Run a complete Lambda error investigation as an agent, not as manual copy/paste. Start from the error URL or request id, build the local investigation workspace, correlate repos and resources, and return an actionable root-cause report with deterministic preflight checks and health verdict filtering.

The skill supports:
- Single incident mode (one function/request id)
- Batch mode (all local CRP lambda repos under `/home/dm-soft-1/Downloads/lambdas/crp_all`)

## Required Input
Collect at least one entry input:
- CloudWatch `logEventViewer` URL (preferred)
- Function name + request id (+ region/time window)
- Existing lambda-error workspace path

For batch mode (all CRP lambdas), collect:
- Region
- Time window (for example last 24h)
- Optional limit for max lambdas to inspect

Use `--dest` when the user asks for a specific workspace location.

## Workflow

### 1. Run deterministic preflight gate
Run and record these checks before doing analysis:

```bash
crp projects list --format json > /tmp/crp.projects.json
aws sts get-caller-identity > /tmp/aws.sts.json
crp config --format json > /tmp/crp.config.json
test -d /home/dm-soft-1/Downloads/lambdas/crp_all
```

When function and region are known, also capture runtime/arch:

```bash
aws lambda get-function-configuration --function-name <fn> --region <region> --output json | jq '{Runtime,Architectures,LastModified,RevisionId}'
```

Preflight result must be explicit:
- `crp_auth`: `pass` or `fail`
- `aws_auth`: `pass` or `fail`
- `github_org_present`: `yes` or `no` (required when cloning is needed)
- `lambda_runtime_checked`: `yes` or `no` (required once `<fn>/<region>` are known)
- `local_crp_all_present`: `yes` or `no`
- `preflight_status`: `pass` only if all required checks passed

Failure actions:
- If any CRP command returns `401`/`Unauthorized`, stop and ask user to run `crp login`, then retry.
- If AWS auth fails, stop and ask user to authenticate AWS CLI before continuing.
- If GitHub org is missing and cloning is needed, stop and ask user to set CRP org config first.
- If `crp_all` path is missing, stop and ask user to sync repos first.

### 2. Choose the right execution command
Use agent-native commands (no `lambda-log-error-url` wrapper, no `la` execution):

```bash
# URL parse + run check-lambda-log directly (preferred)
crp check-lambda-log-url '<cloudwatch-logeventviewer-url>' --run

# Direct run with explicit parameters
crp check-lambda-log --function <fn> --region <region> --request-id <id> --analysis none

# Offline replay from saved logs
crp check-lambda-log --logs-file '<path-to-log-json>' --function <fn> --request-id <id> --analysis none
```

For URL flow, prefer `check-lambda-log-url --run` and force downstream mode `--analysis none` when needed to avoid lambda-ai-tools dependency.

### 3. Batch mode for all CRP lambdas in `crp_all`
When the user asks to run for all downloaded CRP lambdas, discover function candidates from local repo folders and inspect recent failing request ids.

```bash
find /home/dm-soft-1/Downloads/lambdas/crp_all -mindepth 1 -maxdepth 1 -type d | sort > /tmp/crp_all.repos.txt
awk -F/ '{print $NF}' /tmp/crp_all.repos.txt > /tmp/crp_all.lambda_candidates.txt
```

Validate each candidate against AWS and keep existing functions only:

```bash
while read -r fn; do
  aws lambda get-function --function-name "$fn" --region <region> --output json >/dev/null 2>&1 && echo "$fn"
done < /tmp/crp_all.lambda_candidates.txt > /tmp/crp_all.lambda_functions.txt
```

For each valid function, extract latest failing request id in the selected time window:

```bash
start_ms=$(date -d '24 hours ago' +%s000)
while read -r fn; do
  aws logs filter-log-events \
    --log-group-name "/aws/lambda/$fn" \
    --region <region> \
    --start-time "$start_ms" \
    --filter-pattern '"ERROR" || "Task timed out" || "Runtime.ImportModuleError" || "RequestId:"' \
    --output json > "/tmp/${fn}.logscan.json"

  rid=$(jq -r '.events[].message' "/tmp/${fn}.logscan.json" | rg -o 'RequestId:\s*[0-9a-f-]+' -m1 | awk '{print $2}')
  if [ -n "$rid" ]; then
    crp check-lambda-log --function "$fn" --region <region> --request-id "$rid" --analysis none
  fi
done < /tmp/crp_all.lambda_functions.txt
```

Batch report requirements:
- `scanned_functions_count`
- `functions_with_failures_count`
- per-function latest `request_id`
- per-function top hypothesis + fix + verify step
- global health verdict split (production vs smoke/test)

### 4. Capture investigation artifacts
From command output, capture:
- Workspace root path
- Logs file under `logs/`
- Repos clone root
- Any generated summary/evidence JSON paths

Open the logs JSON and extract:
- failing request id
- exception type/message/stack
- resource identifiers (table/queue/topic/bucket/host/path)
- business identifiers (store/user/account/order/correlation ids)
- business context fields required for the final report:
  - `group`
  - `store` (if present)
  - `store_id`
  - `store_name` (best-effort enrichment; do not leave implicit)

When `group` and `store_id` are available, enrich `store_name` from DynamoDB:

```bash
aws dynamodb get-item --table-name storeAccounts --key '{"group":{"S":"<group>"},"store_id":{"S":"<store_id>"}}' --region <region> --output json
```

Preferred `store_name` extraction order from the item:
- `name`
- `store_name`
- `title`
- `shop_name`

### 5. Smart context enrichment (feature/master/brain + runtime cwd)
Build enriched CRP mapping after artifacts are available:

```bash
crp repos list --format json > /tmp/crp.repos.json
crp features list --format json > /tmp/crp.features.json
crp projects list --format json > /tmp/crp.projects.full.json
```

For the failing `repo_id`, resolve:
- linked `feature_ids`
- master repo per feature (check keys in order):
  - `master_repo_id`, `masterRepoId`, `master_repo`, `masterRepo`
- brain repos per feature (check keys in order):
  - `brain_repo_ids`, `brainRepoIds`, `brain_repos`, `brainRepos`
- if a feature has no brain repos, try project-level keys with the same key order

Normalization rules:
- deduplicate master/brain repos
- preserve source of each brain mapping (`feature` or `project`)
- if no explicit brain mapping exists, keep `brain_repos=[]` and mark source `none` (do not invent)

Capture runtime repo context from current working directory:

```bash
git rev-parse --show-toplevel
```

If the command succeeds:
- derive `cwd_repo_id` from the repo folder name
- check if `cwd_repo_id` matches brain pattern `(^|[-_])brains?($|[-_])` (case-insensitive)

If current repo is a brain repo:
- force-include it in analysis context, even when initial CRP feature mapping did not include it
- mark source as `runtime_cwd_brain_repo`
- use it as additional domain context, not as replacement of CRP-linked brain repos

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
- CRP mapping (`repo -> feature(s) -> master repo -> brain repos`)
- runtime repo context captured (and force-included when it is a brain repo)
- at least 2 code evidence points from relevant repos

If any required item is missing:
- run extra collection commands first (do not jump to conclusions)
- list exactly what is missing and why
- return a blocked/partial status only when collection cannot continue

Useful supplemental collection commands:

```bash
crp check-lambda-log-url '<cloudwatch-logeventviewer-url>' --run
crp repos list --format json
crp features list --format json
```

### 7. Correlate behavior across repos
Search across cloned repos using extracted resource ids and domain ids:

```bash
rg -n "<resource-or-id>" <workspace-root>
```

Prioritize paths that:
- write into shared resources that fail downstream
- transform payloads before publish/emit
- recently changed in commits affecting contracts/schemas

Inspect recent commits for candidate files to detect partial migrations or incompatible schema changes.

### 8. Build and test hypotheses
Form 1-3 ranked hypotheses.
For each hypothesis, attach:
- evidence from logs
- evidence from code path(s)
- cross-repo interaction that explains the failure
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
- report critical signature matches (`bridge_order_update_status_error`, `wolt_update_bridge_order_failed`, runtime/import/timeouts)
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

## Guardrails
- Do not call `crp lambda-log-error-url` from this skill.
- Do not call `la run ...` or rely on lambda-ai-tools output.
- Do not ask the user to manually copy logs when CLI helpers can fetch them.
- Do not conclude root cause from one stack trace line without cross-repo/resource correlation.
- Do not skip prerequisite checks for CRP auth, AWS auth, and clone context.
- Do not drop current repo context when the skill runs inside a brain repo.
- Do not run smoke invokes with arbitrary payload shape.
- Do not classify smoke/test-only failures as production regressions.
- Do not provide final fix recommendations when the completeness gate fails.
- Do not stop at findings only; always propose fix + verification commands.
- Do not omit `group`, `store`, `store_id`, `store_name` in the final report; if unavailable, state `unknown` and the data source checked.
- Do not end the report without an explicit final conclusion.

## References
Load these only when needed:
- `<skill-root>/references/report-template.md`
- `<skill-root>/references/search-patterns.md`
- `<skill-root>/references/smoke-profiles.md`
- `<skill-root>/references/health-verdict-filters.md`
