# Safe Smoke Profiles (CodeDeliver)

Use smoke invoke only when needed and only with a valid trigger-shaped payload.

## Rules
- Prefer replaying a sanitized real event shape from recent logs.
- Add a marker field (for example `source="codex-smoke"`) so smoke invocations can be filtered.
- If trigger shape is unknown, skip smoke invoke and rely on logs + metrics.
- Do not interpret malformed smoke failures as production regressions.

## Trigger Profiles

### API Gateway (Lambda proxy)
Minimum fields expected by many CodeDeliver handlers:

```json
{
  "requestContext": {
    "authorizer": {
      "user_id": "smoke_user",
      "store_id": "0",
      "group": "smoke_group"
    }
  },
  "body": "{\"source\":\"codex-smoke\",\"probe\":\"health\"}"
}
```

### SQS

```json
{
  "Records": [
    {
      "messageId": "codex-smoke-1",
      "body": "{\"source\":\"codex-smoke\",\"probe\":\"health\"}",
      "eventSource": "aws:sqs"
    }
  ]
}
```

### EventBridge

```json
{
  "source": "codex-smoke",
  "detail-type": "codex-smoke-check",
  "detail": {
    "probe": "health"
  }
}
```

## Invocation Pattern

```bash
aws lambda invoke \
  --function-name <fn>:<alias> \
  --region <region> \
  --cli-binary-format raw-in-base64-out \
  --payload '<trigger-shaped-json>' \
  --log-type Tail \
  /tmp/<fn>-smoke.json
```

## Safety Checklist Before Invoke
- Function trigger type confirmed from logs/config.
- Payload includes required envelope fields for that trigger.
- Marker field included for downstream filtering.
- Team agreed smoke invoke is safe for the target environment.
