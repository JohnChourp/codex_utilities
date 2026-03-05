# Health Verdict Filters

Use this to avoid false regressions caused by smoke/test invocations.

## Classification
- `production_failure`: failed request id with no smoke/test marker.
- `smoke_or_test_failure`: failed request id where logs contain a known smoke/test marker.
- `critical_signature`: one of:
  - `bridge_order_update_status_error`
  - `wolt_update_bridge_order_failed`
  - `Runtime.ImportModuleError`
  - `Task timed out`
  - `Process exited before completing request`

## Smoke/Test Markers
Treat as smoke/test when any marker matches:
- `source":"codex-smoke"`
- `source":"crp-smoke"`
- `smoke_group`
- `barcode_scanner_id":"smoke"`
- other explicit test markers present in the payload/event

## Suggested Log Scan Flow

```bash
aws logs tail /aws/lambda/<fn> --region <region> --since 30m --format short > /tmp/<fn>.log
```

Collect failed request ids:

```bash
rg "RequestId: .* FAILED|RequestId FAILED" /tmp/<fn>.log
```

For each failed request id, inspect neighboring lines for smoke/test markers.

Scan critical signatures:

```bash
rg "bridge_order_update_status_error|wolt_update_bridge_order_failed|Runtime\\.ImportModuleError|Task timed out|Process exited before completing request" /tmp/<fn>.log
```

## Verdict Rule
Set `healthy_after_fix` only if:
- `production_failures = 0`, and
- `critical_signatures = 0`

Always report:
- UTC window used
- `production_failures`
- `smoke_or_test_failures`
- `critical_signatures`
