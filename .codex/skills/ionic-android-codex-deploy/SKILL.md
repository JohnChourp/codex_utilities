---
name: ionic-android-codex-deploy
description: Build, sync, install, archive, and launch an Ionic/Angular Capacitor app on an Android emulator/device with Codex-friendly defaults. Use when the user wants one-command Android debug deploy for Ionic projects (not native-only Gradle projects).
---

# Ionic Android Codex Deploy

## Overview

Run one command to build an Ionic app, sync Capacitor Android, install debug APK, archive it, and launch the app on an Android target.

## Workflow

1. Run:
```bash
~/.codex/skills/ionic-android-codex-deploy/scripts/ionic_android_codex_deploy.sh --project <ionic-project-root>
```

2. The script will:
- Validate Node/npm, `adb`, and Android emulator tools.
- Validate Ionic/Capacitor project shape.
- Install dependencies if `node_modules` is missing.
- Build web app (`npm run build` or `npx ionic build`).
- Ensure Android platform exists (`npx cap add android` when needed).
- Sync native Android project (`npx cap sync android`).
- Enforce standalone native mode by removing `server.url` from `android/app/src/main/assets/capacitor.config.json` (so no `ionic serve`/localhost is required).
- Reuse connected Android target or boot AVD (default: `Codex Android`).
- Run `android/gradlew installDebug` (with retry on `INSTALL_FAILED_UPDATE_INCOMPATIBLE`).
- Archive generated APK to `build-artifacts/apk/`.
- Launch app on target.

## Options

- `--project <path>`: Ionic project root (default: current directory)
- `--serial <adb-serial>`: target specific adb device/emulator
- `--avd <name>`: preferred AVD for auto-start fallback (default: `Codex Android`)
- `--package <applicationId>`: override package detection
- `--activity <activity>`: launch specific activity
- `--archive-dir <path>`: custom APK archive directory
- `--clean`: run `clean` before `installDebug`
- `--skip-build`: skip web build
- `--skip-launch`: skip app launch
- `-h`, `--help`: show help

## Troubleshooting

- `adb not found`: ensure Android platform-tools is installed and in `PATH`.
- `emulator not found`: ensure Android SDK emulator tools are installed.
- `No AVD found`: create an Android Virtual Device in Android Studio Device Manager.
- `android/gradlew missing`: the script will run `npx cap add android`; if it fails, check Capacitor setup and SDK.
