# Analysis Method

## Source of truth

- Group applicability and thresholds:
  - `codeliver-groups`
- Emergency activation runtime:
  - CloudWatch log group `/aws/lambda/codeliver-group-data-simulation`
  - CloudWatch log group `/aws/lambda/codeliver-app-sync-actions`
- Backlog reconstruction:
  - `codeliver-requests` via `group-timestamp-index`
  - `codeliver-requests-actions` via primary key `group_request_id`
- Current pending snapshot (fast stage):
  - `codeliver-requests` via `group-status-index` (`status = pending`)
- Current simulation-driver snapshot:
  - `codeliver-delivery-guys`

## Backlog definition

The skill reconstructs the same business condition used by `codeliver-group-data-simulation`:

- `status = pending`
- `readyToPickUp = true`
- no `route_id`
- no `delivery_guy_id`
- age from `readyToPickUp_timestamp` at least `SIMULATION_EMERGENCY_MIN_READY_UNASSIGNED_WAIT_MINUTES`

## Two-stage execution model

### Stage A (fast diagnosis)

Computes a read-only current snapshot using the same eligibility gates as the lambda:

- `pending_count`
- `unassigned_count` (`pending` + no `route_id` + no `delivery_guy_id`)
- `ready_unassigned_count` (unassigned + `readyToPickUp = true`)
- `ready_unassigned_aged_threshold_count` (ready-unassigned + age >= wait threshold)

Stage A also correlates CloudWatch emergency logs and current eligible off-duty simulation drivers.

In `auto` mode, Stage A short-circuits when signals are clear; otherwise it escalates to Stage B.
In `quick` mode, Stage A is the final result.

### Stage B (exact reconstruction)

For each request:

1. Read request action history.
2. Start a candidate backlog interval at `request_ready_to_be_picked_up.timestamp`.
3. End the interval on the earliest of:
   - `request_routed`
   - `request_assigned_to_delivery_guy`
   - `request_pending`
   - `request_completed`
   - `request_canceled`
4. Apply the wait gate by shifting the effective interval start forward by the threshold wait minutes.
5. Sweep all effective intervals to calculate:
   - `peak_backlog_count`
   - `peak_windows`
   - `threshold_breach_windows`

## Reason bucket rules

- `feature_not_applicable`
  - group missing
  - `simulation != true`
- `activation_done`
  - any `simulation_emergency_activation_done` log
  - or any `delivery_guy_status_emergency_activation` log in `codeliver-app-sync-actions`
- `threshold_not_reached`
  - Stage A short-circuit: snapshot aged ready-unassigned below threshold and no backlog/attempt logs
  - Stage B exact-mode: `peak_backlog_count < threshold`
- `no_eligible_off_duty_simulation_driver`
  - explicit `simulation_emergency_activation_skipped` log with `reason: no_eligible_off_duty_delivery_guy`
  - or heuristic fallback when threshold is breached and current eligible off-duty snapshot count is zero
- `activation_attempted_but_not_persisted`
  - `simulation_emergency_backlog_detected` or `simulation_emergency_activation_attempted`
  - but no activation-done evidence

## Confidence notes

- The strongest evidence is explicit CloudWatch emergency logs.
- The exact backlog reconstruction is deterministic for the requested range.
- Stage A `threshold_not_reached` is intentionally **medium** confidence unless exact reconstruction runs.
- Carry-over backlog from before the requested range can be missed unless `--deep-lookback-hours` is provided.
- The current eligible off-duty snapshot is a heuristic fallback, not a historical truth snapshot.
- Reports expose `exact_executed` and `short_circuit_reason` for traceability.
