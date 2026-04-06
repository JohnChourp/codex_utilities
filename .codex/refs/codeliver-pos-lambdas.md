# codeliver-pos frontend -> HTTP lambdas

Σκοπός: Καταγραφή των HTTP lambdas που καλούνται από το frontend του `codeliver-pos` (από `*.service.ts`), με normalized paths και observed payloads.

## API Ids -> API Names
- `n4motxwuya` → `codeliver-pos`

## Πηγές
- `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/auth/auth.service.ts`
- `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts`

## codeliver-pos-fetch-delivery-guy-path

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-delivery-guy-path`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:465`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
        realGpsCoords,
      }
```

## codeliver-pos-fetch-delivery-guys

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-delivery-guys`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:369`
```ts
{ type }
```

## codeliver-pos-fetch-delivery-guys-positions

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-delivery-guys-positions`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:324`
```ts
{
        type,
        delivery_guy_id,
      }
```

## codeliver-pos-fetch-routes

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-routes`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:584`
```ts
{ type, lastKey, route_id }
```

## codeliver-pos-fetch-routes-paths

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-routes-paths`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:603`
```ts
{ type, route_id }
```

## codeliver-pos-fetch-routes-paths-calculations

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-routes-paths-calculations`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:635`
```ts
{
        type,
        route_id,
        from_timestamp,
        to_timestamp,
        delivery_guy_id,
}
```

## codeliver-pos-fetch-zones

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-zones`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:355`
```ts
{}
```

## codeliver-pos-handle-customer

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-customer`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:305`
```ts
{ type, customer }
```

## codeliver-pos-handle-delivery-guy

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-delivery-guy`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts`
```ts
payload
```

## codeliver-pos-handle-delivery-request

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-delivery-request`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:506`
```ts
payload
```

## codeliver-pos-handle-delivery-guy-request-rating

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-delivery-guy-request-rating`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:711`
```ts
{
  type: "get",
  request_id,
  delivery_guy_id?,
}
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:729`
```ts
{
  type: "upsert",
  request_id,
  delivery_guy_id?,
  overall_score,
  save_mode: "quick" | "detailed",
  answers?: Array<{ option_id: string; score: number }>,
  comment?: string,
}
```

Observed response shape (success)

```ts
{
  success: true,
  data: {
    rating: {
      group_delivery_guy_id: string,
      request_id: string,
      group: string,
      delivery_guy_id: string,
      store_id: string,
      overall_score: number,
      save_mode: "quick" | "detailed",
      comment: string,
      answers: Array<{ option_id: string; label_snapshot: string; score: number }>,
      questionnaire_version: number,
      questionnaire_snapshot: object,
      request_completed_timestamp: number,
      created_timestamp: number,
      updated_timestamp: number,
      rated_by_user_id: string,
      rated_by_source: "pos",
    } | null,
    questionnaire: object,
  }
}

## codeliver-pos-handle-route

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-route`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:485`
```ts
{
        type,
        route,
        route_id,
        delivery_guy_id,
        requests,
      }
```

## codeliver-pos-handle-store

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-store`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:266`
```ts
{ store, type }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:285`
```ts
{
        type: "update",
        pos_user_updates: posUserUpdates,
      }
```

## codeliver-pos-login

- Normalized: `codeliver-pos/prod/codeliver-pos-login`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/auth/auth.service.ts:73`
```ts
{
        user_id,
        password,
        pos_client_version,
      }
```

## codeliver-pos-renew-token

- Normalized: `codeliver-pos/prod/codeliver-pos-renew-token`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/auth/auth.service.ts:132`
```ts
{
        pos_client_version,
      }
```

## codeliver-pos-search-customers

- Normalized: `codeliver-pos/prod/codeliver-pos-search-customers`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:548`
```ts
{
        type,
        phone,
        exclusiveStartKey,
        store_id,
      }
```

## codeliver-pos-search-delivery-requests

- Normalized: `codeliver-pos/prod/codeliver-pos-search-delivery-requests`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:406`
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

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/control-panel/control-panel.page.ts`
```ts
this.dataStorageService.searchRequestsByStatuses(
  "fetch-requests-by-group-and-statuses",
  this.controlPanelStatuses,
  false,
)
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts`
```ts
{
        type,
        statuses,
      }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:452`
```ts
payload
```

## codeliver-pos-user-remind-password

- Normalized: `codeliver-pos/prod/codeliver-pos-user-remind-password`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:569`
```ts
{
        mobile: number,
      }
```

## test-connection

- Normalized: `codeliver-pos/prod/test-connection`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:94`
```ts
{}
```
