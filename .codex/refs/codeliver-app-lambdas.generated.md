# codeliver-app frontend -> HTTP lambdas

Purpose: Document HTTP lambdas called from the frontend (from *.service.ts) with normalized paths and observed payloads/responses.

## API Ids -> API Names
- `8sw8osiclf` -> `codeliver-app`

## Sources
- `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts`
- `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts`

## test-connection

- Normalized: `codeliver-app/prod/test-connection`
- Method: `POST`
- Route: `/test-connection`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/test-connection"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:193`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-app-fetch-notifications

- Normalized: `codeliver-app/prod/codeliver-app-fetch-notifications`
- Method: `POST`
- Route: `/codeliver-app-fetch-notifications`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-fetch-notifications"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:235`
```ts
{ exclusiveStartKey }
```

Observed response

Response example not observed in service code.

## codeliver-app-fetch-delivery-guy-path

- Normalized: `codeliver-app/prod/codeliver-app-fetch-delivery-guy-path`
- Method: `POST`
- Route: `/codeliver-app-fetch-delivery-guy-path`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-fetch-delivery-guy-path"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:282`
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

## codeliver-app-sync-actions

- Normalized: `codeliver-app/prod/codeliver-app-sync-actions`
- Method: `POST`
- Route: `/codeliver-app-sync-actions`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-sync-actions"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:344`
```ts
{ actions: actionsArray }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:226`
```ts
{ actions: actionsArray }
```

Observed response

Response example not observed in service code.

## codeliver-app-get-requests-stats

- Normalized: `codeliver-app/prod/codeliver-app-get-requests-stats`
- Method: `POST`
- Route: `/codeliver-app-get-requests-stats`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-get-requests-stats"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:439`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-app-fetch-routes

- Normalized: `codeliver-app/prod/codeliver-app-fetch-routes`
- Method: `POST`
- Route: `/codeliver-app-fetch-routes`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-fetch-routes"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:457`
```ts
{
        type,
        lastKey,
        delivery_guy_id,
        route_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-app-fetch-routes-paths

- Normalized: `codeliver-app/prod/codeliver-app-fetch-routes-paths`
- Method: `POST`
- Route: `/codeliver-app-fetch-routes-paths`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-fetch-routes-paths"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:491`
```ts
{ type, routes_ids, route_id }
```

Observed response

Response example not observed in service code.

## codeliver-app-fetch-routes-paths-calculations

- Normalized: `codeliver-app/prod/codeliver-app-fetch-routes-paths-calculations`
- Method: `POST`
- Route: `/codeliver-app-fetch-routes-paths-calculations`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-fetch-routes-paths-calculations"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:515`
```ts
{
        type,
        route_id,
        timestamp,
      }
```

Observed response

Response example not observed in service code.

## codeliver-app-fetch-delivery-requests

- Normalized: `codeliver-app/prod/codeliver-app-fetch-delivery-requests`
- Method: `POST`
- Route: `/codeliver-app-fetch-delivery-requests`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-fetch-delivery-requests"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:552`
```ts
{
        type,
        lastKey,
        delivery_guy_id,
        route_id,
        routes_ids,
      }
```

Observed response

Response example not observed in service code.

## codeliver-app-fetch-delivery-guy-data

- Normalized: `codeliver-app/prod/codeliver-app-fetch-delivery-guy-data`
- Method: `POST`
- Route: `/codeliver-app-fetch-delivery-guy-data`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-fetch-delivery-guy-data"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:674`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-backend-check-delivery-requests

- Normalized: `codeliver-app/prod/codeliver-backend-check-delivery-requests`
- Method: `POST`
- Route: `/codeliver-backend-check-delivery-requests`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-backend-check-delivery-requests"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:207`
```ts
(none)
```

Observed response

Response example not observed in service code.

## codeliver-app-async-actions

- Normalized: `codeliver-app/prod/codeliver-app-async-actions`
- Method: `POST`
- Route: `/codeliver-app-async-actions`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-async-actions"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:331`
```ts
(none)
```

Observed response

Response example not observed in service code.

## codeliver-app-device-login

- Normalized: `codeliver-app/prod/codeliver-app-device-login`
- Method: `POST`
- Route: `/codeliver-app-device-login`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-device-login"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:65`
```ts
{
        device_id,
        password,
      }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:110`
```ts
{
        android_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-app-login-mobile-pin

- Normalized: `codeliver-app/prod/codeliver-app-login-mobile-pin`
- Method: `POST`
- Route: `/codeliver-app-login-mobile-pin`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-login-mobile-pin"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:154`
```ts
{
        mobile,
        pin,
      }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:191`
```ts
{
        pin,
        device_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-app-send-android-id

- Normalized: `codeliver-app/prod/codeliver-app-send-android-id`
- Method: `POST`
- Route: `/codeliver-app-send-android-id`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-send-android-id"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:228`
```ts
{
        device_info,
      }
```

Observed response

Response example not observed in service code.

## codeliver-app-renew-device-token

- Normalized: `codeliver-app/prod/codeliver-app-renew-device-token`
- Method: `POST`
- Route: `/codeliver-app-renew-device-token`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-renew-device-token"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/auth/auth.service.ts:334`
```ts
renewBody
```

Observed response

Response example not observed in service code.
