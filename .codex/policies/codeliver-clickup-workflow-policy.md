# CodeDeliver ClickUp Workflow Guide (On-Demand)

Local-only policy file under `~/.codex/policies/`.
Do not move this rule set into `codexDevAgent` and do not let `sync-global-codex-assets` overwrite or replace it.

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

### Skill-only execution carve-out

- If the user asks only to run an existing local utility/debug skill or equivalent local automation, do not create or update a ClickUp task for that request.
- This carve-out covers execution-only flows such as local live serve, inspect, install, launch, USB debugging, and similar existing helper workflows.
- This carve-out does not apply to implementation, refactor, bugfix, documentation, release, or PM/admin work.
- When the carve-out applies, skip ClickUp search, repo-linking, time tracking, status updates, and closeout comments entirely.

### ClickUp task and write safety

- Every new discussion, actionable request, work item, bug, change, follow-up, or implementation discussion must be tracked in a ClickUp task, even if the user did not explicitly ask to create one.
- Exception: the skill-only execution carve-out above bypasses ClickUp handling completely.
- Before creating a task, search for an existing strongly matching task first.
- If the first or strongest strong match has `created_at` within the last 12 hours, reuse it.
- If only strong matches older than 12 hours exist, do not write to those stale tasks; create a new task titled `[duplicate] {matched task title}` using the first or strongest stale match title.
- If no relevant task exists, create one by default without asking whether a task should be created or asking the user to provide a title, description, or target List when routing can be inferred safely.
- Compose the task title automatically from the request using a short, concrete implementation title.
- Compose the task description automatically with the request context, current repo/folder, scope, and requested outcome.
- Known routing is deterministic and must not trigger an extra List question:
- All routing rules in this section must be resolved in ClickUp organization workspace `DM` by default.
- Exact matches for `optc-team-builder` and `optc-box-exporter` must be searched, routed, and created only under ClickUp workspace `IOANNIS CHOURPOULIADIS`.
- `codeliver-panel` only -> `codeliver-panel`
- `codeliver-sap` only -> `codeliver-sap`
- `codeliver-pos` only -> `codeliver-pos`
- `codeliver-app` only -> `codeliver-app`
- changes spanning more than one of `codeliver-app`, `codeliver-sap`, `codeliver-pos`, `codeliver-panel` -> `codeliver-global-tasks`
- generic or ambiguous `codeliver` work -> `codeliver-global-tasks`
- `cloud-repos-panel` -> `cloud-repos-panel`
- `cloud-fleet` or `Cloud Fleet` -> `cloud-fleet`
- `deliveryfleet-pos` only -> `deliveryfleet-pos`
- `deliveryfleet-app` only -> `deliveryfleet-app`
- changes spanning both `deliveryfleet-pos` and `deliveryfleet-app` -> `deliveryfleet-global-tasks`
- `optc-team-builder` only -> search/create list in `IOANNIS CHOURPOULIADIS`
- `optc-box-exporter` only -> search/create list in `IOANNIS CHOURPOULIADIS`
- For any other project or repo name, extract the likely project identifier from the request or current repo context and search ClickUp Lists for exact or close matches first.
- If one plausible existing List is found, use it directly without asking.
- If multiple plausible existing Lists are found, ask only which of those Lists should receive the task.
- If no plausible List exists, create a new List with the project name.
- New List creation defaults:
- `optc-team-builder` and `optc-box-exporter` -> ClickUp organization `IOANNIS CHOURPOULIADIS`
- CodeDeliver-family projects -> space `CoDeliver.io`
- `cloud-repos-panel` family -> folder `DM / Projects`
- all other projects -> folder `DM / Projects`
- Before creating or writing any task in `codeliver-panel`, `codeliver-sap`, `codeliver-pos`, `codeliver-app`, `codeliver-global-tasks`, `cloud-fleet`, `optc-team-builder`, or `optc-box-exporter`, verify that the list still uses this canonical status schema:
- active: `to do`, `in progress`, `testing`, `update required`, `at risk`, `guidelines`
- closed: `complete`
- If any of those lists drift from the canonical schema, restore the canonical statuses before continuing with task writes in that list.
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
- Exception: skill-only execution requests run directly and do not require delivery-mode, branch, `push only`, or `deploy` questions.
- Default to `local changes only` on the current checked-out branch unless the user explicitly says otherwise.
- Do not ask for delivery mode or target branch again when the user has not overridden those defaults.
- Create or switch branches only when the user explicitly requests a different branch or `PR-ready changes`.
- Do not push or deploy without explicit user confirmation.
- Ask user: `push only` vs `deploy` before release actions.

### Time tracking and closure safety

- Manual tracking policy applies (record discussion start/end in Europe/Athens, add elapsed entry when work completes).
- When discussion on an existing task starts, move it to the list-specific `in progress` status (if available) at that time.
- For the canonical lists above, treat `testing` as the preferred testing-equivalent status and keep `complete` as the only closed status.
- Do not move task to done/complete/closed without a corresponding time entry.
- Move completed implementation tasks in the canonical lists to `testing`; use `ΕΛΕΓΧΟΣ` / `ελεγχος` only for non-canonical lists that actually use that convention.
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
- Check for codexDevAgent updates, ask whether the user wants `update` or `clean-install`, then clone or refresh the repo when needed, compare repo version from `package.json`, and merge the managed `AGENTS.md` workflow block plus sync repo skill folders into `~/.codex`.

## 4) Standard workflow (condensed)

Skill-only execution requests bypass this workflow and use the carve-out above.

1. Confirm context and task scope.
2. Discover, reuse, or auto-create the ClickUp task and validate ownership.
3. Ensure repo linkage is present before implementation.
4. Scout architecture and source-of-truth paths.
5. Write concrete implementation plan into ClickUp task description.
6. At discussion start: set list-specific in-progress status (if available) and start manual timing timeline.
7. Ask clarifying questions and request explicit go-ahead.
8. Assume `local changes only` and the current checked-out branch unless the user explicitly overrides either one.
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
