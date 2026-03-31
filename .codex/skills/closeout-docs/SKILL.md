---
name: closeout-docs
description: Complete end-of-task closeout with ClickUp updates, testing-status transitions, and minimal brief summaries. Use when implementation or discussion work is done and closeout artifacts must be recorded.
---

# Closeout Docs

Use this closeout sequence when work is complete.

## 1) Final ClickUp status and notes

1. Discover the task List statuses before transition (do not assume names from another list).
2. Move the task to `testing` and keep `complete` as the only closed status.
3. If one of the required statuses is missing, do not modify the list automatically; stop and ask the user.
4. Ensure implementation work is not skipped directly from `in progress` to `complete`.
5. Add the smallest useful implementation comment using:
   - `Changed:`
   - `Validated:`
   - `Next:`
6. When follow-ups or limits materially affect the handoff, append one short extra line after `Next:` instead of replacing the compact format.

## 2) Final completion note

1. When task is completed/closed, add a very short non-technical comment.
2. Tag `@Ανέστης Δόμβρης` in that final note.
3. Apply this only on tasks assigned to the requesting user.
4. Ensure corresponding time entry exists before any done/complete/closed transition.

## 3) User-facing summary output

Provide a concise summary with:
1. What changed (repo and key files).
2. What was pushed (if anything).
3. What was deployed (if anything, and where).
4. What ClickUp updates were made (status/time entry/comment).
5. Which ClickUp List the task belongs to.

## 4) Concern comment fallback

Use this when work is blocked or risky:
1. `Issue:`
2. `Impact:`
3. `Need:`

## 5) Optional ClickUp Doc step

After implementation and validation, ask whether to create a ClickUp Doc:
1. How-to doc for non-dev users.
2. Technical/development doc for engineers.

When creating a ClickUp Doc, mention and add/share with:
1. `@Seirino`
2. `@Constantinos Adamidis`
3. `@Alexandros Nikolaos Naziris`
