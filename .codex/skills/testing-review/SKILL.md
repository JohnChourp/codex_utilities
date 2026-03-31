---
name: testing-review
description: perform an independent post-implementation review for code changes that are already complete and in testing or qa. use when the user wants a fresh review pass on a branch, diff, or task before signoff, with optional user-approved live validation in dev or stage. apply relevant repo style skills, collect evidence first, and report findings by severity with file references.
---

# Testing Review

Use this skill to run a fresh, independent review after implementation is already complete.

## 1) Resolve missing context

Confirm only what is needed for the requested review.

Required for most reviews:
1. Repo path under review.
2. Review branch and intended base branch.

Required only when relevant:
3. ClickUp task link/ID if task status, ownership, or writeback matters.
4. Review mode:
   - `review only`
   - `review + live tests`
5. Allowed environment only when live testing is requested:
   - `dev`
   - `stage`
   - `prod` only with explicit approval

If required items are missing, ask only for the missing items.

## 2) Session rules

1. Prefer a new Codex session for the review so the pass is independent from the implementation session.
2. Default to read-only review behavior.
3. Do not edit code, push, deploy, or change ClickUp fields unless the user explicitly switches from review into fix mode.
4. When the user requests ClickUp writes, use `clickup-task-lifecycle` if available and keep comments compact.

## 3) Verify task state when ClickUp context is provided

1. Read the task and confirm it is assigned to the requesting user before any write.
2. Confirm the task is already in a testing-equivalent status for its List.
3. If the task is not in testing, report that clearly and continue review only if the user still wants it.
4. If you need to write a review note or testing result back to ClickUp, mirror the task language.
5. Treat `testing-equivalent` as a status that clearly means implementation is complete and validation or review is the current stage. If the List uses custom statuses, infer the closest equivalent from status names or task history and state the assumption.
6. If `clickup-task-lifecycle` is unavailable, continue with the code review and report that ClickUp verification or writeback could not be completed through the expected workflow.

## 4) Gather review evidence first

Use the helper script in this skill when possible:

```bash
skills/testing-review/scripts/collect_review_context.sh --base <base-branch>
```

If the helper script is unavailable or fails, collect equivalent evidence manually by inspecting the base-branch diff, changed files, impacted tests, and any available validation artifacts.

Then inspect:
1. Changed files and diff summary.
2. Relevant docs and source-of-truth paths.
3. Targeted implementation files, tests, and related contracts.
4. Existing validation evidence from the branch when available.

## 5) Compose with repo-specific review skills

After inspecting the changed files, load the most relevant repo style skills for evaluation.

1. Use `front-end-code-style` when the touched files are primarily Angular/Ionic frontend code such as `mobileorder` or `dmpanel`.
2. Use `back-end-lambda-code-style` when the touched files are primarily lambda/backend code such as `dm_lambda_functions/paneldelivery`.
3. Use both when the change spans frontend and backend concerns.
4. Use `implementation-gate` only when the user wants plan, scope, or release-process compliance checked.
5. Use `closeout-docs` only when the user asks to record a review outcome back after the review is complete.

## 6) Review workflow

1. Read the diff against the confirmed base branch.
2. Review the changed code with a code-review mindset:
   - bugs
   - regressions
   - contract mismatches
   - missing validation
   - missing or weak tests
   - style/pattern violations relative to the target repo
3. Run targeted local checks when available:
   - focused tests
   - lint/typecheck/build for the touched area
4. Keep findings-first reporting:
   - severity ordered
   - file references
   - brief residual risks if no findings are found

## 7) Severity levels

- `critical`: likely production breakage, security issue, data loss, or release blocker
- `high`: strong regression risk or contract mismatch
- `medium`: important correctness, validation, or maintainability weakness
- `low`: non-blocking style, clarity, or minor robustness issue

## 8) Optional live testing branch

Run live tests only when the user explicitly asks for them.

Before live testing, confirm:
1. Allowed environment.
2. Allowed credentials/test accounts or seeded data.
3. Whether browser automation is acceptable.

Execution rules:
1. Prefer the repo's existing e2e or smoke-test framework first.
2. Use Puppeteer or Playwright only when browser-driven validation is needed and no better repo-native path exists.
3. Avoid production testing unless the user explicitly approves it.
4. Keep tests scoped to the changed behavior.
5. Record exact steps, environment, and observed outcomes.
6. Treat live testing as validation, not as permission to mutate data broadly.
7. Do not broaden test scope beyond the changed behavior unless the user explicitly asks for exploratory regression coverage.

## 9) Review output

Use this default structure unless the user asks for a different format.

### Verdict

One-line overall assessment.

### Findings

List findings in severity order. For each finding include:
- severity
- short title
- file reference(s)
- why it matters
- recommended fix

### Open questions or assumptions

Only include unresolved items that affect confidence.

### Change summary

Brief summary of what changed.

### Residual risk or testing gaps

If no findings exist, say so explicitly and note any unverified paths or validation gaps.

## 10) Non-goals

Do not:
- re-implement the task during review
- perform broad exploratory QA unless requested
- rewrite ClickUp task history into long summaries
- treat missing context as permission to guess silently when the assumption affects findings

## 11) Optional ClickUp review note

If the user asks to write back to ClickUp, keep it brief:

```md
Reviewed: <1 line>
Found: <1 line>
Tested: <1 line>
Next: <1 line>
```

Do not move the task out of testing unless the user explicitly asks.
