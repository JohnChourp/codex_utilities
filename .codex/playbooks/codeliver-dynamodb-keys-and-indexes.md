# CodeDeliver DynamoDB table keys and indexes

> Canonical DynamoDB key/index mapping for CodeDeliver.
>
> **Single source of truth:** this file must exist only once under:
>
> - `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md`
>
> Rules:
>
> - Do **NOT** copy this file into any repo/lambda/project folder.
> - Do **NOT** create additional `playbooks/` directories elsewhere.
> - If keys/indexes are missing, verify from IaC/code and update **this** canonical file.

## Scope

Canonical mapping of DynamoDB tables -> primary keys (and known secondary indexes) used across:

- projects: codeliver-app, codeliver-panel, codeliver-pos, codeliver-sap
- lambdas: any lambda with "codeliver" in its name

This file is reference data. Do not "infer" missing keys; verify from IaC/code and update this file.

## Notation conventions

- `—` means "does not exist / not applicable" (e.g., table has no sort key, or GSI has no sort key).
- Types are DynamoDB attribute types:
  - `String`, `Number` (extend if needed: `Binary`, etc.)
- If anything is unknown, keep it explicit:
  - `TBD: verify from IaC` (do not guess)

## Tables

### codeliver-batches

Primary key

- Partition key (PK): group_delivery_guy_id (String)
- Sort key (SK): batch_id (Number)

Secondary indexes

- GSI: None
- LSI: None

### codeliver-customers

Primary key

- Partition key (PK): store_id (String)
- Sort key (SK): customer_id (String)

Secondary indexes

- GSI:
  - group-phone-index: PK group (String), SK phone (String)
  - group-timestamp-index: PK group (String), SK timestamp (String)
  - store_id-phone-index: PK store_id (String), SK phone (String)
  - store_id-timestamp-index: PK store_id (String), SK timestamp (String)
- LSI: None

### codeliver-delivery-guys

Primary key

- Partition key (PK): group (String)
- Sort key (SK): delivery_guy_id (String)

Secondary indexes

- GSI:
  - group-mobile-index: PK group (String), SK mobile (String)
  - mobile-index: PK mobile (String), SK —
  - status-group_delivery_guy_id-index: PK status (String), SK group_delivery_guy_id (String)
  - store_id-phone-index: PK store_id (String), SK phone (String)
- LSI: None

### codeliver-delivery-guys-actions

Primary key

- Partition key (PK): group_delivery_guy_id (String)
- Sort key (SK): timestamp (String)

Secondary indexes

- GSI:
  - group_delivery_guy_id-type-index: PK group_delivery_guy_id (String), SK type (String)
- LSI: None

### codeliver-delivery-guys-coordinates

Primary key

- Partition key (PK): group_delivery_guy_id (String)
- Sort key (SK): timestamp (String)

Secondary indexes

- GSI: None
- LSI: None

### codeliver-delivery-guys-connections

Primary key

- Partition key (PK): group (String)
- Sort key (SK): day (String)

Secondary indexes

- GSI: None
- LSI: None

### codeliver-devices

Primary key

- Partition key (PK): group (String)
- Sort key (SK): device_id (String)

Secondary indexes

- GSI:
  - android_id-index: PK android_id (String), SK —
- LSI: None

### codeliver-devices-sockets

Primary key

- Partition key (PK): connection (String)
- Sort key (SK): expire (Number)

Secondary indexes

- GSI:
  - group-expire-index: PK group (String), SK expire (Number)
  - group_delivery_guy_id-expire-index: PK group_delivery_guy_id (String), SK expire (Number)
  - group_device_id-expire-index: PK group_device_id (String), SK expire (Number)
- LSI: None

### codeliver-group-zones

Primary key

- Partition key (PK): group (String)
- Sort key (SK): zone_id (String)

Secondary indexes

- GSI: None
- LSI: None

### codeliver-groups

Primary key

- Partition key (PK): group (String)
- Sort key (SK): —

Secondary indexes

- GSI: None
- LSI: None

### codeliver-localserver-logs

Primary key

- Partition key (PK): server_id (String)
- Sort key (SK): timestamp (String)

Secondary indexes

