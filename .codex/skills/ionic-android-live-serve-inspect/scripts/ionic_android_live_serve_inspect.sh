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
  --full-prepare         Force full prepare flow (npm install/configure/icons/build-after)
  --skip-prepare         Skip project prepare flow (npm install/configure/icons/build-after)
  --skip-inspect-open    Do not open chrome://inspect/#devices
  --skip-launch          Install only, do not launch app
  --verbose              Stream detailed command output
  -h, --help             Show help
USAGE
}

log() {
    printf '[ionic-android-live-serve-inspect] %s\n' "$*"
}

warn() {
    printf '[ionic-android-live-serve-inspect] Warning: %s\n' "$*" >&2
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
PREPARE_MODE="auto"
PREPARE_LOG_LABEL="auto"
VERBOSE=0
ADB_BIN=""
SERVE_PID=""
TAIL_PID=""
ACTIVE_SERIAL=""
ADB_REVERSE_SET=0
LOG_DIR=""
LAST_LOG_FILE=""
SERVE_LOG_FILE=""

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
        --full-prepare)
            PREPARE_MODE="full"
            PREPARE_LOG_LABEL="--full-prepare"
            shift
            ;;
        --skip-prepare)
            PREPARE_MODE="skip"
            PREPARE_LOG_LABEL="--skip-prepare"
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
        --verbose)
            VERBOSE=1
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
    if [[ -n "$TAIL_PID" ]] && kill -0 "$TAIL_PID" >/dev/null 2>&1; then
        kill "$TAIL_PID" >/dev/null 2>&1 || true
        wait "$TAIL_PID" 2>/dev/null || true
    fi

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

init_log_dir() {
    LOG_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ionic-android-live-serve-inspect.XXXXXX")"
}

make_log_file() {
    local label="$1"
    local safe_label
    safe_label="$(printf '%s' "$label" | tr ' /' '__' | tr -cd '[:alnum:]_.-')"
    [[ -n "$safe_label" ]] || safe_label="command"
    printf '%s/%s.log\n' "$LOG_DIR" "$safe_label"
}

show_log_excerpt() {
    local logfile="$1"
    if [[ ! -f "$logfile" ]]; then
        return 0
    fi

    echo "Log file: $logfile" >&2
    echo "Last output:" >&2
    tail -n 25 "$logfile" >&2 || true
}

run_logged_command() {
    local label="$1"
    shift

    local logfile status
    logfile="$(make_log_file "$label")"
    LAST_LOG_FILE="$logfile"

    if [[ $VERBOSE -eq 1 ]]; then
        set +e
        "$@" 2>&1 | tee "$logfile"
        status=${PIPESTATUS[0]}
        set -e
    else
        set +e
        "$@" >"$logfile" 2>&1
        status=$?
        set -e
    fi

    return "$status"
}

run_project_command() {
    local label="$1"
    shift
    run_logged_command "$label" bash -lc "cd \"$PROJECT_DIR\" && $*"
}

run_android_command() {
    local label="$1"
    shift
    run_logged_command "$label" bash -lc "cd \"$PROJECT_DIR/android\" && $*"
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
    run_project_command "npm-install" "npm install" || {
        show_log_excerpt "$LAST_LOG_FILE"
        fail "npm install failed"
    }
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
    run_project_command "cap-add-android" "printf 'n\n' | npx cap add android" || {
        show_log_excerpt "$LAST_LOG_FILE"
        fail "npx cap add android failed"
    }

    if [[ ! -f "$PROJECT_DIR/android/gradlew" ]]; then
        fail "android/gradlew is still missing after npx cap add android"
    fi
}

sync_android_platform() {
    log "Running npx cap sync android"
    run_project_command "cap-sync-android" "npx cap sync android" || {
        show_log_excerpt "$LAST_LOG_FILE"
        fail "npx cap sync android failed"
    }
}

run_configure_if_available() {
    if ! has_npm_script "configure"; then
        return 0
    fi

    log "Running npm run configure (resilient mode)"
    set +e
    run_project_command "npm-run-configure" "npm run configure"
    local status=$?
    set -e

    if [[ $status -eq 0 ]]; then
        return 0
    fi

    if rg -q "spawn pod ENOENT|Updating iOS native dependencies with pod install - failed|AccessDenied|ListObjectsV2 operation: Access Denied" "$LAST_LOG_FILE"; then
        log "configure hit non-Android prerequisites (iOS pods/AWS). Continuing with Android flow."
        return 0
    fi

    warn "configure exited with status $status. Continuing with Android flow."
    show_log_excerpt "$LAST_LOG_FILE"
    return 0
}

