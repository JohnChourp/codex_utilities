---
name: clickup-task-lifecycle
description: Manage ClickUp task handling from discovery through execution gating and status hygiene. Use when a request involves ClickUp task lookup, task ownership checks, status changes, time tracking rules, language mirroring, or safe task updates.
---

# Clickup Task Lifecycle

Apply this workflow in order.

## 1) Validate task and ownership

1. Treat every new discussion, actionable request, work item, bug, change, follow-up, or implementation discussion as something that must be tracked in ClickUp, even if the user did not explicitly ask to create a task.
2. Search for an existing strongly matching task first.
3. If the first or strongest strong match has `created_at` within the last 12 hours, reuse it.
4. If only strong matches older than 12 hours exist, do not write to those stale tasks. Create a new task titled `[duplicate] {matched task title}` using the first or strongest stale match title.
5. If no relevant task exists, create one by default without asking whether a task should be created.
6. Compose the task title automatically from the request using a short, concrete implementation title.
7. Compose the task description automatically with the request context, current repo/folder, scope, and requested outcome.
8. Apply routing in this order:
   - if the active workflow or local policy provides deterministic routing for the repo or project family, use it directly
   - otherwise search ClickUp Lists for exact or close matches based on the request and current repo context
   - if one plausible List is found, use it directly without asking
   - if multiple plausible Lists are found, ask only which of those Lists should receive the task
   - if no plausible List exists, create a new List with the project name in the workspace's default project folder or space
9. Resolve assignee if unclear and ensure the task is assigned to the requesting user before any write.
10. Treat tasks assigned to other users as read-only.
11. Verify that the task List exposes exactly these statuses:
    - active: `to do`, `at risk`, `in progress`, `testing`
    - closed: `complete`
12. Read the actual list status configuration from list metadata or the ClickUp UI/API. Do not infer the schema only from currently visible task statuses.
13. If one of the required statuses is missing, do not modify the list automatically; stop and ask the user.

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
4. When discussion starts, move the task to list-specific `in progress` if that status exists.
5. Use `testing` as the only testing status and keep `complete` as the only closed status.
6. Use `in progress` before `testing`, and avoid direct transition to `complete` unless the user explicitly asks.

## 4) Apply timing and transition rules

1. Record discussion start time when task discussion starts.
2. Keep the same start marker if implementation begins later.
3. Record end time when work is complete.
4. Calculate elapsed time and add manual `clickup_add_time_entry` using:
   - `start`: now in Europe/Athens
   - `duration`: computed elapsed minutes
5. Avoid moving tasks to done/closed without a corresponding time entry.
6. Prefer moving completed implementation work to `testing`; use `complete` only when the user explicitly confirms.

## 5) Use these core MCP operations

1. Discover task: `clickup_search` (`asset_types=["task"]`).
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
