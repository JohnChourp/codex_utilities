---
name: back-end-lambda-code-style
description: Apply backend coding style for Node.js lambdas in `dm_lambda_functions/paneldelivery`. Use when implementing or refactoring paneldelivery lambdas and you need consistent deliveryManager module usage, lodash and Bluebird iteration style, DynamoDB params patterns, validation/error handling, and API response conventions.
---

# Back End Lambda Code Style

Apply this style baseline before and during backend edits in `dm_lambda_functions/paneldelivery`.

## 1) Runtime and module baseline

1. Keep CommonJS style (`require`, `module.exports`/`exports.handler`) and `"use strict"` when the file already uses it.
2. Mirror the AWS SDK style of the target lambda:
   - keep `aws-sdk` v2 + `new AWS.DynamoDB.DocumentClient()` in v2 files.
   - keep `@aws-sdk/*` v3 command/client style in v3 files.
3. Do not migrate v2 to v3 (or vice versa) unless explicitly requested.
4. Keep region conventions aligned with nearby lambdas (typically `eu-west-1` in v2 files).
5. Reuse existing `@deliverymanager/*` helpers in that lambda family (`lambda_invoke`, `recursive_fns`, `prune_fns`, `s3_fns`).

## 2) Dependencies and collection style

1. Prefer:
   - `const _ = require("lodash");`
   - `const Promise = require("bluebird");`
2. Prefer lodash collection helpers (`_.each`, `_.map`, `_.filter`, `_.find`, `_.pick`, `_.omit`, `_.merge`, `_.cloneDeep`) over custom loop logic.
3. Prefer Bluebird iteration patterns for async collections:
   - `Promise.map(...)` for parallel work
   - `Promise.mapSeries(...)` for ordered updates
   - set explicit `concurrency` when required by workload
4. Avoid introducing new `for`/`while` loops in lambdas; keep the existing functional iteration style.

## 3) Handler, validation, and permissions

1. Define `CustomError` in the handler and throw stable string error codes.
2. Parse authorizer/body defensively and validate required params early.
3. Keep early-return/early-throw guard style for auth and required fields.
4. For privileged actions, keep permission checks through `paneldelivery_users` and existing permission keys.
5. Preserve existing error code vocabulary (`unauthorized`, `invalid_params`, `user_does_not_exist`, etc.).

## 4) DynamoDB query/update patterns

1. Build explicit params objects using established fields:
   - `TableName`, `IndexName`, `KeyConditionExpression`
   - `ExpressionAttributeNames`, `ExpressionAttributeValues`
   - `UpdateExpression`, `ConditionExpression`, `ProjectionExpression`
2. When updating dynamic fields, compose `UpdateExpression` incrementally with matching expression maps.
3. Keep table/index/key naming and composed keys exactly aligned with existing contracts.
4. Use `prune_null`/`prune_empty` consistently where existing lambdas sanitize reads/writes.
5. Use recursive query helpers for paginated reads when the surrounding lambdas already rely on them.

## 5) Lambda invoke and downstream handling

1. Reuse the existing invoke helper (`lambda_invoke` or `lambda_invoke_v3`) used by nearby lambdas.
2. Keep invocation alias/type style used in the file (`$LATEST`, `RequestResponse`, etc.).
3. Normalize invoked lambda responses by parsing `response.body` and checking `success`.
4. Bubble downstream failures via `CustomError` with existing fallback behavior (`comment_id`/`comments` then `"classic_error"`).

## 6) Logging and response contract

1. Keep existing observability markers where expected (for example `RequestId SUCCESS`).
2. Avoid logging sensitive values (tokens, passwords, secrets) in new code paths.
3. Preserve API response envelope conventions:
   - `statusCode: 200`
   - JSON body with `success: true/false`
   - error key style used by that lambda (`comment_id` and/or `comments`)
   - fallback `"classic_error"` for unhandled failures

## 7) Scope rules

1. Keep edits minimal and localized to the requested behavior.
2. Preserve backward compatibility for payload keys (including snake_case backend keys).
3. Follow the quote style, formatting, and naming already present in each touched lambda file.
