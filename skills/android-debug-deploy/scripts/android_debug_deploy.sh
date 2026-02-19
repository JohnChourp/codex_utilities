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

if ! command -v adb >/dev/null 2>&1; then
    echo "adb not found in PATH." >&2
    exit 1
fi

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

ADB_CMD=(adb)
if [[ -n "$SERIAL" ]]; then
    ADB_CMD+=( -s "$SERIAL" )
    if [[ "$("${ADB_CMD[@]}" get-state 2>/dev/null || true)" != "device" ]]; then
        echo "Device '$SERIAL' is not available." >&2
        exit 1
    fi
else
    mapfile -t connected < <(adb devices | awk 'NR>1 && $2=="device" {print $1}')
    if [[ ${#connected[@]} -eq 0 ]]; then
        echo "No connected Android devices found." >&2
        exit 1
    fi
    if [[ ${#connected[@]} -gt 1 ]]; then
        log "Multiple devices found; using the first one: ${connected[0]}"
    fi
    SERIAL="${connected[0]}"
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
        "${ADB_CMD[@]}" shell am start -n "$component"
        log "Launched component: $component"
    else
        "${ADB_CMD[@]}" shell monkey -p "$PACKAGE_NAME" -c android.intent.category.LAUNCHER 1
        log "Launched package via LAUNCHER intent: $PACKAGE_NAME"
    fi
else
    log "Launch skipped (--skip-launch)."
fi

log "Done."
