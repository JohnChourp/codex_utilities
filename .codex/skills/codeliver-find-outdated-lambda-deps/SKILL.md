---
name: codeliver-find-outdated-lambda-deps
description: Scan all local lambda repos under codeliver_all and write a text report with dependencies and devDependencies that have newer stable npm versions.
---

# Codeliver Find Outdated Lambda Dependencies

## Overview

Scan every direct child repo under `/Users/john/Downloads/lambdas/codeliver_all` that contains a `package.json`.
Compare `dependencies` and `devDependencies` against the latest stable npm registry version and overwrite a text report with the results.

## Run

```bash
python3 ~/.codex/skills/codeliver-find-outdated-lambda-deps/scripts/main.py
```

Custom root:

```bash
python3 ~/.codex/skills/codeliver-find-outdated-lambda-deps/scripts/main.py \
  --root /absolute/path/to/lambdas
```

Custom output:

```bash
python3 ~/.codex/skills/codeliver-find-outdated-lambda-deps/scripts/main.py \
  --output /absolute/path/to/report.txt
```

## Behavior

- Scan only direct child repos of the root path.
- Read `dependencies` and `devDependencies` from each `package.json`.
- Compare supported semver specs: exact, `^`, and `~`.
- Skip non-registry or non-semver specs and list them in the report.
- Use live npm registry lookups and do not modify any repo.
- Overwrite the report file on every run.
