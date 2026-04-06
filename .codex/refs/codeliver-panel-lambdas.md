# codeliver-panel frontend -> HTTP lambdas

Σκοπός: Καταγραφή των HTTP lambdas που καλούνται από το frontend του `codeliver-panel` (από `*.service.ts`), με normalized paths και observed payloads.

## API Ids -> API Names
- `0ws8y1lcy5` → `codeliver-panel`

## Πηγές
- `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/auth/auth.service.ts`
- `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts`

## codeliver-fetch-delivery-guy-raw-coordinates

- Normalized: `codeliver-panel/prod/codeliver-fetch-delivery-guy-raw-coordinates`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1156`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
      }
```

## codeliver-panel-connectivity-stats

- Normalized: `codeliver-panel/prod/codeliver-panel-connectivity-stats`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1740`
```ts
data
```

## codeliver-panel-delivery-request-calculations

- Normalized: `codeliver-panel/prod/codeliver-panel-delivery-request-calculations`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1090`
```ts
{
        type,
        request_id,
        route_id,
        requests_ids,
      }
```

## codeliver-panel-device-send-cloud-command

- Normalized: `codeliver-panel/prod/codeliver-panel-device-send-cloud-command`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1580`
```ts
{
        device_id,
        type,
        cloud_command_id,
      }
```

## codeliver-panel-disconnect-user

- Normalized: `codeliver-panel/prod/codeliver-panel-disconnect-user`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1690`
```ts
data
```

## codeliver-panel-fetch-batches

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-batches`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1424`
```ts
{
        delivery_guy_id,
        batchNumber,
      }
```

## codeliver-panel-fetch-delivery-guy-path

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guy-path`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:596`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
        realGpsCoords,
}
```

## codeliver-panel-fetch-delivery-guys-connections

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guys-connections`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts`
```ts
{
  year_month: "YYYY-MM"
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

## codeliver-panel-fetch-delivery-guys

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guys`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:768`
```ts
payload
```

## codeliver-panel-fetch-delivery-guys-actions

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guys-actions`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1217`
```ts
{
  delivery_guy_id,
  date_from?,   // epoch ms
  date_to?,     // epoch ms
  action_type?, // string
  group?,       // optional fallback
}
```

## codeliver-panel-fetch-delivery-guys-positions

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guys-positions`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1386`
```ts
{
        type,
        delivery_guy_id,
      }
```

## codeliver-panel-fetch-delivery-requests-actions

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-requests-actions`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1184`
```ts
{ request_id }
```

## codeliver-panel-fetch-devices

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-devices`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:529`
```ts
{}
```

## codeliver-panel-fetch-devices-sockets

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-devices-sockets`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:580`
```ts
{}
```

## codeliver-panel-fetch-group-stores

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-group-stores`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:615`
```ts
{}
```

## codeliver-panel-fetch-group-zones

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-group-zones`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:662`
```ts
{}
```

## codeliver-panel-fetch-localserver-logs

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-localserver-logs`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1665`
```ts
data
```

## codeliver-panel-fetch-localserver-sockets

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-localserver-sockets`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1253`
```ts
{}
```

## codeliver-panel-fetch-localservers

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-localservers`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1237`
```ts
{}
```

## codeliver-panel-fetch-panel-users

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-panel-users`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1274`
```ts
{}
```

## codeliver-panel-fetch-pos-users

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-pos-users`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:629`
```ts
{}
```

## codeliver-panel-fetch-pos-users-sockets

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-pos-users-sockets`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:514`
```ts
{}
```

## codeliver-panel-fetch-routes

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-routes`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1448`
```ts
{ type, lastKey, route_id, ...rest }
```

## codeliver-panel-fetch-routes-paths

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-routes-paths`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1502`
```ts
{ type, route_id }
```

## codeliver-panel-fetch-routes-paths-calculations

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-routes-paths-calculations`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1061`
```ts
{
        type,
        route_id,
        from_timestamp,
        to_timestamp,
        delivery_guy_id,
      }
```

## codeliver-panel-fetch-users-sockets

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-users-sockets`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1294`
```ts
{}
```

## codeliver-panel-get-requests-stats

- Normalized: `codeliver-panel/prod/codeliver-panel-get-requests-stats`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1703`
```ts
data
```

## codeliver-panel-get-store-stats-devices

- Normalized: `codeliver-panel/prod/codeliver-panel-get-store-stats-devices`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1723`
```ts
{
        store_id,
      }
```

## codeliver-panel-handle-delivery-customer

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-customer`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1315`
```ts
{ type, customer }
```

## codeliver-panel-handle-delivery-guy

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-guy`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:554`
```ts
payload
```

## codeliver-panel-handle-delivery-guy-shift

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-guy-shift`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1198`
```ts
{
        delivery_guy_id,
      }
```

## codeliver-panel-handle-delivery-request

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-request`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1341`
```ts
payload
```

## codeliver-panel-handle-device

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-device`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:844`
```ts
{
        device,
        type,
        device_id,
      }
```

## codeliver-panel-handle-group

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-group`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:681`
```ts
payload
```

Observed rating-related group fields

```ts
{
  enable_rating_delivery_guys_from_requests?: boolean,
  delivery_guy_request_rating_questionnaire?: {
    schema_version: 1,
    questionnaire_version: number,
    detailed_scale_max: 5,
    comment_mode: "optional",
    quick_save_mode: "fill_active_options_with_max",
    options: Array<{
      option_id: string,
      label: string,
      order: number,
      active: boolean,
      created_timestamp: number | null,
      archived_timestamp: number | null,
    }>,
  },
}
```

## codeliver-panel-handle-delivery-guy-request-rating

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-delivery-guy-request-rating`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:832`
```ts
{
  type: "get",
  request_id,
  delivery_guy_id?,
}
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:850`
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
      rated_by_source: "panel",
    } | null,
    questionnaire: object,
  }
}
```

## codeliver-panel-fetch-delivery-guy-request-ratings

- Normalized: `codeliver-panel/prod/codeliver-panel-fetch-delivery-guy-request-ratings`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:874`
```ts
{
  type: "search",
  date_from?,
  date_to?,
  store_id?,
  delivery_guy_id?,
}
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:896`
```ts
{
  type: "delivery-guy-summary",
  delivery_guy_id,
  date_from?,
  date_to?,
}
```

