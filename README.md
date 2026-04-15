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
- `CODEDELIVER_BRAIN_CODEX` when the local CodeDeliver brain checkout exists
- `CRP_BRAIN_CODEX` when the local CRP brain checkout exists

For `direnv`, copy [`.envrc.example`](./.envrc.example) to `.envrc`.

## Ownership

- Shared engine assets live in [`./.codex`](./.codex).
- Domain docs stay in their brain repos:
  - CodeDeliver: `~/Downloads/lambdas/codeliver_all/dm-codeliver-brain/.codex`
  - CRP: `~/Downloads/projects/cloud-repos-panel-brain/.codex`
- CodeDeliver-specific skills live in the CodeDeliver brain repo, not here.

Tracked content in this repo is the portable engine only. Auth, cache, logs, history, sessions, and other machine-local runtime state stay under `CODEX_HOME` but are gitignored.
