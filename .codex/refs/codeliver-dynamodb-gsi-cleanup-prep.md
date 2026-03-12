# CodeDeliver DynamoDB GSI cleanup prep

Scope:

- Stage + Prod only
- Lockstep policy across environments
- No index deletion in this step

Goal:

- Fix the canonical inventory first
- Consolidate local code and local IaC evidence
- Classify GSI candidates into `keep`, `delete-ready`, or `blocked-needs-more-proof`
- Prepare a safe delete order with rollback/watch guidance

## Canonical inventory status

Current state:

- The canonical playbook already contains `codeliver-panel-sockets -> store_id-expire-index`.
- Current-account live audit on March 12, 2026 also confirms the pair is present in DynamoDB.

Runtime evidence:

- `lambdas/codeliver_all/codeliver-panel-disconnect-user/dynamo_db_functions.js`
- Query path:
  - `TableName: "codeliver-panel-sockets"`
  - `IndexName: "store_id-expire-index"`

Status:

- `keep`

## Source-of-truth findings

Local inspection summary:

- Lambda-local `cloudformation/stack.json` files under `lambdas/codeliver_all/*/cloudformation/` are lambda deployment templates only.
- No inspected local lambda template defines DynamoDB tables or `GlobalSecondaryIndexes`.
- A second pass under `/home/dm-soft-1/Downloads/projects` found no local IaC source-of-truth for the target DynamoDB tables/indexes in the inspected repositories.
- Candidate index hits outside lambdas were documentation-only in the inspected project repos.

Operational implication:

- DynamoDB table/index IaC source-of-truth is not available in the inspected local repositories.
- Stage/Prod metric verification must remain manual until the infra repo or AWS-side schema source is identified.

## Lockstep audit buckets

### confirmed-active

- `codeliver-panel-sockets -> store_id-expire-index`
- `codeliver-notifications -> group_delivery_guy_id-timestamp-index`
- `codeliver-notifications -> mobile-type_timestamp-index-all`
- `codeliver-notifications -> notification_id-index`
- `codeliver-sap-sockets -> store_id-expire-index`

### confirmed-unused

These had no runtime hits in `codeliver_all`, no hits in actual app code under `/home/dm-soft-1/Downloads/projects/codeliver`, and no local IaC evidence in the inspected repos.

| Table | Index | Status | Notes |
| --- | --- | --- | --- |
| `codeliver-devices-sockets` | `group_delivery_guy_id-expire-index` | `delete-ready` | No runtime or project-code evidence found |
| `codeliver-localservers` | `group-server_id-index` | `delete-ready` | Current localserver readers use PK/Scan paths |
| `codeliver-notifications` | `route_id-delivery_guy_id-index` | `delete-ready` | No reader/writer path uses it |
| `codeliver-notifications` | `store_id_reason-timestamp-index` | `delete-ready` | No local reporting/search flow found |
| `codeliver-notifications` | `store_id_type-timestamp-index` | `delete-ready` | No local reporting/search flow found |
| `codeliver-notifications` | `store_id_type_reason-timestamp-index` | `delete-ready` | No local reporting/search flow found |
| `codeliver-panel-sockets` | `sessionID-expire-index` | `delete-ready` | No session-based query path found |
| `codeliver-pos-sockets` | `sessionID-expire-index` | `delete-ready` | No session-based query path found |
| `codeliver-requests` | `group_mobile-timestamp-index` | `delete-ready` | No runtime lookup found |
| `codeliver-requests` | `sap-timestamp-index` | `delete-ready` | No runtime lookup found |
| `codeliver-requests` | `store_Id-request_id-index` | `delete-ready` | No runtime lookup found |
| `codeliver-sap-sockets` | `sessionID-expire-index` | `delete-ready` | No session-based query path found |
| `codeliver-store-charges` | `store_id_reason-timestamp-index` | `delete-ready` | No reader/search flow found |
| `codeliver-store-charges` | `store_id_type-timestamp-index` | `delete-ready` | No reader/search flow found |
| `codeliver-store-charges` | `store_id_type_reason-timestamp-index` | `delete-ready` | No reader/search flow found |
| `codeliver-stores` | `partner_id-store_id-index` | `delete-ready` | No partner-based lookup found |
| `codeliver-stores` | `primary_local_server_reset-store_id-index` | `delete-ready` | No runtime reset lookup found |

### unused-but-needs-env-confirmation

