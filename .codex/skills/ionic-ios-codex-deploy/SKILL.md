---
name: ionic-ios-codex-deploy
description: Build, sync, install, archive, and launch an Ionic/Angular Capacitor app on an iOS simulator with Codex defaults. Use when the user wants one-command iOS simulator deploy for Ionic projects.
---

# Ionic iOS Codex Deploy

## Overview

Run one command to build an Ionic app, sync Capacitor iOS, build the simulator app, install it on a Codex simulator, and launch it.

## Workflow

1. Run:
```bash
~/.codex/skills/ionic-ios-codex-deploy/scripts/ionic_ios_codex_deploy.sh --project <ionic-project-root>
```

2. The script will:
- Validate Node/npm and Xcode simulator tools (`xcrun simctl`).
- Reuse or create simulator (default: `Codex iPhone 17 Pro Max`).
- Boot simulator and open Simulator app.
- Validate Ionic/Capacitor project shape.
- Install dependencies if `node_modules` is missing.
- Build web app (`npm run build` or `npx ionic build`).
- Ensure iOS platform exists (`npx cap add ios` when needed).
- Sync native iOS project (`npx cap sync ios`).
- Build debug app for simulator via `xcodebuild`.
- Install `.app` on simulator and launch it.
- Archive built `.app` to `build-artifacts/ios-app/`.

## Options

- `--project <path>`: Ionic project root (default: current directory)
- `--device-name <name>`: simulator name (default: `Codex iPhone 17 Pro Max`)
- `--device-type <id>`: simulator device type ID
- `--runtime <runtime-id>`: explicit iOS runtime ID
- `--udid <sim-udid>`: target an existing simulator by UDID
- `--bundle-id <appId>`: override launch bundle id
- `--archive-dir <path>`: custom `.app` archive directory
- `--skip-build`: skip web build
- `--skip-launch`: skip app launch
- `-h`, `--help`: show help

## Troubleshooting

- `xcrun/simctl not found`: install Xcode and Command Line Tools.
- `No iOS runtime available`: install a simulator runtime from Xcode Settings > Components.
- `workspace missing`: script runs `npx cap add ios`; if it fails, check Capacitor iOS setup.
- `launch failed`: verify bundle id and re-run with `--bundle-id` override if needed.
