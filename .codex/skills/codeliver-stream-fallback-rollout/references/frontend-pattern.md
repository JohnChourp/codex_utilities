# Frontend Pattern

Use this pattern only in the real frontend callers detected by code search.

## Required frontend behavior
- Request stream mode with `Accept: application/x-ndjson`.
- Use `fetch(...)` for streamed reads.
- Keep buffered JSON fallback when the backend responds with normal JSON.
- Preserve the outward contract expected by the page/component subscribers.

## Buffered fallback
- If the response is not NDJSON, parse it as the legacy buffered JSON shape.
- Do not assume every caller is upgraded at the same time.
- Keep old `HttpClient`-style expectations satisfied at the final observable or promise boundary.
- If the response negotiated NDJSON but closes without any usable chunk, retry the same endpoint once without NDJSON `Accept` before throwing `*_stream_incomplete`.

## Tolerant completion
- Track whether at least one valid data chunk arrived, for example `hasReceivedGroupsChunk` or `hasReceivedUsersChunk`.
- If the stream closes cleanly without a terminal `complete` chunk but valid data chunks already arrived and no explicit `error` chunk arrived, treat it as success.
- Emit the accumulated aggregate and log a warning instead of throwing a hard `stream_incomplete` failure.
- If the buffered success contract is an array collection where an empty result is valid, also track whether a valid `meta` chunk arrived and treat a clean meta-only close as success with an empty array result.
- For that empty-result path, clear/update the store with `[]`, emit a success payload such as `{ success: true, sockets: [] }`, and log a distinct warning for the missing terminal `complete`.
- Keep strict failures for:
- malformed or truncated JSON
- zero data chunks when the contract does not allow empty collection success
- explicit `error` chunk
- non-OK HTTP response

## Contract-aware empty collections
- Do not assume `hasReceived*Chunk` is the only safe success gate.
- Inspect the buffered success payload first. If the endpoint's normal success shape is an array collection and `[]` is a valid success value, the stream parser must also tolerate:
  - `meta` followed by `complete` with no data chunks
  - `meta` followed by a clean close with no terminal `complete`
- Example: an endpoint that normally returns `{ success: true, sockets: [] }` must not throw `stream_incomplete` merely because no `sockets_chunk` arrived.

## Update behavior
- Apply incremental store updates on each chunk when that matches the existing UX.
- Keep the final resolved value or emitted value compatible with the current page code.
- Do not change public translation keys unless the repo genuinely needs new user-facing error semantics.

## Known pitfalls
- Custom stream negotiation headers caused browser CORS failures.
- A backend that streams correctly in local smoke tests can still lose the terminal `complete` chunk through the real browser/API Gateway path.
- A backend can also negotiate NDJSON and still close with zero usable chunks if `meta` is emitted too late in the path.
- Treating every missing `complete` as fatal produced user-visible failures even when the data had already arrived.
- Treating meta-only close as fatal on empty-capable collection endpoints causes false failures and stale store state.
- File-level audits can miss this if another caller in the same file already contains the tolerance logic; audit the real caller scope.
