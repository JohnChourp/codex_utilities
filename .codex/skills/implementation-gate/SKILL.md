---
name: implementation-gate
description: Enforce pre-implementation planning, ambiguity cleanup, and explicit go-ahead before coding. Use when a task needs architecture scouting, concrete implementation planning, user confirmation, and controlled transition into active development.
---

# Implementation Gate

Follow this gate before coding.

## 1) Scout architecture and existing paths

1. Read nearby docs first: `ARCHITECTURE.md`, `README.md`, `docs/`, ADRs.
2. Identify services/repos involved and source of truth.
3. Use `rg` to locate contracts/fields and adjacent implementations.
4. Decide persisted vs derived values:
   - Persist values that must survive refresh/devices or historical views.
   - Compute UI-only derived values when safe.

## 2) Write implementation plan into ClickUp description

Include all:
1. Goal and scope (`frontend`, `backend`, `both`).
2. Data model changes (type/nullability).
3. Source-of-truth writer/reader.
4. Contract changes (API/events/websocket).
5. UX behavior and edge cases.
6. i18n keys and language coverage.
7. Acceptance criteria.
8. Test plan (automated + manual).
9. Release plan (push-only vs deploy and environments).

## 3) Resolve ambiguity and request explicit confirmation

1. Ask clarifying questions before implementation.
2. Paste a short, scannable plan to user.
3. Ask user to review ClickUp plan and explicitly confirm.
4. Assume delivery mode `local changes only` and the current checked-out branch unless the user explicitly overrides either one.
5. Do not ask for delivery mode or target branch again when the user has not overridden those defaults.
6. Do not implement before explicit go-ahead (`proceed` or equivalent).

## 4) Transition to implementation only after go-ahead

1. Move task to in-progress equivalent.
2. Start manual time tracking policy for the task timeline.
3. Create or switch branches only when the user explicitly requests a different branch or `PR-ready` flow.
4. Implement minimal, scoped changes only.
5. Preserve existing coding patterns and compatibility.

## 5) Validation and release gate

1. Run focused tests first for changed modules.
2. Run build/typecheck/lint for affected projects when practical.
3. If unrelated failures block full suite, run relevant subset and report limits.
4. Ask user explicitly: push only or deploy.
5. Never push/deploy without explicit confirmation.