- GSI:
  - server_id_type-timestamp-index: PK server_id_type (String), SK timestamp (String)
- LSI: None

### codeliver-localserver-sockets

Primary key

- Partition key (PK): connection (String)
- Sort key (SK): expire (Number)

Secondary indexes

- GSI:
  - group-expire-index: PK group (String), SK expire (Number)
  - group_store_id-expire-index: PK group_store_id (String), SK expire (Number)
- LSI: None

### codeliver-localservers

Primary key

- Partition key (PK): store_id (String)
- Sort key (SK): server_id (String)

Secondary indexes

- GSI:
  - group-server_id-index: PK group (String), SK server_id (String)
- LSI: None

### codeliver-notifications

Primary key

- Partition key (PK): group (String)
- Sort key (SK): notification_id (String)

Secondary indexes

- GSI:
  - group-timestamp-index: PK group (String), SK timestamp (String)
  - group_delivery_guy_id-timestamp-index: PK group_delivery_guy_id (String), SK timestamp (String)
  - mobile-type_timestamp-index-all: PK mobile (String), SK type_timestamp (String)
  - notification_id-index: PK notification_id (String), SK —
  - route_id-delivery_guy_id-index: PK route_id (String), SK delivery_guy_id (String)
  - store_id-timestamp-index: PK store_id (String), SK timestamp (String)
  - store_id_reason-timestamp-index: PK store_id_reason (String), SK timestamp (String)
  - store_id_type-timestamp-index: PK store_id_type (String), SK timestamp (String)
  - store_id_type_reason-timestamp-index: PK store_id_type_reason (String), SK timestamp (String)
- LSI: None

### codeliver-panel-sockets

Primary key

- Partition key (PK): connection (String)
- Sort key (SK): —

Secondary indexes

- GSI:
  - group-expire-index: PK group (String), SK expire (Number)
  - store_id-expire-index: PK store_id (String), SK expire (Number)
  - sessionID-expire-index: PK sessionID (String), SK expire (Number)
- LSI: None

### codeliver-panel-users

Primary key

- Partition key (PK): group (String)
- Sort key (SK): user_id (String)

Secondary indexes

- GSI: None
- LSI: None

### codeliver-pos-sockets

Primary key

- Partition key (PK): connection (String)
- Sort key (SK): —

Secondary indexes

- GSI:
  - group-expire-index: PK group (String), SK expire (Number)
  - sessionID-expire-index: PK sessionID (String), SK expire (Number)
  - store_id-expire-index: PK store_id (String), SK expire (Number)
- LSI: None

### codeliver-pos-users

Primary key

- Partition key (PK): store_id (String)
- Sort key (SK): user_id (String)

Secondary indexes

- GSI: None
- LSI: None

### codeliver-requests

Primary key

- Partition key (PK): group (String)
- Sort key (SK): request_id (String)

Secondary indexes

- GSI:
  - delivery_guy_id-batchNumber-index: PK delivery_guy_id (String), SK batchNumber (Number)
  - delivery_guy_id-phone-index: PK delivery_guy_id (String), SK phone (String)
  - delivery_guy_id-timestamp-index: PK delivery_guy_id (String), SK timestamp (String)
  - group-nextShortCfRequestId-index: PK group (String), SK nextShortCfRequestId (String)
  - group-phone-index: PK group (String), SK phone (String)
  - group-route_id-index: PK group (String), SK route_id (String)
  - group-status-index: PK group (String), SK status (String)
  - group-timestamp-index: PK group (String), SK timestamp (String)
  - group_mobile-timestamp-index: PK group_mobile (String), SK timestamp (String)
  - sap-timestamp-index: PK sap (String), SK timestamp (String)
  - status-timestamp-index: PK status (String), SK timestamp (String)
  - store_Id-request_id-index: PK store_Id (String), SK request_id (String)
  - store_id-phone-index: PK store_id (String), SK phone (String)
  - store_id-timestamp-index: PK store_id (String), SK timestamp (String)
  - zone_id-timestamp-index: PK zone_id (String), SK timestamp (String)
- LSI: None

### codeliver-requests-actions

Primary key

- Partition key (PK): group_request_id (String)
- Sort key (SK): timestamp (String)

Secondary indexes

