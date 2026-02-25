#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  android_debug_deploy.sh [options]

Options:
  --project <path>       Android project root (default: current directory)
  --package <id>         Override package/applicationId detection
  --activity <name>      Activity to launch (e.g. .MainActivity)
  --serial <id>          ADB serial for target device
  --avd <name>           Preferred Android Virtual Device name for auto-launch fallback
  --archive-dir <path>   Output directory for archived APK copies
  --clean                Run clean before installDebug
  --skip-launch          Do not launch app after install
  -h, --help             Show help
EOF
}

log() {
    printf '[android-debug-deploy] %s\n' "$*"
}

PROJECT_DIR="$PWD"
PACKAGE_NAME=""
ACTIVITY_NAME=""
SERIAL="${ADB_SERIAL:-}"
ARCHIVE_DIR=""
CLEAN_BUILD=0
SKIP_LAUNCH=0
ADB_BIN=""
EMULATOR_BIN=""
AVD_NAME="${ANDROID_AVD_NAME:-}"
EMULATOR_LOG=""
EMULATOR_STARTED=0
EMULATOR_PID=""

while (($# > 0)); do
    case "$1" in
        --project)
            PROJECT_DIR="${2:-}"
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
        --serial)
            SERIAL="${2:-}"
            shift 2
            ;;
        --avd)
            AVD_NAME="${2:-}"
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

if [[ -z "$PROJECT_DIR" ]]; then
    echo "Project path is empty." >&2
    exit 1
fi

PROJECT_DIR="$(realpath "$PROJECT_DIR")"

if [[ ! -f "$PROJECT_DIR/gradlew" ]]; then
    echo "gradlew not found in $PROJECT_DIR" >&2
    exit 1
fi

sanitize_filename_part() {
    local value="$1"
    echo "$value" | tr -cs 'A-Za-z0-9._-' '_'
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

    local candidate
    for candidate in "${candidates[@]}"; do
        if [[ -x "$candidate" ]]; then
            export PATH="$(dirname "$candidate"):$PATH"
            ADB_BIN="$candidate"
            log "Using adb from fallback path: $candidate"
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

    local candidate
    for candidate in "${candidates[@]}"; do
        if [[ -x "$candidate" ]]; then
            EMULATOR_BIN="$candidate"
            return 0
        fi
    done
    return 1
}

