# AGENTS.md

<INSTRUCTIONS>
Global Codex state is still stored in `~/.codex`, but CodeDeliver and CRP domain guidance no longer lives here.

## Canonical domain homes

- CodeDeliver (`codeliver-*` repos and lambdas):
  - `$HOME/Downloads/lambdas/codeliver_all/dm-codeliver-brain/.codex`
- Cloud Repos Panel / CRP (`cloud-repos-panel`, `crp-*` lambdas):
  - `$HOME/Downloads/projects/cloud-repos-panel-brain/.codex`

## Global role

- Keep only operational Codex state and machine-local overlays here.
- Do not recreate or restore CodeDeliver/CRP domain `playbooks`, `refs`, or `policies` in `~/.codex`.
- When working in one of the domains above, load the local brain `.codex/AGENTS.md` and the corresponding local `.codex/{policies,playbooks,refs}`.
</INSTRUCTIONS>
