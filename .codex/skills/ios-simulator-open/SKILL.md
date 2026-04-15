---
name: ios-simulator-open
description: Create or reuse an iPhone 17 Pro Max simulator for manual iOS testing.
---

# iOS Simulator Open

## Overview

Run a single command to ensure an iPhone 17 Pro Max simulator exists, boot it, and open the Simulator app focused on that device.

## Workflow

1. Run:
```bash
$CODEX_HOME/skills/ios-simulator-open/scripts/ios_simulator_open.sh
```

2. The script will:
- Check `xcrun simctl` availability.
- Detect available iOS runtimes.
- Fail fast with clear Xcode install steps when no runtime exists.
- Reuse existing simulator by name/device-type when possible.
- Create the simulator when missing.
- Boot and wait until fully ready.
- Open the `Simulator` app on the target UDID.
- Leave the simulator running (no shutdown/kill commands).

## Options

- `--device-name <name>`: Simulator name (default: `Codex iPhone 17 Pro Max`)
- `--device-type <id>`: Device type ID (default: `com.apple.CoreSimulator.SimDeviceType.iPhone-17-Pro-Max`)
- `--runtime <runtime-id>`: Explicit runtime ID (default: newest available iOS runtime)
- `--open`: Open Simulator app on that UDID (enabled by default)
- `-h`, `--help`: Show help

## Execution Rules

- Prefer this skill when the user asks to open/prepare an iOS simulator quickly.
- Keep behavior focused on simulator lifecycle only (no app build/install/deploy).
- Never issue shutdown/erase/kill commands as part of this skill.
- Report the final UDID and booted status after execution.
