# Local Overlay For `sync-global-codex-assets`

Apply these rules in addition to the repo copy of `skills/sync-global-codex-assets/SKILL.md`.

## Local skill policy

1. Keep `sync-global-codex-assets` listed in `~/.codex/.codexDevAgent-local-only-skills`.
2. Do not reinstall `sync-global-codex-assets` into `~/.codex/skills/`; always run it from the `codexDevAgent` repo checkout.

## Preserve-local-skills policy

1. Treat `~/.codex/.codexDevAgent-preserve-local-skills` as the list of intentionally customized installed skills.
2. During `update`, skip overwrite for installed skills listed there.
3. During `clean-install`, skip stale-removal for installed skills listed there unless they are also marked local-only.
4. Report preserved skills separately from added, updated, removed, and local-only skipped skills.
5. If an installed skill gains proven self-correction knowledge from local execution and its canonical local copy is updated, add that skill to `~/.codex/.codexDevAgent-preserve-local-skills` before the next sync/update.

## Self-correcting skill customization

1. Only preserve write-backs that came from a confirmed successful recovery path.
2. Preserve the smallest canonical change that prevents the same failure pattern on the next run.
3. Do not preserve machine-specific noise such as temporary ports, transient auth problems, or one-off device state.

## Operator reminder

If the user intentionally customizes an installed skill, add its name to `~/.codex/.codexDevAgent-preserve-local-skills` before running `update` or `clean-install`.