These had no confirmed runtime usage locally, but they are plausible access patterns or sit on tables where hidden ops/reporting usage is more likely.

| Table | Index | Status | Why blocked |
| --- | --- | --- | --- |
| `codeliver-notifications` | `group-timestamp-index` | `blocked-needs-more-proof` | Current notifications flows use PK query, `group_delivery_guy_id-timestamp-index`, `mobile-type_timestamp-index-all`, and `notification_id-index`, but timeline/reporting usage is still plausible |
| `codeliver-notifications` | `store_id-timestamp-index` | `blocked-needs-more-proof` | No local runtime hit on the notifications table, but the access pattern is plausible for store-scoped notification history |
| `codeliver-store-charges` | `store_id-timestamp-index` | `blocked-needs-more-proof` | Current local readers use PK-by-group, but store-scoped reporting/search usage remains plausible |
| `codeliver-sap-sockets` | `group-expire-index` | `blocked-needs-more-proof` | Current readers mostly use `Scan` or `store_id-expire-index`; this may be env drift or latent legacy usage |

## Deep audit notes for blocked candidates

### `codeliver-notifications -> group-timestamp-index`

Observed local notifications usage:

- Writers:
  - `codeliver-apifon`
  - `codeliver-apifon-webhook`
  - `codeliver-send-firebase-push-notification`
  - `codeliver-app-delivery-guys-actions-handler`
- Readers:
  - `codeliver-sms-sqs-dispatcher`
  - `codeliver-send-sms-gateway`
  - `codeliver-app-fetch-notifications`
  - `codeliver-panel-search-notifications`
- Stream consumer:
  - `codeliver-notifications-stream-ws`

Local conclusion:

- No local reader uses `group-timestamp-index`.
- Keep blocked until Stage + Prod metrics confirm zero usage and external ops/reporting tooling is checked.

### `codeliver-notifications -> store_id-timestamp-index`

Local conclusion:

- No local reader/writer in the inspected repos uses this pair on the notifications table.
- The index name collides with active indexes on other tables, so plain string hits are not enough proof.
- Keep blocked until AWS-side metrics and external tooling checks are complete.

### `codeliver-store-charges -> store_id-timestamp-index`

Local conclusion:

- Local readers found:
  - `codeliver-panel-fetch-charges`
  - `codeliver-panel-search-group-charges`
  - `codeliver-charge-service`
- Those flows use PK/group access locally, not `store_id-timestamp-index`.
- Keep blocked until Stage + Prod metrics confirm zero usage.

### `codeliver-sap-sockets -> group-expire-index`

Local conclusion:

- Current local readers mostly use:
  - `Scan` on `codeliver-sap-sockets`
  - `store_id-expire-index` in `codeliver-sap-ws-cloud-command-response`
- No local `Query` on `group-expire-index` was found.
- Keep blocked until metrics and environment-level schema checks confirm it is unused in both Stage and Prod.

## Cleanup order

Delete waves should remain table-based and lockstep after verification:

1. `codeliver-panel-sockets`, `codeliver-pos-sockets`, `codeliver-sap-sockets`
2. `codeliver-localservers`, `codeliver-devices-sockets`, `codeliver-stores`
3. `codeliver-notifications`, `codeliver-store-charges`
4. `codeliver-requests`

## Wave 1 post-delete watchlists

### `codeliver-panel-sockets`

Delete candidate:

- `sessionID-expire-index`

Watch these lambdas for `ValidationException` spikes:

- `codeliver-panel-disconnect-user`
- `codeliver-panel-fetch-users-sockets`
- `codeliver-panel-send-user-cloud-command`
- `codeliver-panel-ws-cloud-command-response`
- `codeliver-sockets-kinesis-consumer`
- panel fan-out stream lambdas that query `group-expire-index`

### `codeliver-pos-sockets`

Delete candidate:

- `sessionID-expire-index`

Watch these lambdas for `ValidationException` spikes:

- `codeliver-panel-fetch-pos-users-sockets`
- `codeliver-sap-fetch-pos-users-sockets`
- `codeliver-pos-ws-cloud-command-response`
- `codeliver-routes-stream-ws`
- `codeliver-routes-paths-stream-ws`
- `codeliver-serverless-check-store-online`
- `codeliver-sockets-kinesis-consumer`

### `codeliver-sap-sockets`

Delete candidate:

- `sessionID-expire-index`