run_push_icons_android_if_available() {
    if ! has_npm_script "push_icons_android"; then
        return 0
    fi

    log "Refreshing Android launcher icons (npm run push_icons_android)"
    run_project_command "push-icons-android" "npm run push_icons_android" || {
        show_log_excerpt "$LAST_LOG_FILE"
        fail "npm run push_icons_android failed"
    }
}

run_build_after_if_present() {
    if [[ ! -f "$PROJECT_DIR/build-after.js" ]]; then
        return 0
    fi

    log "Running build-after.js to apply native post-processing"
    run_project_command "build-after" "node build-after.js" || {
        show_log_excerpt "$LAST_LOG_FILE"
        fail "build-after.js failed"
    }
}

manifest_references_resource() {
    local resource_ref="$1"
    local manifest_file="$PROJECT_DIR/android/app/src/main/AndroidManifest.xml"
    [[ -f "$manifest_file" ]] || return 1
    rg -q "$resource_ref" "$manifest_file"
}

android_generated_resources_ready() {
    local strings_file="$PROJECT_DIR/android/app/src/main/res/values/strings.xml"
    local icon_file="$PROJECT_DIR/android/app/src/main/res/drawable/ic_tracking.png"

    if manifest_references_resource '@string/applink_host|@string/applink_host_alternate|@string/branch_key|@string/branch_test_key|@bool/branch_test_mode'; then
        [[ -f "$strings_file" ]] || return 1
        rg -q '<string name="branch_key">[^<]+' "$strings_file" || return 1
        rg -q '<string name="applink_host">[^<]+' "$strings_file" || return 1
        rg -q '<string name="applink_host_alternate">[^<]+' "$strings_file" || return 1
        rg -q '<string name="branch_test_key">[^<]+' "$strings_file" || return 1
        rg -q '<bool name="branch_test_mode">[^<]+' "$strings_file" || return 1
    fi

    if manifest_references_resource '@string/default_notification_channel_id|@string/default_notification_channel_name'; then
        [[ -f "$strings_file" ]] || return 1
        rg -q '<string name="default_notification_channel_id">[^<]+' "$strings_file" || return 1
        rg -q '<string name="default_notification_channel_name">[^<]+' "$strings_file" || return 1
    fi

    if manifest_references_resource '@drawable/ic_tracking'; then
        [[ -f "$icon_file" ]] || return 1
    fi

    return 0
}

recover_android_generated_resources() {
    log "Recovering Android generated resources before install retry"
    run_push_icons_android_if_available
    run_build_after_if_present
    sync_android_platform

    if ! android_generated_resources_ready; then
        fail "Android generated resources are still incomplete after recovery"
    fi
}

normalize_native_audio_duplicate_methods() {
    local native_audio_file="$PROJECT_DIR/node_modules/@capacitor-community/native-audio/android/src/main/java/com/getcapacitor/community/audio/NativeAudio.java"
    [[ -f "$native_audio_file" ]] || return 0

    node - "$native_audio_file" <<'NODE'
const fs = require('fs');
const file = process.argv[2];
const source = fs.readFileSync(file, 'utf8');
const duplicateBlock = `    private void requestAudioFocusIfNeeded() {\n        if (this.audioManager != null && this.focusAudio) {\n            this.audioManager.requestAudioFocus(this, AudioManager.STREAM_MUSIC, AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK);\n        }\n    }\n\n    private void abandonAudioFocusIfNeeded() {\n        if (this.audioManager != null && this.focusAudio) {\n            this.audioManager.abandonAudioFocus(this);\n        }\n    }\n\n    private void requestAudioFocusIfNeeded() {\n        if (this.audioManager != null && this.focusAudio) {\n            this.audioManager.requestAudioFocus(this, AudioManager.STREAM_MUSIC, AudioManager.AUDIOFOCUS_GAIN_TRANSIENT);\n        }\n    }\n\n    private void abandonAudioFocusIfNeeded() {\n        if (this.audioManager != null) {\n            this.audioManager.abandonAudioFocus(this);\n        }\n    }\n`;
const canonicalBlock = `    private void requestAudioFocusIfNeeded() {\n        if (this.audioManager != null && this.focusAudio) {\n            this.audioManager.requestAudioFocus(this, AudioManager.STREAM_MUSIC, AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK);\n        }\n    }\n\n    private void abandonAudioFocusIfNeeded() {\n        if (this.audioManager != null && this.focusAudio) {\n            this.audioManager.abandonAudioFocus(this);\n        }\n    }\n`;
let next = source;
if (next.includes(duplicateBlock)) {
  next = next.replace(duplicateBlock, canonicalBlock);
}
const requestMatches = next.match(/private void requestAudioFocusIfNeeded\(\)/g) || [];
const abandonMatches = next.match(/private void abandonAudioFocusIfNeeded\(\)/g) || [];
if (requestMatches.length > 1 || abandonMatches.length > 1) {
  console.error('NativeAudio.java still contains duplicate audio focus helper methods');
  process.exit(1);
}
if (next !== source) {
  fs.writeFileSync(file, next, 'utf8');
}
NODE
}

