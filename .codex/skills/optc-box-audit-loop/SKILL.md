---
name: optc-box-audit-loop
description: Audit and iteratively improve OPTC Box Exporter matching from a case folder that contains one screenshot plus expected.json. Use when the user wants to rerun a saved OPTC case, inspect mismatches, write audit artifacts next to the input image, and keep improving the repo until the ordered character output is correct.
---

# OPTC Box Audit Loop

## Overview

Use this skill for `~/Downloads/projects/optc-box-exporter` when the user wants a repeatable audit/fix loop from a saved case folder.

## Case folder contract

The provided folder must contain:

- exactly one screenshot image (`.png`, `.jpg`, `.jpeg`, or `.webp`)
- `expected.json`
- optional `notes.txt`

`expected.json` is the canonical expected-output source. It should contain ordered `characters` entries in row-major order, left-to-right and top-to-bottom.

## Workflow

1. Confirm the repo exists at:
```text
~/Downloads/projects/optc-box-exporter
```

2. Confirm the user gave a case folder path. If `notes.txt` is missing and the user did not describe the failure in the prompt, ask for a short failure note.

3. Run:
```bash
~/.codex/skills/optc-box-audit-loop/scripts/run.sh "<case-folder>"
```

4. Inspect the generated files in the same case folder:
- `actual-export.json`
- `audit-report.json`
- `actual-grid.html`

5. If the report shows a clear matcher or crop problem, patch the repo, rerun the same command, and iterate until:
- `summary.status` becomes `exact_match`, or
- the report shows a hard blocker such as `expected_id_missing_from_local_units` or `missing_portrait_asset`

## Execution rules

- Keep changes scoped to `optc-box-exporter` and this skill.
- Treat the case folder contents as canonical input, not chat attachments.
- Prefer the `python -m optcbx audit-case` command over re-implementing the audit logic by hand.
- Keep the browser export JSON compatible with the existing `optc-team-builder` import flow.