pick_avd() {
    collect_lines avds "$EMULATOR_BIN" -list-avds
    if [[ ${#avds[@]} -eq 0 ]]; then
        echo "No Android Virtual Devices found. Create one from Android Studio Device Manager." >&2
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
        echo "Requested AVD '$AVD_NAME' was not found." >&2
        printf 'Available AVDs:\n' >&2
        printf '  - %s\n' "${avds[@]}" >&2
        return 1
    fi

    for avd in "${avds[@]}"; do
        if [[ "$avd" == "Motorola_Edge_40_Neo_API_35" ]]; then
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
        serial="$("$ADB_BIN" devices | awk 'NR>1 && $2=="device" {print $1; exit}')"
        if [[ -n "$serial" ]]; then
            break
        fi
        sleep 2
    done

    if [[ -z "$serial" ]]; then
        return 1
    fi

    for i in {1..120}; do
        boot="$("$ADB_BIN" -s "$serial" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
        if [[ "$boot" == "1" ]]; then
            break
        fi
        sleep 2
    done

    echo "$serial"
}

launch_emulator_fallback() {
    local selected_avd safe_avd timestamp log_dir
    if ! ensure_emulator; then
        echo "emulator binary not found in PATH or common SDK locations." >&2
        return 1
    fi
    selected_avd="$(pick_avd)" || return 1
    safe_avd="$(sanitize_filename_part "$selected_avd")"
    timestamp="$(date +%Y%m%d_%H%M%S)"
    log_dir="$PROJECT_DIR/build-artifacts/emulator-logs"
    mkdir -p "$log_dir"
    EMULATOR_LOG="$log_dir/emulator-${safe_avd}-${timestamp}.log"

    log "No connected device detected. Launching emulator AVD: $selected_avd"
    nohup "$EMULATOR_BIN" -avd "$selected_avd" -no-snapshot-load -no-boot-anim </dev/null >"$EMULATOR_LOG" 2>&1 &
    EMULATOR_PID="$!"
    disown "$EMULATOR_PID" 2>/dev/null || true
    EMULATOR_STARTED=1

    local serial
    if ! serial="$(wait_for_online_device)"; then
        echo "Emulator did not become ready in time." >&2
        if [[ -f "$EMULATOR_LOG" ]]; then
            echo "Emulator log: $EMULATOR_LOG" >&2
            tail -n 40 "$EMULATOR_LOG" >&2 || true
        fi
        return 1
    fi

    SERIAL="$serial"
    log "Emulator ready on serial: $SERIAL"
    log "Emulator PID: $EMULATOR_PID"
    if [[ -n "$EMULATOR_LOG" ]]; then
        log "Emulator log: $EMULATOR_LOG"
    fi
}

if ! ensure_adb; then
    echo "adb not found in PATH or common SDK locations." >&2
    echo "Try: export PATH=\"\$HOME/Library/Android/sdk/platform-tools:\$PATH\"" >&2
    exit 1
fi

"$ADB_BIN" start-server >/dev/null 2>&1 || true

if [[ -z "$ARCHIVE_DIR" ]]; then
    ARCHIVE_DIR="$PROJECT_DIR/build-artifacts/apk"
fi

detect_package_name() {
    local file line
    for file in "$PROJECT_DIR/app/build.gradle.kts" "$PROJECT_DIR/app/build.gradle"; do
        if [[ -f "$file" ]]; then
            line="$(rg -n '^[[:space:]]*applicationId[[:space:]]*=' "$file" -m 1 | cut -d: -f2- || true)"
            if [[ -n "$line" ]]; then
                echo "$line" | sed -E 's/.*"([^"]+)".*/\1/'
                return 0
            fi
            line="$(rg -n '^[[:space:]]*namespace[[:space:]]*=' "$file" -m 1 | cut -d: -f2- || true)"
            if [[ -n "$line" ]]; then
                echo "$line" | sed -E 's/.*"([^"]+)".*/\1/'
                return 0
            fi
        fi
    done
    if [[ -f "$PROJECT_DIR/app/src/main/AndroidManifest.xml" ]]; then
        line="$(rg -n 'package=' "$PROJECT_DIR/app/src/main/AndroidManifest.xml" -m 1 | cut -d: -f2- || true)"
        if [[ -n "$line" ]]; then
            echo "$line" | sed -E 's/.*package="([^"]+)".*/\1/'
            return 0
        fi
    fi
    return 1
}

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
        if ! launch_emulator_fallback; then
            exit 1
        fi
    else
        if [[ ${#connected[@]} -gt 1 ]]; then
            log "Multiple devices found; using the first one: ${connected[0]}"
        fi
        SERIAL="${connected[0]}"
    fi
    ADB_CMD+=( -s "$SERIAL" )
fi

log "Project: $PROJECT_DIR"
log "Package: $PACKAGE_NAME"
log "Device: $SERIAL"

run_gradle_install() {
    local tmp status
    tmp="$(mktemp)"
    set +e
    "$PROJECT_DIR/gradlew" "$@" 2>&1 | tee "$tmp"
    status=${PIPESTATUS[0]}
    set -e
    if [[ $status -ne 0 ]]; then
        if rg -q "INSTALL_FAILED_UPDATE_INCOMPATIBLE" "$tmp"; then
            rm -f "$tmp"
            return 2
        fi
        rm -f "$tmp"
        return $status
    fi
    rm -f "$tmp"
    return 0
}

GRADLE_ARGS=()
if [[ $CLEAN_BUILD -eq 1 ]]; then
    GRADLE_ARGS+=(clean)
fi
GRADLE_ARGS+=(installDebug --warning-mode all)

if ! run_gradle_install "${GRADLE_ARGS[@]}"; then
    status=$?
    if [[ $status -eq 2 ]]; then
        log "Detected INSTALL_FAILED_UPDATE_INCOMPATIBLE. Uninstalling old app and retrying."
        "${ADB_CMD[@]}" uninstall "$PACKAGE_NAME" >/dev/null 2>&1 || true
        "$PROJECT_DIR/gradlew" installDebug --warning-mode all
    else
        exit $status
    fi
fi

APK_SOURCE="$(find "$PROJECT_DIR/app/build/outputs/apk/debug" -type f -name '*.apk' | sort | tail -n 1 || true)"
if [[ -z "$APK_SOURCE" ]]; then
    echo "Could not find generated debug APK in app/build/outputs/apk/debug." >&2
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
            log "monkey returned $launch_status; proceeding without failure to keep emulator running."
        fi
        log "Launch intent sent for package: $PACKAGE_NAME"
    fi
else
    log "Launch skipped (--skip-launch)."
fi

if [[ $EMULATOR_STARTED -eq 1 ]]; then
    log "Emulator was auto-started and is intentionally left running for manual testing."
fi

log "Done."
