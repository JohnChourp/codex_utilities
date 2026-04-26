---
name: sync-brain-shared-conflicts
description: Sync the personal shared-agent conflict policy across cloud-repos-panel-brain, optc-team-builder-brain, and dm-codeliver-brain from codex_utilities, updating only each brain AGENTS conflict sections and local conflict-resolution ref.
---

# Sync Brain Shared Conflicts

Use this skill when the user wants the shared `codex_utilities` / `codexDevAgent` conflict-resolution rules synchronized into the three brain repos:

- `cloud-repos-panel-brain`
- `optc-team-builder-brain`
- `dm-codeliver-brain`

## Workflow

1. Load the local `codex_utilities/.codex/AGENTS.md`.
2. Run the bundled script in dry-run first:

```bash
python3 $CODEX_HOME/skills/sync-brain-shared-conflicts/scripts/run.py --dry-run
```

3. If the script reports `decision_required`, stop and ask the user. Include the repo, file, and reason printed by the script.
4. If the dry-run is clean, apply:

```bash
python3 $CODEX_HOME/skills/sync-brain-shared-conflicts/scripts/run.py
```

5. Report exactly which brain repos/files changed.

## Useful Commands

- `--dry-run`: print planned changes without writing.
- `--check`: fail if any target would change or needs a decision.
- `--brains crp,optc,codeliver`: limit the run to selected brains.
- `--show-diff`: include unified diffs in output.
- `--json`: print machine-readable run details.

## Guardrails

- Never edit `codexDevAgent` from this skill.
- Edit `codex_utilities` only when maintaining the skill itself.
- In brain repos, touch only:
  - `.codex/AGENTS.md`
  - `.codex/refs/personal-shared-conflict-resolution.md`
- Do not edit generated `shared-core-resolution.generated.md`.
- Do not guess when a target AGENTS structure is unfamiliar. Treat missing managed sections or merge conflict markers as `decision_required`.
