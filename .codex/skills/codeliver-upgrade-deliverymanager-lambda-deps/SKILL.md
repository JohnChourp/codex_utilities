---
name: codeliver-upgrade-deliverymanager-lambda-deps
description: Upgrade one CodeDeliver lambda repo's npm dependencies to the newest compatible versions by trying npm registry versions from latest to older, restoring the repo state on failed attempts, and keeping the first version that passes local validation.
---

# Codeliver Upgrade Lambda Dependencies

## Overview

Use this skill for a single lambda repo under the local CodeDeliver lambdas root when you want to upgrade all installable npm dependencies in `dependencies` and `devDependencies` with automatic fallback to older versions.

The skill no longer targets only `@deliverymanager/*`. It scans the repo's full dependency surface and, for each eligible package, tries newer registry versions until it finds the newest version that still works with the codebase.

The skill:

- scans one lambda repo by exact folder name
- finds every eligible npm dependency in `dependencies` and `devDependencies`
- resolves available versions live from npm
- tries the newest stable version first, then walks backwards
- keeps the first version that passes local compatibility validation
- requires a post-upgrade code compatibility audit for any upgraded dependency that is actually used at runtime
- restores the previous repo state if a candidate fails
- stops with a failure if any package has no compatible version

Eligible dependency specs are standard registry semver specs such as exact (`1.2.3`), caret (`^1.2.3`), and tilde (`~1.2.3`). Non-registry specs such as `file:`, `workspace:`, git URLs, or other unsupported formats are reported as skipped.

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
3. if the dependency is used by the lambda at runtime, a code-level compatibility audit does not reveal an API or behavior break for the repo's actual usage
4. if the latest version fails, the skill retries progressively older versions until one passes or the package is exhausted

Validator selection:

- use `npm test` only when `scripts.test` exists and is not a placeholder
- placeholder examples include `no test specified` and `console.log('no tests')`
- otherwise run `node --check` on top-level `*.js`, `*.cjs`, and `*.mjs` files

## Post-upgrade Code Audit

After the installer/validator phase succeeds, do not assume the upgrade is safe yet.

If the upgraded package is used at runtime but cannot be loaded directly in the local Node environment because it expects modules provided only in AWS Lambda or another deployment runtime, do not stop at the local load failure. Treat that as a validation gap, not an automatic incompatibility, and continue with an isolated comparison harness that stubs only the missing runtime-provided modules.

For each dependency that changed and is used by the repo at runtime:

1. Search the repo for all imports/requires and direct API touchpoints.
2. Inspect the exact code paths that use the dependency and identify the concrete methods/properties/behavior relied on.
3. Verify the installed upgraded package still exports the required API shape.
4. When the package affects parsing, validation, formatting, serialization, HTTP behavior, or other runtime-sensitive logic, run targeted smoke comparisons between the old version and the upgraded version using representative inputs from the lambda's real flow.
5. Check upstream changelog/release notes for breaking changes relevant to the repo's actual usage, not just generic package changes.
6. If the audit cannot establish compatibility with reasonable confidence, restore the previous version or keep walking back to an older candidate.

Recommended fallback for runtime-provided-module gaps:

1. Pack or extract both the old and upgraded dependency versions into a temp workspace.
2. Add the narrowest possible stub modules only for the missing runtime-provided imports.
3. Execute the exact call pattern used by the lambda against both versions.
4. Compare exported keys, invocation params, return shape, and any caller-visible payload mutations.
5. Only keep the upgrade if the comparison shows equivalent behavior for the repo's real usage.

The closeout should explicitly distinguish:

- install/syntax validation success
- code-level compatibility findings
- remaining business/input risks that pre-existed the upgrade

## Behavior Notes

- The skill preserves the existing version style per dependency:
  - `^1.0.6` stays caret-based
  - `~1.0.6` stays tilde-based
  - `1.0.6` stays exact
- The skill processes packages in deterministic alphabetical order.
- On a failed candidate, it restores `package.json` and existing npm lockfiles before trying the next older version.
- On `--dry-run`, it works on a temp copy and leaves the original repo unchanged.
- The report includes skipped dependencies when a package spec does not support registry-version fallback.
