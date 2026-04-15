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

## Working rules

- Do not recreate or restore CodeDeliver/CRP domain `playbooks`, `refs`, or `policies` inside this shared engine home.
- Do not keep CodeDeliver-specific skill folders here; those belong in the CodeDeliver brain `.codex/skills`.
- When working in one of the domains above, load the local brain `.codex/AGENTS.md` and the corresponding local `.codex/{policies,playbooks,refs}`.
- Do not depend on `~/.codex` for shared skills, launchers, or rules.
</INSTRUCTIONS>