- GSI:
  - group_request_id-type-index: PK group_request_id (String), SK type (String)
- LSI: None

### codeliver-requests-calculations

Primary key

- Partition key (PK): calculation_id (String)
- Sort key (SK): timestamp (String)

Secondary indexes

- GSI:
  - group_request_id-timestamp-index: PK group_request_id (String), SK timestamp (String)
- LSI: None

### codeliver-routes

Primary key

- Partition key (PK): group (String)
- Sort key (SK): route_id (String)

Secondary indexes

- GSI:
  - group-delivery_guy_id-index: PK group (String), SK delivery_guy_id (String)
  - group-status-index: PK group (String), SK status (String)
  - group-updated_timestamp-index: PK group (String), SK updated_timestamp (Number)
- LSI: None

### codeliver-routes-paths

Primary key

- Partition key (PK): route_id (String)
- Sort key (SK): path_id (String)

Secondary indexes

- GSI:
  - route_id-position-index: PK route_id (String), SK position (Number)
- LSI: None

### codeliver-routes-paths-calculations

Primary key

- Partition key (PK): route_id (String)
- Sort key (SK): calculation_id (String)

Secondary indexes

- GSI:
  - route_id-timestamp-index: PK route_id (String), SK timestamp (String)
  - route_id_delivery_guy_id-timestamp-index: PK route_id_delivery_guy_id (String), SK timestamp (String)
- LSI: None

### codeliver-sap-sockets

Primary key

- Partition key (PK): connection (String)
- Sort key (SK): —

Secondary indexes

- GSI:
  - group-expire-index: PK group (String), SK expire (Number)
  - sessionID-expire-index: PK sessionID (String), SK expire (Number)
  - store_id-expire-index: PK store_id (String), SK expire (Number)
- LSI: None

### codeliver-sap-users

Primary key

- Partition key (PK): superadmin_id (String)
- Sort key (SK): —

Secondary indexes

- GSI: None
- LSI: None

### codeliver-store-charges

Primary key

- Partition key (PK): group (String)
- Sort key (SK): timestamp (String)

Secondary indexes

- GSI:
  - store_id-timestamp-index: PK store_id (String), SK timestamp (String)
  - store_id_reason-timestamp-index: PK store_id_reason (String), SK timestamp (String)
  - store_id_type-timestamp-index: PK store_id_type (String), SK timestamp (String)
  - store_id_type_reason-timestamp-index: PK store_id_type_reason (String), SK timestamp (String)
- LSI: None

### codeliver-stores

Primary key

- Partition key (PK): group (String)
- Sort key (SK): store_id (String)

Secondary indexes

- GSI:
  - partner_id-store_id-index: PK partner_id (String), SK store_id (String)
  - primary_local_server_reset-store_id-index: PK primary_local_server_reset (String), SK store_id (String)
- LSI: None

### google-api-counter

Primary key

- Partition key (PK): apikey-date (String)
- Sort key (SK): —

Secondary indexes

- GSI: None
- LSI: None

### Find table definitions

- `rg -n "TableName: *codeliver-" /home/dm-soft-1/Downloads/lambdas/codeliver_all /home/dm-soft-1/Downloads/projects/codeliver`
- `rg -n "codeliver-[a-z0-9-]+" /home/dm-soft-1/Downloads/lambdas/codeliver_all /home/dm-soft-1/Downloads/projects/codeliver`

### Find secondary indexes (GSI/LSI)

- `rg -n "GlobalSecondaryIndexes|LocalSecondaryIndexes" /home/dm-soft-1/Downloads/lambdas/codeliver_all /home/dm-soft-1/Downloads/projects/codeliver`
- `rg -n "IndexName|keySchema|partitionKey|sortKey" /home/dm-soft-1/Downloads/lambdas/codeliver_all /home/dm-soft-1/Downloads/projects/codeliver`

### For a specific table

- `rg -n "codeliver-delivery-guys" /home/dm-soft-1/Downloads/lambdas/codeliver_all /home/dm-soft-1/Downloads/projects/codeliver`

When indexes are discovered/changed, update the “Secondary indexes” column with:

- Index name
- partition key + sort key (+ types)
- use `—` explicitly if an index has no sort key
