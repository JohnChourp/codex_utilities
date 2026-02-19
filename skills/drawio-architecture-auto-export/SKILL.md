---
name: drawio-architecture-auto-export
description: Create a complete architecture diagram for app pages/subpages by reading ARCHITECTURE.md, writing ARCHITECTURE.drawio with a short description in every box, and auto-exporting ARCHITECTURE.png. Use when the user asks for page-flow diagrams, draw.io architecture maps, or automatic drawio+png generation from documented navigation.
---

# Drawio Architecture Auto Export

## Quick Start
Run:

```bash
python3 /home/john/.codex/skills/drawio-architecture-auto-export/scripts/generate_architecture_diagram.py
```

This command reads `ARCHITECTURE.md` in the current directory and creates:
- `ARCHITECTURE.drawio`
- `ARCHITECTURE.png`

By default, PNG export uses installed `drawio` CLI. If CLI is not available, it falls back to Pillow rendering.

## Expected Input Format
Use a Markdown file with these sections:
- `## Ροή από το άνοιγμα της εφαρμογής`
- `## Σελίδες που ανοίγουν από την Αρχική`
- `## Υποσελίδες ...`

For each item, keep:
- title line like `1. \`PageName\` (προαιρετικό label)`
- summary line like `- Σύνοψη: ...`

The skill maps:
- app open -> main page
- main page -> all pages
- selected parent page -> all subpages

## Custom Paths
Use custom filenames when needed:

```bash
python3 /home/john/.codex/skills/drawio-architecture-auto-export/scripts/generate_architecture_diagram.py \
  --input docs/MY_ARCHITECTURE.md \
  --drawio-output docs/MY_ARCHITECTURE.drawio \
  --png-output docs/MY_ARCHITECTURE.png
```

Use a specific drawio binary path:

```bash
python3 /home/john/.codex/skills/drawio-architecture-auto-export/scripts/generate_architecture_diagram.py \
  --drawio-cli /home/john/.local/bin/drawio
```

## Notes
- Keep box descriptions short in `ARCHITECTURE.md`; the script auto-trims very long summaries.
- Preferred PNG export path: `drawio -x -f png`.
- Fallback path: Pillow rendering with Unicode-capable font (DejaVu Sans when available).
- If fallback is needed and Pillow is missing, install it with `pip install pillow`.
