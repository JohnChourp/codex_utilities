# codeliver-panel frontend -> HTTP lambdas

Purpose: Document HTTP lambdas called from the frontend (from *.service.ts) with normalized paths and observed payloads/responses.

## API Ids -> API Names
- `0ws8y1lcy5` -> `codeliver-panel`

## Sources
- `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts`
- `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/auth/auth.service.ts`

## test-connection

- Normalized: `codeliver-panel/prod/test-connection`
- Method: `POST`
- Route: `/test-connection`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/test-connection"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:225`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-send-cloud-command

- Normalized: `codeliver-panel/prod/codeliver-panel-send-cloud-command`
- Method: `POST`
- Route: `/codeliver-panel-send-cloud-command`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-send-cloud-command"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:414`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-panel-user

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-panel-user`
- Method: `POST`
- Route: `/codeliver-panel-handle-panel-user`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-panel-user"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:510`
```ts
{
        type,
        user,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-pos-users-sockets

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-pos-users-sockets`
- Method: `POST`
- Route: `/codeliver-panel-fetch-pos-users-sockets`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-pos-users-sockets"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:535`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-devices

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-devices`
- Method: `POST`
- Route: `/codeliver-panel-fetch-devices`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-devices"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:551`
```ts
{}
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1755`
```ts
{
          group: groupId,
        }
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-delivery-guy

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-guy`
- Method: `POST`
- Route: `/codeliver-panel-handle-delivery-guy`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-delivery-guy"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:587`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-devices-sockets

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-devices-sockets`
- Method: `POST`
- Route: `/codeliver-panel-fetch-devices-sockets`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-devices-sockets"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:613`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-delivery-guy-path

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guy-path`
- Method: `POST`
- Route: `/codeliver-panel-fetch-delivery-guy-path`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-delivery-guy-path"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:629`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
        realGpsCoords,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-group-stores

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-group-stores`
- Method: `POST`
- Route: `/codeliver-panel-fetch-group-stores`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-group-stores"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:649`
```ts
{}
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1678`
```ts
{ group: groupId }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-pos-users

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-pos-users`
- Method: `POST`
- Route: `/codeliver-panel-fetch-pos-users`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-pos-users"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:663`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-pos-user

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-pos-user`
- Method: `POST`
- Route: `/codeliver-panel-handle-pos-user`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-pos-user"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:677`
```ts
{ user, type }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-group-zones

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-group-zones`
- Method: `POST`
- Route: `/codeliver-panel-fetch-group-zones`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-group-zones"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:696`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-group

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-group`
- Method: `POST`
- Route: `/codeliver-panel-handle-group`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-group"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:714`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-store

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-store`
- Method: `POST`
- Route: `/codeliver-panel-handle-store`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-store"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:737`
```ts
{ store, type, store_id }
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-group-zone

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-group-zone`
- Method: `POST`
- Route: `/codeliver-panel-handle-group-zone`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-group-zone"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:765`
```ts
{ type, zone, zone_id }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-delivery-guys

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guys`
- Method: `POST`
- Route: `/codeliver-panel-fetch-delivery-guys`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-delivery-guys"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:801`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1711`
```ts
{
          type: "fetch-delivery-guys-by-group",
          group: groupId,
        }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-delivery-guys-connections

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guys-connections`
- Method: `POST`
- Route: `/codeliver-panel-fetch-delivery-guys-connections`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-delivery-guys-connections"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:830`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-panel-reorder-stores

- Normalized: `codeliver-panel/prod/codeliver-panel-reorder-stores`
- Method: `POST`
- Route: `/codeliver-panel-reorder-stores`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-reorder-stores"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:846`
```ts
{ stores }
```

Observed response

Response example not observed in service code.

## codeliver-panel-reorder-zones

- Normalized: `codeliver-panel/prod/codeliver-panel-reorder-zones`
- Method: `POST`
- Route: `/codeliver-panel-reorder-zones`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-reorder-zones"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:861`
```ts
{ zones }
```

Observed response

Response example not observed in service code.

## codeliver-panel-reorder-delivery-guys

- Normalized: `codeliver-panel/prod/codeliver-panel-reorder-delivery-guys`
- Method: `POST`
- Route: `/codeliver-panel-reorder-delivery-guys`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-reorder-delivery-guys"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:876`
```ts
{ delivery_guys }
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-device

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-device`
- Method: `POST`
- Route: `/codeliver-panel-handle-device`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-device"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:901`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-panel-search-group-delivery-requests

