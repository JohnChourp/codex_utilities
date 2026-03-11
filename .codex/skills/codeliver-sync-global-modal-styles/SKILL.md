---
name: codeliver-sync-global-modal-styles
description: Sync shared modal global.scss selectors from codeliver-panel into parity targets safely.
---

# codeliver-sync-global-modal-styles

## Overview
Use this skill when you need to keep `global.scss` modal sizing/styling logic in sync across CodeDeliver frontends.

Source of truth:
- `projects/codeliver/codeliver-panel/src/global.scss`

Targets:
- `projects/codeliver/codeliver-sap/src/global.scss`
- `projects/codeliver/codeliver-pos/src/global.scss`

Sync policy:
- exact selector-name parity only
- modal selectors (`modal`/`Modal`) + configured modal utility allowlist
- panel wins unless selector/context is denied in config
- insertion of missing selector-context blocks is disabled by default (`allow_insertions: false`) for safe-first runs

## Commands
From any working directory:

```bash
python3 "$HOME/.codex/skills/codeliver-sync-global-modal-styles/scripts/sync_global_modals.py" \
  --mode dry-run \
  --targets sap,pos \
  --source panel-local \
  --selector-policy exact-names \
  --include-utilities \
  --report ./modal-sync-report.json
```

Apply changes:

```bash
python3 "$HOME/.codex/skills/codeliver-sync-global-modal-styles/scripts/sync_global_modals.py" \
  --mode apply \
  --targets sap,pos \
  --source panel-local \
  --selector-policy exact-names \
  --include-utilities \
  --report ./modal-sync-report.json
```

## Options
- `--mode dry-run|apply` (default: `dry-run`)
- `--targets sap,pos` (comma-separated)
- `--source panel-local|panel-head` (default: `panel-local`)
- `--selector-policy exact-names` (required value)
- `--include-utilities` / `--no-include-utilities`
- `--report <path>`
- `--codeliver-root <path>` (default: `/home/dm-soft-1/Downloads/projects/codeliver`)

## Resources
- `references/modal_sync_config.json`: utility allowlist + deny rules + insertion policy
- `scripts/sync_global_modals.py`: core analyzer/apply engine + report generation

## Guardrails
- Never touch non-modal selectors.
- Never overwrite target-only selectors that do not exist in panel.
- Respect denylist selectors/contexts from config.
- Keep changes scoped to target `src/global.scss` files only.
