#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  post_setup_checks.sh [options]

Options:
  --project <path>     Optional project root to inspect after scaffold (default: current directory)
  --require-android    Fail if Android deployment tools are missing
  --require-ios        Fail if iOS simulator tools are missing
  -h, --help           Show help
USAGE
}

log() {
    printf '[ionic-angular-mobile-app-builder] %s\n' "$*"
}

warn() {
    printf '[ionic-angular-mobile-app-builder][warn] %s\n' "$*" >&2
}

fail() {
    printf '[ionic-angular-mobile-app-builder][error] %s\n' "$*" >&2
    exit 1
}

PROJECT_DIR="$PWD"
REQUIRE_ANDROID=0
REQUIRE_IOS=0

while (($# > 0)); do
    case "$1" in
        --project)
            PROJECT_DIR="${2:-}"
            shift 2
            ;;
        --require-android)
            REQUIRE_ANDROID=1
            shift
            ;;
        --require-ios)
            REQUIRE_IOS=1
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

PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd -P)"

check_core_tool() {
    local tool="$1"
    local hint="$2"
    if ! command -v "$tool" >/dev/null 2>&1; then
        fail "$tool is required. $hint"
    fi
    log "Found $tool: $(command -v "$tool")"
}

check_optional_tool() {
    local tool="$1"
    local hint="$2"
    local required="$3"

    if command -v "$tool" >/dev/null 2>&1; then
        log "Found $tool: $(command -v "$tool")"
        return 0
    fi

    if [[ "$required" == "1" ]]; then
        fail "$tool is required. $hint"
    fi

    warn "$tool not found. $hint"
}

check_core_tool node "Install a current Node.js LTS release and ensure node is in PATH."
check_core_tool npm "Install npm together with Node.js."
check_core_tool npx "Ensure npm is installed correctly so npx is available."
check_core_tool python3 "Install Python 3 for the skill helper scripts."

check_optional_tool java "Install a JDK for Android builds." "$REQUIRE_ANDROID"
check_optional_tool adb "Install Android platform-tools and add adb to PATH." "$REQUIRE_ANDROID"
check_optional_tool emulator "Install Android emulator tools from Android Studio." "$REQUIRE_ANDROID"

if command -v xcrun >/dev/null 2>&1 && xcrun simctl help >/dev/null 2>&1; then
    log "Found working Xcode simulator tools."
else
    if [[ $REQUIRE_IOS -eq 1 ]]; then
        fail "xcrun/simctl is required for iOS simulator flows. Install Xcode and Command Line Tools."
    fi
    warn "Xcode simulator tools are unavailable. iOS platform creation or simulator deploy may be skipped."
fi

if [[ -f "$PROJECT_DIR/package.json" ]]; then
    log "Detected package.json in $PROJECT_DIR"
fi

if [[ -f "$PROJECT_DIR/capacitor.config.ts" || -f "$PROJECT_DIR/capacitor.config.json" ]]; then
    log "Detected Capacitor config in $PROJECT_DIR"
fi

log "Environment checks completed."
