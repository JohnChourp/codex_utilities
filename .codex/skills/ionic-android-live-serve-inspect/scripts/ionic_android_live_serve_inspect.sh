#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  ionic_android_live_serve_inspect.sh [options]

Options:
  --project <path>       Ionic project root (default: current directory)
  --port <number>        Ionic serve port (default: 8206)
  --serial <id>          USB ADB serial for target Android device
  --package <id>         Override package/applicationId detection
  --activity <name>      Activity to launch (e.g. .MainActivity)
  --open-inspect         Open chrome://inspect/#devices automatically
  --skip-prepare         Skip project prepare flow (npm install/configure/icons/build-after)
  --skip-inspect-open    Do not open chrome://inspect/#devices
  --skip-launch          Install only, do not launch app
  -h, --help             Show help
USAGE
}

log() {
    printf '[ionic-android-live-serve-inspect] %s\n' "$*"
}

fail() {
    echo "$*" >&2
    exit 1
}

PROJECT_DIR="$PWD"
PORT="8206"
PORT_EXPLICIT=0
SERIAL=""
PACKAGE_NAME=""
ACTIVITY_NAME=""
SKIP_INSPECT_OPEN=1
SKIP_LAUNCH=0
SKIP_PREPARE=0
ADB_BIN=""
SERVE_PID=""
ACTIVE_SERIAL=""
ADB_REVERSE_SET=0

while (($# > 0)); do
    case "$1" in
        --project)
            PROJECT_DIR="${2:-}"
            shift 2
            ;;
        --port)
            PORT="${2:-}"
            PORT_EXPLICIT=1
            shift 2
            ;;
        --serial)
            SERIAL="${2:-}"
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
        --skip-prepare)
            SKIP_PREPARE=1
            shift
            ;;
        --open-inspect)
            SKIP_INSPECT_OPEN=0
            shift
            ;;
        --skip-inspect-open)
            SKIP_INSPECT_OPEN=1
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
            fail "Unknown option: $1"
            ;;
    esac
done

if [[ -z "$PROJECT_DIR" ]]; then
    fail "Project path is empty"
fi

PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd -P)"

if [[ ! "$PORT" =~ ^[0-9]+$ ]]; then
    fail "Invalid port '$PORT'. Use a numeric value, e.g. --port 8206"
fi
if ((PORT < 1 || PORT > 65535)); then
    fail "Port '$PORT' is out of range (1-65535)"
fi

on_signal() {
    log "Interrupt received. Stopping session..."
    exit 130
}

cleanup() {
    if [[ $ADB_REVERSE_SET -eq 1 && -n "$ACTIVE_SERIAL" && -n "$ADB_BIN" ]]; then
        "$ADB_BIN" -s "$ACTIVE_SERIAL" reverse --remove "tcp:$PORT" >/dev/null 2>&1 || true
        log "Removed adb reverse tcp:$PORT from device $ACTIVE_SERIAL"
    fi

    if [[ -n "$SERVE_PID" ]] && kill -0 "$SERVE_PID" >/dev/null 2>&1; then
        kill "$SERVE_PID" >/dev/null 2>&1 || true
        wait "$SERVE_PID" 2>/dev/null || true
        log "Stopped ionic serve (pid: $SERVE_PID)"
    fi
}

trap on_signal INT TERM
trap cleanup EXIT

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

    local candidate
    for candidate in "${candidates[@]}"; do
        if [[ -x "$candidate" ]]; then
            ADB_BIN="$candidate"
            export PATH="$(dirname "$candidate"):$PATH"
            return 0
        fi
    done

    return 1
}

is_port_open() {
    local port="$1"
    node - "$port" <<'NODE' >/dev/null 2>&1
const net = require('net');
const port = Number(process.argv[2]);
const socket = net.createConnection({ host: '127.0.0.1', port, timeout: 800 });
socket.on('connect', () => { socket.destroy(); process.exit(0); });
socket.on('timeout', () => { socket.destroy(); process.exit(1); });
socket.on('error', () => process.exit(1));
NODE
}

is_server_ready() {
    local port="$1"
    node - "$port" <<'NODE' >/dev/null 2>&1
const http = require('http');
const port = Number(process.argv[2]);
const req = http.get({ host: '127.0.0.1', port, path: '/', timeout: 1200 }, res => {
  const ok = res.statusCode >= 200 && res.statusCode < 500;
  res.resume();
  process.exit(ok ? 0 : 1);
});
req.on('timeout', () => { req.destroy(); process.exit(1); });
req.on('error', () => process.exit(1));
NODE
}

run_npm_install() {
    log "Running npm install"
    (
        cd "$PROJECT_DIR"
        npm install
    )
}

