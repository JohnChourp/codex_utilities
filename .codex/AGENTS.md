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
- Before proposing or implementing any change, first audit whether the requested behavior already exists. That audit must include README-first review plus code confirmation in the relevant scope. If the behavior is already implemented, say so clearly and avoid planning or applying duplicate changes.
- In default mode, before making any change, first restate your understanding and ask every needed clarifying question in one batch. If a request contains many separate changes, break them out and ask about each one individually so the user can confirm exactly what will change. Reserve autonomous execution only for clearly trivial single-step requests with one safe interpretation.
- Exception: when the user explicitly invokes a local skill or helper workflow and that workflow already defines a safe default execution mode, execute with that documented default instead of asking for confirmation again. Only ask when the user wants to override the documented default or the local prerequisites are unclear.
- For local skill execution, prefer an internal recovery loop before surfacing failure: inspect the blocker, try the narrowest safe fallback, verify the result, and only then report the outcome.
- Keep skill-execution chat quiet during retries; avoid step-by-step retry narration unless the user explicitly asks for debugging detail.
- Before trusting any path from a skill, policy, playbook, or prior run, verify it against the current machine and workspace.
- Never hardcode user-specific absolute paths in reusable `.codex` assets. Prefer `$HOME`, `Path.home()`, `~`, environment-derived roots, or runtime path discovery.
- If a path assumption fails because the current machine differs from the path embedded in a skill or doc, self-correct automatically, rerun with the detected real path, and persist the validated portability fix back into the relevant global `.codex` asset.
- Write back skill/policy knowledge only after a fallback is confirmed by a successful end result. Do not persist failed or speculative recoveries.
- When a local installed skill gains proven recovery knowledge, also protect it from future sync overwrite via the local preserve-skills mechanism.
- Before any cross-project parity change, ask which targets must stay in lockstep. If the user asks for scoped work, keep that scope and state the parity exception.
- For any change that touches a path listed in `.codex/policies/codeliver-parity-rules.md`, run a proactive parity sweep before implementation: include mapped entry-point plus sibling HTML/SCSS and co-located child components by default, unless the user explicitly scopes out parity.
- Do not run credentialed AWS commands unless the current prompt explicitly asks for them. Otherwise give exact commands for local execution.
- Never run Lambda deploy commands, `git commit`, or `git push` automatically. Execute them only when the user explicitly and specifically requests that exact action in the current prompt.
- For lambda repos in `codeliver-sap`, `codeliver-panel`, `codeliver-pos`, `codeliver-app`, and `cloud-repos-panel`, treat deploy as a single production rollout: a `deploy:prod` action is considered to affect the shared production footprint used by both `cap8` and `cap8-dev`. Do not propose split per-environment rollout stages (`cap8-dev` first, then `cap8`) unless the user explicitly asks for environment-separated rollout.
- For JavaScript work under `$HOME/Downloads/lambdas`, do not consider the task complete until you run the lambda's targeted validation plus `npx eslint` on every changed `.js` file from within the lambda tree. Treat `no-undef`, missing helper references, and other ESLint failures as mandatory fixes before closeout.
- For project work under `$HOME/Downloads/projects`, do not consider the task complete until you run the project's targeted validation plus `npx eslint` on every changed lintable source file from the relevant project root, and any broken-translation audit required by `.codex/policies/codeliver-general-working-rules-policy.md`. Prefer the project's local `eslint.config.*` or `.eslintrc*`; if absent, fall back to `$HOME/Downloads/projects/eslint.config.mjs`. Treat `no-undef`, unresolved imports, and other ESLint failures as mandatory fixes before closeout.
- For Angular/Ionic projects under `$HOME/Downloads/projects`, add lightweight debug presence tracing by default unless the user explicitly scopes it out: routed pages should log `console.log("<PageName> component")` from `ionViewDidEnter`; inline modal components should log the same message on every open via an `isOpen` transition hook such as `ngOnChanges` (or an equivalent modal-present event), not `ngOnInit`; other shared components should log from `ngOnInit` only when their selector is instantiated outside `@for`/`*ngFor`, and components rendered inside loops must be excluded to avoid browser log spam.
- For Angular/Ionic project work under `$HOME/Downloads/projects`, always run `$HOME/.codex/scripts/audit_angular_debug_traces.py --project <project-root-or-current-path>` before closeout; the script should audit git-changed Angular files by default and fall back to a full project scan when there are no changed Angular files, and every reported trace gap must be fixed or explicitly scoped out.
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

### Skill-only execution handling

- If the user asks only to run an existing local utility/debug skill or equivalent local automation, still create a new ClickUp task for that conversation.
- This handling covers execution-only flows such as local live serve, inspect, install, launch, USB debugging, and similar helper workflows.
- These flows may still run directly, but they do not bypass ClickUp creation, repo-linking, time tracking, status updates, or closeout comments.

### ClickUp task and write safety