Watch these lambdas for `ValidationException` spikes:

- `codeliver-sap-ws-cloud-command-response`
- `codeliver-sap-users-stream-ws`
- `codeliver-sap-fetch-admin-sockets`
- `codeliver-groups-stream-ws`
- `codeliver-panel-stores-stream-ws`
- `codeliver-sockets-kinesis-consumer`

## Manual Stage/Prod verification commands

Use the same commands for both Stage and Prod. Change the AWS profile, start/end dates, table name, and index name as needed.

### Metric: `ConsumedReadCapacityUnits`

```bash
aws cloudwatch get-metric-statistics \
  --profile <AWS_PROFILE> \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=<TABLE_NAME> Name=GlobalSecondaryIndexName,Value=<INDEX_NAME> \
  --start-time 2026-03-01T00:00:00Z \
  --end-time 2026-03-12T00:00:00Z \
  --period 86400 \
  --statistics Sum \
  --region eu-west-1
```

### Metric: `SuccessfulRequestLatency`

```bash
aws cloudwatch get-metric-statistics \
  --profile <AWS_PROFILE> \
  --namespace AWS/DynamoDB \
  --metric-name SuccessfulRequestLatency \
  --dimensions Name=TableName,Value=<TABLE_NAME> Name=GlobalSecondaryIndexName,Value=<INDEX_NAME> \
  --start-time 2026-03-01T00:00:00Z \
  --end-time 2026-03-12T00:00:00Z \
  --period 86400 \
  --statistics Average Maximum \
  --region eu-west-1
```

### Example: `codeliver-notifications -> group-timestamp-index`

```bash
aws cloudwatch get-metric-statistics \
  --profile <AWS_PROFILE> \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=codeliver-notifications Name=GlobalSecondaryIndexName,Value=group-timestamp-index \
  --start-time 2026-03-01T00:00:00Z \
  --end-time 2026-03-12T00:00:00Z \
  --period 86400 \
  --statistics Sum \
  --region eu-west-1
```

```bash
aws cloudwatch get-metric-statistics \
  --profile <AWS_PROFILE> \
  --namespace AWS/DynamoDB \
  --metric-name SuccessfulRequestLatency \
  --dimensions Name=TableName,Value=codeliver-notifications Name=GlobalSecondaryIndexName,Value=group-timestamp-index \
  --start-time 2026-03-01T00:00:00Z \
  --end-time 2026-03-12T00:00:00Z \
  --period 86400 \
  --statistics Average Maximum \
  --region eu-west-1
```

### Example: `codeliver-notifications -> store_id-timestamp-index`

```bash
aws cloudwatch get-metric-statistics \
  --profile <AWS_PROFILE> \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=codeliver-notifications Name=GlobalSecondaryIndexName,Value=store_id-timestamp-index \
  --start-time 2026-03-01T00:00:00Z \
  --end-time 2026-03-12T00:00:00Z \
  --period 86400 \
  --statistics Sum \
  --region eu-west-1
```

### Example: `codeliver-store-charges -> store_id-timestamp-index`

```bash
aws cloudwatch get-metric-statistics \
  --profile <AWS_PROFILE> \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=codeliver-store-charges Name=GlobalSecondaryIndexName,Value=store_id-timestamp-index \
  --start-time 2026-03-01T00:00:00Z \
  --end-time 2026-03-12T00:00:00Z \
  --period 86400 \
  --statistics Sum \
  --region eu-west-1
```

### Example: `codeliver-sap-sockets -> group-expire-index`

```bash
aws cloudwatch get-metric-statistics \
  --profile <AWS_PROFILE> \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=codeliver-sap-sockets Name=GlobalSecondaryIndexName,Value=group-expire-index \
  --start-time 2026-03-01T00:00:00Z \
  --end-time 2026-03-12T00:00:00Z \
  --period 86400 \
  --statistics Sum \
  --region eu-west-1
```

## Delete-readiness decision rules

- If local source-of-truth stays empty and both Stage + Prod metrics remain empty/zero for the verification window, classify the index as `delete-ready`.
- If Stage or Prod shows activity, or an external infra/tooling repo shows a real query path, classify as `keep`.
- If local code stays clean but Stage/Prod evidence is missing or inconsistent, keep `blocked-needs-more-proof`.
- Because the policy is lockstep, any Stage/Prod divergence blocks the delete wave until the contract is reconciled.
