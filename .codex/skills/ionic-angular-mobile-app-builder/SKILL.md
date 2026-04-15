---
name: ionic-angular-mobile-app-builder
description: Create brand-new Ionic Angular mobile apps from scratch with a polished mobile-first UI shell, latest stable Angular and Ionic, stable-by-default Capacitor, and Android/iOS native setup. Use when Codex should scaffold a new app from only a short project-type description such as "travel planner app", "recipe app", or "fitness tracker".
---

# Ionic Angular Mobile App Builder

## Overview

Use this skill to bootstrap a new Ionic Angular app when the user provides only the kind of app they want to build. Prefer the built-in scripts so version resolution, native setup, and starter UI stay consistent.

## Default Contract

1. Treat the user input as the project type and derive the rest:
   - project slug
   - display name
   - default app id
   - visual palette
2. Use the latest stable Angular and Ionic versions at runtime.
3. Use the latest stable Capacitor by default. Use preview Capacitor only when the user explicitly asks for bleeding-edge or preview mode.
4. Build a mobile app shell, not a single landing page.
5. Generate Android and iOS platforms when the environment supports them.

## Workflow

1. Normalize the project type into a safe project slug.
2. Resolve current package versions:
```bash
python3 $CODEX_HOME/skills/ionic-angular-mobile-app-builder/scripts/resolve_versions.py
```
3. Check local prerequisites:
```bash
bash $CODEX_HOME/skills/ionic-angular-mobile-app-builder/scripts/post_setup_checks.sh
```
4. Scaffold the app:
```bash
python3 $CODEX_HOME/skills/ionic-angular-mobile-app-builder/scripts/main.py scaffold \
  --project-type "travel planner app" \
  --destination /absolute/path/for/new/project
```
5. Validate the generated project:
```bash
cd /absolute/path/for/new/project/<generated-project-slug>
npm run build
npx cap sync
```
6. Reuse the existing deploy skills after scaffold:
   - Android: `$CODEX_HOME/skills/ionic-android-codex-deploy/scripts/ionic_android_codex_deploy.sh --project <project-root>`
   - iOS: `$CODEX_HOME/skills/ionic-ios-codex-deploy/scripts/ionic_ios_codex_deploy.sh --project <project-root>`

## Commands

### Resolve versions

```bash
python3 $CODEX_HOME/skills/ionic-angular-mobile-app-builder/scripts/main.py versions
```

### Run environment checks

```bash
python3 $CODEX_HOME/skills/ionic-angular-mobile-app-builder/scripts/main.py check
```

### Scaffold a project with defaults

```bash
python3 $CODEX_HOME/skills/ionic-angular-mobile-app-builder/scripts/main.py scaffold \
  --project-type "recipe app"
```

### Scaffold with explicit names

```bash
python3 $CODEX_HOME/skills/ionic-angular-mobile-app-builder/scripts/main.py scaffold \
  --project-type "fitness tracker" \
  --project-name pulse-path \
  --app-name "Pulse Path" \
  --app-id com.example.pulsepath \
  --destination /absolute/path/projects
```

### Opt into preview Capacitor

```bash
python3 $CODEX_HOME/skills/ionic-angular-mobile-app-builder/scripts/main.py scaffold \
  --project-type "creator app" \
  --capacitor-channel next
```

## Output Shape

The scaffolded project should contain:

1. Angular standalone app bootstrap.
2. Ionic standalone components and providers.
3. A bright, intentional mobile-first starter UI:
   - hero section
   - metric cards
   - feature/discovery screen
   - profile/preferences screen
4. Capacitor config plus Android and iOS platforms when supported.
5. Native-friendly npm scripts for build and sync.

## Troubleshooting

1. If `node`, `npm`, or `npx` is missing, stop and fix the toolchain first.
2. If `adb` or Android SDK tools are missing, scaffold the project anyway and explain the install steps before Android deploy.
3. If Xcode or simulator tools are missing, scaffold the project anyway and skip iOS platform creation with a clear warning.
4. If version resolution from npm fails, re-run `resolve_versions.py` to inspect the failing package and fall back to manual `npm view` commands.

## Resources

1. `scripts/resolve_versions.py`: resolve Angular, Ionic, and Capacitor versions from npm.
2. `scripts/post_setup_checks.sh`: validate local prerequisites and explain remediation.
3. `scripts/bootstrap_project.sh`: create the project, install packages, apply the starter UI, and set up Capacitor.
4. `assets/mobile-shell/`: reusable starter files copied into the generated project.
5. `references/reference.md`: operational notes, assumptions, and fallback commands.
