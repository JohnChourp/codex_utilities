#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  ionic_android_codex_deploy.sh [options]

Options:
  --project <path>       Ionic project root (default: current directory)
  --serial <id>          ADB serial for target device/emulator
  --avd <name>           Preferred AVD name when auto-starting emulator (default: Codex Android)
  --package <id>         Override package/applicationId detection
  --activity <name>      Activity to launch (e.g. .MainActivity)
  --archive-dir <path>   Output directory for archived APK copies
  --clean                Run clean before installDebug
  --skip-build           Skip web build (npm run build / ionic build)
  --skip-launch          Do not launch app after install
  -h, --help             Show help
USAGE
}

log() {
    printf '[ionic-android-codex-deploy] %s\n' "$*"
}

PROJECT_DIR="$PWD"
SERIAL="${ADB_SERIAL:-}"
AVD_NAME="Codex Android"
PACKAGE_NAME=""
ACTIVITY_NAME=""
ARCHIVE_DIR=""
CLEAN_BUILD=0
SKIP_BUILD=0
SKIP_LAUNCH=0
ADB_BIN=""
EMULATOR_BIN=""
EMULATOR_STARTED=0
EMULATOR_LOG=""

while (($# > 0)); do
    case "$1" in
        --project)
            PROJECT_DIR="${2:-}"
            shift 2
            ;;
        --serial)
            SERIAL="${2:-}"
            shift 2
            ;;
        --avd)
            AVD_NAME="${2:-}"
            shift 2
            ;;
        --package)
            PACKAGE_NAME="${2:-}"
            shift 2
            ;;
        --activity)
            ACTIVITY_NAME="${2:-}"
            shift 2
            ;;
        --archive-dir)
            ARCHIVE_DIR="${2:-}"
            shift 2
            ;;
        --clean)
            CLEAN_BUILD=1
            shift
            ;;
        --skip-build)
            SKIP_BUILD=1
            shift
            ;;
        --skip-launch)
            SKIP_LAUNCH=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd -P)"

if [[ ! -f "$PROJECT_DIR/package.json" ]]; then
    echo "package.json not found in $PROJECT_DIR" >&2
    exit 1
fi

if [[ ! -f "$PROJECT_DIR/capacitor.config.ts" && ! -f "$PROJECT_DIR/capacitor.config.json" ]]; then
    echo "capacitor.config.ts/json not found in $PROJECT_DIR" >&2
    exit 1
fi

ensure_adb() {
    if command -v adb >/dev/null 2>&1; then
        ADB_BIN="$(command -v adb)"
        return 0
    fi

    local candidates=()
    if [[ -n "${ANDROID_HOME:-}" ]]; then
        candidates+=("${ANDROID_HOME}/platform-tools/adb")
    fi
    if [[ -n "${ANDROID_SDK_ROOT:-}" ]]; then
        candidates+=("${ANDROID_SDK_ROOT}/platform-tools/adb")
    fi
    candidates+=(
        "${HOME}/Library/Android/sdk/platform-tools/adb"
        "/Users/${USER}/Library/Android/sdk/platform-tools/adb"
    )

    local c
    for c in "${candidates[@]}"; do
        if [[ -x "$c" ]]; then
            export PATH="$(dirname "$c"):$PATH"
            ADB_BIN="$c"
            return 0
        fi
    done
    return 1
}

ensure_emulator() {
    if command -v emulator >/dev/null 2>&1; then
        EMULATOR_BIN="$(command -v emulator)"
        return 0
    fi

    local candidates=()
    if [[ -n "${ANDROID_HOME:-}" ]]; then
        candidates+=("${ANDROID_HOME}/emulator/emulator")
    fi
    if [[ -n "${ANDROID_SDK_ROOT:-}" ]]; then
        candidates+=("${ANDROID_SDK_ROOT}/emulator/emulator")
    fi
    candidates+=(
        "${HOME}/Library/Android/sdk/emulator/emulator"
        "/Users/${USER}/Library/Android/sdk/emulator/emulator"
    )

    local c
    for c in "${candidates[@]}"; do
        if [[ -x "$c" ]]; then
            EMULATOR_BIN="$c"
            return 0
        fi
    done
    return 1
}

collect_lines() {
    local __dest="$1"
    shift
    local lines=()
    local line
    while IFS= read -r line; do
        [[ -n "$line" ]] && lines+=("$line")
    done < <("$@")
    eval "$__dest=(\"\${lines[@]}\")"
}

has_build_script() {
    (
        cd "$PROJECT_DIR"
        node -e 'const p=require("./package.json"); process.exit(p?.scripts?.build ? 0 : 1)'
    )
}

