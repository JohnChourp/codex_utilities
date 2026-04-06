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

### Skill-only execution handling

- If the user asks only to run an existing local utility/debug skill or equivalent local automation, still create a new ClickUp task for that conversation.
- This handling covers execution-only flows such as local live serve, inspect, install, launch, USB debugging, and similar existing helper workflows.
- These flows may still run directly, but they do not bypass ClickUp creation, repo-linking, time tracking, status updates, or closeout comments.

### ClickUp task and write safety

- Every new conversation must create a new ClickUp task, even if the request is identical or very similar to a recent one and even if the user did not explicitly ask to create a task.
- Do not search for, reuse, revive, or duplicate-match an older task for the current conversation.
- ClickUp routing must use ids first and names second, in this order: `workspace_id -> space_id -> folder_id -> list_id`.
- Live-confirmed workspaces:
- `workspace_id=9015329079` (cached root label: `Workspace`)
- `workspace_id=9014849358`, `workspace_name=IOANNIS CHOURPOULIADIS's Workspace`
- Live-confirmed canonical routing targets:
- `Codeliver` space `space_id=901510669130`: `codeliver-panel=901506309888`, `codeliver-app=901506309882`, `codeliver-pos=901506319729`, `codeliver-sap=901508601568`, `codeliver-global-tasks=901515418339`.
- Deprecated legacy `CoDeliver.io` space `space_id=90151073880`: keep for historical reference only, never create new tasks there.
- Live `Delivery Feet` space `space_id=90156023875` (canonical alias `Delivery Fleet`): `deliveryfleet-pos=901514051062`, `deliveryfleet-app=901514051088`.
- Under `workspace_id=9015329079`, `DM` is a space: `space_id=90151066397`. Under `DM`, `Projects` folder `folder_id=90151552991` contains `cloud-repos-panel=901506686257`, live `Cloud Fleet=901502564110` (canonical alias `cloud-fleet`), and `Cloud Fleet Integrations=901502619784` as a separate list.
- Under `workspace_id=9014849358`, live-confirmed `ionic angular` space: `space_id=90144305724`.
- Repo registry remains canonical at `GITHUB REPOS` space `space_id=90151074892`, `Repositories` list `list_id=901502503337`.
- Treat workspace and space labels separately: `IOANNIS CHOURPOULIADIS's Workspace` is a workspace; `DM` is a space under `workspace_id=9015329079`, not a workspace label.
- Do not deterministically auto-route any target inside `workspace_id=9014849358` until its exact `space_id` and `list_id` are re-verified live.
- `workspace_id=9014849358` workspace-scoped provisional targets must not be used for deterministic auto-routing or auto-creation until live ids are re-verified:
- under `ionic angular` (`space_id=90144305724`): `LearnByzantineMusic`, `optc-team-builder`, `Do-not-disturb-controller`, `orologion-mega`, `create-fonts-from-ocr-photos`, `oseth-bus-route-planner`
- under `Jupiter Notebok` (space id still unconfirmed): `optc-box-exporter`
- Other provisional or unconfirmed targets must not be used for deterministic auto-routing or auto-creation until live ids are re-verified: `codeliver-tasks-to-day`, `deliveryfleet-global-tasks`.
- Create the new task by default without asking whether a task should be created or asking the user to provide a title, description, or target List when routing can be inferred safely.
- Compose the task title automatically from the request using a short, concrete implementation title.
- Compose the task description automatically with the request context, current repo/folder, scope, and requested outcome.
- Known routing is deterministic and must not trigger an extra List question:
- `codeliver-panel` only -> list `901506309888`
- `codeliver-sap` only -> list `901508601568`
- `codeliver-pos` only -> list `901506319729`
- `codeliver-app` only -> list `901506309882`
- changes spanning more than one of `codeliver-app`, `codeliver-sap`, `codeliver-pos`, `codeliver-panel` -> list `901515418339` (`codeliver-global-tasks`)
- generic or ambiguous `codeliver` work -> list `901515418339` (`codeliver-global-tasks`)
- `cloud-repos-panel` -> list `901506686257`
- `cloud-fleet` or `Cloud Fleet` -> list `901502564110` (live name `Cloud Fleet`)
- `deliveryfleet-pos` only -> list `901514051062`
- `deliveryfleet-app` only -> list `901514051088`
- Do not deterministically route `LearnByzantineMusic`, `optc-team-builder`, `Do-not-disturb-controller`, `orologion-mega`, `create-fonts-from-ocr-photos`, `oseth-bus-route-planner`, `optc-box-exporter`, or any other provisional target until a stable live id is re-verified.
- For any other project or repo name, extract the likely project identifier from the request or current repo context and search ClickUp Lists for exact or close matches first.
- If one plausible existing List is found, use it directly without asking.
- If multiple plausible existing Lists are found, ask only which of those Lists should receive the task.
- If no plausible List exists, create a new List with the project name.
- New List creation defaults:
- CodeDeliver-family projects -> `Codeliver` space `901510669130`
- `cloud-repos-panel` and `cloud-fleet` families -> `DM / Projects` folder `90151552991`
- Targets currently associated with `workspace_id=9014849358` must not be auto-created until their exact `space_id` and `list_id` are re-verified, except that `ionic angular` itself is live-confirmed as `space_id=90144305724`.
- Never auto-create in deprecated `CoDeliver.io`.
- Never auto-create in provisional or unconfirmed targets until live ids are re-verified.
- Before creating or writing any task in `codeliver-panel`, `codeliver-sap`, `codeliver-pos`, `codeliver-app`, `codeliver-global-tasks`, `cloud-repos-panel`, `cloud-fleet`, `deliveryfleet-pos`, or `deliveryfleet-app`, verify that the list exposes exactly these statuses:
- active: `to do`, `at risk`, `in progress`, `testing`
- closed: `complete`
- If one of the required statuses is missing, do not modify the list automatically; stop and ask the user.
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
- Exception: skill-only execution requests still require the same ClickUp lifecycle, but they may run directly and do not require delivery-mode, branch, `push only`, or `deploy` questions.
- Default to `local changes only` on the current checked-out branch unless the user explicitly says otherwise.
- Do not ask for delivery mode or target branch again when the user has not overridden those defaults.
- Create or switch branches only when the user explicitly requests a different branch or `PR-ready changes`.
- Do not push or deploy without explicit user confirmation.
- Ask user: `push only` vs `deploy` before release actions.

