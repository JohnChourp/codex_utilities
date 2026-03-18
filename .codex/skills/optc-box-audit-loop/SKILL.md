---
name: optc-box-audit-loop
description: Audit and iteratively improve OPTC Box Exporter matching from a strict case folder with input screenshot, provided output images, and corrected/favorites metadata.
---

# OPTC Box Audit Loop

## Overview

Use this skill for `~/Downloads/projects/optc-box-exporter` when the user wants a repeatable audit/fix loop from a saved case folder.

Default local case-folder location is the skill directory itself:

```text
~/.codex/skills/optc-box-audit-loop
```

So by default the skill reads images and JSON from:

- `~/.codex/skills/optc-box-audit-loop/input`
- `~/.codex/skills/optc-box-audit-loop/output`
- `~/.codex/skills/optc-box-audit-loop/meta`

## Case folder contract (strict)

The provided folder must contain this exact structure:

```text
<case-folder>/
  input/
    <exactly-one-screenshot>.png|jpg|jpeg|webp
  output/
    <one-or-more-output-character-images>.png|jpg|jpeg|webp
  meta/
    corrected.json
    optcbx-favorites-*.json or favorites*.json (optional; newest file auto-detected)
    notes.txt (optional)
```

Rules:

- `input/` must have exactly one image.
- `output/` must have at least one image.
- `meta/corrected.json` is the canonical expected source.
- `output/` image order is natural filename sort (`1,2,10` not `1,10,2`).
- Keep `output/` clean between runs to avoid stale artifacts.

## Chat-to-case staging rule

When the user sends assets progressively:

- first image -> place into `input/`
- second and all following images -> place into `output/`
- downloaded favorites JSON -> place into `meta/`
- corrected canonical JSON -> place into `meta/corrected.json`

## Workflow

1. Confirm the repo exists at:
```text
~/Downloads/projects/optc-box-exporter
```

2. If the user did not provide a case-folder path, use the default skill directory case folder (`~/.codex/skills/optc-box-audit-loop`).
If `meta/notes.txt` is missing and the prompt has no failure context, ask for a short failure note.

3. Run:
```bash
~/.codex/skills/optc-box-audit-loop/scripts/run.sh [case-folder]
```

4. Inspect generated files in the same case folder:
- `actual-export.json`
- `actual-grid.html`
- `provided-export.json`
- `provided-grid.html`
- `audit-report.json`

5. If report shows a clear matcher or crop problem, patch the repo, rerun the same command, and iterate until `summary.status` becomes `exact_match`.

## Execution rules

- Keep changes scoped to `optc-box-exporter` and this skill.
- Treat case-folder files as canonical inputs, not ad-hoc chat parsing.
- Prefer `python -m optcbx audit-case` over hand-rolled audit logic.
- Keep browser export JSON compatible with the existing `optc-team-builder` import flow.