repair_native_audio_patch_if_needed() {
    local patch_script="$PROJECT_DIR/build_scripts/patch-native-audio-plugin.js"
    local native_audio_file="$PROJECT_DIR/node_modules/@capacitor-community/native-audio/android/src/main/java/com/getcapacitor/community/audio/NativeAudio.java"

    [[ -f "$native_audio_file" ]] || return 0

    if [[ -f "$patch_script" ]]; then
        log "Re-running native-audio patch before install retry"
        run_project_command "native-audio-repatch" "node build_scripts/patch-native-audio-plugin.js" || {
            show_log_excerpt "$LAST_LOG_FILE"
            fail "native-audio re-patch failed"
        }
    fi

    normalize_native_audio_duplicate_methods || fail "native-audio duplicate-method recovery failed"
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
    if ! android_generated_resources_ready; then
        recover_android_generated_resources
    fi
}

project_supports_fast_prepare_skip() {
    [[ -d "$PROJECT_DIR/node_modules" ]] || return 1
    [[ -f "$PROJECT_DIR/android/gradlew" ]] || return 1
    [[ -f "$PROJECT_DIR/android/app/src/main/assets/capacitor.config.json" ]] || return 1
    return 0
}

resolve_prepare_mode() {
    if [[ "$PREPARE_MODE" == "skip" || "$PREPARE_MODE" == "full" ]]; then
        return 0
    fi

    if project_supports_fast_prepare_skip; then
        PREPARE_MODE="skip"
        PREPARE_LOG_LABEL="auto fast path"
        log "Using fast Android-only path (auto --skip-prepare)"
        return 0
    fi

    PREPARE_MODE="full"
    PREPARE_LOG_LABEL="auto full prepare"
    log "Fast path unavailable; running full prepare"
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
    SERVE_LOG_FILE="$(make_log_file "ionic-serve")"
    (
        cd "$PROJECT_DIR"
        exec npx ionic serve --port "$PORT" --host 0.0.0.0 --no-open --no-interactive
    ) >"$SERVE_LOG_FILE" 2>&1 &
    SERVE_PID="$!"

    if [[ $VERBOSE -eq 1 ]]; then
        tail -n +1 -f "$SERVE_LOG_FILE" &
        TAIL_PID="$!"
    fi

    local i
    for i in {1..90}; do
        if ! kill -0 "$SERVE_PID" >/dev/null 2>&1; then
            show_log_excerpt "$SERVE_LOG_FILE"
            fail "ionic serve exited early (pid: $SERVE_PID)"
        fi
        if is_server_ready "$PORT"; then
            if [[ -n "$TAIL_PID" ]] && kill -0 "$TAIL_PID" >/dev/null 2>&1; then
                kill "$TAIL_PID" >/dev/null 2>&1 || true
                wait "$TAIL_PID" 2>/dev/null || true
                TAIL_PID=""
            fi
            log "Ionic live server is ready at http://127.0.0.1:$PORT"
            return 0
        fi
        sleep 1
    done

    show_log_excerpt "$SERVE_LOG_FILE"
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
    set +e
    run_android_command "gradlew-install-debug" "./gradlew installDebug --warning-mode all"
    local status=$?
    set -e

    if [[ $status -ne 0 ]]; then
        if rg -q "INSTALL_FAILED_UPDATE_INCOMPATIBLE|INSTALL_FAILED_VERSION_DOWNGRADE" "$LAST_LOG_FILE"; then
            return 2
        fi
        show_log_excerpt "$LAST_LOG_FILE"
        return "$status"
    fi

    return 0
}