Observed response notes

- `type: "search"` returns `ratings`, `summary`, `stores`, `delivery_guys`, and `current_questionnaire`.
- `type: "delivery-guy-summary"` returns current delivery-guy info plus `range` and `lifetime` aggregates.
- Current implementation uses direct PK query for per-delivery-guy summary and scan fallback for group/store reporting because no canonical secondary index mapping exists yet for `codeliver-rating-delivery-guys-requests`.

## codeliver-panel-handle-group-zone

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-group-zone`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:732`
```ts
{ type, zone, zone_id }
```

## codeliver-panel-handle-localserver

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-localserver`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1611`
```ts
{
        localserver: modifiedData,
        type: type,
      }
```

## codeliver-panel-handle-panel-user

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-panel-user`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:489`
```ts
{
        type,
        user,
      }
```

## codeliver-panel-handle-pos-user

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-pos-user`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:643`
```ts
{ user, type }
```

## codeliver-panel-handle-route

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-route`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1473`
```ts
{
        type,
        route,
        route_id,
        delivery_guy_id,
      }
```

## codeliver-panel-handle-store

- Normalized: `codeliver-panel/prod/codeliver-panel-handle-store`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:704`
```ts
{ store, type, store_id }
```

## codeliver-panel-localserver-remote-login

- Normalized: `codeliver-panel/prod/codeliver-panel-localserver-remote-login`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1565`
```ts
data
```

## codeliver-panel-login

- Normalized: `codeliver-panel/prod/codeliver-panel-login`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/auth/auth.service.ts:61`
```ts
{
        user_id,
        password,
        panel_client_version,
      }
```

## codeliver-panel-renew-token

- Normalized: `codeliver-panel/prod/codeliver-panel-renew-token`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/auth/auth.service.ts:106`
```ts
{
        panel_client_version,
      }
```

## codeliver-panel-reorder-delivery-guys

- Normalized: `codeliver-panel/prod/codeliver-panel-reorder-delivery-guys`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:827`
```ts
{ delivery_guys }
```

## codeliver-panel-reorder-stores

- Normalized: `codeliver-panel/prod/codeliver-panel-reorder-stores`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:796`
```ts
{ stores }
```

## codeliver-panel-reorder-zones

- Normalized: `codeliver-panel/prod/codeliver-panel-reorder-zones`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:811`
```ts
{ zones }
```

## codeliver-panel-search-group-charges

- Normalized: `codeliver-panel/prod/codeliver-panel-search-group-charges`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1004`
```ts
{
        type,
        charge_type,
        exclusiveStartKey,
        store_id,
        reason,
      }
```

## codeliver-panel-search-group-delivery-customers

- Normalized: `codeliver-panel/prod/codeliver-panel-search-group-delivery-customers`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1034`
```ts
{
        type,
        phone,
        exclusiveStartKey,
        store_id,
      }
```

## codeliver-panel-search-group-delivery-requests

- Normalized: `codeliver-panel/prod/codeliver-panel-search-group-delivery-requests`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:882`
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
      }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:935`
```ts
payload
```

## codeliver-panel-search-localserver-logs

- Normalized: `codeliver-panel/prod/codeliver-panel-search-localserver-logs`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1644`
```ts
dataToSend
```

## codeliver-panel-search-notifications

- Normalized: `codeliver-panel/prod/codeliver-panel-search-notifications`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:972`
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

## codeliver-panel-send-cloud-command

- Normalized: `codeliver-panel/prod/codeliver-panel-send-cloud-command`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:392`
```ts
data
```

## codeliver-panel-send-user-cloud-command

- Normalized: `codeliver-panel/prod/codeliver-panel-send-user-cloud-command`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1544`
```ts
data
```

## codeliver-recalculate-route-and-paths-distances-and-polylines

- Normalized: `codeliver-panel/prod/codeliver-recalculate-route-and-paths-distances-and-polylines`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:1124`
```ts
{
        type,
        route,
      }
```

## test-connection

- Normalized: `codeliver-panel/prod/test-connection`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-panel/src/app/shared/data.storage.service.ts:214`
```ts
{}
```
