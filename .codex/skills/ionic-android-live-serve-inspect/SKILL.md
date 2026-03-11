---
name: ionic-android-live-serve-inspect
description: Start Ionic live serve, wire Android debugging, and open Chrome device inspection.
---

# Ionic Android Live Serve Inspect

## Overview

Run one command to start an Ionic live server, connect a USB Android phone to that server via `adb reverse`, install/launch the Capacitor app, and open Chrome device inspect.

## Workflow

1. Run:
```bash
~/.codex/skills/ionic-android-live-serve-inspect/scripts/ionic_android_live_serve_inspect.sh --project <ionic-project-root>
```

2. The script will:
- Validate required tools (`node`, `npm`, `adb`, `rg`).
- Validate Ionic/Capacitor project shape.
- Run `npm install` before Android setup.
- If available, run `npm run configure` in resilient mode (continues when failure is only iOS pod/AWS prerequisite related).
- Ensure Android platform exists (`npx cap add android` when needed).
- If available, refresh Android icons via `npm run push_icons_android`.
- If `build-after.js` exists, run it to apply native post-processing (e.g. Branch resources).
- Sync native Android project (`npx cap sync android`).
- Validate Branch Android string resources when `capacitor-branch-deep-links` is present and auto-fix missing entries.
- Start `ionic serve` on the requested port (default `8206`) and wait until it is reachable.
  - If the default port is busy and `--port` is not explicitly provided, it auto-selects the next free port.
- Write live config to native `capacitor.config.json` (`server.url=http://localhost:<port>`, `server.cleartext=true`).
- Detect a connected USB Android device (or use provided `--serial`).
- Apply USB tunnel (`adb reverse tcp:<port> tcp:<port>`).
- Run `android/gradlew installDebug` with retry on `INSTALL_FAILED_UPDATE_INCOMPATIBLE`.
- Launch the app on device (unless `--skip-launch`).
- Open `chrome://inspect/#devices` in Chrome (unless `--skip-inspect-open`).
- Keep session active in foreground until `Ctrl+C`.

## Options

- `--project <path>`: Ionic project root (default: current directory)
- `--port <number>`: Ionic serve port (default: `8206`)
- `--serial <adb-serial>`: target specific USB adb device
- `--package <applicationId>`: override package detection
- `--activity <activity>`: launch specific activity
- `--open-inspect`: open `chrome://inspect/#devices` automatically (default is no auto-open)
- `--skip-prepare`: skip project prepare flow (`npm install` / `configure` / icons / `build-after.js`)
- `--skip-inspect-open`: keep browser closed explicitly (default behavior)
- `--skip-launch`: install only, do not launch app
- `-h`, `--help`: show help

## Troubleshooting

- `adb not found`: install Android platform-tools and ensure `adb` is in `PATH`.
- `No USB Android device found`: enable developer options + USB debugging and reconnect phone.
- `Port already in use`: if using default port, the script auto-selects a nearby free port; if you passed `--port`, choose another one manually (e.g. `--port 8210`).
- `inspect tab not opening`: install Chrome/Chromium and retry; app session keeps running even if inspect open fails.
- `INSTALL_FAILED_UPDATE_INCOMPATIBLE`: script retries uninstall/install automatically.
- App opens then immediately crashes with `Resources$NotFoundException String resource ID #0x0`: this is commonly missing Branch Android strings; script now auto-runs `build-after.js` + `npx cap sync android` when needed.
- `npm run configure` fails with `pod ENOENT` or AWS `AccessDenied`: Android flow continues by design; install/launch can still succeed.
