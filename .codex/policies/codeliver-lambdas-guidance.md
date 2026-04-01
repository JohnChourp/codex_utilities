# CodeDeliver Lambdas Guidance (On-Demand)

Use this policy file when the task is lambda-first or lambda-only.

## Local paths and assumptions

- Assume lambda code is already downloaded under:
  - `/home/dm-soft-1/Downloads/lambdas`
- Assume lambdas are connected with projects via shared models, APIs, auth flows, events, queues, tables, and routes.
- If local paths are not accessible in the current execution environment, state it explicitly and provide exact commands for the user to run locally and paste results back.

## Lambda-first scanning policy

- Lambda source of truth:
  - Lambda names, handlers, event shapes, IAM policies, env vars
  - Shared libs/utilities used across lambdas
  - Cross-lambda references (SNS/SQS/EventBridge, DynamoDB, API Gateway routes)
- Prefer `rg` and `find` for discovery:
  - `rg "delivery guy|courier|driver|device" /home/dm-soft-1/Downloads/lambdas`
  - `rg "httpApi|httpApiEvent|events:|path:|method:|handler:" /home/dm-soft-1/Downloads/lambdas`
  - `find /home/dm-soft-1/Downloads/lambdas -maxdepth 3 -type f -name "README.md" -o -name "package.json" -o -name "template.y*ml" -o -name "serverless.y*ml"`

## Downstream expansion (mandatory)

- For every identified lambda, expand one hop downstream:
  - Find publishes:
    - `rg -n "publish\\(|SendMessageCommand|PutEventsCommand|EventBridge|SNS|SQS" /home/dm-soft-1/Downloads/lambdas`
  - Find data stores:
    - `rg -n "DynamoDB|DocumentClient|PutCommand|UpdateCommand|QueryCommand|ScanCommand|S3" /home/dm-soft-1/Downloads/lambdas`
  - Find consumers of same resources:
    - `rg -n "<topic-or-queue-or-event-or-table-name>" /home/dm-soft-1/Downloads/lambdas /home/dm-soft-1/Downloads/projects`

## Debugging mindset for lambda flows

- Assume bug impact can span multiple components.
- Identify likely entrypoints (handler, queue consumer, scheduled job, API route).
- Validate integration edges from code/IaC (never guess resource names, keys, env vars, IAM).
- Keep fixes minimal and style-consistent.

## Mandatory validation before closeout

- For every changed JavaScript file inside `$HOME/Downloads/lambdas`, run `npx eslint <changed-file.js>` from within the lambda tree before considering the task done.
- Use the shared config discovered from `$HOME/Downloads/lambdas/eslint.config.mjs`; do not skip lint just because `node -c` or the package test script passes.
- Treat `no-undef`, removed helper references, and similar static-analysis failures as required fixes, not optional warnings.
- Keep the repo's lightweight validation too, such as `npm test` or the package `test` script, when it is available and relevant to the touched files.

## Playbooks and refs usage

- Never guess DynamoDB keys/indexes; use:
  - `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md`
- For item attribute shapes (requests/routes/route_paths etc.):
  - `.codex/playbooks/codeliver-dynamodb-item-examples.md`
- For frontend-to-lambda call confirmation:
  - `.codex/refs/codeliver-*-lambdas.md`
