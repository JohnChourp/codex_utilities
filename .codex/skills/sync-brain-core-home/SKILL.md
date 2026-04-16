---
name: sync-brain-core-home
description: Sync a brain repo to a declared shared core repo with portable fallback resolution for shared Codex assets, then update only the brain AGENTS managed block plus generated resolution docs.
---

# Sync Brain Core Home

Use this skill when the user gives:

- a shared core repo
- a brain repo

and wants the brain repo to resolve shared Codex assets through a fixed fallback chain:

1. declared core repo
2. already-defined brain core
3. global `~/.codex`

## Inputs

Collect exactly:

- `core`: absolute path or repo name
- `brain`: absolute path or repo name

## Workflow

1. Resolve both repos from the provided path or name.
2. Fail fast if either repo does not have a `.codex` directory.
3. Discover any already-defined brain core from:
   - `brain/.codex/core-home.json`
   - shared-home hints in `brain/.codex/AGENTS.md`
4. Build the fallback chain in this order:
   - declared core
   - existing brain-defined core
   - `~/.codex` if present
5. Deduplicate missing or repeated entries.
6. Update only these brain files:
   - `.codex/AGENTS.md`
   - `.codex/core-home.json`
   - `.codex/refs/shared-core-resolution.generated.md`

## Command

Run the bundled script directly:

```bash
python3 $CODEX_HOME/skills/sync-brain-core-home/scripts/run.py --core <path-or-name> --brain <path-or-name>
```

Useful flags:

- `--dry-run`
- `--print-resolution`

## Guardrails

- Do not rewrite the whole brain `.codex`.
- Do not modify domain policies, playbooks, refs, `.system`, or existing `skill.runtime.json` files inside the brain repo.
- Update only the managed block in `AGENTS.md`.
- Replace hardcoded shared-core wording with generic wording that points to the generated shared-core resolution ref.
- Keep domain-specific docs local to the brain repo; use the shared core chain only for general/shared assets.
