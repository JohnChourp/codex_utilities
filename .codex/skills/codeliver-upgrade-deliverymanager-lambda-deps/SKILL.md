---
name: codeliver-upgrade-deliverymanager-lambda-deps
description: Upgrade one CodeDeliver lambda's @deliverymanager/* packages to the newest compatible versions by trying npm registry versions from latest to older, restoring the repo state on failed attempts, and keeping the first version that passes local validation.
---

# Codeliver Upgrade deliverymanager Lambda Dependencies

## Overview

Use this skill for a single lambda repo under the local CodeDeliver lambdas root when you want to upgrade only `@deliverymanager/*` packages with automatic fallback to older versions.

The skill:

- scans one lambda repo by exact folder name
- finds every `@deliverymanager/*` dependency in `dependencies` and `devDependencies`
- resolves available versions live from npm
- tries the newest stable version first, then walks backwards
- keeps the first version that passes local compatibility validation
- restores the previous repo state if a candidate fails
- stops with a failure if any package has no compatible version

## Run

Default root:

```bash
python3 ~/.codex/skills/codeliver-upgrade-deliverymanager-lambda-deps/scripts/main.py \
  --lambda codeliver-panel-login
```

Dry run against a temp copy:

```bash
python3 ~/.codex/skills/codeliver-upgrade-deliverymanager-lambda-deps/scripts/main.py \
  --lambda codeliver-panel-login \
  --dry-run
```

Custom root:

```bash
python3 ~/.codex/skills/codeliver-upgrade-deliverymanager-lambda-deps/scripts/main.py \
  --lambda codeliver-panel-login \
  --root /absolute/path/to/lambdas
```

JSON report:

```bash
python3 ~/.codex/skills/codeliver-upgrade-deliverymanager-lambda-deps/scripts/main.py \
  --lambda codeliver-panel-login \
  --json
```

## Compatibility Rule

Compatibility means:

1. `npm install` succeeds
2. the best available local validator succeeds

Validator selection:

- use `npm test` only when `scripts.test` exists and is not a placeholder
- placeholder examples include `no test specified` and `console.log('no tests')`
- otherwise run `node --check` on top-level `*.js`, `*.cjs`, and `*.mjs` files

## Behavior Notes

- The skill preserves the existing version style per dependency:
  - `^1.0.6` stays caret-based
  - `1.0.6` stays exact
- The skill processes packages in deterministic alphabetical order.
- On a failed candidate, it restores `package.json` and existing npm lockfiles before trying the next older version.
- On `--dry-run`, it works on a temp copy and leaves the original repo unchanged.