- Normalized: `codeliver-panel/prod/codeliver-panel-search-group-delivery-requests`
- Method: `POST`
- Route: `/codeliver-panel-search-group-delivery-requests`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-search-group-delivery-requests"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:937`
```ts
{
        type,
        phone,
        store_id,
        delivery_guy_id,
        status,
        exclusiveStartKey,
        route_id,
        request_id,
        nextShortCfRequestId,
      }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:970`
```ts
{
        type,
        statuses,
      }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1027`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-panel-search-notifications

- Normalized: `codeliver-panel/prod/codeliver-panel-search-notifications`
- Method: `POST`
- Route: `/codeliver-panel-search-notifications`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-search-notifications"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1064`
```ts
{
        type,
        charge_type,
        exclusiveStartKey,
        store_id,
        reason,
        delivery_guy_id,
        mobile,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-search-group-charges

- Normalized: `codeliver-panel/prod/codeliver-panel-search-group-charges`
- Method: `POST`
- Route: `/codeliver-panel-search-group-charges`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-search-group-charges"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1096`
```ts
{
        type,
        charge_type,
        exclusiveStartKey,
        store_id,
        reason,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-search-group-delivery-customers

- Normalized: `codeliver-panel/prod/codeliver-panel-search-group-delivery-customers`
- Method: `POST`
- Route: `/codeliver-panel-search-group-delivery-customers`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-search-group-delivery-customers"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1126`
```ts
{
        type,
        phone,
        exclusiveStartKey,
        store_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-routes-paths-calculations

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-routes-paths-calculations`
- Method: `POST`
- Route: `/codeliver-panel-fetch-routes-paths-calculations`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-routes-paths-calculations"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1153`
```ts
{
        type,
        route_id,
        from_timestamp,
        to_timestamp,
        delivery_guy_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-delivery-request-calculations

- Normalized: `codeliver-panel/prod/codeliver-panel-delivery-request-calculations`
- Method: `POST`
- Route: `/codeliver-panel-delivery-request-calculations`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-delivery-request-calculations"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1182`
```ts
{
        type,
        request_id,
        route_id,
        requests_ids,
      }
```

Observed response

Response example not observed in service code.

## codeliver-recalculate-route-and-paths-distances-and-polylines

- Normalized: `codeliver-panel/prod/codeliver-recalculate-route-and-paths-distances-and-polylines`
- Method: `POST`
- Route: `/codeliver-recalculate-route-and-paths-distances-and-polylines`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-recalculate-route-and-paths-distances-and-polylines"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1216`
```ts
{
        type,
        route,
      }
```

Observed response

Response example not observed in service code.

## codeliver-fetch-delivery-guy-raw-coordinates

- Normalized: `codeliver-panel/prod/codeliver-fetch-delivery-guy-raw-coordinates`
- Method: `POST`
- Route: `/codeliver-fetch-delivery-guy-raw-coordinates`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-fetch-delivery-guy-raw-coordinates"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1248`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-delivery-requests-actions

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-requests-actions`
- Method: `POST`
- Route: `/codeliver-panel-fetch-delivery-requests-actions`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-delivery-requests-actions"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1276`
```ts
{ request_id }
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-delivery-guy-shift

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-guy-shift`
- Method: `POST`
- Route: `/codeliver-panel-handle-delivery-guy-shift`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-delivery-guy-shift"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1290`
```ts
{
        delivery_guy_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-delivery-guys-actions

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guys-actions`
- Method: `POST`
- Route: `/codeliver-panel-fetch-delivery-guys-actions`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-delivery-guys-actions"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1309`
```ts
{ delivery_guy_id }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-localservers

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-localservers`
- Method: `POST`
- Route: `/codeliver-panel-fetch-localservers`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-localservers"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1329`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-localserver-sockets

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-localserver-sockets`
- Method: `POST`
- Route: `/codeliver-panel-fetch-localserver-sockets`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-localserver-sockets"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1345`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-panel-users

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-panel-users`
- Method: `POST`
- Route: `/codeliver-panel-fetch-panel-users`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-panel-users"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1367`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-users-sockets

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-users-sockets`
- Method: `POST`
- Route: `/codeliver-panel-fetch-users-sockets`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-users-sockets"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1387`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-delivery-customer

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-customer`
- Method: `POST`
- Route: `/codeliver-panel-handle-delivery-customer`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-delivery-customer"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1411`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-delivery-request

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-request`
- Method: `POST`
- Route: `/codeliver-panel-handle-delivery-request`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-delivery-request"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1445`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-delivery-guys-positions

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guys-positions`
- Method: `POST`
- Route: `/codeliver-panel-fetch-delivery-guys-positions`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-delivery-guys-positions"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1463`
```ts
{
        type,
        delivery_guy_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-batches

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-batches`
- Method: `POST`
- Route: `/codeliver-panel-fetch-batches`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-batches"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1501`
```ts
{
        delivery_guy_id,
        batchNumber,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-routes

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-routes`
- Method: `POST`
- Route: `/codeliver-panel-fetch-routes`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-routes"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1525`
```ts
{ type, lastKey, route_id, ...rest }
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-route

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-route`
- Method: `POST`
- Route: `/codeliver-panel-handle-route`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-route"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1550`
```ts
{
        type,
        route,
        route_id,
        delivery_guy_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-routes-paths

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-routes-paths`
- Method: `POST`
- Route: `/codeliver-panel-fetch-routes-paths`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-routes-paths"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1579`
```ts
{ type, route_id }
```

