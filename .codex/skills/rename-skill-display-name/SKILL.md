---
name: "Rename Skill Display Name"
description: Update only the UI-facing display name of an existing Codex skill in the skills list/chips without changing its trigger name, path, workflow, or behavior.
---

# Rename Skill Display Name

Use this skill when the user wants a skill to appear with a different name in the Codex skills list, but does not want any change to how the skill is triggered or how it works.

## Scope

- Change only the list/chip display name.
- Do not rename the skill folder.
- Do not change `SKILL.md` frontmatter `name` unless the user explicitly asks for that too.
- Do not modify scripts, references, prompts, or workflow logic.

## Inputs

Collect:

- the target skill, as one of:
  - full path to the skill folder
  - full path to the skill `SKILL.md`
  - known skill folder name under `/Users/john/.codex/skills`
- the exact new display name

## Workflow

1. Resolve the target skill directory.
2. Update only `agents/openai.yaml`:
   - if the file exists, update `interface.display_name`
   - if the file does not exist, create it with an `interface.display_name` entry only
3. Verify the result by reading back the final `display_name`.
4. Report the changed file path.

## Resource

Use the bundled script for deterministic edits:

- `python /Users/john/.codex/skills/rename-skill-display-name/scripts/set_skill_display_name.py --skill <path-or-name> --display-name "<new name>"`

Examples:

- `python /Users/john/.codex/skills/rename-skill-display-name/scripts/set_skill_display_name.py --skill /Users/john/.codex/skills/crp-repos-harden-pr --display-name "Repo Harden PR"`
- `python /Users/john/.codex/skills/rename-skill-display-name/scripts/set_skill_display_name.py --skill crp-repos-harden-deploy --display-name "Repo Harden Deploy"`

## Guardrails

- Prefer `agents/openai.yaml` for UI renames.
- Preserve all existing keys in `agents/openai.yaml`.
- If `interface.display_name` is missing, add it without rewriting unrelated fields.
- If the target skill cannot be resolved, stop and report the candidate paths checked.
