---
name: codeliver-link-missing-cloud-repos
description: Find `codeliver-*` repos from Cloud Repos Panel S3 inventory (`ORG-repos.json`) that are missing from the CRP project `codeliver`, then auto-link them to the best existing feature (or fallback feature). Use when the user asks to sync missing cloud repos into the project automatically.
---

# Codeliver Link Missing Cloud Repos

## Overview
Run one command to sync missing `codeliver-*` repos from S3 to CRP project links with deterministic rules and a JSON report.

## Workflow
1. Verify prerequisites.
- `crp` is logged in (`~/.crp/config.json` has token).
- AWS CLI credentials can read `s3://cloud-repos-panel-data/<org>-repos.json`.

2. Run the sync script.
- Dry run first:
```bash
python3 scripts/sync_missing_cloud_repos.py --dry-run
```
- Apply links:
```bash
python3 scripts/sync_missing_cloud_repos.py
```

3. Review the generated report.
- Default output: `./missing-cloud-repos-sync-report.json`
- Report includes:
- missing repos found
- target feature selected per repo
- created fallback subproject/feature (if any)
- link success/failure per repo

## Placement Rules
1. Compute missing repos as:
- repos in S3 `<org>-repos.json` matching prefix (`codeliver-` by default)
- minus repos already linked to the target project.

2. Pick target feature per missing repo:
- Score repo name tokens against all project feature name tokens.
- If score is above threshold (`--min-match-score`, default `2`), link to best-scored feature.
- Otherwise link to fallback feature (`uncategorized-repos` by default).

3. Fallback bootstrap:
- If fallback feature is missing and auto-create is enabled, create:
- subproject: `cloud-repos-auto-linking` (or `--auto-subproject-name`)
- feature: fallback feature name (or `--auto-feature-name` if fallback is an id)

## Script
`scripts/sync_missing_cloud_repos.py`

Useful flags:
- `--dry-run`
- `--project-name codeliver`
- `--project-id <id>`
- `--fallback-feature uncategorized-repos`
- `--min-match-score 2`
- `--bucket cloud-repos-panel-data`
- `--crp-org admin`
- `--out /tmp/report.json`
