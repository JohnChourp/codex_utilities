---
name: android-debug-deploy
description: Build, install, archive, and launch an Android debug APK on a connected device in one run. Use when the user asks to avoid repetitive terminal commands like `./gradlew installDebug`, manual APK copying, and `adb` launch commands.
---

# Android Debug Deploy

## Overview

Run the deployment script to execute the full debug cycle automatically: detect device, build/install, archive APK with timestamp, and launch app.

## Workflow

1. Run the script:
```bash
~/.codex/skills/android-debug-deploy/scripts/android_debug_deploy.sh --project <android-project-root>
```

2. Let the script do:
- Verify `adb` and connected device.
- Run `./gradlew installDebug --warning-mode all` (optionally `clean` first).
- Retry once automatically for `INSTALL_FAILED_UPDATE_INCOMPATIBLE` by uninstalling old package and reinstalling.
- Copy generated APK to `build-artifacts/apk/` with timestamp.
- Launch app on the connected device.

## Options

Use these optional flags when needed:
- `--project <path>`: Android project root (default: current directory).
- `--package <applicationId>`: Override automatic package detection.
- `--activity <activity>`: Launch specific activity (`.MainActivity` or full component).
- `--serial <device-serial>`: Target specific device when multiple are connected.
- `--archive-dir <path>`: Custom directory for archived APK copies.
- `--clean`: Run `clean` before `installDebug`.
- `--skip-launch`: Build/install/archive only, without app launch.

## Execution Rules

- Prefer this skill whenever the user asks for one-command Android deploy to phone.
- Use defaults first; only pass explicit package/activity when auto-detection fails.
- Report archive path and launch result after execution.
