---
name: "Codeliver Link Repos"
description: Sync CodeDeliver repos locally and in cloud, including missing cloud-repo auto-linking.
---

# Codeliver Link Repos

## Overview

Sync workflow for Codeliver repositories based on:
- GitHub org repos where name contains `codeliver-` (archived excluded by default), and
- cloud repos already linked in codeliver project `codeliver`.

Default behavior:
1. Discover GitHub repos that match `codeliver-`.
2. Build target set:
   - matched GitHub repos
   - plus special repos: `codeliver-sap`, `codeliver-panel`, `codeliver-pos`, `codeliver-app`, `codeliver-cost-wizard-react`, `codeliver-website`, `codeliver-integration-partners`, `codeliver-partners-panel`, `codeliver-io`
3. Auto-create missing cloud repo links in codeliver project `codeliver`:
   - in subproject `cloud-repos-auto-linking` (created if missing)
   - in feature `auto-linked-codeliver-repos` (created if missing)
4. Local sync/clone:
   - `codeliver-sap`, `codeliver-panel`, `codeliver-pos`, `codeliver-app`, `codeliver-cost-wizard-react`, `codeliver-website`, `codeliver-integration-partners`, `codeliver-partners-panel`, `codeliver-io` -> `/Users/john/Downloads/projects/<repo>`
   - all other target repos -> `/Users/john/Downloads/lambdas/codeliver_all/<repo>`
   - existing repos: `fetch --all --prune` + `pull --ff-only`
   - missing repos: clone with preferred protocol; auto-fallback from SSH to HTTPS on publickey failures
5. Refresh project repo artifacts:
  - `/Users/john/Downloads/lambdas/codeliver_all/current-codeliver-project-repos-full-list.json`
  - single-file artifact with all cloud repos found by scanning all features of the selected project (`search_mode: all-features`; fallback to project-level list only if feature-level API is unavailable)
  - cleanup of legacy text/json sync artifacts so only the JSON list remains persisted

## Auth + non-blocking behavior

- Cloud-link stage requires auth token at `~/.codeliver/config.json` (`api.auth.token`).
- If `~/.codeliver/config.json` is missing/empty but env var `CODELIVER_AUTH_TOKEN` exists, the orchestrator auto-bootstraps/updates `~/.codeliver/config.json` before cloud stage.
- If auth is still missing:
  - default run (`codeliver_all.sh`) does **not** block; it skips cloud-link and falls back to local-only sync using discovered local `codeliver-*` repos.
  - explicit cloud-only run (`--only-cloud-link-clone`) fails fast with a clear auth error.
- Special project repos are resolved in both layouts:
  - `/Users/john/Downloads/projects/<repo>`
  - `/Users/john/Downloads/projects/codeliver/<repo>` (auto-detected/preferred when present)

## Run

```bash
~/.codex/skills/codeliver-link-missing-cloud-repos/scripts/codeliver_all.sh
```

Only local git sync (from target repos file):

```bash
~/.codex/skills/codeliver-link-missing-cloud-repos/scripts/codeliver_all.sh --only-sync
```

Only cloud-link + local clone/sync stage:

```bash
~/.codex/skills/codeliver-link-missing-cloud-repos/scripts/codeliver_all.sh --only-cloud-link-clone
```

Dry run:

```bash
~/.codex/skills/codeliver-link-missing-cloud-repos/scripts/codeliver_all.sh --dry-run
```

Force HTTPS clone preference:

```bash
~/.codex/skills/codeliver-link-missing-cloud-repos/scripts/codeliver_all.sh --clone-prefer https
```

Bootstrap config on the fly (single run) with env token:

```bash
CODELIVER_AUTH_TOKEN="<your-token>" ~/.codex/skills/codeliver-link-missing-cloud-repos/scripts/codeliver_all.sh
```

## Main Arguments (cloud stage)

- `--project-name` (default: `codeliver`)
- `--api-route-prefix` (default: `crp`)
- `--project-id` (optional override)
- `--name-contains` (default: `codeliver-`)
- `--include-special-repos` (default: `codeliver-sap,codeliver-panel,codeliver-pos,codeliver-app,codeliver-cost-wizard-react,codeliver-website,codeliver-integration-partners,codeliver-partners-panel,codeliver-io`)
- `--exclude-archived` (default enabled)
- `--include-archived` (override)
- `--auto-subproject-name` (default: `cloud-repos-auto-linking`)
- `--auto-feature-name` (default: `auto-linked-codeliver-repos`)
- `--clone-prefer` (`ssh` or `https`, default: `ssh`)
- `--github-org` (optional override)
- `--repos-list-out` (default: `/Users/john/Downloads/lambdas/codeliver_all/current-codeliver-target-repos.txt`)
- `--out` (default: `/Users/john/Downloads/lambdas/codeliver_all/codeliver-cloud-repos-sync-report.json`)
- `--all-cloud-repos-out` (default: `/Users/john/Downloads/lambdas/codeliver_all/current-codeliver-project-repos-full-list.json`)
- `--dry-run`
- `--no-local-sync`

## Optional env vars

- `CONCURRENCY` (default: `20`) for sync stage
- `REPORT_DIR` (default: `/Users/john/Downloads/lambdas/_sync_reports`) for sync stage text reports
- `CODELIVER_AUTH_TOKEN` (optional) auto-bootstrap token for `~/.codeliver/config.json` when missing

## Output files

- Persisted output:
  - `/Users/john/Downloads/lambdas/codeliver_all/current-codeliver-project-repos-full-list.json` (single file with all cloud repos found from all-features search for the selected project)
- Non-persisted (temporary during run):
  - cloud stage report
  - target repos list
  - sync text reports

## CRP project mode

For project `crp`, run with:

```bash
~/.codex/skills/codeliver-link-missing-cloud-repos/scripts/codeliver_all.sh --project-name crp --api-route-prefix crp
```

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

- Orchestrator: `scripts/codeliver_all.sh`
- Sync-only stage: `scripts/sync_codeliver_all.sh`
- Cloud-link + local sync stage: `scripts/sync_codeliver_cloud_repos.py`
