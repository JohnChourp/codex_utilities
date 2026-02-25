#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  ios_simulator_open.sh [options]

Options:
  --device-name <name>   Simulator name (default: Codex iPhone 17 Pro Max)
  --device-type <id>     Device type identifier (default: com.apple.CoreSimulator.SimDeviceType.iPhone-17-Pro-Max)
  --runtime <id>         Runtime identifier (default: newest available iOS runtime)
  --open                 Open Simulator app on selected UDID (default behavior)
  -h, --help             Show help
EOF
}

log() {
    printf '[ios-simulator-open] %s\n' "$*"
}

DEVICE_NAME="Codex iPhone 17 Pro Max"
DEVICE_TYPE="com.apple.CoreSimulator.SimDeviceType.iPhone-17-Pro-Max"
RUNTIME_ID=""
OPEN_SIMULATOR=1

while (($# > 0)); do
    case "$1" in
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
        --open)
            OPEN_SIMULATOR=1
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

if ! command -v xcrun >/dev/null 2>&1; then
    echo "xcrun not found. Install Xcode Command Line Tools first." >&2
    exit 1
fi

if ! xcrun simctl help >/dev/null 2>&1; then
    echo "simctl is not available. Make sure Xcode is installed correctly." >&2
    exit 1
fi

mapfile -t AVAILABLE_IOS_RUNTIMES < <(
    xcrun simctl list runtimes available | awk '/^iOS / && /com\.apple\.CoreSimulator\.SimRuntime\.iOS-/ { print $NF }'
)

if [[ ${#AVAILABLE_IOS_RUNTIMES[@]} -eq 0 ]]; then
    cat >&2 <<'EOF'
No available iOS Simulator runtime was found.

Install one from Xcode, then rerun:
1) Open Xcode
2) Go to Xcode > Settings... > Components
3) Download an iOS Simulator runtime (for example iOS 26)
4) Re-run this script
EOF
    exit 1
fi

if [[ -n "$RUNTIME_ID" ]]; then
    if ! printf '%s\n' "${AVAILABLE_IOS_RUNTIMES[@]}" | grep -Fxq "$RUNTIME_ID"; then
        echo "Requested runtime is not available: $RUNTIME_ID" >&2
        echo "Available iOS runtimes:" >&2
        printf '  - %s\n' "${AVAILABLE_IOS_RUNTIMES[@]}" >&2
        exit 1
    fi
else
    RUNTIME_ID="$(
        printf '%s\n' "${AVAILABLE_IOS_RUNTIMES[@]}" \
            | awk '{v=$0; sub(/^.*iOS-/, "", v); gsub(/-/, ".", v); print v "|" $0}' \
            | sort -t'|' -k1,1V \
            | tail -n1 \
            | cut -d'|' -f2
    )"
fi

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

UDID="$(find_existing_udid "$DEVICE_NAME" "$RUNTIME_ID" "$DEVICE_TYPE" || true)"

if [[ -z "$UDID" ]]; then
    log "Creating simulator: name='$DEVICE_NAME', type='$DEVICE_TYPE', runtime='$RUNTIME_ID'"
    UDID="$(xcrun simctl create "$DEVICE_NAME" "$DEVICE_TYPE" "$RUNTIME_ID")"
    log "Created simulator UDID: $UDID"
else
    log "Reusing existing simulator UDID: $UDID"
fi

BOOT_LOG="$(mktemp)"
if ! xcrun simctl boot "$UDID" >"$BOOT_LOG" 2>&1; then
    if grep -Eiq "already booted|current state: Booted|Unable to boot device in current state: Booted" "$BOOT_LOG"; then
        log "Simulator already booted: $UDID"
    else
        cat "$BOOT_LOG" >&2
        rm -f "$BOOT_LOG"
        exit 1
    fi
fi
rm -f "$BOOT_LOG"

xcrun simctl bootstatus "$UDID" -b

if [[ $OPEN_SIMULATOR -eq 1 ]]; then
    open -a Simulator --args -CurrentDeviceUDID "$UDID"
fi

STATUS_LINE="$(xcrun simctl list devices | grep -m1 "$UDID" || true)"
if [[ -z "$STATUS_LINE" || "$STATUS_LINE" != *"(Booted)"* ]]; then
    echo "Simulator is not in Booted state: $UDID" >&2
    exit 1
fi

log "Runtime: $RUNTIME_ID"
log "Device Type: $DEVICE_TYPE"
log "Device Name: $DEVICE_NAME"
log "Device Status: $STATUS_LINE"
log "Done. Simulator is left running."
