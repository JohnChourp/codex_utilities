# Lambda Error Report Template

Use this structure in the final answer.

## 1) Incident Summary
- Function / region / request id
- Error signature (type + short message)
- First seen context (URL or source)
- Data completeness status (`complete` or `partial`)
- One-line incident summary in plain language

## 2) Business Context (Required)
- `group`
- `store`
- `store_id`
- `store_name`
- If any field is missing, set it to `unknown` and state which source was checked (logs, payload, DynamoDB table)

## 3) Preflight Gate
- `crp_auth` result
- `aws_auth` result
- `github_org_present` result (when cloning is needed)
- Lambda runtime/architecture snapshot
- Overall `preflight_status` (`pass` or `fail`)

## 4) Repo and Feature Context
- Primary repo
- Runtime repo (if current working repo is a brain repo, include as `runtime_cwd_brain_repo`)
- Feature(s)
- Master repo(s)
- Brain repo(s) and source (`feature` / `project` / `runtime_cwd_brain_repo`)

## 5) Key Evidence
- Log evidence (most relevant lines/fields)
- Code evidence (file paths + behavior)
- Cross-repo/resource evidence (who writes, who reads, where mismatch occurs)

## 6) Most Likely Root Cause
- One short statement describing the causal chain
- Confidence score (0.0-1.0)

## 7) Fix Plan
- Step-by-step changes (minimal and concrete)
- Risk notes (compatibility, migration, side effects)
- Rollback approach if fix fails

## 8) Verification Plan
- Commands/tests to validate fix
- Expected observable outcomes in logs/metrics/behavior

## 9) Health Verdict (Filtered)
- Time window used (UTC)
- `production_failures` count
- `smoke_or_test_failures` count
- `critical_signatures` count/list
- Final status (`healthy_after_fix` / `not_healthy_after_fix`)

## 10) Final Conclusion (Required)
- `Where is the problem?`
- `Why is it happening?`
- `What is the impact / what happens next?`

## 11) Open Questions (if any)
- Explicit unknowns that block certainty
- Exact data needed to close each gap
