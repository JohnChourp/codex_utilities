# CodeDeliver DynamoDB lambda triggers

> Canonical DynamoDB stream -> lambda trigger mapping for CodeDeliver.
>
> **Single source of truth:** this file must exist only once under:
>
> - `.codex/playbooks/codeliver-dynamodb-lambda-triggers.md`
>
> Rules:
>
> - Do **NOT** copy this file into any repo/lambda/project folder.
> - Do **NOT** create additional `playbooks/` directories elsewhere.
> - If triggers are missing, verify from IaC/code and update **this** canonical file.

## Scope

Canonical mapping of DynamoDB tables -> lambda stream triggers used across:

- projects: codeliver-app, codeliver-panel, codeliver-pos, codeliver-sap
- lambdas: any lambda with "codeliver" in its name

This file is reference data. Do not infer missing triggers; verify from IaC/code and update this file.

## Notation conventions

- If anything is unknown, keep it explicit:
  - `TBD: verify from IaC` (do not guess)
- Lambda triggers are listed per table:
  - `TBD: add mapping` until verified from IaC/code.

## Tables

### codeliver-batches

Lambda triggers: None

### codeliver-customers

Lambda triggers

- codeliver-customers-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-delivery-guys

Lambda triggers

- codeliver-panel-delivery-guys-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-delivery-guys-actions

Lambda triggers

- codeliver-app-delivery-guys-actions-handler: Batch size = 300, Batch window = 3, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-delivery-guys-coordinates

Lambda triggers

- codeliver-delivery-guy-coordinates-stream-ws: Batch size = 1, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}
- codeliver-delivery-guys-coordinates-stream-update-routes-paths: Batch size = 100, Batch window = 3, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-devices

Lambda triggers

- codeliver-panel-devices-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-devices-sockets

Lambda triggers: None

### codeliver-group-zones

Lambda triggers

- codeliver-panel-group-zones-stream-ws: Batch size = 1, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-groups

Lambda triggers

- codeliver-groups-stream-ws: Batch size = 1, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-localserver-logs

Lambda triggers

- codeliver-localserver-logs-handler: Batch size = 300, Batch window = 10, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-localserver-sockets

Lambda triggers: None

### codeliver-localservers

Lambda triggers

- codeliver-delete-localserver-logs-stream: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}
- codeliver-localserver-stream-localserverws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}
- codeliver-localservers-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-notifications

Lambda triggers

- codeliver-notifications-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-panel-sockets

Lambda triggers: None

### codeliver-panel-users

Lambda triggers

- codeliver-panel-users-streams-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-pos-sockets

Lambda triggers: None

### codeliver-pos-users

Lambda triggers

- codeliver-pos-users-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-requests

Lambda triggers

- codeliver-delivery-requests-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-requests-actions

Lambda triggers

- codeliver-delivery-request-actions: Batch size = 1, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-requests-calculations

Lambda triggers

- codeliver-requests-calculations-stream-update-requests: Batch size = 100, Batch window = 3, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-routes

Lambda triggers

- codeliver-routes-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-routes-paths

Lambda triggers

- codeliver-routes-paths-stream-update-routes-requests-paths: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}
- codeliver-routes-paths-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-routes-paths-calculations

Lambda triggers

- codeliver-routes-paths-calculations-stream-update-routes-paths: Batch size = 100, Batch window = 3, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-sap-sockets

Lambda triggers: None

### codeliver-sap-users

Lambda triggers

- codeliver-sap-users-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-store-charges

Lambda triggers

- codeliver-charges-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### codeliver-stores

Lambda triggers

- codeliver-panel-stores-stream-ws: Batch size = 100, Batch window = 0, Retry attempts = -1, Maximum age of record = -1, Split batch on error = false, Concurrent batches per shard = 1, Tumbling window duration = 0, Report batch item failures = false, Filter criteria = {}

### google-api-counter

Lambda triggers: None