install_dependencies_if_needed() {
    if [[ -d "$PROJECT_DIR/node_modules" ]]; then
        return 0
    fi

    log "node_modules not found; installing dependencies"
    if [[ -f "$PROJECT_DIR/package-lock.json" ]]; then
        (
            cd "$PROJECT_DIR"
            npm ci
        )
    else
        (
            cd "$PROJECT_DIR"
            npm install
        )
    fi
}

run_web_build_if_needed() {
    if [[ $SKIP_BUILD -eq 1 ]]; then
        log "Skipping web build (--skip-build)"
        return 0
    fi

    if has_build_script; then
        log "Running npm run build"
        (
            cd "$PROJECT_DIR"
            npm run build
        )
    else
        log "No build script found; running npx ionic build"
        (
            cd "$PROJECT_DIR"
            npx ionic build
        )
    fi
}

ensure_android_platform() {
    if [[ -f "$PROJECT_DIR/android/gradlew" ]]; then
        return 0
    fi

    if [[ -d "$PROJECT_DIR/android" ]]; then
        local existing_entries=()
        while IFS= read -r entry; do
            [[ -n "$entry" ]] && existing_entries+=("$entry")
        done < <(find "$PROJECT_DIR/android" -mindepth 1 -maxdepth 1 ! -name '.DS_Store' ! -name '.gitkeep' -print)

        if [[ ${#existing_entries[@]} -gt 0 ]]; then
            echo "android/ exists but android/gradlew is missing. Non-placeholder files were found, so refusing to overwrite platform." >&2
            echo "Remove/fix $PROJECT_DIR/android manually, then re-run." >&2
            return 1
        fi

        log "Found placeholder android/ directory without gradlew; recreating platform"
        rm -rf "$PROJECT_DIR/android"
    fi

    log "Android platform missing; running npx cap add android"
    (
        cd "$PROJECT_DIR"
        # Avoid blocking on Capacitor telemetry prompt in non-interactive runs.
        printf 'n\n' | npx cap add android
    )

    if [[ ! -f "$PROJECT_DIR/android/gradlew" ]]; then
        echo "android/gradlew is still missing after npx cap add android" >&2
        exit 1
    fi
}

sync_android_platform() {
    log "Running npx cap sync android"
    (
        cd "$PROJECT_DIR"
        npx cap sync android
    )
}

enforce_standalone_native_config() {
    local native_config="$PROJECT_DIR/android/app/src/main/assets/capacitor.config.json"
    local result=""

    if [[ ! -f "$native_config" ]]; then
        echo "Native Capacitor config not found at $native_config after sync" >&2
        return 1
    fi

    result="$(
        node - "$native_config" <<'NODE'
const fs = require("fs");

const path = process.argv[2];
const raw = fs.readFileSync(path, "utf8");
let json;
try {
    json = JSON.parse(raw);
} catch (error) {
    console.error(`Failed to parse JSON in ${path}: ${error.message}`);
    process.exit(2);
}

let changed = false;
if (json && typeof json === "object" && json.server && typeof json.server === "object") {
    if (Object.prototype.hasOwnProperty.call(json.server, "url")) {
        delete json.server.url;
        changed = true;
    }
    if (Object.keys(json.server).length === 0) {
        delete json.server;
        changed = true;
    }
}

if (changed) {
    fs.writeFileSync(path, `${JSON.stringify(json, null, 2)}\n`);
    process.stdout.write("changed");
} else {
    process.stdout.write("unchanged");
}
NODE
    )"

    if [[ "$result" == "changed" ]]; then
        log "Removed native Capacitor server.url to enforce standalone APK (no localhost dependency)"
    else
        log "Native Capacitor config already standalone (no server.url)"
    fi
}

detect_package_name() {
    local f line

    for f in "$PROJECT_DIR/capacitor.config.ts" "$PROJECT_DIR/capacitor.config.json"; do
        if [[ -f "$f" ]]; then
            line="$(rg -n "appId[[:space:]]*[:=][[:space:]]*['\"][^'\"]+['\"]" "$f" -m 1 | cut -d: -f2- || true)"
            if [[ -n "$line" ]]; then
                echo "$line" | sed -E "s/.*appId[[:space:]]*[:=][[:space:]]*['\"]([^'\"]+)['\"].*/\1/"
                return 0
            fi
        fi
    done

    for f in "$PROJECT_DIR/android/app/build.gradle.kts" "$PROJECT_DIR/android/app/build.gradle"; do
        if [[ -f "$f" ]]; then
            line="$(rg -n '^[[:space:]]*applicationId[[:space:]]*=' "$f" -m 1 | cut -d: -f2- || true)"
            if [[ -n "$line" ]]; then
                echo "$line" | sed -E 's/.*"([^"]+)".*/\1/'
                return 0
            fi
        fi
    done

    if [[ -f "$PROJECT_DIR/android/app/src/main/AndroidManifest.xml" ]]; then
        line="$(rg -n 'package=' "$PROJECT_DIR/android/app/src/main/AndroidManifest.xml" -m 1 | cut -d: -f2- || true)"
        if [[ -n "$line" ]]; then
            echo "$line" | sed -E 's/.*package="([^"]+)".*/\1/'
            return 0
        fi
    fi

    return 1
}

pick_avd() {
    local avds=()
    collect_lines avds "$EMULATOR_BIN" -list-avds

    if [[ ${#avds[@]} -eq 0 ]]; then
        echo "No Android Virtual Devices found. Create one in Android Studio Device Manager." >&2
        return 1
    fi

    local avd
    if [[ -n "$AVD_NAME" ]]; then
        for avd in "${avds[@]}"; do
            if [[ "$avd" == "$AVD_NAME" ]]; then
                echo "$avd"
                return 0
            fi
        done
        echo "[ionic-android-codex-deploy] Preferred AVD '$AVD_NAME' not found; using fallback" >&2
    fi

    for avd in "${avds[@]}"; do
        if [[ "$avd" == *Codex* ]]; then
            echo "$avd"
            return 0
        fi
    done

    echo "${avds[0]}"
}

wait_for_online_device() {
    local serial=""
    local boot=""
    local i

    for i in {1..120}; do
        serial="$($ADB_BIN devices | awk 'NR>1 && $2=="device" {print $1; exit}')"
        if [[ -n "$serial" ]]; then
            break
        fi
        sleep 2
    done

    if [[ -z "$serial" ]]; then
        return 1
    fi

    for i in {1..120}; do
        boot="$($ADB_BIN -s "$serial" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
        if [[ "$boot" == "1" ]]; then
            echo "$serial"
            return 0
        fi
        sleep 2
    done

    return 1
}

launch_emulator_fallback() {
    local selected_avd
    local timestamp
    local log_dir

    if ! ensure_emulator; then
        echo "emulator not found in PATH or common Android SDK locations" >&2
        return 1
    fi

    selected_avd="$(pick_avd)" || return 1

    timestamp="$(date +%Y%m%d_%H%M%S)"
    log_dir="$PROJECT_DIR/build-artifacts/emulator-logs"
    mkdir -p "$log_dir"
    EMULATOR_LOG="$log_dir/android-emulator-${timestamp}.log"

    log "Launching emulator AVD: $selected_avd"
    nohup "$EMULATOR_BIN" -avd "$selected_avd" -no-snapshot-load -no-boot-anim </dev/null >"$EMULATOR_LOG" 2>&1 &
    disown "$!" 2>/dev/null || true
    EMULATOR_STARTED=1

    if ! SERIAL="$(wait_for_online_device)"; then
        echo "Emulator did not become ready in time" >&2
        echo "Emulator log: $EMULATOR_LOG" >&2
        return 1
    fi

    log "Emulator ready on serial: $SERIAL"
}

run_gradle_install() {
    local tmp
    local status
    tmp="$(mktemp)"

    set +e
    (
        cd "$PROJECT_DIR/android"
        ./gradlew "$@" 2>&1
    ) | tee "$tmp"
    status=${PIPESTATUS[0]}
    set -e

    if [[ $status -ne 0 ]]; then
        if rg -q "INSTALL_FAILED_UPDATE_INCOMPATIBLE" "$tmp"; then
            rm -f "$tmp"
            return 2
        fi
        rm -f "$tmp"
        return "$status"
    fi

    rm -f "$tmp"
    return 0
}

if ! command -v node >/dev/null 2>&1; then
    echo "node is required" >&2
    exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
    echo "npm is required" >&2
    exit 1
fi
if ! command -v rg >/dev/null 2>&1; then
    echo "rg (ripgrep) is required" >&2
    exit 1
fi
if ! ensure_adb; then
    echo "adb not found in PATH or common Android SDK locations" >&2
    exit 1
fi

"$ADB_BIN" start-server >/dev/null 2>&1 || true

install_dependencies_if_needed
run_web_build_if_needed
ensure_android_platform
sync_android_platform
enforce_standalone_native_config

if [[ -z "$PACKAGE_NAME" ]]; then
    if ! PACKAGE_NAME="$(detect_package_name)"; then
        echo "Could not detect package name. Pass --package <id>." >&2
        exit 1
    fi
fi

ADB_CMD=("$ADB_BIN")

if [[ -n "$SERIAL" ]]; then
    ADB_CMD+=( -s "$SERIAL" )
    if [[ "$("${ADB_CMD[@]}" get-state 2>/dev/null || true)" != "device" ]]; then
        echo "Device '$SERIAL' is not available." >&2
        exit 1
    fi
else
    connected=()
    while IFS= read -r dev_serial; do
        [[ -n "$dev_serial" ]] && connected+=("$dev_serial")
    done < <("$ADB_BIN" devices | awk 'NR>1 && $2=="device" {print $1}')

    if [[ ${#connected[@]} -eq 0 ]]; then
        launch_emulator_fallback
    else
        if [[ ${#connected[@]} -gt 1 ]]; then
            log "Multiple devices found; using first: ${connected[0]}"
        fi
        SERIAL="${connected[0]}"
    fi

    ADB_CMD+=( -s "$SERIAL" )
fi

if [[ -z "$ARCHIVE_DIR" ]]; then
    ARCHIVE_DIR="$PROJECT_DIR/build-artifacts/apk"
fi

log "Project: $PROJECT_DIR"
log "Package: $PACKAGE_NAME"
log "Target serial: $SERIAL"

gradle_args=()
if [[ $CLEAN_BUILD -eq 1 ]]; then
    gradle_args+=(clean)
fi
gradle_args+=(installDebug --warning-mode all)

if ! run_gradle_install "${gradle_args[@]}"; then
    status=$?
    if [[ $status -eq 2 ]]; then
        log "Detected INSTALL_FAILED_UPDATE_INCOMPATIBLE; uninstalling and retrying"
        "${ADB_CMD[@]}" uninstall "$PACKAGE_NAME" >/dev/null 2>&1 || true
        (
            cd "$PROJECT_DIR/android"
            ./gradlew installDebug --warning-mode all
        )
    else
        exit "$status"
    fi
fi

APK_SOURCE="$(find "$PROJECT_DIR/android/app/build/outputs/apk/debug" -type f -name '*.apk' | sort | tail -n 1 || true)"
if [[ -z "$APK_SOURCE" ]]; then
    echo "Could not find generated debug APK in android/app/build/outputs/apk/debug" >&2
    exit 1
fi

mkdir -p "$ARCHIVE_DIR"
timestamp="$(date +%Y%m%d_%H%M%S)"
apk_base="$(basename "${APK_SOURCE%.apk}")"
APK_ARCHIVE_PATH="$ARCHIVE_DIR/${apk_base}-${timestamp}.apk"
cp "$APK_SOURCE" "$APK_ARCHIVE_PATH"
log "Archived APK: $APK_ARCHIVE_PATH"

if [[ $SKIP_LAUNCH -eq 0 ]]; then
    if [[ -n "$ACTIVITY_NAME" ]]; then
        component="$ACTIVITY_NAME"
        if [[ "$component" != */* ]]; then
            if [[ "$component" == .* ]]; then
                component="${PACKAGE_NAME}/${component}"
            elif [[ "$component" == "$PACKAGE_NAME"* ]]; then
                component="$component"
            else
                component="${PACKAGE_NAME}/.${component}"
            fi
        fi
        "${ADB_CMD[@]}" shell am start -W -n "$component"
        log "Launched component: $component"
    else
        set +e
        launch_output="$("${ADB_CMD[@]}" shell monkey -p "$PACKAGE_NAME" -c android.intent.category.LAUNCHER 1 2>&1)"
        launch_status=$?
        set -e
        printf '%s\n' "$launch_output"
        if [[ $launch_status -ne 0 ]]; then
            log "monkey returned $launch_status; attempting fallback launcher resolution"
            resolved_component="$("${ADB_CMD[@]}" shell cmd package resolve-activity --brief "$PACKAGE_NAME" 2>/dev/null | tr -d '\r' | tail -n 1 || true)"
            if [[ "$resolved_component" == */* ]]; then
                set +e
                fallback_output="$("${ADB_CMD[@]}" shell am start -W -n "$resolved_component" 2>&1)"
                fallback_status=$?
                set -e
                printf '%s\n' "$fallback_output"
                if [[ $fallback_status -eq 0 ]]; then
                    log "Fallback launch succeeded with component: $resolved_component"
                else
                    log "Fallback launch failed with status $fallback_status"
                fi
            else
                log "Could not resolve launcher component for package: $PACKAGE_NAME"
            fi
        fi
        log "Launch intent sent for package: $PACKAGE_NAME"
    fi
else
    log "Launch skipped (--skip-launch)"
fi

if [[ $EMULATOR_STARTED -eq 1 ]]; then
    log "Emulator was auto-started and left running for manual testing"
    if [[ -n "$EMULATOR_LOG" ]]; then
        log "Emulator log: $EMULATOR_LOG"
    fi
fi

log "Done"
