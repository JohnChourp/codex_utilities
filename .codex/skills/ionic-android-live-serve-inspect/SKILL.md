---
name: ionic-android-live-serve-inspect
description: Start Ionic live serve, wire Android debugging, and optionally open Chrome device inspection.
---

# Ionic Android Live Serve Inspect

## Overview

Run one command to start an Ionic live server, connect a USB Android phone to that server via `adb reverse`, and install/launch the Capacitor app. Chrome device inspect is opt-in only.

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
~/.codex/skills/ionic-android-live-serve-inspect/scripts/ionic_android_live_serve_inspect.sh --project <ionic-project-root>
```

2. The script will:
- Validate required tools (`node`, `npm`, `adb`, `rg`).
- Validate Ionic/Capacitor project shape.
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
- Apply USB tunnel (`adb reverse tcp:<port> tcp:<port>`).
- Run `android/gradlew installDebug` with retry on `INSTALL_FAILED_UPDATE_INCOMPATIBLE`.
- Launch the app on device (unless `--skip-launch`).
- Open `chrome://inspect/#devices` in Chrome only when `--open-inspect` is explicitly passed.
- Run in quiet mode by default and keep noisy command output in temp log files.
- Keep session active in foreground until `Ctrl+C`.

## Options

- `--project <path>`: Ionic project root (default: current directory)
- `--port <number>`: Ionic serve port (default: `8206`)
- `--serial <adb-serial>`: target specific USB adb device
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
- `No USB Android device found`: enable developer options + USB debugging and reconnect phone.
- `Port already in use`: if using default port, the script auto-selects a nearby free port; if you passed `--port`, choose another one manually (e.g. `--port 8210`).
- `inspect tab not opening`: install Chrome/Chromium and retry; app session keeps running even if inspect open fails.
- Want the old heavier behavior: rerun with `--full-prepare`.
- `INSTALL_FAILED_UPDATE_INCOMPATIBLE`: script retries uninstall/install automatically.
- `npm run configure` fails with `pod ENOENT` or AWS `AccessDenied`: prefer Android-only continuation instead of rerunning the full prepare path.
- App opens then immediately crashes with `Resources$NotFoundException String resource ID #0x0`: this is commonly missing Branch Android strings; script now auto-runs `build-after.js` + `npx cap sync android` when needed.
- `installDebug` fails with missing Android resources (`branch_*`, notification channel strings, `ic_tracking`): regenerate Android-only resources before retrying install.
- `installDebug` fails with duplicate `requestAudioFocusIfNeeded` / `abandonAudioFocusIfNeeded`: re-run the repo's native-audio patch script and retry once.
- Need full command output for debugging: rerun with `--verbose`.