has_npm_script() {
    local script_name="$1"
    node - "$PROJECT_DIR/package.json" "$script_name" <<'NODE' >/dev/null 2>&1
const fs = require('fs');
const packageJsonPath = process.argv[2];
const scriptName = process.argv[3];
const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const hasScript = !!(pkg && pkg.scripts && Object.prototype.hasOwnProperty.call(pkg.scripts, scriptName));
process.exit(hasScript ? 0 : 1);
NODE
}

ensure_android_platform() {
    if [[ -f "$PROJECT_DIR/android/gradlew" ]]; then
        return 0
    fi

    log "Android platform missing; running npx cap add android"
    (
        cd "$PROJECT_DIR"
        printf 'n\n' | npx cap add android
    )

    if [[ ! -f "$PROJECT_DIR/android/gradlew" ]]; then
        fail "android/gradlew is still missing after npx cap add android"
    fi
}

sync_android_platform() {
    log "Running npx cap sync android"
    (
        cd "$PROJECT_DIR"
        npx cap sync android
    )
}

run_configure_if_available() {
    if ! has_npm_script "configure"; then
        return 0
    fi

    log "Running npm run configure (resilient mode)"
    local tmp status
    tmp="$(mktemp)"

    set +e
    (
        cd "$PROJECT_DIR"
        npm run configure 2>&1
    ) | tee "$tmp"
    status=${PIPESTATUS[0]}
    set -e

    if [[ $status -eq 0 ]]; then
        rm -f "$tmp"
        return 0
    fi

    if rg -q "spawn pod ENOENT|Updating iOS native dependencies with pod install - failed|AccessDenied|ListObjectsV2 operation: Access Denied" "$tmp"; then
        log "configure hit non-Android prerequisites (iOS pods/AWS). Continuing with Android flow."
        rm -f "$tmp"
        return 0
    fi

    log "configure exited with status $status. Continuing with Android flow."
    rm -f "$tmp"
    return 0
}

run_push_icons_android_if_available() {
    if ! has_npm_script "push_icons_android"; then
        return 0
    fi

    log "Refreshing Android launcher icons (npm run push_icons_android)"
    (
        cd "$PROJECT_DIR"
        npm run push_icons_android
    )
}

run_build_after_if_present() {
    if [[ ! -f "$PROJECT_DIR/build-after.js" ]]; then
        return 0
    fi

    log "Running build-after.js to apply native post-processing"
    (
        cd "$PROJECT_DIR"
        node build-after.js
    )
}

ensure_branch_resources_if_needed() {
    if ! rg -q '"capacitor-branch-deep-links"' "$PROJECT_DIR/package.json"; then
        return 0
    fi

    local strings_file="$PROJECT_DIR/android/app/src/main/res/values/strings.xml"
    if [[ ! -f "$strings_file" ]]; then
        return 0
    fi

    if rg -q '<string name="branch_key">[^<]+' "$strings_file" \
        && rg -q '<string name="applink_host">[^<]+' "$strings_file" \
        && rg -q '<string name="applink_host_alternate">[^<]+' "$strings_file"; then
        return 0
    fi

    log "Branch plugin detected but Android Branch strings are missing. Attempting auto-fix."
    run_build_after_if_present
    sync_android_platform

    if ! rg -q '<string name="branch_key">[^<]+' "$strings_file"; then
        fail "Missing Android branch_key resource in strings.xml after auto-fix. Run: npm run configure && node build-after.js && npx cap sync android"
    fi
}

