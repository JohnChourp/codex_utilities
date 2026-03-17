---
name: optc-box-browser-run
description: Bootstrap the local OPTC Box Exporter browser UI, download portraits if missing, start the Flask server, and open the app in the browser. Use when the user wants this specific repo to run successfully in a browser with one skill.
---

# OPTC Box Browser Run

## Overview

Use this skill for `~/Downloads/projects/optc-box-exporter` when the goal is to make the local browser UI run end-to-end with minimal manual steps.

## Workflow

1. Confirm the repo exists at:
```text
~/Downloads/projects/optc-box-exporter
```

2. Run:
```bash
~/.codex/skills/optc-box-browser-run/scripts/run.sh
```

3. The script will:
- Use a compatible local Python interpreter.
- Create or reuse the repo venv.
- Install the browser-safe Python dependencies.
- Download portraits when `data/Portraits` is missing.
- Start or reuse the local Flask server.
- Wait for `http://127.0.0.1:1234/runtime-status`.
- Open `http://127.0.0.1:1234` in the browser on macOS.

## Execution Rules

- Keep this skill scoped to the OPTC Box Exporter repo only.
- Prefer the repo script `tools/run-browser.sh` instead of retyping setup commands.
- If startup fails, inspect `.runtime/browser.log`, apply the narrowest safe fix in the repo, and retry.
- Stop only after the browser UI is reachable or there is a hard external blocker such as network failure.
