---
name: codeliver-npm-install-repos
description: Run bulk npm install across already-downloaded local CodeDeliver lambda repositories.
---

# Codeliver npm install Repos

## Overview

Run `npm i` in every direct child repo under `codeliver_all` that contains a `package.json`.
Use this skill for one-shot dependency bootstrap or refresh across all local Codeliver lambdas.
The default run uses `CONCURRENCY=20` parallel workers.

## Run

```bash
~/.codex/skills/codeliver-npm-install-repos/scripts/npm_install_all_codeliver_repos.sh
```

Dry run:

```bash
~/.codex/skills/codeliver-npm-install-repos/scripts/npm_install_all_codeliver_repos.sh --dry-run
```

Custom root:

```bash
~/.codex/skills/codeliver-npm-install-repos/scripts/npm_install_all_codeliver_repos.sh --root /path/to/repos
```

Override concurrency:

```bash
CONCURRENCY=10 ~/.codex/skills/codeliver-npm-install-repos/scripts/npm_install_all_codeliver_repos.sh
```

## Behavior

- Scan direct subfolders inside the root path.
- Run `npm i` only in folders that contain `package.json`.
- Run installs in parallel with default `CONCURRENCY=20`.
- Continue on failures and print a summary.
- Exit with non-zero status when at least one repo fails.

## Optional env vars

- `CONCURRENCY` (default: `20`) for parallel npm install workers

## Script

- `scripts/npm_install_all_codeliver_repos.sh`
