# AGENTS.md

<INSTRUCTIONS>
This repo is the canonical shared engine for portable Codex assets.

## Shared engine home

- Set `CODEX_HOME` to this repo's `.codex`.
- Keep shared executable assets here:
  - `skills/`
  - `scripts/`
  - `bin/`
  - `rules/`
- Keep only gitignored machine-local operational state under the active `CODEX_HOME`.

## Canonical domain docs homes

- CodeDeliver (`codeliver-*` repos and lambdas):
  - `$HOME/Downloads/lambdas/codeliver_all/dm-codeliver-brain/.codex`
- Cloud Repos Panel / CRP (`cloud-repos-panel`, `crp-*` lambdas):
  - `$HOME/Downloads/projects/cloud-repos-panel-brain/.codex`
- OPTC (`optc-team-builder`, `optc-box-exporter`, and OPTC workflows):
  - `$HOME/Downloads/projects/optc-team-builder-brain/.codex`

## Working rules

- Do not recreate or restore CodeDeliver/CRP/OPTC domain `playbooks`, `refs`, or `policies` inside this shared engine home.
- Do not keep CodeDeliver/CRP/OPTC-specific skill folders here; those belong in the matching domain brain `.codex/skills`.
- When working in one of the domains above, load the local brain `.codex/AGENTS.md` and the corresponding local `.codex/{policies,playbooks,refs}`.
- Do not depend on `~/.codex` for shared skills, launchers, or rules.
- Shared lambda dependency rule:
  - Treat `$HOME/Downloads/projects/codex_utilities/Downloads/lambdas` as the canonical shared npm home for `@aws-sdk/*` packages.
  - Before adding or reinstalling `@aws-sdk/*` inside an individual lambda repo, first check whether the needed package is already available from the shared `Downloads/lambdas/node_modules` install.
  - If a required `@aws-sdk/*` package is missing, add it once to the shared `Downloads/lambdas/package.json` and install it there instead of repeating the install in every lambda.
  - Only add per-lambda `@aws-sdk/*` installs when a repo has an explicit isolated-runtime requirement and that requirement is documented in the repo.
  - Prefer running shells through `source ./activate-codex-home.sh` so `NODE_PATH` includes the shared `Downloads/lambdas/node_modules` location.
- After code changes, always run repo-native validation for the affected project.
- For TypeScript repos, do not treat a successful framework build as sufficient proof that TypeScript is healthy; run an explicit typecheck step in addition to repo-native validation.
- Prefer an existing repo-native typecheck entrypoint such as `npm run typecheck` when available.
- When there is no dedicated typecheck script, choose the most specific valid `tsconfig` for the changed runtime instead of blindly using the root `tsconfig.json`.
- For Angular/Ionic application repos, default to `tsconfig.app.json` for app-level typecheck and only run spec/test `tsconfig` validation when the repo already has a working spec typing setup or an existing spec validation command.
- Treat the root `tsconfig.json` as a fallback only when it is clearly the correct compile target for the changed area.
- If validation exposes limited, clear pre-existing issues, try to fix them in the same session. If it exposes broad unrelated debt, stop and present a separate plan instead of silently expanding scope.
</INSTRUCTIONS>
