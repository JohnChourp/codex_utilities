---
name: sync-global-codex-assets
description: Merge this repo's workflow overlay into an existing global `~/.codex/AGENTS.md` and sync repo skills into `~/.codex/skills` with backup, overwrite-safe one-way copy, and a short diff/report. Use when you want to install or refresh Codex workflow assets from a source repo without replacing unrelated global instructions.
---

# Sync Global Codex Assets

Use this skill when a workflow-assets repo should update the global Codex home safely.

## 1) Preconditions

1. Confirm the source repo contains:
   - `AGENTS.md`
   - `skills/`
2. Treat the source repo as the one-way source of truth for the workflow overlay and skill folders being synced.
3. Do not replace unrelated global instructions outside the workflow overlay block.

## 2) Merge policy

1. Backup the current global `~/.codex/AGENTS.md` before any overwrite.
2. Replace only the workflow/policy overlay block in the global file:
   - detect the first heading matching `# Codex Workflow Guide (`
   - replace from that heading to EOF with the source repo `AGENTS.md`
3. Preserve all global instructions above that boundary.

## 3) Skill sync policy

1. Copy each first-level source skill directory from `skills/` into `~/.codex/skills/`.
2. Overwrite existing target skill directories with the source copy.
3. Keep the sync one-way: source repo -> global `.codex`.
4. Print a short report listing:
   - backup path
   - workflow merge target
   - skills copied/updated

## 4) Recommended command

```bash
bash skills/sync-global-codex-assets/scripts/sync_global_codex_assets.sh
```

Optional arguments:

```bash
bash skills/sync-global-codex-assets/scripts/sync_global_codex_assets.sh /path/to/source/repo /path/to/target/.codex
bash skills/sync-global-codex-assets/scripts/sync_global_codex_assets.sh --dry-run
```

## 5) Safety rules

1. Fail fast if the source repo is missing `AGENTS.md` or `skills/`.
2. Fail fast if the target global file does not contain the workflow boundary heading.
3. Never delete unrelated files under the target `.codex` root.
4. Use this skill for merge-and-sync workflows instead of manually replacing the full global `AGENTS.md`.
