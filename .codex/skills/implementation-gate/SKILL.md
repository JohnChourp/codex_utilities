---
name: implementation-gate
description: Enforce pre-implementation planning, ambiguity cleanup, and explicit go-ahead before coding tasks. Use for implementation work, not simple Q&A or read-only analysis.
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

## 2) Pick a plan mode before writing to ClickUp

1. Default to the smallest useful mode:
   - `small`: low-risk work, no schema/infra changes
   - `medium`: moderate change, limited risk
   - `large/risky`: schema, infra, multi-repo, broad refactor, or unclear/high-risk work
2. Use the compact templates in `docs/CLICKUP_COMPACT_TEMPLATES.md`.
3. Do not write a full implementation plan unless the task is `large/risky`.
4. Do not restate unchanged requirements, repo context, or acceptance criteria.

## 3) Resolve ambiguity and request explicit confirmation

1. Ask clarifying questions only when ambiguity or risk requires it.
2. Paste a short, scannable plan to user.
3. Ask user to review the ClickUp plan and explicitly confirm.
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
2. Run repo-native validation for affected projects when practical.
3. For TypeScript repos with `tsconfig*`, run a separate explicit typecheck in addition to framework build validation; build alone is insufficient evidence for TypeScript health.
4. Prefer an existing repo script such as `npm run typecheck`. Otherwise choose the most specific valid `tsconfig` for the changed runtime instead of defaulting to the root `tsconfig.json`.
5. For Angular/Ionic application repos, prefer `tsconfig.app.json` for application changes and only run spec/test `tsconfig` validation when the repo already has a working test typing setup or an existing spec validation path.
6. Treat the root `tsconfig.json` as a fallback only when it is clearly the correct compile target for the changed area.
7. Example: in `codeliver-panel`, `npm run build` and `ionic build --prod` pass, but `npx tsc -p tsconfig.json --noEmit` is not a safe default because it pulls in current spec-related diagnostics; `npx tsc -p tsconfig.app.json --noEmit` is the correct default app-level typecheck.
8. If unrelated failures block the full suite, run the relevant subset and report limits. If the extra validation reveals limited, clear pre-existing issues, try to fix them in the same session; if it reveals broad unrelated debt, stop and present a separate plan instead of silently expanding scope.
9. Ask user explicitly: push only or deploy.
10. Never push/deploy without explicit confirmation.
