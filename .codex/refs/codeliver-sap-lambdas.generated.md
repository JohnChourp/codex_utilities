# codeliver-sap frontend -> HTTP lambdas

Purpose: Document HTTP lambdas called from the frontend (from *.service.ts) with normalized paths and observed payloads/responses.

## API Ids -> API Names
- `y3hl4t4f22` -> `codeliver-sap`
- `0ws8y1lcy5` -> `codeliver-panel`

## Sources
- `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts`
- `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/auth/auth.service.ts`

## test-connection

- Normalized: `codeliver-sap/prod/test-connection`
- Method: `POST`
- Route: `/test-connection`
- URL: `this.url + "test-connection"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:245`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-panel-users

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-panel-users`
- Method: `POST`
- Route: `/codeliver-sap-fetch-panel-users`
- URL: `this.url + "codeliver-sap-fetch-panel-users"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:394`
```ts
{ group }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:414`
```ts
{ group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-panel-users-sockets

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-panel-users-sockets`
- Method: `POST`
- Route: `/codeliver-sap-fetch-panel-users-sockets`
- URL: `this.url + "codeliver-sap-fetch-panel-users-sockets"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:425`
```ts
{ group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-panel-user

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-panel-user`
- Method: `POST`
- Route: `/codeliver-sap-handle-panel-user`
- URL: `this.url + "codeliver-sap-handle-panel-user"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:445`
```ts
{
        group,
        type,
        user,
      }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-pos-users-sockets

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-pos-users-sockets`
- Method: `POST`
- Route: `/codeliver-sap-fetch-pos-users-sockets`
- URL: `this.url + "codeliver-sap-fetch-pos-users-sockets"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:471`
```ts
{ group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-pos-users

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-pos-users`
- Method: `POST`
- Route: `/codeliver-sap-fetch-pos-users`
- URL: `this.url + "codeliver-sap-fetch-pos-users"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:485`
```ts
{ group }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:499`
```ts
{ group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-pos-user

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-pos-user`
- Method: `POST`
- Route: `/codeliver-sap-handle-pos-user`
- URL: `this.url + "codeliver-sap-handle-pos-user"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:510`
```ts
{
        group,
        type,
        user,
      }
```

Observed response

Response example not observed in service code.

## codeliver-sap-user-remind-password

- Normalized: `codeliver-sap/prod/codeliver-sap-user-remind-password`
- Method: `POST`
- Route: `/codeliver-sap-user-remind-password`
- URL: `this.url + "codeliver-sap-user-remind-password"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:538`
```ts
body
```

Observed response

Response example not observed in service code.

## codeliver-sap-send-user-credentials

- Normalized: `codeliver-sap/prod/codeliver-sap-send-user-credentials`
- Method: `POST`
- Route: `/codeliver-sap-send-user-credentials`
- URL: `this.url + "codeliver-sap-send-user-credentials"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:556`
```ts
body
```

Observed response

Response example not observed in service code.

## codeliver-sap-send-panel-user-credentials

- Normalized: `codeliver-sap/prod/codeliver-sap-send-panel-user-credentials`
- Method: `POST`
- Route: `/codeliver-sap-send-panel-user-credentials`
- URL: `this.url + "codeliver-sap-send-panel-user-credentials"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:574`
```ts
{
        user_id,
        panel,
        store_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-users

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-users`
- Method: `POST`
- Route: `/codeliver-sap-fetch-users`
- URL: `this.url + "codeliver-sap-fetch-users"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:603`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-admin-sockets

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-admin-sockets`
- Method: `POST`
- Route: `/codeliver-sap-fetch-admin-sockets`
- URL: `this.url + "codeliver-sap-fetch-admin-sockets"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:628`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-user

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-user`
- Method: `POST`
- Route: `/codeliver-sap-handle-user`
- URL: `this.url + "codeliver-sap-handle-user"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:648`
```ts
{
        user,
        type,
      }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:671`
```ts
{ user, type }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:689`
```ts
{ user: newEditAdmin, type }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-localservers

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-localservers`
- Method: `POST`
- Route: `/codeliver-sap-fetch-localservers`
- URL: `this.url + "codeliver-sap-fetch-localservers"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:707`
```ts
{ group }
```

Observed response

Response example not observed in service code.

## codeliver-panel-send-user-cloud-command

- Normalized: `codeliver-panel/prod/codeliver-panel-send-user-cloud-command`
- Method: `POST`
- Route: `/codeliver-panel-send-user-cloud-command`
- URL: `"https://0ws8y1lcy5.execute-api.eu-west-1.amazonaws.com/prod/codeliver-panel-send-user-cloud-command"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:722`
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

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:742`
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

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:754`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-groups

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-groups`
- Method: `POST`
- Route: `/codeliver-sap-fetch-groups`
- URL: `this.url + "codeliver-sap-fetch-groups"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:768`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-delivery-requests

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-requests`
- Method: `POST`
- Route: `/codeliver-sap-fetch-delivery-requests`
- URL: `this.url + "codeliver-sap-fetch-delivery-requests"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:804`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:832`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:863`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-routes

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-routes`
- Method: `POST`
- Route: `/codeliver-sap-fetch-routes`
- URL: `this.url + "codeliver-sap-fetch-routes"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:901`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-routes-paths

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-routes-paths`
- Method: `POST`
- Route: `/codeliver-sap-fetch-routes-paths`
- URL: `this.url + "codeliver-sap-fetch-routes-paths"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:919`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-route

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-route`
- Method: `POST`
- Route: `/codeliver-sap-handle-route`
- URL: `this.url + "codeliver-sap-handle-route"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:945`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-group

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-group`
- Method: `POST`
- Route: `/codeliver-sap-handle-group`
- URL: `this.url + "codeliver-sap-handle-group"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:967`
```ts
body
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1038`
```ts
{ group, type }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1059`
```ts
{ group, type }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1083`
```ts
{ group, type }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1123`
```ts
body
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1144`
```ts
body
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-zones

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-zones`
- Method: `POST`
- Route: `/codeliver-sap-fetch-zones`
- URL: `this.url + "codeliver-sap-fetch-zones"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1156`
```ts
{ group }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1177`
```ts
{ group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-stores

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-stores`
- Method: `POST`
- Route: `/codeliver-sap-fetch-stores`
- URL: `this.url + "codeliver-sap-fetch-stores"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1189`
```ts
{ group, type }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1210`
```ts
{ group, type: "fetch-stores-by-group" }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1619`
```ts
{ group: groupId, type: "fetch-stores-by-group" }
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-store

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-store`
- Method: `POST`
- Route: `/codeliver-sap-handle-store`
- URL: `this.url + "codeliver-sap-handle-store"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1221`
```ts
{ store, type, store_id, group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-zone

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-zone`
- Method: `POST`
- Route: `/codeliver-sap-handle-zone`
- URL: `this.url + "codeliver-sap-handle-zone"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1252`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-reorder-stores

- Normalized: `codeliver-sap/prod/codeliver-sap-reorder-stores`
- Method: `POST`
- Route: `/codeliver-sap-reorder-stores`
- URL: `this.url + "codeliver-sap-reorder-stores"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1283`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-reorder-zones

- Normalized: `codeliver-sap/prod/codeliver-sap-reorder-zones`
- Method: `POST`
- Route: `/codeliver-sap-reorder-zones`
- URL: `this.url + "codeliver-sap-reorder-zones"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1309`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-reorder-delivery-guys

- Normalized: `codeliver-sap/prod/codeliver-sap-reorder-delivery-guys`
- Method: `POST`
- Route: `/codeliver-sap-reorder-delivery-guys`
- URL: `this.url + "codeliver-sap-reorder-delivery-guys"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1336`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-delivery-guys

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guys`
- Method: `POST`
- Route: `/codeliver-sap-fetch-delivery-guys`
- URL: `this.url + "codeliver-sap-fetch-delivery-guys"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1363`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1397`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1413`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1652`
```ts
{
          type: "fetch-delivery-guys-by-group",
          group: groupId,
        }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-delivery-guys-connections

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guys-connections`
- Method: `POST`
- Route: `/codeliver-sap-fetch-delivery-guys-connections`
- URL: `this.url + "codeliver-sap-fetch-delivery-guys-connections"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1421`
```ts
data
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-delivery-devices

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-devices`
- Method: `POST`
- Route: `/codeliver-sap-fetch-delivery-devices`
- URL: `this.url + "codeliver-sap-fetch-delivery-devices"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1440`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1466`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1696`
```ts
{ group: groupId }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-delivery-devices-sockets

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-devices-sockets`
- Method: `POST`
- Route: `/codeliver-sap-fetch-delivery-devices-sockets`
- URL: `this.url + "codeliver-sap-fetch-delivery-devices-sockets"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1478`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-delivery-guy

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-delivery-guy`
- Method: `POST`
- Route: `/codeliver-sap-handle-delivery-guy`
- URL: `this.url + "codeliver-sap-handle-delivery-guy"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1515`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-device

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-device`
- Method: `POST`
- Route: `/codeliver-sap-handle-device`
- URL: `this.url + "codeliver-sap-handle-device"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1547`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-device-send-cloud-command

- Normalized: `codeliver-sap/prod/codeliver-sap-device-send-cloud-command`
- Method: `POST`
- Route: `/codeliver-sap-device-send-cloud-command`
- URL: `this.url + "codeliver-sap-device-send-cloud-command"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1592`
```ts
payload
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1765`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-delivery-guy-path

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guy-path`
- Method: `POST`
- Route: `/codeliver-sap-fetch-delivery-guy-path`
- URL: `this.url + "codeliver-sap-fetch-delivery-guy-path"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1786`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
        realGpsCoords,
        group,
      }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-delivery-guy-raw-coordinates

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guy-raw-coordinates`
- Method: `POST`
- Route: `/codeliver-sap-fetch-delivery-guy-raw-coordinates`
- URL: `this.url + "codeliver-sap-fetch-delivery-guy-raw-coordinates"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1807`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
        group,
      }
```

Observed response

Response example not observed in service code.

## codeliver-sap-handle-delivery-guy-shift

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-delivery-guy-shift`
- Method: `POST`
- Route: `/codeliver-sap-handle-delivery-guy-shift`
- URL: `this.url + "codeliver-sap-handle-delivery-guy-shift"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1836`
```ts
{ delivery_guy_id, group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-delivery-guys-actions

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guys-actions`
- Method: `POST`
- Route: `/codeliver-sap-fetch-delivery-guys-actions`
- URL: `this.url + "codeliver-sap-fetch-delivery-guys-actions"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1851`
```ts
{ delivery_guy_id, group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-fetch-batches

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-batches`
- Method: `POST`
- Route: `/codeliver-sap-fetch-batches`
- URL: `this.url + "codeliver-sap-fetch-batches"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1869`
```ts
{ delivery_guy_id, batchNumber, group }
```

Observed response

Response example not observed in service code.

## codeliver-sap-login

- Normalized: `codeliver-sap/prod/codeliver-sap-login`
- Method: `POST`
- Route: `/codeliver-sap-login`
- URL: `this.url + "codeliver-sap-login"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/auth/auth.service.ts:76`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-sap-renew-token

- Normalized: `codeliver-sap/prod/codeliver-sap-renew-token`
- Method: `POST`
- Route: `/codeliver-sap-renew-token`
- URL: `this.url + "codeliver-sap-renew-token"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-sap/src/app/shared/auth/auth.service.ts:121`
```ts
payload
```

Observed response

Response example not observed in service code.