prepare_android_project() {
    run_npm_install
    run_configure_if_available
    ensure_android_platform
    run_push_icons_android_if_available
    run_build_after_if_present
    sync_android_platform
    ensure_branch_resources_if_needed
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

select_usb_device() {
    if [[ -n "$SERIAL" ]]; then
        if [[ "$SERIAL" == emulator-* ]]; then
            fail "Serial '$SERIAL' is an emulator. This skill requires a USB Android phone"
        fi
        if [[ "$("$ADB_BIN" -s "$SERIAL" get-state 2>/dev/null || true)" != "device" ]]; then
            fail "Device '$SERIAL' is not available"
        fi
        ACTIVE_SERIAL="$SERIAL"
        return 0
    fi

    local devices=()
    while IFS= read -r serial; do
        [[ -n "$serial" ]] && devices+=("$serial")
    done < <("$ADB_BIN" devices | awk 'NR>1 && $2=="device" && $1 !~ /^emulator-/ {print $1}')

    if [[ ${#devices[@]} -eq 0 ]]; then
        fail "No USB Android device found. Connect phone with USB debugging enabled and retry"
    fi

    if [[ ${#devices[@]} -gt 1 ]]; then
        log "Multiple USB devices found; using first: ${devices[0]}"
    fi

    ACTIVE_SERIAL="${devices[0]}"
    SERIAL="$ACTIVE_SERIAL"
}

start_ionic_serve() {
    if is_port_open "$PORT"; then
        if [[ $PORT_EXPLICIT -eq 1 ]]; then
            fail "Port $PORT is already in use. Use a different port, e.g. --port 8210"
        fi

        local candidate
        local found=0
        for candidate in $(seq $((PORT + 1)) $((PORT + 20))); do
            if ! is_port_open "$candidate"; then
                log "Port $PORT is busy; switching to available port $candidate"
                PORT="$candidate"
                found=1
                break
            fi
        done

        if [[ $found -eq 0 ]]; then
            fail "Port $PORT is busy and no available fallback port found in range $((PORT + 1))-$((PORT + 20))"
        fi
    fi

    log "Starting ionic serve on port $PORT"
    (
        cd "$PROJECT_DIR"
        npx ionic serve --port "$PORT" --host 0.0.0.0 --no-open --no-interactive
    ) &
    SERVE_PID="$!"

    local i
    for i in {1..90}; do
        if ! kill -0 "$SERVE_PID" >/dev/null 2>&1; then
            fail "ionic serve exited early (pid: $SERVE_PID). Check output above"
        fi
        if is_server_ready "$PORT"; then
            log "Ionic live server is ready at http://127.0.0.1:$PORT"
            return 0
        fi
        sleep 1
    done

    fail "Ionic server did not become ready in time on port $PORT"
}

write_native_live_server_config() {
    local native_config="$PROJECT_DIR/android/app/src/main/assets/capacitor.config.json"
    if [[ ! -f "$native_config" ]]; then
        fail "Native Capacitor config not found at $native_config"
    fi

    node - "$native_config" "$PORT" <<'NODE'
const fs = require('fs');
const file = process.argv[2];
const port = String(process.argv[3]);
const raw = fs.readFileSync(file, 'utf8');
let json;
try {
  json = JSON.parse(raw);
} catch (error) {
  console.error(`Failed to parse JSON in ${file}: ${error.message}`);
  process.exit(1);
}
if (!json || typeof json !== 'object') {
  console.error(`Invalid JSON root in ${file}`);
  process.exit(1);
}
if (!json.server || typeof json.server !== 'object') {
  json.server = {};
}
json.server.url = `http://localhost:${port}`;
json.server.cleartext = true;
fs.writeFileSync(file, `${JSON.stringify(json, null, 2)}\n`);
NODE

    log "Updated native capacitor.config.json with server.url=http://localhost:$PORT"
}

ensure_android_manifest_allows_cleartext() {
    local manifest_file="$PROJECT_DIR/android/app/src/main/AndroidManifest.xml"
    if [[ ! -f "$manifest_file" ]]; then
        fail "AndroidManifest.xml not found at $manifest_file"
    fi

    node - "$manifest_file" <<'NODE'
const fs = require('fs');
const file = process.argv[2];
const xml = fs.readFileSync(file, 'utf8');
const appTagRegex = /<application\b[^>]*>/m;
const match = xml.match(appTagRegex);
if (!match) {
  console.error(`Could not find <application> tag in ${file}`);
  process.exit(1);
}
const appTag = match[0];
let newAppTag = appTag;

if (/android:usesCleartextTraffic\s*=/.test(appTag)) {
  newAppTag = appTag.replace(/android:usesCleartextTraffic\s*=\s*"[^"]*"/, 'android:usesCleartextTraffic="true"');
} else {
  newAppTag = appTag.replace(/>$/, ' android:usesCleartextTraffic="true">');
}

if (newAppTag !== appTag) {
  const updated = xml.replace(appTag, newAppTag);
  fs.writeFileSync(file, updated);
}
NODE

    log "Ensured AndroidManifest.xml has android:usesCleartextTraffic=\"true\""
}

run_gradle_install() {
    local tmp status
    tmp="$(mktemp)"

    set +e
    (
        cd "$PROJECT_DIR/android"
        ./gradlew installDebug --warning-mode all 2>&1
    ) | tee "$tmp"
    status=${PIPESTATUS[0]}
    set -e

    if [[ $status -ne 0 ]]; then
        if rg -q "INSTALL_FAILED_UPDATE_INCOMPATIBLE|INSTALL_FAILED_VERSION_DOWNGRADE" "$tmp"; then
            rm -f "$tmp"
            return 2
        fi
        rm -f "$tmp"
        return "$status"
    fi

    rm -f "$tmp"
    return 0
}

launch_app() {
    if [[ $SKIP_LAUNCH -eq 1 ]]; then
        log "Launch skipped (--skip-launch)"
        return 0
    fi

    local adb_cmd=("$ADB_BIN" -s "$ACTIVE_SERIAL")

    if [[ -n "$ACTIVITY_NAME" ]]; then
        local component="$ACTIVITY_NAME"
        if [[ "$component" != */* ]]; then
            if [[ "$component" == .* ]]; then
                component="${PACKAGE_NAME}/${component}"
            elif [[ "$component" == "$PACKAGE_NAME"* ]]; then
                component="$component"
            else
                component="${PACKAGE_NAME}/.${component}"
            fi
        fi
        "${adb_cmd[@]}" shell am start -W -n "$component"
        log "Launched component: $component"
        return 0
    fi

    set +e
    local launch_output launch_status
    launch_output="$("${adb_cmd[@]}" shell monkey -p "$PACKAGE_NAME" -c android.intent.category.LAUNCHER 1 2>&1)"
    launch_status=$?
    set -e

    printf '%s\n' "$launch_output"
    if [[ $launch_status -ne 0 ]]; then
        log "monkey launch returned $launch_status"
        return "$launch_status"
    fi

    log "Launch intent sent for package: $PACKAGE_NAME"
}

open_inspect_tab() {
    if [[ $SKIP_INSPECT_OPEN -eq 1 ]]; then
        log "Inspect tab open skipped (--skip-inspect-open)"
        return 0
    fi

    local url="chrome://inspect/#devices"
    local browser
    for browser in google-chrome google-chrome-stable chromium chromium-browser; do
        if command -v "$browser" >/dev/null 2>&1; then
            "$browser" "$url" >/dev/null 2>&1 &
            disown "$!" 2>/dev/null || true
            log "Opened inspect tab via $browser"
            return 0
        fi
    done

    if command -v xdg-open >/dev/null 2>&1; then
        if xdg-open "$url" >/dev/null 2>&1; then
            log "Opened inspect tab via xdg-open"
            return 0
        fi
    fi

    log "Warning: could not open chrome://inspect/#devices automatically"
    return 0
}

if ! command -v node >/dev/null 2>&1; then
    fail "node is required"
fi
if ! command -v npm >/dev/null 2>&1; then
    fail "npm is required"
fi
if ! command -v rg >/dev/null 2>&1; then
    fail "rg (ripgrep) is required"
fi
if ! ensure_adb; then
    fail "adb not found in PATH or common Android SDK locations"
fi

if [[ ! -f "$PROJECT_DIR/package.json" ]]; then
    fail "package.json not found in $PROJECT_DIR"
fi
if [[ ! -f "$PROJECT_DIR/capacitor.config.ts" && ! -f "$PROJECT_DIR/capacitor.config.json" ]]; then
    fail "capacitor.config.ts/json not found in $PROJECT_DIR"
fi

"$ADB_BIN" start-server >/dev/null 2>&1 || true

if [[ $SKIP_PREPARE -eq 1 ]]; then
    log "Project prepare skipped (--skip-prepare)"
    ensure_android_platform
    sync_android_platform
else
    prepare_android_project
fi
start_ionic_serve

if [[ -z "$PACKAGE_NAME" ]]; then
    if ! PACKAGE_NAME="$(detect_package_name)"; then
        fail "Could not detect package name. Pass --package <id>"
    fi
fi

select_usb_device
write_native_live_server_config
ensure_android_manifest_allows_cleartext

"$ADB_BIN" -s "$ACTIVE_SERIAL" reverse "tcp:$PORT" "tcp:$PORT"
ADB_REVERSE_SET=1
log "Applied adb reverse tcp:$PORT tcp:$PORT on device $ACTIVE_SERIAL"

if ! run_gradle_install; then
    status=$?
    if [[ $status -eq 2 ]]; then
        log "Detected incompatible installed package; uninstalling and retrying installDebug"
        "$ADB_BIN" -s "$ACTIVE_SERIAL" uninstall "$PACKAGE_NAME" >/dev/null 2>&1 || true
        (
            cd "$PROJECT_DIR/android"
            ./gradlew installDebug --warning-mode all
        )
    else
        exit "$status"
    fi
fi

launch_app
open_inspect_tab

log "Project: $PROJECT_DIR"
log "Package: $PACKAGE_NAME"
log "Target serial: $ACTIVE_SERIAL"
log "Live URL: http://localhost:$PORT"
log "Inspect URL: chrome://inspect/#devices"
log "Session active. Press Ctrl+C to stop"

echo "Debug commands:"
echo "  adb -s $ACTIVE_SERIAL logcat"
echo "  adb -s $ACTIVE_SERIAL reverse --list"
echo "  chrome://inspect/#devices"

set +e
wait "$SERVE_PID"
serve_status=$?
set -e

if [[ $serve_status -ne 0 ]]; then
    fail "ionic serve exited with status $serve_status"
fi
