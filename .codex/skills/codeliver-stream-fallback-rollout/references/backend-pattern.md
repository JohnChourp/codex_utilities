# Backend Pattern

Use this pattern for CodeDeliver frontend-facing lambdas that must stream safely without breaking old clients.

## Required backend behavior
- Negotiate streaming with `Accept: application/x-ndjson`.
- Return legacy buffered JSON when NDJSON is not explicitly requested.
- Keep public error codes and auth behavior unchanged.
- Export a clear buffered path and a clear stream path.
- Dispatch the main `handler` between buffered and stream modes instead of forcing one mode globally.
- Emit the first `meta` chunk immediately after auth validation and before any expensive collection load/scan.

## Preferred shape
- `buffered_handler(event)`
- `experimental_stream_handler_raw(event, responseStream)`
- `stream_handler = awslambda.streamifyResponse(...)`
- `handler(event, responseStream, context)` or equivalent dispatch wrapper

## Why `Accept`
- A custom header like `X-Codeliver-Response-Mode` triggered browser CORS preflight failures because API Gateway did not allow it.
- `Accept` is the proven negotiation signal for this rollout and avoids inventing a new allowlist dependency.

## Awaited close
- Do not end with a bare `responseStream.end()` and return immediately.
- Wrap the end path in an awaited helper so the lambda does not exit before the stream is flushed through the real browser/API Gateway path.
- Apply the same helper to buffered fallback response streams when the repo uses the same stream response API.

## Early meta
- A browser/API Gateway path can surface `200 + application/x-ndjson` and still close before the first useful data chunk reaches the caller.
- If the lambda waits for a full scan/query/load before sending `meta`, the frontend may see a zero-byte NDJSON success and fall into `*_stream_incomplete`.
- Validate auth first, then write `meta`, then continue with the expensive collection load and chunk emission.

## NDJSON contract
- First chunk: `meta`
- Zero or more data chunks such as `groups_chunk` or `users_chunk`
- Terminal chunk: `complete`
- Failure chunk: `error`

Do not rename stable chunk types unless the repo already uses a different contract.

## Smoke test expectations
- Assert NDJSON content type on stream path.
- Assert buffered JSON fallback on legacy path.
- Assert error path in both modes.
- Keep tests mocked and local; no network calls.

## README parity
Document:
- the `Accept: application/x-ndjson` negotiation
- buffered fallback for legacy callers
- any stream env vars such as `STREAM_PAGE_LIMIT` and `STREAM_DEBUG_DELAY_MS`
- manual infra verification when the repo does not own API Gateway
