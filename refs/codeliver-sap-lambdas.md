# codeliver-sap frontend -> HTTP lambdas

Σκοπός: Καταγραφή των HTTP lambdas που καλούνται από το frontend του `codeliver-sap` (από `*.service.ts`), με normalized paths και observed payloads.

## API Ids -> API Names
- `0ws8y1lcy5` → `codeliver-panel`
- `y3hl4t4f22` → `codeliver-sap`

## Πηγές
- `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/auth/auth.service.ts`
- `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts`

## codeliver-panel-disconnect-user

- Normalized: `codeliver-panel/prod/codeliver-panel-disconnect-user`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:673`
```ts
data
```

## codeliver-panel-localserver-remote-login

- Normalized: `codeliver-panel/prod/codeliver-panel-localserver-remote-login`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:658`
```ts
data
```

## codeliver-panel-send-user-cloud-command

- Normalized: `codeliver-panel/prod/codeliver-panel-send-user-cloud-command`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:634`
```ts
data
```

## codeliver-sap-fetch-delivery-guys-connections

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guys-connections`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts`
```ts
{
  year_month: "YYYY-MM",
  group
}
```

Observed response shape (success)

```ts
{
  success: true,
  data: {
    group: string,
    year_month: "YYYY-MM",
    month_peak_count: number,
    month_avg_count_30m: number,
    month_total_count_30m: number,
    peak_day: string | null,
    daily: Array<{ day: string; peak_count: number; peak_time_utc: string | null; avg_count_30m: number }>,
    days_details: Array<{
      day: string;
      day_peak_count: number;
      day_peak_time_utc: string | null;
      day_peak_slot_utc: string | null;
      day_total_count_30m: number;
      day_avg_count_30m: number;
      active_slots_30m: Array<{ slot_utc: string; peak_count: number; peak_time_utc: string | null }>;
    }>
  }
}
```

## codeliver-sap-device-send-cloud-command

- Normalized: `codeliver-sap/prod/codeliver-sap-device-send-cloud-command`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1178`
```ts
{ device_id, type, cloud_command_id, group }
```

## codeliver-sap-fetch-admin-sockets

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-admin-sockets`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:537`
```ts
{}
```

## codeliver-sap-fetch-batches

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-batches`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1274`
```ts
{ delivery_guy_id, batchNumber, group }
```

## codeliver-sap-fetch-delivery-devices

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-devices`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1063`
```ts
payload
```

## codeliver-sap-fetch-delivery-devices-sockets

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-devices-sockets`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1084`
```ts
payload
```

## codeliver-sap-fetch-delivery-guy-path

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guy-path`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1192`
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

## codeliver-sap-fetch-delivery-guy-raw-coordinates

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guy-raw-coordinates`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1213`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
        group,
      }
```

## codeliver-sap-fetch-delivery-guys

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guys`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1036`
```ts
payload
```

## codeliver-sap-fetch-delivery-guys-actions

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-guys-actions`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1256`
```ts
{ delivery_guy_id, group }
```

## codeliver-sap-fetch-delivery-requests

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-delivery-requests`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:768`
```ts
{
  type: "fetch-requests-by-group-and-status",
  group,
  status: normalizedStatus,
  exclusiveStartKey,
}
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:800`
```ts
{
  type: "fetch-requests-by-group-and-statuses",
  group,
  statuses: normalizedStatuses,
}
```

## codeliver-sap-fetch-groups

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-groups`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:688`
```ts
{}
```

## codeliver-sap-fetch-localservers

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-localservers`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:616`
```ts
{ group }
```

## codeliver-sap-fetch-panel-users

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-panel-users`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:324`
```ts
{ group }
```

## codeliver-sap-fetch-panel-users-sockets

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-panel-users-sockets`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:344`
```ts
{ group }
```

## codeliver-sap-fetch-pos-users

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-pos-users`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:405`
```ts
{ group }
```

## codeliver-sap-fetch-pos-users-sockets

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-pos-users-sockets`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:391`
```ts
{ group }
```

## codeliver-sap-fetch-stores

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-stores`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:873`
```ts
{ group, type }
```

## codeliver-sap-fetch-users

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-users`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:512`
```ts
{}
```

## codeliver-sap-fetch-zones

- Normalized: `codeliver-sap/prod/codeliver-sap-fetch-zones`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:852`
```ts
{ group }
```

## codeliver-sap-handle-delivery-guy

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-delivery-guy`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1119`
```ts
payload
```

## codeliver-sap-handle-delivery-guy-shift

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-delivery-guy-shift`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1241`
```ts
{ delivery_guy_id, group }
```

## codeliver-sap-handle-device

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-device`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1148`
```ts
payload
```

## codeliver-sap-handle-group

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-group`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:724`
```ts
body
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:784`
```ts
{ group, type }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:806`
```ts
{ group, type }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:830`
```ts
{ group, type }
```

## codeliver-sap-handle-panel-user

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-panel-user`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:365`
```ts
{
        group,
        type,
        user,
      }
```

## codeliver-sap-handle-pos-user

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-pos-user`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:420`
```ts
{
        group,
        type,
        user,
      }
```

## codeliver-sap-handle-store

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-store`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:894`
```ts
{ store, type, store_id, group }
```

## codeliver-sap-handle-user

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-user`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:558`
```ts
{
        user,
        type,
      }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:580`
```ts
{ user, type }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:598`
```ts
{ user: newEditAdmin, type }
```

## codeliver-sap-handle-zone

- Normalized: `codeliver-sap/prod/codeliver-sap-handle-zone`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:925`
```ts
payload
```

## codeliver-sap-login

- Normalized: `codeliver-sap/prod/codeliver-sap-login`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/auth/auth.service.ts:77`
```ts
{
  superadmin_id,
  password,
  sap_client_version
}
```

## codeliver-sap-renew-token

- Normalized: `codeliver-sap/prod/codeliver-sap-renew-token`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/auth/auth.service.ts:122`
```ts
{
  sap_client_version
}
```

## codeliver-sap-reorder-delivery-guys

- Normalized: `codeliver-sap/prod/codeliver-sap-reorder-delivery-guys`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:1009`
```ts
payload
```

## codeliver-sap-reorder-stores

- Normalized: `codeliver-sap/prod/codeliver-sap-reorder-stores`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:956`
```ts
payload
```

## codeliver-sap-reorder-zones

- Normalized: `codeliver-sap/prod/codeliver-sap-reorder-zones`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:982`
```ts
payload
```

## codeliver-sap-send-panel-user-credentials

- Normalized: `codeliver-sap/prod/codeliver-sap-send-panel-user-credentials`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:484`
```ts
{
        user_id,
        panel,
        store_id,
      }
```

## codeliver-sap-send-user-credentials

- Normalized: `codeliver-sap/prod/codeliver-sap-send-user-credentials`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:465`
```ts
body
```

## codeliver-sap-user-remind-password

- Normalized: `codeliver-sap/prod/codeliver-sap-user-remind-password`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:447`
```ts
body
```

## test-connection

- Normalized: `codeliver-sap/prod/test-connection`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-sap/src/app/shared/data.storage.service.ts:187`
```ts
{}
```
