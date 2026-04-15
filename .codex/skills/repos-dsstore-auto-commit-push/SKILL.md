---
name: repos-dsstore-auto-commit-push
description: Auto-fix DS_Store-only repo changes, then commit and push them safely.
---

# Repos DS_Store Auto Commit Push

## Overview

Scan all Git repos under:
- `~/Downloads/lambdas`
- `~/Downloads/projects`

For each repo, act only when uncommitted changes are exclusively `.DS_Store` files:
- Ensure `.DS_Store` exists in `.gitignore`.
- Untrack tracked `.DS_Store` files with `git rm --cached`.
- Stage relevant changes.
- Commit and push to upstream branch.
- On push failures, auto-attempt safe recovery:
  - update `origin` URL when the remote reports repository relocation,
  - run `git pull --rebase --autostash` on non-fast-forward, then retry push once.

## Run

```bash
$CODEX_HOME/skills/repos-dsstore-auto-commit-push/scripts/fix_ds_store_and_commit_push.sh
```

## Optional env vars

- `TARGET_ROOTS` (default: `~/Downloads/lambdas,~/Downloads/projects`)
- `CONCURRENCY` (default: `8`)
- `REPORT_DIR` (default: `~/Downloads/_dsstore_skill_reports`)
- `COMMIT_MESSAGE` (default: `chore(gitignore): ignore .DS_Store`)
- `DRY_RUN` (default: `0`)

## Output files

- `dsstore_skill_failures.txt` (single combined failures/skip file for both lambdas + projects, overwritten on each run)

On each run, previous `dsstore_skill_*` report/history files are deleted first.

## Statuses

- `CANDIDATE_FIXED_COMMITTED_PUSHED`
- `SKIPPED_NON_DS_CHANGES`
- `SKIPPED_NOTHING_TO_COMMIT`
- `SKIPPED_SAFETY_UNEXPECTED_CHANGES`
- `COMMIT_FAILED`
- `PUSH_FAILED`
- `REPO_SCAN_FAILED`
- `SKIPPED_CLEAN`
- `DRY_RUN_CANDIDATE`
