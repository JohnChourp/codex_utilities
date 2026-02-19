# codeliver-app frontend -> HTTP lambdas

Σκοπός: Καταγραφή των HTTP lambdas που καλούνται από το frontend του `codeliver-app` (από `*.service.ts`), με normalized paths και observed payloads.

## API Ids -> API Names
- `8sw8osiclf` → `codeliver-app`

## Πηγές
- `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts`
- `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts`

## codeliver-app-async-actions

- Normalized: `codeliver-app/prod/codeliver-app-async-actions`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:312`
```ts
{
  actions: actionsArray,
  paused: Boolean(paused),
  connected: Boolean(networkStatus?.connected),
  connectionType: networkStatus?.connectionType ?? null,
}
```

## codeliver-backend-check-delivery-requests

- Normalized: `codeliver-app/prod/codeliver-backend-check-delivery-requests`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:196`
```ts
{}
```

## codeliver-app-device-login

- Normalized: `codeliver-app/prod/codeliver-app-device-login`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:66`
```ts
{
        device_id,
        password,
      }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:111`
```ts
{
        android_id,
      }
```

## codeliver-app-fetch-delivery-guy-data

- Normalized: `codeliver-app/prod/codeliver-app-fetch-delivery-guy-data`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:626`
```ts
payload
```

## codeliver-app-fetch-delivery-guy-path

- Normalized: `codeliver-app/prod/codeliver-app-fetch-delivery-guy-path`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:282`
```ts
{
        delivery_guy_id,
        type,
        date_from,
        date_to,
        realGpsCoords,
      }
```

## codeliver-app-fetch-delivery-requests

- Normalized: `codeliver-app/prod/codeliver-app-fetch-delivery-requests`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:504`
```ts
{
        type,
        lastKey,
        delivery_guy_id,
        route_id,
        routes_ids,
      }
```

## codeliver-app-fetch-notifications

- Normalized: `codeliver-app/prod/codeliver-app-fetch-notifications`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:235`
```ts
{ exclusiveStartKey }
```

## codeliver-app-fetch-routes

- Normalized: `codeliver-app/prod/codeliver-app-fetch-routes`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:409`
```ts
{
        type,
        lastKey,
        delivery_guy_id,
        route_id,
      }
```

## codeliver-app-fetch-routes-paths

- Normalized: `codeliver-app/prod/codeliver-app-fetch-routes-paths`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:443`
```ts
{ type, routes_ids, route_id }
```

## codeliver-app-fetch-routes-paths-calculations

- Normalized: `codeliver-app/prod/codeliver-app-fetch-routes-paths-calculations`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:467`
```ts
{
        type,
        route_id,
        timestamp,
      }
```

## codeliver-app-get-requests-stats

- Normalized: `codeliver-app/prod/codeliver-app-get-requests-stats`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:390`
```ts
payload
```

## codeliver-app-login-mobile-pin

- Normalized: `codeliver-app/prod/codeliver-app-login-mobile-pin`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:155`
```ts
{
        mobile,
        pin,
      }
```

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:192`
```ts
{
        pin,
        device_id,
      }
```

## codeliver-app-renew-device-token

- Normalized: `codeliver-app/prod/codeliver-app-renew-device-token`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:335`
```ts
renewBody
```

## codeliver-app-send-android-id

- Normalized: `codeliver-app/prod/codeliver-app-send-android-id`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:229`
```ts
{
        device_info,
      }
```

## codeliver-app-sync-actions

- Normalized: `codeliver-app/prod/codeliver-app-sync-actions`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:343`
```ts
{ actions: actionsArray }
```

## test-connection

- Normalized: `codeliver-app/prod/test-connection`

Observed payloads (body)

Source: `/home/dm-soft-1/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:192`
```ts
{}
```
