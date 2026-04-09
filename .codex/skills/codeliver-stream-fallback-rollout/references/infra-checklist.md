# Infra Checklist

Use this only as a verify-only checklist unless the user explicitly asks for AWS or IaC work.

## Browser-facing stream checklist
- Verify the API Gateway route or integration is configured for response streaming.
- Verify the frontend origin is allowed by CORS.
- Verify the chosen negotiation strategy does not require extra CORS allowlist changes.
- Prefer `Accept: application/x-ndjson` over custom headers for negotiation.

## Legacy compatibility checklist
- Verify legacy callers still receive buffered JSON when they do not request NDJSON.
- Verify the main handler route still points at the same exported `handler`.
- Verify no external consumer depends on `exports.handler` always being the raw stream path.

## Runtime checklist
- Verify the terminal `complete` chunk survives the real API Gateway/browser path.
- If it does not, keep the frontend tolerant completion behavior and keep the awaited end helper in the lambda.
- Verify a zero-byte NDJSON close recovers to buffered JSON retry instead of surfacing `*_stream_incomplete`.
- Verify stream smoke tests still cover buffered fallback and error handling after each rollout.

## Out of scope by default
- No credentialed AWS CLI commands
- No API Gateway mutations
- No deploy actions
- No push actions
