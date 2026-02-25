#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  ionic_ios_codex_deploy.sh [options]

Options:
  --project <path>       Ionic project root (default: current directory)
  --device-name <name>   Simulator name (default: Codex iPhone 17 Pro Max)
  --device-type <id>     Simulator device type identifier
  --runtime <id>         Explicit iOS runtime identifier
  --udid <id>            Target simulator UDID
  --bundle-id <id>       Override launch bundle identifier
  --archive-dir <path>   Output directory for archived .app copies
  --skip-build           Skip web build (npm run build / ionic build)
  --skip-launch          Do not launch app after install
  -h, --help             Show help
USAGE
}

log() {
    printf '[ionic-ios-codex-deploy] %s\n' "$*"
}

PROJECT_DIR="$PWD"
DEVICE_NAME="Codex iPhone 17 Pro Max"
DEVICE_TYPE="com.apple.CoreSimulator.SimDeviceType.iPhone-17-Pro-Max"
RUNTIME_ID=""
UDID=""
BUNDLE_ID=""
ARCHIVE_DIR=""
SKIP_BUILD=0
SKIP_LAUNCH=0

while (($# > 0)); do
    case "$1" in
        --project)
            PROJECT_DIR="${2:-}"
            shift 2
            ;;
        --device-name)
            DEVICE_NAME="${2:-}"
            shift 2
            ;;
        --device-type)
            DEVICE_TYPE="${2:-}"
            shift 2
            ;;
        --runtime)
            RUNTIME_ID="${2:-}"
            shift 2
            ;;
        --udid)
            UDID="${2:-}"
            shift 2
            ;;
        --bundle-id)
            BUNDLE_ID="${2:-}"
            shift 2
            ;;
        --archive-dir)
            ARCHIVE_DIR="${2:-}"
            shift 2
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
if ! command -v xcrun >/dev/null 2>&1; then
    echo "xcrun is required. Install Xcode Command Line Tools." >&2
    exit 1
fi
if ! xcrun simctl help >/dev/null 2>&1; then
    echo "simctl is unavailable. Make sure Xcode is installed correctly." >&2
    exit 1
fi

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

ensure_ios_platform() {
    if [[ -d "$PROJECT_DIR/ios/App/App.xcworkspace" ]]; then
        return 0
    fi

    log "iOS platform missing; running npx cap add ios"
    (
        cd "$PROJECT_DIR"
        npx cap add ios
    )

    if [[ ! -d "$PROJECT_DIR/ios/App/App.xcworkspace" ]]; then
        echo "ios/App/App.xcworkspace is still missing after npx cap add ios" >&2
        exit 1
    fi
}

sync_ios_platform() {
    log "Running npx cap sync ios"
    (
        cd "$PROJECT_DIR"
        npx cap sync ios
    )
}

latest_runtime_id() {
    xcrun simctl list runtimes available \
        | awk '/^iOS / && /com\.apple\.CoreSimulator\.SimRuntime\.iOS-/ { print $NF }' \
        | awk '{v=$0; sub(/^.*iOS-/, "", v); gsub(/-/, ".", v); print v "|" $0}' \
        | sort -t'|' -k1,1V \
        | tail -n 1 \
        | cut -d'|' -f2
}

runtime_exists() {
    local runtime="$1"
    xcrun simctl list runtimes available | rg -Fq "$runtime"
}

find_existing_udid() {
    local target_name="$1"
    local runtime_id="$2"
    local device_type="$3"

    xcrun simctl list devices -j \
        | /usr/bin/python3 -c '
import json
import sys

target_name = sys.argv[1]
runtime_id = sys.argv[2]
device_type = sys.argv[3]
data = json.load(sys.stdin)
devices = data.get("devices", {})

for dev in devices.get(runtime_id, []):
    if dev.get("isAvailable") and dev.get("name") == target_name and dev.get("deviceTypeIdentifier") == device_type:
        print(dev["udid"])
        sys.exit(0)

for _, entries in devices.items():
    for dev in entries:
        if dev.get("isAvailable") and dev.get("name") == target_name and dev.get("deviceTypeIdentifier") == device_type:
            print(dev["udid"])
            sys.exit(0)
' "$target_name" "$runtime_id" "$device_type"
}

udid_exists() {
    local udid="$1"
    xcrun simctl list devices -j | /usr/bin/python3 -c '
import json
import sys

udid = sys.argv[1]
data = json.load(sys.stdin)
for entries in data.get("devices", {}).values():
    for dev in entries:
        if dev.get("udid") == udid and dev.get("isAvailable"):
            sys.exit(0)
sys.exit(1)
' "$udid"
}

