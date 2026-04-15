---
name: android-debug-deploy
description: Build, install, archive, and launch one Android debug APK in a single workflow.
---

# Android Debug Deploy

## Overview

Run the deployment script to execute the full debug cycle automatically: detect device, build/install, archive APK with timestamp, and launch app.

## Workflow

1. Run the script:
```bash
$CODEX_HOME/skills/android-debug-deploy/scripts/android_debug_deploy.sh --project <android-project-root>
```

2. Let the script do:
- Verify `adb` and connected device.
- First try to use an already running Android emulator/device if one exists.
- Assume the user may already have emulator windows open from Android Studio and/or Xcode; deploy always targets the Android `adb` device list.
- Auto-detect `adb` from common macOS SDK paths when it is missing from `PATH`.
- If no device is connected, auto-launch an Android Studio emulator (AVD) and wait until it is fully booted.
- Run `./gradlew installDebug --warning-mode all` (optionally `clean` first).
- Retry once automatically for `INSTALL_FAILED_UPDATE_INCOMPATIBLE` by uninstalling old package and reinstalling.
- Copy generated APK to `build-artifacts/apk/` with timestamp.
- Launch app on the connected device.
- Keep the emulator running after successful launch so you can continue manual testing.

## MacBook Quickstart (Recommended)

1. One-time executable permission:
```bash
chmod +x $CODEX_HOME/skills/android-debug-deploy/scripts/android_debug_deploy.sh
```

2. Deploy:
```bash
$CODEX_HOME/skills/android-debug-deploy/scripts/android_debug_deploy.sh --project <android-project-root>
```

## macOS Troubleshooting

- `permission denied` on script:
```bash
bash $CODEX_HOME/skills/android-debug-deploy/scripts/android_debug_deploy.sh --project <android-project-root>
```

- `adb not found`:
  - The script now auto-checks:
    - `$ANDROID_HOME/platform-tools/adb`
    - `$ANDROID_SDK_ROOT/platform-tools/adb`
    - `$HOME/Library/Android/sdk/platform-tools/adb`
  - If still not found, export manually:
```bash
export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"
```

## Options

Use these optional flags when needed:
- `--project <path>`: Android project root (default: current directory).
- `--package <applicationId>`: Override automatic package detection.
- `--activity <activity>`: Launch specific activity (`.MainActivity` or full component).
- `--serial <device-serial>`: Target specific device when multiple are connected.
- `--avd <name>`: Preferred AVD to auto-launch when no device is connected (or set `ANDROID_AVD_NAME` env var).
- `--archive-dir <path>`: Custom directory for archived APK copies.
- `--clean`: Run `clean` before `installDebug`.
- `--skip-launch`: Build/install/archive only, without app launch.

## Execution Rules

- Prefer this skill whenever the user asks for one-command Android deploy to phone.
- Use defaults first; only pass explicit package/activity when auto-detection fails.
- When no connected device is found, assume the user has an emulator open (Android Studio and/or Xcode) and always complete build/debug/deploy on an Android emulator target so the user can test immediately.
- Always check `adb devices` first and deploy to the already-available Android target when present.
- If only an iOS Simulator is open (Xcode) and no Android `adb` target exists, auto-start an Android AVD and deploy there.
- For no-device scenarios, it now boots an emulator automatically (prefers `Motorola_Edge_40_Neo_API_35` when available, else first AVD).
- Do not close/kill emulator when launch succeeds; the emulator must remain open for user testing.
- After successful launch, no emulator shutdown commands are allowed (`adb emu kill`, `pkill`, or similar).
- If executed by an agent/tool runner, run it inside a persistent interactive TTY session and keep that session alive after completion; avoid short-lived one-shot runners that may terminate child GUI processes.
- After deploy finishes, explicitly verify emulator persistence with `adb devices -l` and report the active device serial (for example `emulator-5554`) in the final output.
- For guaranteed persistence, run the script from your own local Terminal/Android Studio session (not from a short-lived remote/agent command runner).
- Report archive path and launch result after execution.
