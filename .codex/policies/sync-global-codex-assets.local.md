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

## Operator reminder

If the user intentionally customizes an installed skill, add its name to `~/.codex/.codexDevAgent-preserve-local-skills` before running `update` or `clean-install`.
