---
name: clickup-task-lifecycle
description: Manage ClickUp task handling from discovery through execution gating and status hygiene. Use when a request involves ClickUp task lookup, task ownership checks, status changes, time tracking rules, language mirroring, or safe task updates.
---

# Clickup Task Lifecycle

Apply this workflow in order.

## 1) Validate task and ownership

1. Treat every new conversation as something that must create a new ClickUp task, even if the request is identical or very similar to a recent one.
2. Do not search for, reuse, revive, or duplicate-match an older task for the current conversation.
3. Create the new task by default without asking whether a task should be created.
4. Compose the task title automatically from the request using a short, concrete implementation title.
5. Compose the task description automatically with the request context, current repo/folder, scope, and requested outcome.
6. Apply routing in this order:
   - Use ids first and names second in this order: `workspace_id -> space_id -> folder_id -> list_id`.
   - Live-confirmed workspaces are `workspace_id=9015329079` (cached root label: `Workspace`) and `workspace_id=9014849358` (`workspace_name=IOANNIS CHOURPOULIADIS's Workspace`).
   - Under `workspace_id=9015329079`, `DM` is a space: `space_id=90151066397`.
   - Under `workspace_id=9014849358`, live-confirmed `ionic angular` space is `space_id=90144305724`.
   - Use deterministic ids directly for these live-confirmed targets:
     - `cloud-fleet` or `Cloud Fleet` -> `901502564110`
     - `deliveryfleet-pos` -> `901514051062`
     - `deliveryfleet-app` -> `901514051088`
   - Treat live `Delivery Feet` (`90156023875`) as the canonical routing target for the `Delivery Fleet` alias.
   - Treat `Cloud Fleet Integrations` (`901502619784`) as distinct from `cloud-fleet`.
   - Treat workspace and space labels separately: `IOANNIS CHOURPOULIADIS's Workspace` is a workspace; `DM` is a space under `workspace_id=9015329079`, not a workspace label.
   - Do not deterministically auto-route any target inside `workspace_id=9014849358` until its exact `space_id` and `list_id` are re-verified live.
   - Under `workspace_id=9014849358`, treat these as workspace-scoped provisional targets until live ids are re-verified:
     - under `ionic angular` (`space_id=90144305724`): `LearnByzantineMusic`, `Do-not-disturb-controller`, `orologion-mega`, `create-fonts-from-ocr-photos`, `oseth-bus-route-planner`
   - Do not auto-route or auto-create other provisional targets until live ids are re-verified: `deliveryfleet-global-tasks`.
   - Otherwise search ClickUp Lists for exact or close matches based on the request and current repo context.
   - If one plausible List is found, use it directly without asking.
   - If multiple plausible Lists are found, ask only which of those Lists should receive the task.
   - If no plausible List exists, create a new List with the project name in the canonical target space/folder instead of a deprecated or provisional container.
7. Resolve assignee if unclear and ensure the task is assigned to the requesting user before any write.
8. Treat tasks assigned to other users as read-only.
9. Verify that the task List exposes exactly these statuses:
    - active: `to do`, `at risk`, `in progress`, `testing`
    - closed: `complete`
10. Read the actual list status configuration from list metadata or the ClickUp UI/API. Do not infer the schema only from currently visible task statuses.
11. If one of the required statuses is missing, do not modify the list automatically; stop and ask the user.

## 2) Enforce write safety

1. Write only on tasks assigned to the requesting user.
2. Do not change due date, priority, assignees, or move to done/closed unless explicitly requested.
3. Use ClickUp `@Display Name` mention syntax when notification intent exists.
4. Keep ClickUp text compact by default using `docs/CLICKUP_COMPACT_TEMPLATES.md`.
5. Prefer fixed templates over narrative prose.

## 3) Keep language and status policy consistent

1. Write chat in English by default.
2. Mirror task language for ClickUp descriptions/comments.
3. Inspect list-specific statuses before any status update (never assume from another list/folder/space).
4. When discussion starts, move the new conversation task to list-specific `in progress` if that status exists.
5. Use `testing` as the only testing status and keep `complete` as the only closed status.
6. Use `in progress` before `testing`, and avoid direct transition to `complete` unless the user explicitly asks.

## 4) Apply timing and transition rules

1. Record discussion start time when task discussion starts.
2. Keep the same start marker if implementation begins later.
3. Record end time when the conversation closes.
4. Calculate elapsed time and add manual `clickup_add_time_entry` using:
   - `start`: now in Europe/Athens
   - `duration`: computed elapsed minutes
5. Avoid moving tasks to done/closed without a corresponding time entry.
6. Move the conversation task to `testing` when the conversation ends, including planning, debugging, read-only, and implementation discussions; use `complete` only when the user explicitly confirms.

## 5) Use these core MCP operations

1. Create task: `clickup_create_task`.
2. Read task: `clickup_get_task`.
3. Discover effective list statuses (via list metadata when available; otherwise infer from scoped `clickup_search` results in the same list).
4. Update status/fields: `clickup_update_task`.
5. Add summary/fallback note comment: `clickup_create_task_comment`.
6. Add elapsed manual entry: `clickup_add_time_entry`.

## 6) Comment size defaults

1. Work-done comments should default to:
   - `Changed:`
   - `Validated:`
   - `Next:`
2. Concern/blocker comments should default to:
   - `Issue:`
   - `Impact:`
   - `Need:`
3. Keep comments brief and direct.
4. Do not restate unchanged context.
