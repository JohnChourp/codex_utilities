---
name: codeliver-simulation-emergency-audit
description: Audit CodeDeliver simulation emergency congestion for a specific group and date range. Use when the user wants to know whether a group actually bottlenecked, what the peak ready-unassigned backlog was, and why emergency off-duty delivery-guy activation did or did not happen.
---

# CodeDeliver Simulation Emergency Audit

Use this skill when the question is specifically about simulation emergency activation, backlog congestion, or why an off-duty simulation delivery guy was not auto-activated.

## What this skill answers

- Whether the group is eligible for simulation emergency activation.
- The effective emergency thresholds from `codeliver-groups`.
- Whether `delivery_guy_status_emergency_activation` actually happened.
- The peak `pending + readyToPickUp + no route_id + no delivery_guy_id` backlog for the requested range.
- Which reason bucket best explains the outcome:
  - `feature_not_applicable`
  - `threshold_not_reached`
  - `no_eligible_off_duty_simulation_driver`
  - `activation_attempted_but_not_persisted`
  - `activation_done`

## Important scope boundary

- `alert_promotion_mode` and `default_alert_all_after_alerted_count` belong to route alert queue promotion.
- They do **not** auto-switch an off-duty delivery guy to `available`.
- Emergency activation is implemented by `codeliver-group-data-simulation` through `delivery_guy_status_emergency_activation`.

## How to run

Prefer the bundled script instead of ad-hoc shell snippets:

```bash
python3 ~/.codex/skills/codeliver-simulation-emergency-audit/scripts/run.py audit nikitas --date 2026-03-12
```

Useful variants:

```bash
python3 ~/.codex/skills/codeliver-simulation-emergency-audit/scripts/run.py audit nikitas --date 2026-03-12 --mode quick
python3 ~/.codex/skills/codeliver-simulation-emergency-audit/scripts/run.py audit nikitas --from 2026-03-12T00:00:00 --to 2026-03-12T23:59:59 --timezone Europe/Athens
python3 ~/.codex/skills/codeliver-simulation-emergency-audit/scripts/run.py audit nikitas --date 2026-03-12 --deep-lookback-hours 24 --json
python3 ~/.codex/skills/codeliver-simulation-emergency-audit/scripts/run.py test
```

## Modes

- `quick`
  - Reads `codeliver-groups`
  - Checks current simulation/off-duty snapshot
  - Queries CloudWatch logs in `codeliver-group-data-simulation` and `codeliver-app-sync-actions`
  - Fast verdict only
- `exact`
  - Adds `codeliver-requests` + per-request `codeliver-requests-actions` reconstruction
  - Computes peak ready-unassigned backlog and breach windows
  - Correlates backlog with current eligible emergency-driver snapshot and emergency logs/actions

## References

- Method details and evidence mapping: `references/analysis-method.md`
- The executable logic lives in `scripts/simulation_emergency_audit.py`