ensure_simulator_ready() {
    if [[ -n "$UDID" ]]; then
        if ! udid_exists "$UDID"; then
            echo "Requested UDID not found/available: $UDID" >&2
            exit 1
        fi
        log "Using provided simulator UDID: $UDID"
    else
        if [[ -z "$RUNTIME_ID" ]]; then
            RUNTIME_ID="$(latest_runtime_id)"
        fi

        if [[ -z "$RUNTIME_ID" ]]; then
            echo "No available iOS simulator runtime found." >&2
            exit 1
        fi

        if ! runtime_exists "$RUNTIME_ID"; then
            echo "Requested runtime is not available: $RUNTIME_ID" >&2
            exit 1
        fi

        UDID="$(find_existing_udid "$DEVICE_NAME" "$RUNTIME_ID" "$DEVICE_TYPE" || true)"
        if [[ -z "$UDID" ]]; then
            log "Creating simulator: name='$DEVICE_NAME', type='$DEVICE_TYPE', runtime='$RUNTIME_ID'"
            UDID="$(xcrun simctl create "$DEVICE_NAME" "$DEVICE_TYPE" "$RUNTIME_ID")"
        else
            log "Reusing simulator UDID: $UDID"
        fi
    fi

    boot_log="$(mktemp)"
    if ! xcrun simctl boot "$UDID" >"$boot_log" 2>&1; then
        if rg -Eiq "already booted|current state: Booted|Unable to boot device in current state: Booted" "$boot_log"; then
            log "Simulator already booted: $UDID"
        else
            cat "$boot_log" >&2
            rm -f "$boot_log"
            exit 1
        fi
    fi
    rm -f "$boot_log"

    xcrun simctl bootstatus "$UDID" -b
    open -a Simulator --args -CurrentDeviceUDID "$UDID"
}

detect_bundle_id_from_capacitor() {
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
    return 1
}

detect_bundle_id_from_app() {
    local app_path="$1"
    local plist="$app_path/Info.plist"
    if [[ ! -f "$plist" ]]; then
        return 1
    fi

    /usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$plist" 2>/dev/null || true
}

find_built_app_path() {
    local derived_data="$1"
    local default_path="$derived_data/Build/Products/Debug-iphonesimulator/App.app"
    local discovered_path=""

    if [[ -d "$default_path" ]]; then
        echo "$default_path"
        return 0
    fi

    discovered_path="$(find "$derived_data/Build/Products/Debug-iphonesimulator" -maxdepth 2 -type d -name '*.app' \
        | rg -v '/(Tests|UITests)\.app$' \
        | head -n 1 || true)"
    echo "$discovered_path"
}

install_dependencies_if_needed
ensure_simulator_ready
run_web_build_if_needed
ensure_ios_platform
sync_ios_platform

if [[ -z "$BUNDLE_ID" ]]; then
    BUNDLE_ID="$(detect_bundle_id_from_capacitor || true)"
fi

DERIVED_DATA="$PROJECT_DIR/build-artifacts/ios-derived-data"
mkdir -p "$DERIVED_DATA"

log "Building iOS simulator app"
xcodebuild \
    -workspace "$PROJECT_DIR/ios/App/App.xcworkspace" \
    -scheme App \
    -configuration Debug \
    -sdk iphonesimulator \
    -destination "id=$UDID" \
    -derivedDataPath "$DERIVED_DATA" \
    build

APP_PATH="$(find_built_app_path "$DERIVED_DATA")"
if [[ -z "$APP_PATH" || ! -d "$APP_PATH" ]]; then
    echo "Could not find built .app under $DERIVED_DATA" >&2
    exit 1
fi

BUILT_BUNDLE_ID="$(detect_bundle_id_from_app "$APP_PATH")"
if [[ -z "$BUNDLE_ID" ]]; then
    BUNDLE_ID="$BUILT_BUNDLE_ID"
fi
if [[ -z "$BUNDLE_ID" ]]; then
    echo "Could not detect bundle id. Pass --bundle-id <id>." >&2
    exit 1
fi

log "Installing app on simulator"
xcrun simctl install "$UDID" "$APP_PATH"

if [[ -z "$ARCHIVE_DIR" ]]; then
    ARCHIVE_DIR="$PROJECT_DIR/build-artifacts/ios-app"
fi
mkdir -p "$ARCHIVE_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
archive_name="$(basename "${APP_PATH%.app}")-${timestamp}.app"
APP_ARCHIVE_PATH="$ARCHIVE_DIR/$archive_name"
ditto "$APP_PATH" "$APP_ARCHIVE_PATH"
log "Archived app: $APP_ARCHIVE_PATH"

if [[ $SKIP_LAUNCH -eq 0 ]]; then
    set +e
    launch_output="$(xcrun simctl launch "$UDID" "$BUNDLE_ID" 2>&1)"
    launch_status=$?
    set -e
    printf '%s\n' "$launch_output"
    if [[ $launch_status -ne 0 ]]; then
        echo "Failed to launch bundle id '$BUNDLE_ID' on simulator '$UDID'" >&2
        exit "$launch_status"
    fi
    log "Launch succeeded for bundle id: $BUNDLE_ID"
else
    log "Launch skipped (--skip-launch)"
fi

status_line="$(xcrun simctl list devices | rg -m1 "$UDID" || true)"
log "Project: $PROJECT_DIR"
log "Simulator UDID: $UDID"
if [[ -n "$RUNTIME_ID" ]]; then
    log "Runtime: $RUNTIME_ID"
fi
log "Bundle ID: $BUNDLE_ID"
if [[ -n "$status_line" ]]; then
    log "Simulator status: $status_line"
fi
log "Done. Simulator is left running"
