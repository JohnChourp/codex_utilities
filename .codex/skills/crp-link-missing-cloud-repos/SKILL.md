---
name: "CRP Link Repos"
description: Sync CRP repos locally and in cloud, including missing cloud-repo auto-linking.
---

# CRP Link Repos

## Overview

Sync workflow for CRP repositories based on:
- GitHub org repos where name contains `crp-` (archived excluded by default), and
- cloud repos already linked in CRP project `crp`.

Default behavior:
1. Discover GitHub repos that match `crp-`.
2. Build target set:
   - matched GitHub repos
   - plus special repos: `cloud-repos-panel`, `crp-cli`
3. Auto-create missing cloud repo links in CRP project `crp`:
   - in subproject `cloud-repos-auto-linking` (created if missing)
   - in feature `auto-linked-crp-repos` (created if missing)
4. Local sync/clone:
   - `cloud-repos-panel`, `crp-cli` -> `/Users/john/Downloads/projects/<repo>`
   - all other target repos -> `/Users/john/Downloads/lambdas/crp_all/<repo>`
   - existing repos: `fetch --all --prune` + `pull --ff-only`
   - missing repos: clone with preferred protocol; auto-fallback from SSH to HTTPS on publickey failures
5. Refresh project repo artifacts:
  - `/Users/john/Downloads/lambdas/crp_all/current-crp-project-repos-full-list.json`
  - `/Users/john/Downloads/lambdas/crp_all/current-crp-cloud-repos-from-all-features.txt` (single file with all unique cloud repos found by scanning all features in project `crp`)
  - cleanup of legacy sync artifacts while keeping the canonical JSON list and the feature-based cloud-repos list persisted

## Run

```bash
~/.codex/skills/crp-link-missing-cloud-repos/scripts/crp_all.sh
```

Only local git sync (from target repos file):

```bash
~/.codex/skills/crp-link-missing-cloud-repos/scripts/crp_all.sh --only-sync
```

Only cloud-link + local clone/sync stage:

```bash
~/.codex/skills/crp-link-missing-cloud-repos/scripts/crp_all.sh --only-cloud-link-clone
```

Dry run:

```bash
~/.codex/skills/crp-link-missing-cloud-repos/scripts/crp_all.sh --dry-run
```

Force HTTPS clone preference:

```bash
~/.codex/skills/crp-link-missing-cloud-repos/scripts/crp_all.sh --clone-prefer https
```

## Main Arguments (cloud stage)

- `--project-name` (default: `crp`)
- `--project-id` (optional override)
- `--name-contains` (default: `crp-`)
- `--include-special-repos` (default: `cloud-repos-panel,crp-cli`)
- `--exclude-archived` (default enabled)
- `--include-archived` (override)
- `--auto-subproject-name` (default: `cloud-repos-auto-linking`)
- `--auto-feature-name` (default: `auto-linked-crp-repos`)
- `--clone-prefer` (`ssh` or `https`, default: `ssh`)
- `--github-org` (optional override)
- `--repos-list-out` (default: `/Users/john/Downloads/lambdas/crp_all/current-crp-target-repos.txt`)
- `--features-cloud-repos-out` (default: `/Users/john/Downloads/lambdas/crp_all/current-crp-cloud-repos-from-all-features.txt`)
- `--out` (default: `/Users/john/Downloads/lambdas/crp_all/crp-cloud-repos-sync-report.json`)
- `--dry-run`
- `--no-local-sync`

## Optional env vars

- `CONCURRENCY` (default: `20`) for sync stage parallel workers
- `REPORT_DIR` (default: `/Users/john/Downloads/lambdas/_sync_reports`) for sync stage text reports

## Output files

- Persisted output:
  - `/Users/john/Downloads/lambdas/crp_all/current-crp-project-repos-full-list.json`
  - `/Users/john/Downloads/lambdas/crp_all/current-crp-cloud-repos-from-all-features.txt`
- Non-persisted (temporary during run):
  - cloud stage report
  - target repos list
  - sync text reports

## JSON report fields (cloud stage)

- `github_repo_count`
- `github_filtered_repo_count`
- `missing_cloud_repo_count`
- `created_cloud_repo_count`
- `local_sync_summary`
- `repos[]` entries with:
  - `cloud_status` (`already_linked`, `cloud_linked`, `cloud_link_planned`, `cloud_link_failed`)
  - `local_status` (`synced`, `cloned`, `exists`, `skipped_dirty`, `clone_failed`, etc.)

## Scripts

- Orchestrator: `scripts/crp_all.sh`
- Sync-only stage: `scripts/sync_crp_all.sh`
- Cloud-link + local sync stage: `scripts/sync_crp_cloud_repos.py`
