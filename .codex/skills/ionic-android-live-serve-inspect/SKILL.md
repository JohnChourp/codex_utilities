---
name: ionic-android-live-serve-inspect
description: Start Ionic live serve, wire Android debugging, and optionally open Chrome device inspection.
---

# Ionic Android Live Serve Inspect

## Overview

Run one command to start an Ionic live server, connect a USB Android phone to that server via `adb reverse`, and install/launch the Capacitor app. Chrome device inspect is opt-in only.

When `--project` is omitted, the launcher auto-discovers Ionic/Capacitor projects from the current working directory, the user's home tree, and common workspace roots. If more than one project matches, it opens an interactive terminal chooser.
The chooser ranks the current repo/invocation match first, so a `codeliver-app` checkout appears at the top when it is present.

Every run writes the visible `report.md` file in the same `scripts/` folder as `run.py`, and keeps the per-run logs in a hidden `.ionic-android-live-serve-inspect/<timestamp>/` artifact directory beside it. The report is created immediately and kept up to date by both the Python bootstrap and the shell launcher. The launcher also auto-detects the Android SDK, writes `android/local.properties` when needed, and keeps the foreground session alive after the app launch.
`run.py` prints the exact `report.md` path immediately, and the launcher keeps appending a final summary even on early failures or `Ctrl+C` exits.

This is a direct-run local debug skill. When the user only asks to run this flow, execute it immediately without ClickUp workflow, branch/delivery questions, or verbose narration. Keep progress updates minimal and keep the completion message short unless the user asks for details.

Default chat contract for this skill:
- Send at most one short start line before running.
- Stay silent while the flow is running unless there is a real blocker that needs the user.
- If an internal retry or fallback succeeds, do not narrate it.
- Default to the fast Android-only path; do not ask for or open browser/inspect unless the user explicitly requests it.
- On success, reply with one short line only: live URL/port and whether app launch succeeded. Mention inspect only if it was explicitly requested.
- Do not include file lists, log summaries, or post-run analysis unless the user explicitly asks.

When the first path fails, prefer internal recovery over chat narration: inspect the existing logs, apply the narrowest Android-safe fallback, and only surface a blocker if the recovery path still fails. If a fallback succeeds and is reproducible, fold it back into this skill.

## Workflow

1. Run:
```bash
~/.codex/bin/ionic-android-live-serve-inspect --project <ionic-project-root>
```

Fallback local entrypoints:
- Generic launcher: `~/.codex/bin/run-skill ionic-android-live-serve-inspect --project <ionic-project-root>`
- Direct wrapper: `python3 ~/.codex/skills/ionic-android-live-serve-inspect/scripts/run.py --project <ionic-project-root>`
- Direct shell launcher: `~/.codex/skills/ionic-android-live-serve-inspect/scripts/ionic_android_live_serve_inspect.sh --project <ionic-project-root>`

2. The script will:
- Validate required tools (`node`, `npm`, `adb`) and use `rg` when available with `grep` fallback.
- Validate Ionic/Capacitor project shape.
- Auto-discover the Ionic project when `--project` is omitted; accept either a path or a fuzzy project name.
- Prefer a fast Android-only path by default when the project already has `node_modules/` and `android/`.
- Run `npm install` and `npm run configure` only when the fast path is unavailable or the user explicitly requests full prepare.
- Ensure Android platform exists (`npx cap add android` when needed).
- If available, refresh Android icons via `npm run push_icons_android`.
- If `build-after.js` exists, run it to apply native post-processing (e.g. Branch resources).
- Sync native Android project (`npx cap sync android`).
- Validate Branch Android string resources when `capacitor-branch-deep-links` is present and auto-fix missing entries.
- If `installDebug` later fails because generated Android resources are missing, regenerate Android-only resources (`push_icons_android` -> `build-after.js` -> `npx cap sync android`) and retry.
- If `installDebug` later fails on known duplicate native-audio patch methods, re-run the local native-audio patch script and retry once.
- Start `ionic serve` on the requested port (default `8206`) and wait until it is reachable.
  - If the default port is busy and `--port` is not explicitly provided, it auto-selects the next free port.