- Every new conversation must create a new ClickUp task, even if the request is identical or very similar to a recent one and even if the user did not explicitly ask to create a task.
- Do not search for, reuse, revive, or duplicate-match an older task for the current conversation.
- ClickUp routing must use ids first and names second, in this order: `workspace_id -> space_id -> folder_id -> list_id`.
- Live-confirmed workspaces:
- `workspace_id=9015329079` (cached root label: `Workspace`)
- `workspace_id=9014849358`, `workspace_name=IOANNIS CHOURPOULIADIS's Workspace`
- Live-confirmed canonical targets:
- `Codeliver` space: `space_id=901510669130` with `codeliver-panel=901506309888`, `codeliver-app=901506309882`, `codeliver-pos=901506319729`, `codeliver-sap=901508601568`, `codeliver-global-tasks=901515418339`.
- Under `workspace_id=9015329079`, `DM` is a space: `space_id=90151066397`. Under `DM`, `Projects` folder `folder_id=90151552991` contains `cloud-repos-panel=901506686257`, live `Cloud Fleet=901502564110` (canonical alias `cloud-fleet`), and `Cloud Fleet Integrations=901502619784` as a separate list.
- Live `Delivery Feet` space: `space_id=90156023875` (canonical alias `Delivery Fleet`) with `deliveryfleet-pos=901514051062` and `deliveryfleet-app=901514051088`.
- Under `workspace_id=9014849358`, live-confirmed `ionic angular` space: `space_id=90144305724`.
- Repo registry stays canonical at `GITHUB REPOS` space `space_id=90151074892`, `Repositories` list `list_id=901502503337`.
- `CoDeliver.io` space `space_id=90151073880` is deprecated legacy state. Do not create new tasks there.
- Treat workspace and space labels separately: `IOANNIS CHOURPOULIADIS's Workspace` is a workspace; `DM` is a space under `workspace_id=9015329079`, not a workspace label.
- Do not deterministically auto-route any target inside `workspace_id=9014849358` until its exact `space_id` and `list_id` are re-verified live.
- `workspace_id=9014849358` workspace-scoped provisional targets must not be used for auto-routing or auto-creation until live ids are re-verified:
- under `ionic angular` (`space_id=90144305724`): `LearnByzantineMusic`, `optc-team-builder`, `Do-not-disturb-controller`, `orologion-mega`, `create-fonts-from-ocr-photos`, `oseth-bus-route-planner`
- under `Jupiter Notebok` (space id still unconfirmed): `optc-box-exporter`
- Other provisional or unconfirmed targets must not be used for auto-routing or auto-creation until live ids are re-verified: `codeliver-tasks-to-day`, `deliveryfleet-global-tasks`.
- Create the new task by default without asking whether a task should be created.
- Compose the task title automatically from the request using a short, concrete implementation title.
- Compose the task description automatically with the request context, current repo/folder, scope, and requested outcome.
- Apply routing in this order:
- if the active workflow/policy provides deterministic routing for the repo or project family, use it directly
- otherwise search ClickUp Lists for exact or close matches based on the request and current repo context
- if one plausible List is found, use it directly without asking
- if multiple plausible Lists are found, ask only which of those Lists should receive the task
- if no plausible List exists, create a new List with the project name in the workspace's default project folder or space
- Resolve assignee if unclear and ensure the task is assigned to the requesting user before any write.
- Verify the task List exposes exactly these statuses:
- active: `to do`, `at risk`, `in progress`, `testing`
- closed: `complete`
- Read the actual list status configuration from list metadata or the ClickUp API/UI; do not infer the schema only from currently visible task statuses.
- If one of the required statuses is missing, do not modify the list automatically; stop and ask the user.
- Write only on tasks assigned to the requesting user.
- Treat tasks assigned to others as read-only.
- Do not change due date, priority, assignees, or move to done/closed unless explicitly requested.

### Mentions and language

- In ClickUp comments/descriptions/docs, use `@Display Name` mentions when notification intent exists.
- Chat with user in English by default.
- Mirror existing task language for ClickUp comments/descriptions.
- Keep ClickUp descriptions and comments compact by default.
- Write repo markdown docs in English.

### ClickUp writing size defaults

- Use staged ClickUp writing:
- `small` task: `Scope` + up to 2 `Change` bullets + up to 2 `Checks` bullets
- `medium` task: `Scope` + up to 3 `Plan` bullets + up to 3 `Checks` bullets + 1-line `Risk`
- `large/risky` task: full plan only when schema, infra, multi-repo, broad refactor, or unclear/high-risk work justifies it
- Work-done comments should default to 3 short lines: `Changed`, `Validated`, `Next`.
- Concern/blocker comments should default to 3 short lines: `Issue`, `Impact`, `Need`.
- Do not restate unchanged requirements, repo context, or acceptance criteria in ClickUp text.

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
- Use `testing` as the only testing status and keep `complete` as the only closed status.
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

7. `testing-review`
- Run an independent review session for tasks already in testing.
- Reuse repo-specific style skills during review and optionally run user-approved live tests.

8. `sync-global-codex-assets`
- Check for codexDevAgent updates, ask whether the user wants `update` or `clean-install`, then clone or refresh the repo when needed, compare repo version from `package.json`, merge the managed `AGENTS.md` workflow block, sync repo skill folders into `~/.codex`, skip local-only skills, and honor the machine-local overlay file at `~/.codex/policies/sync-global-codex-assets.local.md` when it exists.

## 4) Standard workflow (condensed)

Skill-only execution requests still follow this workflow for ClickUp creation and closeout.

1. Confirm context and task scope.
2. Create a new ClickUp task for the conversation and validate ownership.
3. Ensure repo linkage is present before implementation.
4. Scout architecture and source-of-truth paths.
5. Write a staged ClickUp plan: `small`, `medium`, or `large/risky`.
6. At discussion start: set the new task to list-specific `in progress` (if available) and start manual timing timeline.
7. Ask clarifying questions and request explicit go-ahead.
8. Assume `local changes only` and the current checked-out branch unless the user explicitly overrides either one.
9. Implement minimal scoped changes, mirroring existing code style.
10. Run targeted validation (tests/build/lint as practical).
11. Ask `push only` vs `deploy`, then execute only what user confirms.
12. Move the conversation task to `testing`, add change summary comment, and log time entry.
13. If the user wants an independent pass while the task is in testing, run `testing-review` in a fresh session and optionally perform scoped live tests.
14. Provide concise final summary to user and state which ClickUp List the task belongs to.

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
- `docs/CLICKUP_COMPACT_TEMPLATES.md`
