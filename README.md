# codex_utilities

Canonical shared engine for portable Codex assets.

## Startup

Preferred shell bootstrap:

```bash
source ./activate-codex-home.sh
```

This exports:

- `CODEX_HOME=<repo>/.codex`
- `PATH=$CODEX_HOME/bin:$PATH`
- `CODEX_UTILITIES_LAMBDAS_NODE_MODULES=<repo>/Downloads/lambdas/node_modules` when the shared lambda install exists
- `NODE_PATH=$CODEX_UTILITIES_LAMBDAS_NODE_MODULES[:$NODE_PATH]` so local lambda tools can resolve shared `@aws-sdk/*` packages without per-repo installs
- `CODEDELIVER_BRAIN_CODEX` when the local CodeDeliver brain checkout exists
- `CRP_BRAIN_CODEX` when the local CRP brain checkout exists

For `direnv`, copy [`.envrc.example`](./.envrc.example) to `.envrc`.

## Shared Lint Wrappers

After `source ./activate-codex-home.sh`, the following wrappers are available from `PATH`:

- `shared-project-eslint <target-project-dir> [eslint args...]`
- `shared-lambda-eslint <target-lambda-dir> [eslint args...]`

Examples:

```bash
shared-project-eslint ~/Downloads/projects/codeliver-app src/app/home/home.page.ts
shared-lambda-eslint ~/Downloads/lambdas/codeliver_all/codeliver-routes-merge plans/simple_plan.js
```

These wrappers force the canonical shared ESLint installs/configs from:

- `./Downloads/projects` for Angular/Ionic/web projects
- `./Downloads/lambdas` for lambda repos

## Ownership

- Shared engine assets live in [`./.codex`](./.codex).
- Domain docs stay in their brain repos:
  - CodeDeliver: `~/Downloads/lambdas/codeliver_all/dm-codeliver-brain/.codex`
  - CRP: `~/Downloads/projects/cloud-repos-panel-brain/.codex`
- CodeDeliver-specific skills live in the CodeDeliver brain repo, not here.

Tracked content in this repo is the portable engine only. Auth, cache, logs, history, sessions, and other machine-local runtime state stay under `CODEX_HOME` but are gitignored.

## Shared Lambda Dependencies

Use [`./Downloads/lambdas/package.json`](./Downloads/lambdas/package.json) as the canonical shared install for `@aws-sdk/*` packages used across local lambda repos.

- First check the shared `Downloads/lambdas/node_modules` install before adding `@aws-sdk/*` to an individual lambda.
- If a required `@aws-sdk/*` package is missing, add it once here and install it here.
- Avoid per-lambda `@aws-sdk/*` installs unless a repo explicitly requires isolated local dependencies.
