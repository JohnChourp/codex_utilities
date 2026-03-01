---
name: crp-npm-install-repos
description: Install npm dependencies across already-downloaded local CRP lambda repos under `/Users/john/Downloads/lambdas/crp_all` by running `npm i` per repo. Use when the user asks for bulk dependency install/refresh in all local CRP lambdas.
---

# CRP npm install Repos

## Overview

Run `npm i` in every direct child repo under `crp_all` that contains a `package.json`.
Use this skill for one-shot dependency bootstrap or refresh across all local CRP lambdas.

## Run

```bash
~/.codex/skills/crp-npm-install-repos/scripts/npm_install_all_crp_repos.sh
```

Dry run:

```bash
~/.codex/skills/crp-npm-install-repos/scripts/npm_install_all_crp_repos.sh --dry-run
```

Custom root:

```bash
~/.codex/skills/crp-npm-install-repos/scripts/npm_install_all_crp_repos.sh --root /path/to/repos
```

## Behavior

- Scan direct subfolders inside the root path.
- Run `npm i` only in folders that contain `package.json`.
- Continue on failures and print a summary.
- Exit with non-zero status when at least one repo fails.

## Script

- `scripts/npm_install_all_crp_repos.sh`
