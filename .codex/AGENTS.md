# AGENTS.md

<INSTRUCTIONS>
Global guidance for Codex assistance on CodeDeliver.

## Canonical sources

- This file is the only canonical `AGENTS.md`.
- Canonical supporting docs live under `.codex/playbooks/`, `.codex/policies/`, and `.codex/refs/`.
- Do not create or copy `AGENTS.md` into repos. If a repo needs guidance, reference the canonical `.codex/...` path.
- If the user asks to update `AGENTS.md`, edit only `.codex/AGENTS.md`.

## Global invariants

- Always reply in Greek.
- Keep replies concise, actionable, and grounded in repository code.
- In default mode, act autonomously and avoid clarifying questions unless a missing answer would be risky.
- Before any cross-project parity change, ask which targets must stay in lockstep. If the user asks for scoped work, keep that scope and state the parity exception.
- Do not run credentialed AWS commands unless the current prompt explicitly asks for them. Otherwise give exact commands for local execution.
- If asked to build or install, keep iterating until success or a hard external blocker. For Android `installDebug`, uninstall and retry on `INSTALL_FAILED_UPDATE_INCOMPATIBLE`.
- End every reply with direct links to the files you touched.
- Run `ionic build` only after changes under `projects/`. Skip it for docs, lambdas, or `.codex`-only changes.

## Core routing

| Need | Load |
| --- | --- |
| Lambda-only work | `.codex/policies/codeliver-lambdas-guidance.md` |
| Project/component-only work | `.codex/policies/codeliver-projects-guidance.md` |
| End-to-end work | both files above |
| Shared parity areas or lockstep sync | `.codex/policies/codeliver-parity-rules.md` |
| Frontend/template/translation/logging/UI safety | `.codex/policies/codeliver-general-working-rules-policy.md` |
| Playwright/Figma/Notion/Linear routing | `.codex/policies/codeliver-mcp-routing-policy.md` |
| Lambda contracts/hardening/deploy/handled errors | `.codex/policies/codeliver-lambda-hardening-policy.md` |
| README or ROADMAP behavior | `.codex/policies/codeliver-documentation-roadmap-policy.md` |
| ClickUp lifecycle or MCP workflow | `.codex/policies/codeliver-clickup-workflow-policy.md` |

Keep `.codex/playbooks/*` and `.codex/refs/*` as canonical lookup sources.

## Playbook rules

- Never guess DynamoDB PK, SK, GSI, or LSI names and types.
- For `requests`, `routes`, `route_paths`, and similar items, consult `.codex/playbooks/codeliver-dynamodb-item-examples.md` before adding or changing attributes.
- Use the relevant playbook directly for DynamoDB keys/triggers, SQS, API Gateway, S3, EventBridge, and CloudFront questions.

## Authorizer claims

- SAP: `superadmin_id` only. No `group`.
- Panel: `user_id`, `group`.
- POS: `user_id`, `store_id`, `group`.
- App: `device_id`, `delivery_guy_id`, `group`.
</INSTRUCTIONS>
