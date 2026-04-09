---
name: codeliver-stream-fallback-rollout
description: Audit and apply the canonical CodeDeliver rollout for frontend-facing lambdas that need NDJSON streaming with buffered fallback, backward compatibility, frontend parser tolerance, smoke tests, lint, docs, and infra verification without AWS mutations.
---

# codeliver-stream-fallback-rollout

## Overview
Use this skill when the user wants a specific CodeDeliver frontend-facing lambda to support streaming safely without breaking legacy callers.

The skill audits the target lambda repo first, auto-detects the real frontend callers, applies only the missing backend and frontend rollout pieces, validates the touched scope, and reports any external API Gateway or CORS checks the user must verify manually.

## Fast path
- If the user already gave a lambda repo path, use it directly.
- If the current working directory is the target lambda repo, use that path directly.
- Start with `python3 scripts/audit_stream_rollout_target.py --repo /abs/path/to/lambda`.
- Read only the files suggested by the audit before editing anything else.
- Preserve existing error codes, response bodies, auth behavior, and handled-error semantics.
- Do not deploy, push, or run credentialed AWS commands.

## Canonical rollout
- Backend negotiation is `Accept: application/x-ndjson`.
- Legacy callers remain buffered-by-default when NDJSON is not explicitly requested.
- Main handler dispatches between buffered and stream paths; do not point `exports.handler` blindly at the stream handler.
- Prefer exports such as `buffered_handler`, `experimental_stream_handler_raw`, and `stream_handler` when the repo style supports them.
- After auth validation, emit the initial `meta` chunk before any expensive collection load/scan so the real browser path does not end as a zero-byte NDJSON success.
- Stream shutdown must be awaited. Do not trust a bare `responseStream.end()` in production browser paths.
- Frontend callers must use `fetch(...)` for streamed reads, keep buffered JSON fallback, and tolerate a cleanly closed stream when valid data chunks already arrived but the terminal `complete` chunk is missing.
- Frontend callers must also retry the same endpoint once without NDJSON `Accept` when the response negotiated NDJSON but closed without any usable chunks before escalating to `*_stream_incomplete`.
- If the endpoint's buffered success payload allows an empty array collection result, frontend callers must also tolerate a clean meta-only close as empty success instead of requiring a data chunk.
- Never reintroduce custom negotiation headers like `X-Codeliver-Response-Mode`; they caused CORS preflight failures in production.

## Workflow
1. Run `python3 scripts/audit_stream_rollout_target.py --repo /abs/path/to/lambda`.
2. If the audit says the rollout is already complete, confirm the findings in the suggested files and stop unless the user asked for normalization.
3. Read `references/backend-pattern.md` before backend changes.
4. Read `references/frontend-pattern.md` only for the real caller files reported by the audit.
5. Read `references/infra-checklist.md` when the endpoint is browser-facing or the audit flags stream/CORS prerequisites outside the repo.
6. Apply backend rollout only where missing:
- NDJSON negotiation via `Accept`
- buffered fallback for legacy callers
- awaited stream end or buffered end path
- smoke test parity
- README parity
7. Apply frontend rollout only in the detected caller files:
- explicit `Accept: application/x-ndjson`
- streamed `fetch(...)`
- buffered JSON fallback
- one-shot buffered retry without NDJSON `Accept` for zero-byte / no-valid-chunk NDJSON closes
- inspect the buffered success payload before deciding whether `hasReceived*Chunk` can be the only success gate
- tolerant incomplete-stream success when valid chunks already arrived
- tolerant incomplete-stream success after `meta` when the endpoint allows an empty array success payload
- warning log instead of hard failure when only the terminal `complete` marker is missing
8. Run `python3 scripts/validate_stream_rollout.py --repo /abs/path/to/lambda` and then execute the suggested commands.
9. Report changed files, validation results, and only the manual infra checks that remain outside the repo.

## Guardrails
- Audit first; do not duplicate an already-correct rollout.
- Do not assume the frontend target from the lambda family alone. Use code search to find the real caller files.
- Do not switch to custom request headers for negotiation.
- Do not remove buffered JSON compatibility for legacy callers.
- Do not change public error-code values or rename NDJSON chunk types unless the repo already uses a different stable contract.
- Do not treat file-level feature presence as proof for a specific caller; audit the actual caller scope.
- Do not treat a clean stream close as failure when valid data chunks already updated the aggregate and no explicit error chunk arrived.
- Do not treat a zero-byte NDJSON close as “already complete” unless the caller retries buffered mode or the contract has an explicit alternative success path.
- Do not assume `hasReceived*Chunk` alone is sufficient for every collection endpoint; inspect whether the buffered success shape allows `[]`.
- Keep smoke tests narrow and deterministic; avoid network calls.
- Keep infra handling verify-only unless the user explicitly asks for external AWS work.

## Resources
### scripts/audit_stream_rollout_target.py
Static repo auditor that detects:
- lambda family and repo shape
- stream vs buffered handler exports
- negotiation style (`Accept` vs legacy custom header vs none)
- awaited end/flush helper presence
- smoke test and README coverage
- real frontend callers inside known CodeDeliver projects
- frontend parser/fallback/tolerance gaps

Usage:
- `python3 scripts/audit_stream_rollout_target.py --repo /abs/path/to/lambda`
- `python3 scripts/audit_stream_rollout_target.py --repo /abs/path/to/lambda --format json`

### scripts/validate_stream_rollout.py
Validation helper that converts the audit into a scoped command checklist for:
- lambda smoke tests
- lambda `npx eslint`
- frontend `npx eslint`
- Angular debug-trace audit when relevant
- manual infra verification reminders

Usage:
- `python3 scripts/validate_stream_rollout.py --repo /abs/path/to/lambda`
- `python3 scripts/validate_stream_rollout.py --repo /abs/path/to/lambda --format json`

### references/backend-pattern.md
Canonical backend pattern for:
- `Accept` negotiation
- buffered fallback
- awaited stream end
- smoke-test expectations

### references/frontend-pattern.md
Canonical frontend pattern for:
- streamed `fetch(...)`
- buffered fallback parsing
- tolerant completion when `complete` is missing
- contract-aware empty-collection success when only `meta` survives the browser/API Gateway path

### references/infra-checklist.md
Verify-only checklist for API Gateway, CORS, and response streaming prerequisites.

## Example prompts
- `Use $codeliver-stream-fallback-rollout for ~/Downloads/lambdas/codeliver_all/codeliver-sap-fetch-groups`
- `Audit whether ~/Downloads/lambdas/codeliver_all/codeliver-sap-fetch-users already has the full stream fallback rollout`
- `Apply the stream rollout with buffered backward compatibility to this CodeDeliver lambda and its real frontend callers`
