---
name: optc-team-builder-android-release
description: Create an OPTC Team Builder Android GitHub release with version bump, build, tag, push, and release notes.
---

# OPTC Team Builder Android Release

## Overview

Χρησιμοποίησε αυτό το skill όταν θέλεις manual Android release για το `optc-team-builder` repo με ενιαίο version bump, native build, tag push και GitHub Release asset.

## Workflow

1. One-time local signing setup για νέο machine/profile:
```bash
./scripts/setup-release-signing.sh
source ~/.android/optc-team-builder/release-signing.env
```

2. Τρέξε:
```bash
~/.codex/skills/optc-team-builder-android-release/scripts/run_release.sh --bump patch
```

3. Το skill runner κάνει preflight:
- φορτώνει αυτόματα `~/.android/optc-team-builder/release-signing.env` αν υπάρχει
- αν λείπουν signing vars, τρέχει το repo-local `scripts/setup-release-signing.sh`
- ξαναφορτώνει το env file και μετά συνεχίζει στο repo release script
- αν λείπει `gh auth`, κάνει fallback σε tag push flow χωρίς direct GitHub Release publish

4. Το repo script εκτελεί:
- update version σε `package.json`, `package-lock.json`, Android `versionName`/`versionCode`, iOS `MARKETING_VERSION`/`CURRENT_PROJECT_VERSION`
- `npm run build:mobile`
- `./gradlew clean assembleRelease`
- `git commit` με message `release: vX.Y.Z`
- `git tag vX.Y.Z`
- `git push` branch + tag
- δημιουργία release notes και `gh release create` με signed APK asset

## Local signing storage

- keystore: `~/.android/optc-team-builder/release-upload-key.jks`
- env file: `~/.android/optc-team-builder/release-signing.env`
- alias default: `optc_team_builder_upload`

## Required env contract

- `ANDROID_SIGNING_STORE_FILE`
- `ANDROID_SIGNING_STORE_PASSWORD`
- `ANDROID_SIGNING_KEY_ALIAS`
- `ANDROID_SIGNING_KEY_PASSWORD`

## Options

- `--project <path>`: override project path
- `--bump patch|minor|major`: semantic bump (default: `patch`)
- `--version X.Y.Z`: explicit version
- `--code N`: explicit versionCode / build number
- `--no-push`: local commit/tag μόνο
- `--skip-gh-release`: παραλείπει το `gh release create`

## Execution Rules

- Δεν κάνει Play Store, App Store ή TestFlight publish.
- Το setup παραμένει local-only. Δεν προσθέτει GitHub Secrets flow ή GitHub Actions signing bootstrap.
- Αν βρεθεί keystore αλλά λείπει το αντίστοιχο `release-signing.env`, το setup script αποτυγχάνει καθαρά για να μη χαθούν άγνωστα credentials.
- Αν λείπει `gh auth`, κάνει fallback σε tag push flow χωρίς GitHub Release publish.