### Time tracking and closure safety

- Manual tracking policy applies (record discussion start/end in Europe/Athens, add elapsed entry when work completes).
- When a new conversation task starts, move it to the list-specific `in progress` status (if available) at that time.
- For the lists above, use `testing` as the only testing status and keep `complete` as the only closed status.
- Do not move task to done/complete/closed without a corresponding time entry.
- Move the conversation task to `testing` when the conversation ends, including planning, debugging, read-only, and implementation discussions.
- Before any status change, explicitly discover statuses for the task's List (do not assume from other Lists).
- Use `in progress` before `testing`, and do not jump directly to `complete` unless the user explicitly asks.

## 3) Skill routing (primary execution path)

Use these skills as the default source of detailed instructions.

1. `clickup-task-lifecycle`
- Task discovery, ownership checks, safe updates, status and time-entry rules.

2. `clickup-repo-linking`
- Repo-registry lookup and task-to-repo linking.
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

Skill-only execution requests still follow this workflow for ClickUp creation and closeout.

1. Confirm context and task scope.
2. Create a new ClickUp task for the conversation and validate ownership.
3. Ensure repo linkage is present before implementation.
4. Scout architecture and source-of-truth paths.
5. Write concrete implementation plan into ClickUp task description.
6. At discussion start: set the new task to list-specific `in progress` (if available) and start manual timing timeline.
7. Ask clarifying questions and request explicit go-ahead.
8. Assume `local changes only` and the current checked-out branch unless the user explicitly overrides either one.
9. Implement minimal scoped changes, mirroring existing code style.
10. Run targeted validation (tests/build/lint as practical).
11. Ask `push only` vs `deploy`, then execute only what user confirms.
12. Move the conversation task to `testing`, add change summary comment, and log time entry.
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
