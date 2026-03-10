---
name: sync-global-codex-assets
description: Check for updates to the codexDevAgent workflow assets, clone or refresh the source repo when needed, and safely merge the managed AGENTS.md workflow block plus sync repo skill folders into ~/.codex. Use when the user asks to check for updates, run a safe update, run a clean install, refresh installed Codex skills, or update global Codex instructions from this repo.
---

# Sync Global Codex Assets

Use this skill when the user wants to update their installed Codex workflow assets from `codexDevAgent`.

## 1) Use the bundled script

When the user asks to update Codex assets, first ask whether they want:

1. `update`
2. `clean-install`

Run:

```bash
skills/sync-global-codex-assets/scripts/sync_global_codex_assets.sh check
```

or:

```bash
skills/sync-global-codex-assets/scripts/sync_global_codex_assets.sh update
```

or:

```bash
skills/sync-global-codex-assets/scripts/sync_global_codex_assets.sh clean-install
```

Use `--dry-run` to preview mutations.

## 2) Source repo resolution policy

Resolve the source repo in this order:

1. Use `--source <path>` when the caller provides one.
2. If the current working directory already looks like `codexDevAgent`, use it directly.
3. Otherwise use the cached clone at `~/.codex/repos/codexDevAgent`.
4. If the cached clone does not exist, clone `https://github.com/Al3xSy/codexDevAgent.git`.
5. If the cached clone exists, refresh it with `git fetch` and `git pull --ff-only`.
6. Read the repo version from `package.json` and compare it to the installed version marker in `~/.codex/.codexDevAgent-version`.

## 3) AGENTS merge policy

Treat the repo `AGENTS.md` as the managed workflow overlay.

On `update` and `clean-install`:

1. If target `~/.codex/AGENTS.md` does not exist, create it from the repo copy.
2. If it exists, preserve everything above the first heading that starts with:
   - `# Codex Workflow Guide (`
3. Replace that heading and everything below it with the repo `AGENTS.md` content.
4. Fail fast if the target file exists but the boundary heading is missing.
5. Create a timestamped backup before mutating the target file.

## 4) Skills sync policy

1. In `update`, sync each first-level folder from repo `skills/` into `~/.codex/skills/`.
2. Overwrite same-named installed skill folders completely.
3. In `clean-install`, also remove stale repo-managed skills recorded from prior syncs before copying the current repo skills.
4. Do not delete unrelated installed skills.
5. Report which skills would be added, updated, or removed.
6. After a successful `update` or `clean-install`, write the installed source version into `~/.codex/.codexDevAgent-version`.

## 5) Safety rules

1. Run `check` before `update` or `clean-install` when the user asks whether updates exist.
2. Use `--dry-run` whenever the user wants a preview.
3. Do not overwrite the target `AGENTS.md` blindly.
4. Do not delete unrelated user content from `~/.codex`.
5. Keep `clean-install` deletions limited to repo-managed skills tracked from prior syncs.
6. If the cached source repo is dirty, fail instead of pulling over local edits.
