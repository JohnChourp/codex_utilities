# Rollout patterns

Use this reference only after the audit script classifies the target repo.

## Pattern A: `custom-error-stack-ready`
Use this when the repo already preserves throw-site stacks through `CustomError` or equivalent `Error.captureStackTrace` usage.

Typical signals:
- `errors.js` contains `Error.captureStackTrace(...)`
- the repo uses `throw new CustomError(...)`
- `handled_errors.js` already exists

Preferred rollout:
1. Extend `handled_errors.js` with a pure helper like `extractErrorOrigin(error)`.
2. Add a compact line helper like `buildErrorOriginLogLine(error, metadata)`.
3. Update the top-level catch to log one compact string line `kind error_code file line`.
4. Add focused tests for stack parsing and the compact line builder.

Canonical payload:
- one string line: `kind error_code file line`

Known good example:
- `codeliver-routes-merge`

## Pattern B: `handled-error-needs-stack-wrapper`
Use this when handled failures are thrown as plain strings or lightweight markers that do not retain a stack.

Typical signals:
- `throw "some_code"` or `throw 'some_code'`
- handled-error markers exist but there is no stack-carrying helper
- the top-level catch can detect handled errors but cannot recover the throw site

Preferred rollout:
1. Add a stack-carrying handled-error helper in `handled_errors.js`.
2. Convert only the local handled throws required to preserve origin.
3. Reuse the same `extractErrorOrigin(...)` and compact line builder approach.
4. Update the top-level catch and any terminal partial-failure flow that should report the first captured failure.
5. Add focused tests for handled wrapper behavior plus compact line building.

Known good example:
- `codeliver-app-sync-actions`

## Invariants
- Do not change public API/response contracts.
- Keep `ACTION:SLACK_HANDLED_ERROR_HE1=...` unchanged.
- Keep `RequestId SUCCESS` unchanged for handled flows.
- Keep redacted event logging unchanged.
- Keep rollback behavior unchanged.
- Do not emit full stack dumps by default.
- Log only the first useful app origin file and line.
- Do not prefix the compact line with any extra label.

## Handled error normalization checks
After a repo moves to stack-carrying handled errors, audit for these anti-patterns before considering the rollout complete:

- `comment_id = error`
- `hard_error_comment_id = error`
- `first_failed_comment_id = error`
- raw handled-error comparisons such as `error === "someone_else_accepted"`

Preferred fix:
1. Normalize caught handled errors immediately with a helper like `getErrorCode(...)` or `normalizeCommentId(...)`.
2. Use the normalized code in `comment_id`, batch failure summaries, handled-error markers, and Slack-facing handled error reporting.
3. Preserve the original handled code when available. Do not collapse it into a generic fallback like `action_failed`.
