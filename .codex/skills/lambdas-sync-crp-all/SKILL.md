---
name: lambdas-sync-crp-all
description: Sync all git repos under crp_all with fetch/pull, auto-reclone empty repos, and write txt reports for failures and skipped pulls.
---

# Lambdas Sync `crp_all`

## Overview

Sync all immediate repo folders under:
`/Users/john/Downloads/lambdas/crp_all`

Behavior:
- Runs `git fetch --all --prune` on each repo.
- Runs `git pull --ff-only` only when safe.
- If repo has unborn `HEAD`, deletes and reclones from `origin`.
- If repo is dirty, skips pull and records `SKIPPED_PULL_DIRTY`.

## Run

```bash
~/.codex/skills/lambdas-sync-crp-all/scripts/sync_crp_all.sh
```

## Optional env vars

- `CONCURRENCY` (default: `20`)
- `REPORT_DIR` (default: `/Users/john/Downloads/lambdas/_sync_reports`)

## Output files

- `crp_all_sync_report_<timestamp>.txt` (all repo statuses)
- `crp_all_sync_failures_<timestamp>.txt` (failed + skipped-pull statuses)

## Statuses

- `SYNCED`
- `FETCH_FAILED`
- `PULL_FAILED`
- `RECLONE_FAILED`
- `RECLONED`
- `RECLONED_BUT_EMPTY`
- `SKIPPED_PULL_DIRTY`
- `SKIPPED_PULL_NO_UPSTREAM`
- `SKIPPED_NOT_GIT_TOPLEVEL`

