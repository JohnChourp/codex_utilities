---
name: codeliver-refresh-playbooks-refs-after-infra-changes
description: Update CodeDeliver playbooks/refs after infra changes (new lambdas, API gateways, queues, tables, buckets, triggers). Use when asked to refresh canonical docs from code/IaC.
---

# codeliver-refresh-playbooks-refs-after-infra-changes

## Overview
Update canonical `.codex/playbooks` and `.codex/refs` to reflect current CodeDeliver infrastructure and contracts. Write playbook/ref content in English.

## Workflow (edits expected)
1. Identify the change trigger.
- New lambdas, gateways, S3, EventBridge, SQS, DynamoDB triggers.
- Known schema/payload changes.

2. Gather evidence from code/IaC.
- Lambdas: `rg -n "httpApi|events:|Schedule|SQS|SNS|EventBridge|DynamoDB|S3" /home/dm-soft-1/Downloads/lambdas`
- Lambda configs: `rg -n "serverless|template\.ya?ml|handler" /home/dm-soft-1/Downloads/lambdas`
- Frontend usage (only `*.service.ts`): `rg -n "HttpClient|fetch\\(|/api/|/v1/" /home/dm-soft-1/Downloads/projects -g "*.service.ts"`
- Read lambda READMEs for contract details.

3. Update playbooks (canonical contracts).
- Update the matching file under `.codex/playbooks` only.
- Add or adjust schemas, required fields, event names, error codes, and observed examples.
- For DynamoDB keys/indexes, consult `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md`.
- For queues/gateways/buckets/event bridges/cloudfronts, consult the matching playbook.

4. Update refs (usage maps).
- Update `.codex/refs` to include producers/consumers, flows, and usage indexes.
- Keep refs as usage summaries, not contracts.

5. Validate consistency.
- Cross-check that resources referenced in code exist in playbooks.
- Ensure refs only reference playbook-backed contracts.

## Resources
### scripts/scan_infra_keywords.py
Scan lambdas for infra-related keywords and optionally write a markdown report you can paste into a playbook/ref.

Usage:
- `python scripts/scan_infra_keywords.py` (text)
- `python scripts/scan_infra_keywords.py --format md` (markdown)
- `python scripts/scan_infra_keywords.py --format md --out` (writes default `infra-scan.md`)
- `python scripts/scan_infra_keywords.py --format md --out /home/dm-soft-1/.codex/refs/infra-scan.md`

## Guardrails
- Never guess; if data is missing, mark it and request evidence.
- Do not duplicate playbooks/refs inside repo folders.
- Keep changes minimal and scoped to verified differences.
