---
name: paneldf-find-outdated-lambda-deps
description: Scan all local lambda repos under paneldf_all and write a JSON report with dependencies and devDependencies that have newer stable npm versions.
---

# PanelDF Find Outdated Lambda Dependencies

## Overview

Scan every direct child repo under `~/Downloads/lambdas/paneldf_all` that contains a `package.json`.
Compare `dependencies` and `devDependencies` against the latest stable npm registry version and overwrite a JSON report with the results.

## Run

```bash
python3 $CODEX_HOME/skills/paneldf-find-outdated-lambda-deps/scripts/main.py
```

Custom root:

```bash
python3 $CODEX_HOME/skills/paneldf-find-outdated-lambda-deps/scripts/main.py \
  --root /absolute/path/to/lambdas
```

Custom output:

```bash
python3 $CODEX_HOME/skills/paneldf-find-outdated-lambda-deps/scripts/main.py \
  --output /absolute/path/to/report.json
```

## Behavior

- Scan only direct child repos of the root path.
- Read `dependencies` and `devDependencies` from each `package.json`.
- Compare supported semver specs: exact, `^`, and `~`.
- Write JSON output instead of text.
- Omit repositories that have neither outdated nor skipped dependencies.
- Skip non-registry or non-semver specs and list them in the report.
- For private npm packages such as `@deliverymanager/*`, reuse npm auth from `NODE_AUTH_TOKEN` / `NPM_TOKEN`, then `~/.npmrc.automation`, then `~/.npmrc`.
- On Ubuntu/Linux machines, if private packages still show `404`, refresh the workstation token with `whc npm-automation set` or `whc u` and rerun the skill.
- Use live npm registry lookups and do not modify any repo.
- Overwrite the JSON report file on every run.
