---
name: clickup-task-lifecycle
description: Manage ClickUp task handling from discovery through execution gating and status hygiene. Use when a request involves ClickUp task lookup, task ownership checks, status changes, time tracking rules, language mirroring, or safe task updates.
---

# Clickup Task Lifecycle

Apply this workflow in order.

## 1) Validate task and ownership

1. Ask for an existing ClickUp task link/ID before any ClickUp write operation.
2. Create a task only when no relevant task exists, and ask which List to use.
3. Resolve assignee if unclear and ensure the task is assigned to the requesting user before any write.
4. Treat tasks assigned to other users as read-only.

## 2) Enforce write safety

1. Write only on tasks assigned to the requesting user.
2. Do not change due date, priority, assignees, or move to done/closed unless explicitly requested.
3. Use ClickUp `@Display Name` mention syntax when notification intent exists.

## 3) Keep language and status policy consistent

1. Write chat in English by default.
2. Mirror task language for ClickUp descriptions/comments.
3. Inspect list-specific statuses before any status update (never assume from another list/folder/space).
4. When discussion starts, move the task to list-specific `in progress` if that status exists.
5. If list has `in progress` and testing-equivalent statuses, use them and avoid direct transition to `complete`.
6. Use `ΕΛΕΓΧΟΣ`/`ελεγχος` as testing-equivalent when list conventions match.
7. If list appears to have only `to do` + `complete`, ask explicit user confirmation before `complete`, and document that fallback in a task comment.

## 4) Apply timing and transition rules

1. Record discussion start time when task discussion starts.
2. Keep the same start marker if implementation begins later.
3. Record end time when work is complete.
4. Calculate elapsed time and add manual `clickup_add_time_entry` using:
   - `start`: now in Europe/Athens
   - `duration`: computed elapsed minutes
5. Avoid moving tasks to done/closed without a corresponding time entry.
6. Prefer moving completed implementation work to testing-equivalent; use `complete` only when list flow requires it and user explicitly confirms.

## 5) Use these core MCP operations

1. Discover task: `clickup_search` (`asset_types=["task"]`).
2. Read task: `clickup_get_task`.
3. Discover effective list statuses (via list metadata when available; otherwise infer from scoped `clickup_search` results in the same list).
4. Update status/fields: `clickup_update_task`.
5. Add summary/fallback note comment: `clickup_create_task_comment`.
6. Add elapsed manual entry: `clickup_add_time_entry`.
