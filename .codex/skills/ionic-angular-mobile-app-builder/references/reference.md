# Ionic Angular Mobile App Builder Reference

## Purpose

Use this skill to create a new Ionic Angular app from scratch when the input is only a short project-type phrase.

## Runtime Decisions

1. Angular comes from `@angular/cli@latest` at scaffold time.
2. Ionic comes from `@ionic/angular@latest`.
3. Capacitor uses `latest` by default and `next` only when explicitly requested.
4. The starter UI is copied from `assets/mobile-shell/` and themed deterministically from the project type.

## Generated Defaults

1. `project-name`: slugified project type, trimmed to a safe npm package-style name.
2. `app-name`: title-cased version of the project type.
3. `app-id`: `com.example.<slug-without-dashes>`.
4. `webDir`: `dist/<project-name>/browser`, with fallback to `dist/<project-name>` after the first build if Angular outputs a non-browser folder.

## Fallback Commands

### Resolve package versions manually

```bash
npm view @angular/cli dist-tags --json
npm view @angular/core dist-tags --json
npm view @ionic/angular dist-tags --json
npm view @capacitor/core dist-tags --json
```

### Android native setup

```bash
npx cap add android
npx cap sync android
```

### iOS native setup

```bash
npx cap add ios
npx cap sync ios
```

## Existing Deploy Skills

1. Android deploy script:
   `~/.codex/skills/ionic-android-codex-deploy/scripts/ionic_android_codex_deploy.sh`
2. iOS deploy script:
   `~/.codex/skills/ionic-ios-codex-deploy/scripts/ionic_ios_codex_deploy.sh`

## Known Limits

1. This v1 skill is for new apps only. It does not upgrade existing repos.
2. iOS platform creation requires macOS plus working Xcode tools.
3. Android deployment requires Android SDK tools, but Android platform scaffolding itself can still be generated without a connected device.
