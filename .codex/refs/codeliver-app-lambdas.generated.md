# codeliver-app frontend -> HTTP lambdas

Purpose: Document HTTP lambdas called from the frontend (from *.service.ts) with normalized paths and observed payloads/responses.

## API Ids -> API Names
- `8sw8osiclf` -> `codeliver-app`

## Sources
- `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts`

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

## codeliver-app-sync-actions

- Normalized: `codeliver-app/prod/codeliver-app-sync-actions`
- Method: `POST`
- Route: `/codeliver-app-sync-actions`
- URL: `"https://8sw8osiclf.execute-api.eu-west-1.amazonaws.com/prod/codeliver-app-sync-actions"`

Observed request payload/options

Source: `/Users/john/Downloads/projects/codeliver/codeliver-app/src/app/shared/data-storage.service.ts:363`
```ts
{ actions: actionsArray }
```

Observed response

Response example not observed in service code.
