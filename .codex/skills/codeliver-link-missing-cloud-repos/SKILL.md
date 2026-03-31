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
   - `codeliver-sap`, `codeliver-panel`, `codeliver-pos`, `codeliver-app`, `codeliver-cost-wizard-react`, `codeliver-website`, `codeliver-integration-partners`, `codeliver-partners-panel`, `codeliver-io` -> `~/Downloads/projects/<repo>`
   - all other target repos -> `~/Downloads/lambdas/codeliver_all/<repo>`
   - existing repos: `fetch --all --prune` + `pull --ff-only` only when the working tree is clean
   - exception: if the only local dirty file is `package-lock.json`, the sync stage auto-reverts that file and continues with `pull --ff-only`
   - dirty repos are never auto-stashed or auto-merged; the sync report now records their `ahead/behind` state after fetch
   - if a dirty repo is still behind its upstream after fetch, the repo is reported as a sync failure (`SKIPPED_PULL_DIRTY_BEHIND` / `SKIPPED_PULL_DIRTY_DIVERGED`) so it cannot be mistaken for a successful sync
   - successful pulls now also print a one-line summary for how many repos were actually behind upstream commits and received the latest changes during this run
   - missing repos: clone with preferred protocol; auto-fallback from SSH to HTTPS on publickey failures
5. Refresh project repo artifacts:
  - `~/Downloads/lambdas/codeliver_all/current-codeliver-project-repos-full-list.json`
  - single-file artifact with all cloud repos found by scanning all features of the selected project (`search_mode: all-features`; fallback to project-level list only if feature-level API is unavailable)
  - cleanup of legacy text/json sync artifacts so only the JSON list remains persisted

## Auth + non-blocking behavior

- Cloud-link stage resolves auth config by API route prefix:
  - `crp-*` endpoints use `~/.crp/config.json`
  - other prefixes use `~/.codeliver/config.json`
- For `crp-*` endpoints this means the skill uses the DM/CRP organization credentials by default.
- If the selected config is `~/.codeliver/config.json` and it is missing/empty while env var `CODELIVER_AUTH_TOKEN` exists, the orchestrator auto-bootstraps/updates `~/.codeliver/config.json` before cloud stage.
- Tokens that look like GitHub PATs (`ghp_...`, `github_pat_...`) are rejected as invalid API auth tokens.
- If the cloud API returns `401 Unauthorized`, rerun `crp token renew` or `crp login` and then retry the skill.
- If auth is still missing:
  - default run (`codeliver_all.sh`) does **not** block; it skips cloud-link and falls back to local-only sync using discovered local `codeliver-*` repos.
  - explicit cloud-only run (`--only-cloud-link-clone`) fails fast with a clear auth error.
- If cloud API calls fail during the default run, the orchestrator also stays non-blocking:
  - it falls back to cached target repos when available
  - otherwise it rebuilds the target list from local `codeliver-*` directories and continues the git sync stage
  - explicit cloud-only run (`--only-cloud-link-clone`) still fails fast so cloud issues remain visible when requested
- Special project repos are resolved in both layouts:
  - `~/Downloads/projects/<repo>`
  - `~/Downloads/projects/codeliver/<repo>` (auto-detected/preferred when present)

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
- `--repos-list-out` (default: `~/Downloads/lambdas/codeliver_all/current-codeliver-target-repos.txt`)
- `--out` (default: `~/Downloads/lambdas/codeliver_all/codeliver-cloud-repos-sync-report.json`)
- `--all-cloud-repos-out` (default: `~/Downloads/lambdas/codeliver_all/current-codeliver-project-repos-full-list.json`)
- `--dry-run`
- `--no-local-sync`

## Optional env vars

- `CONCURRENCY` (default: `20`) for sync stage parallel workers
- `REPORT_DIR` (default: `~/Downloads/lambdas/_sync_reports`) for sync stage text reports
- `CODELIVER_AUTH_TOKEN` (optional) auto-bootstrap token for `~/.codeliver/config.json` when missing

## Output files

- Persisted output:
  - `~/Downloads/lambdas/codeliver_all/current-codeliver-project-repos-full-list.json` (single file with all cloud repos found from all-features search for the selected project)
- Non-persisted (temporary during run):
  - cloud stage report
  - target repos list
  - sync text reports

## Dirty repo safety

- The sync stage always runs `fetch` first.
- If the only local dirty file is `package-lock.json`, the skill reverts that file automatically and proceeds with sync.
- If the repo has local uncommitted changes, the skill does not run `pull --ff-only`.
- The report detail includes the branch divergence against upstream after fetch.
- If the repo is dirty and `behind > 0`, treat that repo as not synced and resolve it manually by either committing/stashing/discarding local changes and rerunning the sync, or pulling the repo explicitly once it is clean.

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
- stdout one-line summary: `Repos updated from behind: <count>`
- `repos[]` entries with:
  - `cloud_status` (`already_linked`, `cloud_linked`, `cloud_link_planned`, `cloud_link_failed`)
  - `local_status` (`synced`, `cloned`, `exists`, `skipped_dirty`, `clone_failed`, etc.)

## Scripts

- Orchestrator: `scripts/codeliver_all.sh`
- Sync-only stage: `scripts/sync_codeliver_all.sh`
- Cloud-link + local sync stage: `scripts/sync_codeliver_cloud_repos.py`