- Write live config to native `capacitor.config.json` (`server.url=http://localhost:<port>`, `server.cleartext=true`).
- Detect a connected USB Android device (or use provided `--serial`).
- Detect or accept `--device-api` before `adb reverse`; fail fast on API levels below 21.
- Apply USB tunnel (`adb reverse tcp:<port> tcp:<port>`).
- Run `android/gradlew installDebug` with retry on `INSTALL_FAILED_UPDATE_INCOMPATIBLE`.
- Launch the app on device (unless `--skip-launch`).
- Open `chrome://inspect/#devices` in Chrome only when `--open-inspect` is explicitly passed.
- Run in quiet mode by default and keep noisy command output in temp log files.
- Keep session active in foreground until `Ctrl+C`.

## Options

- `--project <path|name>`: Ionic project root, workspace root, or fuzzy project name
- `--port <number>`: Ionic serve port (default: `8206`)
- `--serial <adb-serial>`: target specific USB adb device
- `--device-api <sdk-int>`: Android API level override for USB reverse gating
- `--package <applicationId>`: override package detection
- `--activity <activity>`: launch specific activity
- `--open-inspect`: open `chrome://inspect/#devices` automatically; never implied by default
- `--full-prepare`: force the heavy prepare flow (`npm install` / `configure` / icons / `build-after.js`)
- `--skip-prepare`: force skipping the heavy prepare flow
- `--skip-inspect-open`: keep browser closed explicitly (default behavior)
- `--skip-launch`: install only, do not launch app
- `--verbose`: stream detailed command output instead of quiet mode
- `-h`, `--help`: show help

## Troubleshooting

- `adb not found`: install Android platform-tools and ensure `adb` is in `PATH`.
- `run.py` says `Unable to locate shared skill runtime support`: the local shared runtime under `~/.codex/skills/.system/skill-runtime-lib` is missing or incomplete.
- Need the full logs after a run: open the `report.md` file next to `run.py` and inspect it directly.
- If the shell exits early before the live session starts, `run.py` still leaves a bootstrap `report.md` and appends a final summary there.
- `No USB Android device found`: enable developer options + USB debugging and reconnect phone.
- `Port already in use`: if using default port, the script auto-selects a nearby free port; if you passed `--port`, choose another one manually (e.g. `--port 8210`).
- `Project prompt not appearing`: pass a more specific `--project <path>` or set `IONIC_PROJECT_SEARCH_ROOTS` to narrow the search roots.
- `inspect tab not opening`: install Chrome/Chromium and retry; app session keeps running even if inspect open fails.
- Want the old heavier behavior: rerun with `--full-prepare`.
- `Device API 20 or lower`: the skill stops before `adb reverse`; use an API 21+ USB Android device or pass `--device-api 21+` only if you know the target supports reverse.
- `SDK location not found`: the skill auto-detects the Android SDK from env/common paths and writes `android/local.properties`; if it still cannot find a valid SDK, set `ANDROID_HOME` or `ANDROID_SDK_ROOT`.
- `INSTALL_FAILED_UPDATE_INCOMPATIBLE`: script retries uninstall/install automatically.
- `npm run configure` fails with `pod ENOENT` or AWS `AccessDenied`: prefer Android-only continuation instead of rerunning the full prepare path.
- App opens then immediately crashes with `Resources$NotFoundException String resource ID #0x0`: this is commonly missing Branch Android strings; script now auto-runs `build-after.js` + `npx cap sync android` when needed.
- `installDebug` fails with missing Android resources (`branch_*`, notification channel strings, `ic_tracking`): regenerate Android-only resources before retrying install.
- `installDebug` fails with duplicate `requestAudioFocusIfNeeded` / `abandonAudioFocusIfNeeded`: re-run the repo's native-audio patch script and retry once.
- `rg` is not installed: the skill falls back to `grep`; no action is needed unless both tools are unavailable.
- Need full command output for debugging: rerun with `--verbose`.