attempt_gradle_install_with_recovery() {
    local install_status
    local did_recover_resources=0
    local did_repair_native_audio=0

    while true; do
        set +e
        run_gradle_install
        install_status=$?
        set -e

        if [[ $install_status -eq 0 ]]; then
            return 0
        fi

        if [[ $install_status -eq 2 ]]; then
            log "Detected incompatible installed package; uninstalling and retrying installDebug"
            "$ADB_BIN" -s "$ACTIVE_SERIAL" uninstall "$PACKAGE_NAME" >/dev/null 2>&1 || true
            run_android_command "gradlew-install-debug-retry" "./gradlew installDebug --warning-mode all" || {
                show_log_excerpt "$LAST_LOG_FILE"
                fail "installDebug retry failed"
            }
            return 0
        fi

        if [[ $did_recover_resources -eq 0 ]] && rg -q "resource string/applink_host|resource string/applink_host_alternate|resource string/branch_key|resource string/branch_test_key|resource bool/branch_test_mode|resource drawable/ic_tracking|resource string/default_notification_channel_id|resource string/default_notification_channel_name" "$LAST_LOG_FILE"; then
            did_recover_resources=1
            recover_android_generated_resources
            continue
        fi

        if [[ $did_repair_native_audio -eq 0 ]] && rg -q "requestAudioFocusIfNeeded\\(\\) is already defined|abandonAudioFocusIfNeeded\\(\\) is already defined" "$LAST_LOG_FILE"; then
            did_repair_native_audio=1
            repair_native_audio_patch_if_needed
            continue
        fi

        return "$install_status"
    done
}

launch_app() {
    if [[ $SKIP_LAUNCH -eq 1 ]]; then
        log "Launch skipped (--skip-launch)"
        return 0
    fi

    local adb_cmd=("$ADB_BIN" -s "$ACTIVE_SERIAL")
    local logfile status

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

        logfile="$(make_log_file "launch-activity")"
        LAST_LOG_FILE="$logfile"
        set +e
        "${adb_cmd[@]}" shell am start -W -n "$component" >"$logfile" 2>&1
        status=$?
        set -e
        if [[ $status -ne 0 ]]; then
            show_log_excerpt "$logfile"
            return "$status"
        fi
        log "Launched component: $component"
        return 0
    fi

    logfile="$(make_log_file "launch-monkey")"
    LAST_LOG_FILE="$logfile"
    set +e
    "${adb_cmd[@]}" shell monkey -p "$PACKAGE_NAME" -c android.intent.category.LAUNCHER 1 >"$logfile" 2>&1
    status=$?
    set -e

    if [[ $status -ne 0 ]]; then
        show_log_excerpt "$logfile"
        log "monkey launch returned $status"
        return "$status"
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

    warn "could not open chrome://inspect/#devices automatically"
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

init_log_dir

if [[ ! -f "$PROJECT_DIR/package.json" ]]; then
    fail "package.json not found in $PROJECT_DIR"
fi
if [[ ! -f "$PROJECT_DIR/capacitor.config.ts" && ! -f "$PROJECT_DIR/capacitor.config.json" ]]; then
    fail "capacitor.config.ts/json not found in $PROJECT_DIR"
fi

"$ADB_BIN" start-server >/dev/null 2>&1 || true

resolve_prepare_mode

if [[ "$PREPARE_MODE" == "skip" ]]; then
    log "Project prepare skipped ($PREPARE_LOG_LABEL)"
    ensure_android_platform
    sync_android_platform
    if ! android_generated_resources_ready; then
        recover_android_generated_resources
    fi
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

set +e
attempt_gradle_install_with_recovery
gradle_status=$?
set -e

if [[ $gradle_status -ne 0 ]]; then
    exit "$gradle_status"
fi

launch_app
open_inspect_tab

log "Project: $PROJECT_DIR"
log "Package: $PACKAGE_NAME"
log "Target serial: $ACTIVE_SERIAL"
log "Live URL: http://localhost:$PORT"
log "Inspect URL: chrome://inspect/#devices"
log "Session active. Press Ctrl+C to stop"

set +e
wait "$SERVE_PID"
serve_status=$?
set -e

if [[ $serve_status -ne 0 ]]; then
    show_log_excerpt "$SERVE_LOG_FILE"
    fail "ionic serve exited with status $serve_status"
fi