Observed response

Response example not observed in service code.

## codeliver-panel-send-user-cloud-command

- Normalized: `codeliver-panel/prod/codeliver-panel-send-user-cloud-command`
- Method: `POST`
- Route: `/codeliver-panel-send-user-cloud-command`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-send-user-cloud-command"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1606`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-panel-localserver-remote-login

- Normalized: `codeliver-panel/prod/codeliver-panel-localserver-remote-login`
- Method: `POST`
- Route: `/codeliver-panel-localserver-remote-login`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-localserver-remote-login"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1626`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-panel-device-send-cloud-command

- Normalized: `codeliver-panel/prod/codeliver-panel-device-send-cloud-command`
- Method: `POST`
- Route: `/codeliver-panel-device-send-cloud-command`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-device-send-cloud-command"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1649`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1826`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-panel-handle-localserver

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-localserver`
- Method: `POST`
- Route: `/codeliver-panel-handle-localserver`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-handle-localserver"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1860`
```ts
{
        localserver: modifiedData,
        type: type,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-search-localserver-logs

- Normalized: `codeliver-panel/prod/codeliver-panel-search-localserver-logs`
- Method: `POST`
- Route: `/codeliver-panel-search-localserver-logs`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-search-localserver-logs"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1892`
```ts
dataToSend
```

Observed response

Response example not observed in service code.

## codeliver-panel-fetch-localserver-logs

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-localserver-logs`
- Method: `POST`
- Route: `/codeliver-panel-fetch-localserver-logs`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-fetch-localserver-logs"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1912`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-panel-disconnect-user

- Normalized: `codeliver-panel/prod/codeliver-panel-disconnect-user`
- Method: `POST`
- Route: `/codeliver-panel-disconnect-user`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-disconnect-user"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1937`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-panel-get-requests-stats

- Normalized: `codeliver-panel/prod/codeliver-panel-get-requests-stats`
- Method: `POST`
- Route: `/codeliver-panel-get-requests-stats`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-get-requests-stats"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1949`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-panel-get-store-stats-devices

- Normalized: `codeliver-panel/prod/codeliver-panel-get-store-stats-devices`
- Method: `POST`
- Route: `/codeliver-panel-get-store-stats-devices`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-get-store-stats-devices"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1967`
```ts
{
        store_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-panel-connectivity-stats

- Normalized: `codeliver-panel/prod/codeliver-panel-connectivity-stats`
- Method: `POST`
- Route: `/codeliver-panel-connectivity-stats`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-connectivity-stats"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1983`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-panel-login

- Normalized: `codeliver-panel/prod/codeliver-panel-login`
- Method: `POST`
- Route: `/codeliver-panel-login`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-login"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/auth/auth.service.ts:82`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-panel-renew-token

- Normalized: `codeliver-panel/prod/codeliver-panel-renew-token`
- Method: `POST`
- Route: `/codeliver-panel-renew-token`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-renew-token"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-panel/src/app/shared/auth/auth.service.ts:129`
```ts
payload
```

Observed response

Response example not observed in service code.
