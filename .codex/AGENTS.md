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
- For local skill execution, prefer an internal recovery loop before surfacing failure: inspect the blocker, try the narrowest safe fallback, verify the result, and only then report the outcome.
- Keep skill-execution chat quiet during retries; avoid step-by-step retry narration unless the user explicitly asks for debugging detail.
- Before trusting any path from a skill, policy, playbook, or prior run, verify it against the current machine and workspace.
- Never hardcode user-specific absolute paths in reusable `.codex` assets. Prefer `$HOME`, `Path.home()`, `~`, environment-derived roots, or runtime path discovery.
- If a path assumption fails because the current machine differs from the path embedded in a skill or doc, self-correct automatically, rerun with the detected real path, and persist the validated portability fix back into the relevant global `.codex` asset.
- Write back skill/policy knowledge only after a fallback is confirmed by a successful end result. Do not persist failed or speculative recoveries.
- When a local installed skill gains proven recovery knowledge, also protect it from future sync overwrite via the local preserve-skills mechanism.
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
| Skill-only local utility/debug execution | `.codex/policies/codeliver-skill-execution-policy.md` |

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

# Codex Workflow Guide (Policy + Skill Routing)

This file is the optimized operating policy for Codex sessions.

- Keep this file short and enforceable.
- Use skills for detailed execution playbooks.
- Full historical detail is preserved in `docs/AGENTS_FULL_REFERENCE.md`.

## 1) Start: confirm context

Always confirm:

- current repository/folder
- scope: `frontend`, `backend`, or `end-to-end`
- environments involved (`dev`/`stage`/`prod`) when relevant

## 2) Non-negotiable rules

### ClickUp task and write safety

- Every new discussion, actionable request, work item, bug, change, follow-up, or implementation discussion must be tracked in a ClickUp task, even if the user did not explicitly ask to create one.
- Exception: skill-only execution requests follow `.codex/policies/codeliver-skill-execution-policy.md` and do not create or update ClickUp tasks.
- Before creating a task, search for an existing strongly matching task and reuse it instead of opening a duplicate.
- If no relevant task exists, create one by default without asking whether a task should be created.
- Compose the task title automatically from the request using a short, concrete implementation title.
- Compose the task description automatically with the request context, current repo/folder, scope, and requested outcome.
- Known routing is deterministic and must not trigger an extra List question:
- `codeliver-panel` -> `codeliver-panel`
- `codeliver-sap` -> `codeliver-sap`
- `codeliver-pos` -> `codeliver-pos`
- `codeliver-app` -> `codeliver-app`
- generic or ambiguous `codeliver` work -> `codeliver-globals-tasks`
- `cloud-repos-panel` -> `cloud-repos-panel`
- For any other project or repo name, extract the likely project identifier from the request or current repo context and search ClickUp Lists for exact or close matches first.
- If one plausible existing List is found, use it directly without asking.
- If multiple plausible existing Lists are found, ask only which of those Lists should receive the task.
- If no plausible List exists, create a new List with the project name.
- New List creation defaults:
- CodeDeliver-family projects -> space `CoDeliver.io`
- `cloud-repos-panel` family -> folder `DM / Projects`
- all other projects -> folder `DM / Projects`
- Write only on tasks assigned to the requesting user.
- Treat tasks assigned to others as read-only.
- Do not change due date, priority, assignees, or move to done/closed unless explicitly requested.

### Mentions and language

- In ClickUp comments/descriptions/docs, use `@Display Name` mentions when notification intent exists.
- Chat with user in English by default.
- Mirror existing task language for ClickUp comments/descriptions.
- Write repo markdown docs in English.

### Approval and release controls

- Do not implement before explicit user go-ahead.
- Exception: skill-only execution requests follow `.codex/policies/codeliver-skill-execution-policy.md` and run directly without delivery-mode, branch, or release questions.
- Before any code changes, ask delivery mode and branch:
- `local changes only` or `PR-ready changes`
- target branch name (create/switch branch only after user confirms)
- Do not push or deploy without explicit user confirmation.
- Ask user: `push only` vs `deploy` before release actions.

### Time tracking and closure safety

