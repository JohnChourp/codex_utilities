---
name: codeliver-audit-lambdas-projects-playbooks-refs
description: Audit CodeDeliver lambdas and projects to decide if new playbooks/refs are needed or existing ones are incomplete. Use when asked to propose new canonical docs, assess coverage, or spot missing contracts/mappings.
---

# codeliver-audit-lambdas-projects-playbooks-refs

## Overview
Audit the CodeDeliver codebase to identify missing or stale playbooks/refs and propose concrete additions with evidence. Draft any proposed playbook/ref content in English.

## Workflow (audit-only, no edits)
1. Collect current canonical docs.
- List `.codex/playbooks/*.md` and `.codex/refs/*.md`.
- Note existing contracts and mappings to avoid duplicates.

2. Scan for integration contracts and resources.
- Lambdas: `rg -n "httpApi|httpApiEvent|events:|path:|method:|handler:" /home/dm-soft-1/Downloads/lambdas`
- Queues/topics/events/tables/buckets: `rg -n "SQS|SNS|EventBridge|DynamoDB|S3|CloudFront|API Gateway" /home/dm-soft-1/Downloads/lambdas`
- Frontend usage (only `*.service.ts`): `rg -n "HttpClient|fetch\\(|/api/|/v1/" /home/dm-soft-1/Downloads/projects -g "*.service.ts"`
- Read lambda READMEs for contract hints.

3. Detect gaps.
- New resource types without playbooks.
- New integration contracts (payload schemas, event names, error codes).
- New or missing refs (maps, flow docs, usage indexes).

4. Propose additions (in English).
For each proposed playbook/ref, provide:
- Name + target folder (`.codex/playbooks` vs `.codex/refs`).
- Why it is needed (contract vs usage summary).
- Evidence (file paths, symbols, sample snippets).
- Suggested source-of-truth files.

## Resources
### scripts/collect_doc_inventory.py
Print a quick inventory of existing playbooks/refs.

Usage:
- `python scripts/collect_doc_inventory.py`
- Optional: `--root /home/dm-soft-1` if running elsewhere.

## Guardrails
- Do not edit files in this skill; only propose.
- Do not duplicate playbooks/refs inside repos.
- Never guess resource names or schemas; cite code/IaC/README evidence.
- Keep suggestions minimal and scoped to real gaps.
