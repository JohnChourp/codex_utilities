---
name: closeout-docs
description: Complete closeout with ClickUp updates, testing transitions, and concise delivery summaries.
---

# Closeout Docs

Use this closeout sequence when work is complete.

## 1) Final ClickUp status and notes

1. Discover the task List statuses before transition (do not assume names from another list).
2. If testing-equivalent exists (e.g. `ΕΛΕΓΧΟΣ`/`ελεγχος`), move task there.
3. If list has explicit `in progress`, ensure implementation work is not skipped directly to `complete`.
4. If list truly has only `to do` + `complete`, ask explicit user confirmation before `complete` and record this fallback in a comment.
5. Add a concise implementation comment covering:
   - repos/files touched
   - key behavior changes
   - tests/validation run
   - follow-ups or known limits

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

## 4) Optional ClickUp Doc step

After implementation and validation, ask whether to create a ClickUp Doc:
1. How-to doc for non-dev users.
2. Technical/development doc for engineers.

When creating a ClickUp Doc, mention and add/share with:
1. `@Seirino`
2. `@Constantinos Adamidis`
3. `@Alexandros Nikolaos Naziris`
