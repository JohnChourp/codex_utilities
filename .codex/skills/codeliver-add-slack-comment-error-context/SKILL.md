---
name: codeliver-add-slack-comment-error-context
description: Apply reusable ACTION:SLACK_COMMENT error-context logging to CodeDeliver Node.js lambdas. Use when a user asks to add or extend Slack debug markers with high-signal IDs (group/store_id/request_id/path_id/route_id/device_id/batch_id/customer_id/timestamp/day/zone_id/server_id/connection/notification_id/user_id/calculation_id/apikey_date) without extra fetches while preserving existing error-handling behavior.
---

# codeliver-add-slack-comment-error-context

## Overview
Apply a consistent `ACTION:SLACK_COMMENT=...` marker on lambda error paths so production debugging has key identifiers in one log line.

Keep behavior stable: do not change business logic, return payloads, handled-error policy flow, or downstream contracts.

## Workflow
1. Read target lambda files first:
- `index.js`
- `handled_errors.js`
- `errors.js`
- `README.md`
- `ROADMAP.md`

2. Locate the terminal error path:
- find `catch (error)` in handler
- keep existing `ACTION:SLACK_HANDLED_ERROR_HE1` and `RequestId SUCCESS` behavior untouched

3. Add reusable helper functions in `index.js` (before handler export):
- parse optional `event.body` safely when JSON
- collect high-signal keys from already-available inputs only
- sanitize values (`|` replacement, whitespace normalization, length cap)

4. Build marker from existing payload/context only (no fetches):
- preferred keys/order:
  - `group`
  - `delivery_guy_id`
  - `store_id`
  - `request_id`
  - `path_id`
  - `route_id`
  - `device_id`
  - `batch_id`
  - `customer_id`
  - `timestamp`
  - `day`
  - `zone_id`
  - `server_id`
  - `connection`
  - `notification_id`
  - `user_id`
  - `calculation_id`
  - `apikey_date`
  - `comment_id`

5. Resolve each key with fallback chain where available:
- `event.<key>`
- `event.body.<key>` (when parseable)
- `event.pathParameters.<key>`
- `event.queryStringParameters.<key>`
- `event.requestContext.authorizer.<key>`
- `event.requestContext.authorizer.claims.<key>`
- request id fallback: `event.requestContext.requestId` then `context.awsRequestId`
- connection fallback: include `connection`, `connection_id`, `connectionId`, `requestContext.connectionId`
- apikey date fallback: include `apikey-date`, `apikey_date`, and lower-cased header variants

6. Emit marker inside `catch` before handled/unhandled branching:
- `console.log(buildSlackComment(...))` only when payload is non-empty
- always append `comment_id` to marker payload

7. Keep sensitive-data policy:
- never add password/token/cookie raw values to marker
- do not dump full bodies into `ACTION:SLACK_COMMENT`

8. Update docs when behavior changes:
- add short note in lambda `README.md` (error logging/diagnostics)
- update `ROADMAP.md` `Completed` with the new capability

9. Validate:
- run `npm test` in lambda root
- run `rg -n "ACTION:SLACK_COMMENT|buildSlackComment|comment_id" index.js README.md ROADMAP.md`

## Guardrails
- Do not add DB/API calls for missing identifiers.
- Do not alter success/failure payload schema.
- Do not remove existing handled-error markers.
- Prefer minimal diffs and style consistency with lambda.
- If marker already exists, extend existing logic instead of duplicating helpers.

## Output Pattern
Target marker format:
- `ACTION:SLACK_COMMENT=key1:value1|key2:value2|...|comment_id:<code>`

Only include keys with meaningful values.