- Manual tracking policy applies (record discussion start/end in Europe/Athens, add elapsed entry when work completes).
- When discussion on an existing task starts, move it to the list-specific `in progress` status (if available) at that time.
- Do not move task to done/complete/closed without a corresponding time entry.
- Move completed implementation tasks to testing-equivalent status (often `ΕΛΕΓΧΟΣ` / `ελεγχος`, list-dependent).
- Before any status change, explicitly discover statuses for the task's List (do not assume from other Lists).
- If the List has `in progress` and testing-equivalent statuses, use them (do not jump directly to `complete`).
- If a List truly has only terminal flow (for example `to do` + `complete`), ask explicit user confirmation before setting `complete`, and note this limitation in a task comment.

## 3) Skill routing (primary execution path)

Use these skills as the default source of detailed instructions.

1. `clickup-task-lifecycle`
- Task discovery, ownership checks, safe updates, status and time-entry rules.

2. `clickup-repo-linking`
- Repo-registry lookup/create and task-to-repo linking.
- Repo registry list: `901502503337`.
- Registry URL: `https://app.clickup.com/9015329079/v/l/6-901502503337-1?pr=90151074892`.

3. `implementation-gate`
- Architecture scouting, plan writing, ambiguity cleanup, approval gate, release gating.

4. `front-end-code-style`
- Angular Ionic frontend style for `mobileorder`/`dmpanel`:
- declaration order (`@Input/@Output` -> `public` -> `private`)
- camelCase naming
- NgRx subscription lifecycle patterns
- avoid non-trivial function calls in template bindings (precompute in `.ts`)

5. `back-end-lambda-code-style`
- Node.js lambda backend style for `dm_lambda_functions/paneldelivery`:
- keep deliveryManager helper usage and existing AWS SDK style per lambda
- prefer lodash + Bluebird iteration (`Promise.map`/`Promise.mapSeries`) over new loop constructs
- preserve DynamoDB params-object, `CustomError`, and response conventions

6. `closeout-docs`
- Testing status transition, closeout comments, final summaries, optional ClickUp docs.

7. `sync-global-codex-assets`
- Project-local helper for codexDevAgent updates. Ask whether the user wants `update` or `clean-install`, then clone or refresh the repo when needed, compare repo version from `package.json`, merge the managed `AGENTS.md` workflow block, sync repo skill folders into `~/.codex`, skip local-only skills, and honor the machine-local overlay file at `~/.codex/policies/sync-global-codex-assets.local.md` when it exists.

## 4) Standard workflow (condensed)

Skill-only execution requests use the dedicated carve-out policy and skip the ClickUp/branch/release workflow below.

1. Confirm context and task scope.
2. Validate ClickUp task existence and ownership.
3. Ensure repo linkage is present before implementation.
4. Scout architecture and source-of-truth paths.
5. Write concrete implementation plan into ClickUp task description.
6. At discussion start: set list-specific in-progress status (if available) and start manual timing timeline.
7. Ask clarifying questions and request explicit go-ahead.
8. Ask delivery mode (`local changes` vs `PR-ready`) and target branch before editing files.
9. Implement minimal scoped changes, mirroring existing code style.
10. Run targeted validation (tests/build/lint as practical).
11. Ask `push only` vs `deploy`, then execute only what user confirms.
12. Move task to testing-equivalent status (if available), add change summary comment, and log time entry.
13. Provide concise final summary to user.

## 5) ClickUp MCP quick fallback

If ClickUp MCP fails because of auth/setup:

1. `codex mcp list`
2. If missing: `codex mcp add clickup --url https://mcp.clickup.com/mcp`
3. `codex mcp login clickup`
4. Verify with `codex mcp list --json`
5. Retry with narrower search scope

## 6) Optional documentation closeout

After implementation and validation, ask if user wants a ClickUp Doc:

- non-technical how-to
- technical/development handoff

When creating a ClickUp Doc, include/share with:

- `@Seirino`
- `@Constantinos Adamidis`
- `@Alexandros Nikolaos Naziris`

## 7) Full reference

For complete legacy workflow details, templates, and expanded procedures:

- `docs/AGENTS_FULL_REFERENCE.md`
