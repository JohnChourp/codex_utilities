---
name: codeliver-lambda-error-origin-rollout
description: Audit a CodeDeliver Node.js lambda repo and apply the canonical origin-log rollout so handled, custom, and classic errors emit one compact `kind error_code file line` log line without changing response contracts.
---

# codeliver-lambda-error-origin-rollout

## Overview
Use this skill when the user wants a specific CodeDeliver lambda repo to start logging where an error originated as one compact line `kind error_code file line` for handled, custom, or classic errors.

The skill audits the target repo, chooses the right rollout pattern, applies the minimal code changes, adds focused tests, and validates the repo without changing public response behavior.

## Fast path
- If the user already gave a repo path, proceed without extra questions.
- Start with `python3 scripts/audit_error_origin_repo.py --repo /abs/path/to/repo`.
- Read only the files suggested by the audit first.
- Preserve existing response contracts, `ACTION:SLACK_HANDLED_ERROR_HE1=...`, `RequestId SUCCESS`, redacted event logging, and rollback behavior.
- Default validation is the repo's `npm test`. If that is missing or fails for unrelated reasons, run the narrowest relevant test command and report the blocker.

## Workflow
1. Run `scripts/audit_error_origin_repo.py` on the target repo.
2. If the pattern is `already-instrumented`, inspect the current origin log line and only normalize if it deviates from the canonical schema.
- Even when the repo is already instrumented, audit for handled-error normalization bugs such as `comment_id = error` or raw `error === "code"` comparisons after a move to `HandledError`.
- If those anti-patterns exist, fix them before stopping so specific handled codes do not collapse into generic fallbacks like `action_failed`.
3. If the pattern is `custom-error-stack-ready`:
- extend `handled_errors.js` with a pure stack parser helper such as `extractErrorOrigin(error)`
- add a compact line builder such as `buildErrorOriginLogLine(...)`
- update the top-level catch to log the one-line string directly
- add unit tests for stack parsing and compact line building
4. If the pattern is `handled-error-needs-stack-wrapper`:
- add a stack-carrying handled-error helper in `handled_errors.js`
- replace local plain-string handled throws only where needed so origin is preserved
- then add the same compact origin logging and focused tests
5. If the pattern is `manual-review`, inspect `errors.js`, `handled_errors.js`, and the main catch flow before editing anything. Adapt to repo-local conventions instead of forcing a new abstraction.
6. Run validation.
7. Report the detected pattern, changed files, and validation result.

## Canonical log schema
The origin log should be a single string line:
- `kind error_code file line`

## Guardrails
- Never change API/body contracts only to improve observability.
- Keep existing `ACTION:SLACK_HANDLED_ERROR_HE1=...` logging untouched.
- Keep `RequestId SUCCESS` behavior untouched for handled flows.
- Keep any redaction/sanitization logic untouched.
- Do not add full stack dumps by default. Log only the first useful app origin file and line.
- Do not prefix the compact line with any extra label.
- Do not rewrite all `throw new CustomError(...)` call sites when `Error.captureStackTrace` already preserves the source.
- For repos that throw plain strings for handled failures, convert only the local handled-error throws required to retain origin.
- After a repo adopts `HandledError`, never assign caught errors directly to `comment_id`, `hard_error_comment_id`, or similar code fields. Normalize them first via a helper such as `getErrorCode(...)` or `normalizeCommentId(...)`.
- Never compare caught handled errors as raw objects (`error === "some_code"`). Compare normalized codes instead.
- Never let a specific handled code collapse into a generic fallback like `action_failed` if the original code is still recoverable.
- Prefer repo-local naming and style over forcing a global abstraction.

## Pattern selection
- Read `references/rollout-patterns.md` when the audit reports `custom-error-stack-ready` or `handled-error-needs-stack-wrapper`.
- If the repo already has origin logging, compare its line format against the canonical schema before deciding whether to patch it.
- If the repo does not contain `handled_errors.js`, do not invent one immediately. First inspect the existing error helpers and catch flow.

## Resources
### scripts/audit_error_origin_repo.py
Static repo auditor that detects:
- candidate handler files
- `handled_errors.js` / `errors.js`
- `CustomError` stack support
- plain string handled throws
- whether compact origin logging already exists
- handled-error normalization anti-patterns such as `comment_id = error` and raw `error === "code"` comparisons
- suggested rollout pattern

Usage:
- `python3 scripts/audit_error_origin_repo.py --repo /abs/path/to/repo`
- `python3 scripts/audit_error_origin_repo.py --repo /abs/path/to/repo --format text`

### references/rollout-patterns.md
Compact reference for the two rollout patterns already proven in:
- `codeliver-routes-merge`
- `codeliver-app-sync-actions`

## Example prompts
- `Run codeliver-lambda-error-origin-rollout for ~/Downloads/lambdas/codeliver_all/codeliver-routes-merge`
- `Audit whether ~/Downloads/lambdas/codeliver_all/codeliver-app-sync-actions already has canonical compact origin logging`
- `Apply the error-origin rollout to this CodeDeliver lambda repo and keep the response contract unchanged`
