# codeliver-pos frontend -> HTTP lambdas

Purpose: Document HTTP lambdas called from the frontend (from *.service.ts) with normalized paths and observed payloads/responses.

## API Ids -> API Names
- `n4motxwuya` -> `codeliver-pos`

## Sources
- `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts`
- `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/auth/auth.service.ts`

## test-connection

- Normalized: `codeliver-pos/prod/test-connection`
- Method: `POST`
- Route: `/test-connection`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/test-connection"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:94`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-pos-handle-store

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-store`
- Method: `POST`
- Route: `/codeliver-pos-handle-store`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-handle-store"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:265`
```ts
{ store, type }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:284`
```ts
{
        type: "update",
        pos_user_updates: posUserUpdates,
      }
```

Observed response

Response example not observed in service code.

## codeliver-pos-handle-customer

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-customer`
- Method: `POST`
- Route: `/codeliver-pos-handle-customer`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-handle-customer"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:311`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-pos-fetch-delivery-guys-positions

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-delivery-guys-positions`
- Method: `POST`
- Route: `/codeliver-pos-fetch-delivery-guys-positions`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-fetch-delivery-guys-positions"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:339`
```ts
{
        type,
        delivery_guy_id,
      }
```

Observed response

Response example not observed in service code.

## codeliver-pos-fetch-zones

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-zones`
- Method: `POST`
- Route: `/codeliver-pos-fetch-zones`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-fetch-zones"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:371`
```ts
{}
```

Observed response

Response example not observed in service code.

## codeliver-pos-fetch-delivery-guys

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-delivery-guys`
- Method: `POST`
- Route: `/codeliver-pos-fetch-delivery-guys`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-fetch-delivery-guys"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:385`
```ts
{ type }
```

Observed response

Response example not observed in service code.

## codeliver-pos-search-delivery-requests

- Normalized: `codeliver-pos/prod/codeliver-pos-search-delivery-requests`
- Method: `POST`
- Route: `/codeliver-pos-search-delivery-requests`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-search-delivery-requests"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:422`
```ts
{
        type,
        phone,
        delivery_guy_id,
        status,
        exclusiveStartKey,
        route_id,
        nextShortCfRequestId,
      }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:450`
```ts
{
        type,
        statuses,
      }
```
Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:504`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-pos-fetch-delivery-guy-path

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-delivery-guy-path`
- Method: `POST`
- Route: `/codeliver-pos-fetch-delivery-guy-path`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-fetch-delivery-guy-path"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:516`
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

## codeliver-pos-handle-route

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-route`
- Method: `POST`
- Route: `/codeliver-pos-handle-route`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-handle-route"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:536`
```ts
{
        type,
        delivery_guy_id,
        requests,
      }
```

Observed response

Response example not observed in service code.

## codeliver-pos-handle-delivery-request

- Normalized: `codeliver-pos/prod/codeliver-pos-handle-delivery-request`
- Method: `POST`
- Route: `/codeliver-pos-handle-delivery-request`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-handle-delivery-request"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:560`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-pos-search-customers

- Normalized: `codeliver-pos/prod/codeliver-pos-search-customers`
- Method: `POST`
- Route: `/codeliver-pos-search-customers`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-search-customers"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:578`
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

## codeliver-pos-user-remind-password

- Normalized: `codeliver-pos/prod/codeliver-pos-user-remind-password`
- Method: `POST`
- Route: `/codeliver-pos-user-remind-password`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-user-remind-password"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:599`
```ts
{
        mobile: number,
      }
```

Observed response

Response example not observed in service code.

## codeliver-pos-fetch-routes

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-routes`
- Method: `POST`
- Route: `/codeliver-pos-fetch-routes`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-fetch-routes"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:614`
```ts
{ type, lastKey, route_id }
```

Observed response

Response example not observed in service code.

## codeliver-pos-fetch-routes-paths

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-routes-paths`
- Method: `POST`
- Route: `/codeliver-pos-fetch-routes-paths`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-fetch-routes-paths"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:633`
```ts
{ type, route_id }
```

Observed response

Response example not observed in service code.

## codeliver-pos-fetch-routes-paths-calculations

- Normalized: `codeliver-pos/prod/codeliver-pos-fetch-routes-paths-calculations`
- Method: `POST`
- Route: `/codeliver-pos-fetch-routes-paths-calculations`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-fetch-routes-paths-calculations"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/data.storage.service.ts:665`
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

## codeliver-pos-login

- Normalized: `codeliver-pos/prod/codeliver-pos-login`
- Method: `POST`
- Route: `/codeliver-pos-login`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-login"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/auth/auth.service.ts:106`
```ts
payload
```

Observed response

Response example not observed in service code.

## codeliver-pos-renew-token

- Normalized: `codeliver-pos/prod/codeliver-pos-renew-token`
- Method: `POST`
- Route: `/codeliver-pos-renew-token`
- URL: `"https://n4motxwuya.execute-api.eu-west-1.amazonaws.com/prod/codeliver-pos-renew-token"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-pos/src/app/shared/auth/auth.service.ts:164`
```ts
payload
```

Observed response

Response example not observed in service code.
