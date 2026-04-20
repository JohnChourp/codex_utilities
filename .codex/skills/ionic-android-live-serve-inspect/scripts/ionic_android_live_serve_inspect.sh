#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  ionic_android_live_serve_inspect.sh [options]

Options:
  --project <path|name>  Ionic project root, workspace root, or fuzzy project name
  --port <number>        Ionic serve port (default: 8206)
  --serial <id>          USB ADB serial for target Android device
  --device-api <sdk>     Android API level override for adb reverse gating
  --package <id>         Override package/applicationId detection
  --activity <name>      Activity to launch (e.g. .MainActivity)
  --open-inspect         Open chrome://inspect/#devices automatically
  --full-prepare         Force heavy prepare flow (npm install/icons/build-after); configure still runs
  --skip-prepare         Skip heavy prepare flow (npm install/icons/build-after); configure still runs
  --skip-inspect-open    Do not open chrome://inspect/#devices
  --skip-launch          Install only, do not launch app
  --verbose              Stream detailed command output
  -h, --help             Show help
USAGE
}

log() {
    local line="[ionic-android-live-serve-inspect] $*"
    printf '%s\n' "$line"
    report_write_line "$line"
}

warn() {
    local line="[ionic-android-live-serve-inspect] Warning: $*"
    printf '%s\n' "$line" >&2
    report_write_line "$line"
}

fail() {
    local line="$*"
    echo "$line" >&2
    report_write_line "[ionic-android-live-serve-inspect] ERROR: $line"
    exit 1
}

REPORT_DIR=""
REPORT_FILE=""
REPORT_LATEST_DIR=""
REPORT_LATEST_FILE=""
REPORT_TARGETS=()
REPORT_INITIALIZED=0
RUN_EXIT_STATUS=0
SESSION_STARTED_AT_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
LAUNCH_METHOD="not-attempted"
LAUNCH_COMPONENT=""
ANDROID_SDK_ROOT_RESOLVED=""

report_bootstrap_target() {
    local target="$1"
    local invoked_cwd="${IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOKED_CWD:-${CODEX_SKILL_INVOKED_CWD:-$PWD}}"
    local invocation_basename="${IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOCATION_BASENAME:-${CODEX_SKILL_INVOKED_BASENAME:-$(basename "$invoked_cwd")}}"

    [[ -n "$target" ]] || return 0
    [[ -s "$target" ]] && return 0

    {
        printf '%s\n' '# ionic-android-live-serve-inspect report'
        printf '\n'
        printf '%s\n' "- Started (UTC): $SESSION_STARTED_AT_UTC"
        printf '%s\n' "- Invoked cwd: $invoked_cwd"
        printf '%s\n' "- Invocation basename: $invocation_basename"
        printf '%s\n' "- Command: ${IONIC_ANDROID_LIVE_SERVE_INSPECT_COMMAND:-unknown}"
        printf '%s\n' "- Report dir: ${REPORT_DIR:-unknown}"
        printf '%s\n' "- Latest report: ${REPORT_LATEST_FILE:-unknown}"
        printf '\n'
        printf '%s\n' '## Live logs'
        printf '%s\n' "[ionic-android-live-serve-inspect] Report file: $target"
    } >> "$target"
}

report_write_line() {
    local line="$*"
    local target

    [[ ${#REPORT_TARGETS[@]} -gt 0 ]] || return 0

    for target in "${REPORT_TARGETS[@]}"; do
        [[ -n "$target" ]] || continue
        printf '%s\n' "$line" >> "$target"
    done
}

report_write_blank_line() {
    local target

    [[ ${#REPORT_TARGETS[@]} -gt 0 ]] || return 0

    for target in "${REPORT_TARGETS[@]}"; do
        [[ -n "$target" ]] || continue
        printf '\n' >> "$target"
    done
}

report_append_file() {
    local title="$1"
    local file="$2"
    local line=""

    [[ -n "$REPORT_FILE" ]] || return 0
    [[ -f "$file" ]] || return 0

    report_write_blank_line
    report_write_line "### $title"
    report_write_line '```text'
    while IFS= read -r line || [[ -n "${line:-}" ]]; do
        report_write_line "$line"
    done < "$file"
    report_write_line '```'
}

report_finalize() {
    local status="$1"

    [[ ${#REPORT_TARGETS[@]} -gt 0 ]] || return 0

    report_write_blank_line
    report_write_line "## Final summary"
    report_write_line "- Exit status: $status"
    report_write_line "- Session started (UTC): $SESSION_STARTED_AT_UTC"
    report_write_line "- Project root: ${PROJECT_DIR:-unknown}"
    report_write_line "- Package: ${PACKAGE_NAME:-unknown}"
    report_write_line "- Serial: ${ACTIVE_SERIAL:-unknown}"
    report_write_line "- Device API: ${DEVICE_API:-unknown}"
    report_write_line "- Android SDK root: ${ANDROID_SDK_ROOT_RESOLVED:-unknown}"
    report_write_line "- Port: $PORT"
    report_write_line "- Prepare mode: $PREPARE_MODE"
    report_write_line "- Launch method: $LAUNCH_METHOD"
    report_write_line "- Launch component: ${LAUNCH_COMPONENT:-unknown}"
    report_write_line "- adb reverse: $([[ $ADB_REVERSE_SET -eq 1 ]] && echo applied || echo not-applied)"
    report_write_line "- Report file: $REPORT_FILE"
    report_write_line "- Latest report file: ${REPORT_LATEST_FILE:-unknown}"
    report_write_line "- Command log dir: $REPORT_DIR"
}

PATH="${PATH:-/usr/bin:/bin}"

append_path_dir() {
    local dir="$1"
    [[ -n "$dir" && -d "$dir" ]] || return 0

    case ":$PATH:" in
        *":$dir:"*) ;;
        *) PATH="$dir:$PATH" ;;
    esac
}

bootstrap_path() {
    local script_dir
    local code_home_default
    local code_home
    local dir
    local vscode_dirs=("$HOME"/.vscode/extensions/openai.chatgpt-*/bin/*)

    script_dir="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    code_home_default="$(cd -- "$script_dir/../../.." && pwd)"
    code_home="${CODEX_HOME:-$code_home_default}"

    for dir in \
        "$HOME/.local/bin" \
        "$HOME/bin" \
        "$HOME/.n/bin" \
        "/usr/local/bin" \
        "/opt/homebrew/bin"; do
        append_path_dir "$dir"
    done

    if [[ -n "${ANDROID_HOME:-}" ]]; then
        append_path_dir "${ANDROID_HOME}/platform-tools"
        append_path_dir "${ANDROID_HOME}/emulator"
    fi
    if [[ -n "${ANDROID_SDK_ROOT:-}" ]]; then
        append_path_dir "${ANDROID_SDK_ROOT}/platform-tools"
        append_path_dir "${ANDROID_SDK_ROOT}/emulator"
    fi

    if [[ -e "${vscode_dirs[0]:-}" ]]; then
        for dir in "${vscode_dirs[@]}"; do
            append_path_dir "$dir"
        done
    fi

    append_path_dir "$code_home/bin"

    export PATH
    hash -r 2>/dev/null || true
}

SEARCH_TOOL=""

detect_search_tool() {
    if command -v rg >/dev/null 2>&1; then
        SEARCH_TOOL="rg"
        return 0
    fi
    if command -v grep >/dev/null 2>&1; then
        SEARCH_TOOL="grep"
        return 0
    fi
    return 1
}

search_quiet() {
    local pattern="$1"
    shift

    if [[ "$SEARCH_TOOL" == "rg" ]]; then
        rg -q -- "$pattern" "$@"
        return $?
    fi

    grep -E -q -- "$pattern" "$@"
}

search_first_line() {
    local pattern="$1"
    shift

    if [[ "$SEARCH_TOOL" == "rg" ]]; then
        rg -n -m 1 -- "$pattern" "$@"
        return $?
    fi

    grep -E -n -m 1 -- "$pattern" "$@"
}

canonicalize_dir() {
    local dir="$1"
    (
        cd "$dir" >/dev/null 2>&1 && pwd -P
    )
}

is_project_root() {
    local dir="$1"
    [[ -f "$dir/package.json" ]] || return 1
    [[ -f "$dir/capacitor.config.ts" || -f "$dir/capacitor.config.json" ]] || return 1
    return 0
}

find_project_root_from_path() {
    local dir="$1"
    local current

    current="$(canonicalize_dir "$dir" 2>/dev/null)" || return 1

    while [[ -n "$current" ]]; do
        if is_project_root "$current"; then
            printf '%s\n' "$current"
            return 0
        fi

        [[ "$current" == "/" ]] && return 1
        current="$(dirname "$current")"
    done

    return 1
}

to_lowercase() {
    printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

project_hint_matches() {
    local candidate="$1"
    local hint="$2"
    local candidate_lc
    local hint_lc
    local base_lc

    candidate_lc="$(to_lowercase "$candidate")"
    hint_lc="$(to_lowercase "$hint")"
    base_lc="$(to_lowercase "$(basename "$candidate")")"

    [[ "$base_lc" == "$hint_lc" ]] && return 0

    case "$candidate_lc" in
        *"/$hint_lc"|*"/$hint_lc/"*|*"$hint_lc"*) return 0 ;;
    esac

    return 1
}

is_same_or_descendant() {
    local ancestor="$1"
    local candidate="$2"

    [[ -n "$ancestor" && -n "$candidate" ]] || return 1

    case "$candidate" in
        "$ancestor"|"$ancestor"/*) return 0 ;;
    esac

    return 1
}

sort_project_candidates() {
    local invocation_cwd="${IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOKED_CWD:-${CODEX_SKILL_INVOKED_CWD:-}}"
    local invocation_name="${IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOCATION_BASENAME:-${CODEX_SKILL_INVOKED_BASENAME:-}}"
    local sorted=()
    local candidate

    if [[ ${#PROJECT_CANDIDATES[@]} -le 1 ]]; then
        return 0
    fi

    while IFS= read -r candidate; do
        [[ -n "$candidate" ]] && sorted+=("$candidate")
    done < <(node - "$invocation_cwd" "$invocation_name" "${PROJECT_CANDIDATES[@]}" <<'NODE'
const path = require('path');

const invocationCwd = process.argv[2] || '';
const invocationName = (process.argv[3] || '').toLowerCase();
const candidates = process.argv.slice(4).filter(Boolean);

function normalize(value) {
  try {
    return path.resolve(value).replace(/\\/g, '/');
  } catch (error) {
    return String(value || '');
  }
}

function score(candidate) {
  const normalized = normalize(candidate);
  const base = path.basename(normalized).toLowerCase();
  let value = 0;

  if (invocationCwd) {
    const cwd = normalize(invocationCwd);
    if (normalized === cwd) {
      value += 10000;
    } else if (cwd === normalized || cwd.startsWith(`${normalized}/`)) {
      value += 9500;
    }
  }

  if (invocationName) {
    if (base === invocationName) {
      value += 8000;
    }
    if (normalized.endsWith(`/${invocationName}`)) {
      value += 7500;
    }
    if (normalized.includes(`/${invocationName}/`)) {
      value += 200;
    }
  }

  value -= normalized.split('/').length / 1000;
  return value;
}

const ranked = candidates
  .map(candidate => ({ candidate, score: score(candidate) }))
  .sort((left, right) => {
    if (right.score !== left.score) {
      return right.score - left.score;
    }
    return left.candidate.localeCompare(right.candidate);
  })
  .map(entry => entry.candidate);

process.stdout.write(ranked.join('\n'));
NODE
    )

    PROJECT_CANDIDATES=("${sorted[@]}")
}

PROJECT_SEARCH_ROOTS=()
PROJECT_CANDIDATES=()

add_project_search_root() {
    local root="$1"
    local canonical
    local existing

    [[ -n "$root" && -d "$root" ]] || return 0
    canonical="$(canonicalize_dir "$root" 2>/dev/null)" || return 0

    for existing in "${PROJECT_SEARCH_ROOTS[@]}"; do
        [[ "$existing" == "$canonical" ]] && return 0
    done

    PROJECT_SEARCH_ROOTS+=("$canonical")
}

build_project_search_roots() {
    local invocation_cwd="${IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOKED_CWD:-${CODEX_SKILL_INVOKED_CWD:-}}"
    local extra_roots="${IONIC_PROJECT_SEARCH_ROOTS:-}"
    local root
    local old_ifs="$IFS"
    local extra_root_list=()

    PROJECT_SEARCH_ROOTS=()

    add_project_search_root "$invocation_cwd"
    add_project_search_root "$PWD"
    add_project_search_root "$HOME"
    add_project_search_root "$HOME/Downloads"
    add_project_search_root "$HOME/Downloads/projects"
    add_project_search_root "$HOME/Downloads/lambdas"
    add_project_search_root "$HOME/Documents"
    add_project_search_root "$HOME/Desktop"
    add_project_search_root "$HOME/Projects"
    add_project_search_root "$HOME/projects"
    add_project_search_root "$HOME/dev"
    add_project_search_root "$HOME/src"
    add_project_search_root "$HOME/work"
    add_project_search_root "$HOME/repos"
    add_project_search_root "$HOME/Workspace"
    add_project_search_root "$HOME/Code"
    add_project_search_root "$HOME/Development"
    add_project_search_root "$HOME/AndroidStudioProjects"

    if [[ -n "$extra_roots" ]]; then
        IFS=':' read -r -a extra_root_list <<< "$extra_roots"
        for root in "${extra_root_list[@]}"; do
            add_project_search_root "$root"
        done
    fi

    IFS="$old_ifs"
}

discover_project_candidates() {
    local max_depth="${IONIC_PROJECT_DISCOVERY_DEPTH:-5}"
    local candidate

    PROJECT_CANDIDATES=()

    while IFS= read -r candidate; do
        [[ -n "$candidate" ]] && PROJECT_CANDIDATES+=("$candidate")
    done < <(node - "$max_depth" "${PROJECT_SEARCH_ROOTS[@]}" <<'NODE'
const fs = require('fs');
const path = require('path');

const maxDepth = Number(process.argv[2] || 5);
const roots = process.argv.slice(3).filter(Boolean);
const ignore = new Set([
  'node_modules',
  'android',
  'ios',
  'dist',
  'build',
  'www',
  'coverage',
  '.git',
  '.angular',
  '.ionic',
  '.nx',
  '.turbo',
  '.next',
  '.cache',
  '.config',
  '.local',
  '.gradle'
]);
const results = [];
const seen = new Set();

function existsFile(dir, name) {
  try {
    return fs.statSync(path.join(dir, name)).isFile();
  } catch (error) {
    return false;
  }
}

function isProjectRoot(dir) {
  return existsFile(dir, 'package.json')
    && (existsFile(dir, 'capacitor.config.ts') || existsFile(dir, 'capacitor.config.json'));
}

function canonicalize(dir) {
  try {
    return fs.realpathSync(dir);
  } catch (error) {
    return path.resolve(dir);
  }
}

function walk(dir, depth) {
  if (depth > maxDepth) {
    return;
  }

  let stat;
  try {
    stat = fs.statSync(dir);
  } catch (error) {
    return;
  }

  if (!stat.isDirectory()) {
    return;
  }

  const canonical = canonicalize(dir);
  if (seen.has(canonical)) {
    return;
  }

  if (isProjectRoot(dir)) {
    seen.add(canonical);
    results.push(canonical);
  }

  if (depth === maxDepth) {
    return;
  }

  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch (error) {
    return;
  }

  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }

    if (ignore.has(entry.name) || entry.name.startsWith('.')) {
      continue;
    }

    walk(path.join(dir, entry.name), depth + 1);
  }
}

for (const root of roots) {
  if (!root) {
    continue;
  }

  walk(path.resolve(root), 0);
}

process.stdout.write(results.join('\n'));
NODE
    )
}

filter_project_candidates_by_hint() {
    local hint="$1"
    local filtered=()
    local candidate

    for candidate in "${PROJECT_CANDIDATES[@]}"; do
        if project_hint_matches "$candidate" "$hint"; then
            filtered+=("$candidate")
        fi
    done

    PROJECT_CANDIDATES=("${filtered[@]}")
}

resolve_project_choice() {
    local choice="$1"
    local candidate
    local resolved
    local filtered=()

    case "$choice" in
        q|quit|exit)
            fail "Project selection cancelled"
            ;;
    esac

    if [[ "$choice" =~ ^[0-9]+$ ]]; then
        if ((choice >= 1 && choice <= ${#PROJECT_CANDIDATES[@]})); then
            printf '%s\n' "${PROJECT_CANDIDATES[$((choice - 1))]}"
            return 0
        fi
        return 1
    fi

    if [[ -d "$choice" ]]; then
        if resolved="$(find_project_root_from_path "$choice" 2>/dev/null)"; then
            printf '%s\n' "$resolved"
            return 0
        fi
    fi

    for candidate in "${PROJECT_CANDIDATES[@]}"; do
        if project_hint_matches "$candidate" "$choice"; then
            filtered+=("$candidate")
        fi
    done

    if [[ ${#filtered[@]} -eq 1 ]]; then
        printf '%s\n' "${filtered[0]}"
        return 0
    fi

    if [[ ${#filtered[@]} -gt 1 ]]; then
        PROJECT_CANDIDATES=("${filtered[@]}")
        return 2
    fi

    return 1
}

prompt_for_project_selection() {
    local choice=""
    local resolved=""
    local i

    if [[ ! -t 0 ]]; then
        return 1
    fi

    while true; do
        printf '\nSelect Ionic project:\n' >&2
        for i in "${!PROJECT_CANDIDATES[@]}"; do
            printf '  %d) %s\n' "$((i + 1))" "${PROJECT_CANDIDATES[$i]}" >&2
        done
        printf 'Enter number or path [1]: ' >&2
        IFS= read -r choice || return 1
        [[ -z "$choice" ]] && choice=1

        resolved="$(resolve_project_choice "$choice")"
        case $? in
            0)
                printf '%s\n' "$resolved"
                return 0
                ;;
            2)
                continue
                ;;
        esac

        printf 'Invalid selection. Enter a number from the list, a full path, or q to quit.\n' >&2
    done
}

resolve_project_dir() {
    local raw="${PROJECT_DIR_RAW:-}"
    local explicit_root=""
    local invocation_cwd="${IONIC_ANDROID_LIVE_SERVE_INSPECT_INVOKED_CWD:-${CODEX_SKILL_INVOKED_CWD:-}}"
    local selected=""

    if [[ -n "$raw" ]]; then
        if [[ -d "$raw" ]]; then
            if explicit_root="$(find_project_root_from_path "$raw" 2>/dev/null)"; then
                PROJECT_DIR="$explicit_root"
                log "Using project root from --project: $PROJECT_DIR"
                return 0
            fi

            log "Searching for Ionic projects under $raw"
            PROJECT_SEARCH_ROOTS=()
            add_project_search_root "$raw"
            discover_project_candidates
        else
            log "Searching for Ionic projects matching '$raw'"
            build_project_search_roots
            discover_project_candidates

            filter_project_candidates_by_hint "$raw"
            sort_project_candidates
        fi
    else
        if [[ -n "$invocation_cwd" ]] && explicit_root="$(find_project_root_from_path "$invocation_cwd" 2>/dev/null)"; then
            PROJECT_DIR="$explicit_root"
            log "Using project root from invocation directory: $PROJECT_DIR"
            return 0
        fi
        if explicit_root="$(find_project_root_from_path "$PWD" 2>/dev/null)"; then
            PROJECT_DIR="$explicit_root"
            log "Using project root from current directory: $PROJECT_DIR"
            return 0
        fi
        build_project_search_roots
        discover_project_candidates
    fi

    sort_project_candidates

    if [[ ${#PROJECT_CANDIDATES[@]} -eq 0 ]]; then
        if [[ -n "$raw" && -d "$raw" ]]; then
            fail "No Ionic project root found under $raw"
        fi
        fail "No Ionic project root found. Pass --project <path|name> or set IONIC_PROJECT_SEARCH_ROOTS"
    fi

    if [[ ${#PROJECT_CANDIDATES[@]} -eq 1 ]]; then
        PROJECT_DIR="${PROJECT_CANDIDATES[0]}"
        log "Using project root: $PROJECT_DIR"
        return 0
    fi

    selected="$(prompt_for_project_selection)" || {
        printf 'No project selected.\n' >&2
        exit 1
    }

    PROJECT_DIR="$selected"
    log "Using project root: $PROJECT_DIR"
}

validate_device_api() {
    local value="$1"

    [[ "$value" =~ ^[0-9]+$ ]] || fail "Invalid device API '$value'. Use a numeric SDK level, e.g. --device-api 21"
    if ((value < 1 || value > 1000)); then
        fail "Device API '$value' is out of range"
    fi
}

detect_device_api() {
    local sdk

    sdk="$("$ADB_BIN" -s "$ACTIVE_SERIAL" shell getprop ro.build.version.sdk 2>/dev/null | tr -d '\r\n')"
    [[ -n "$sdk" ]] || return 1
    printf '%s\n' "$sdk"
}

resolve_device_api() {
    if [[ -n "$DEVICE_API" ]]; then
        validate_device_api "$DEVICE_API"
        log "Using supplied device API $DEVICE_API"
        return 0
    fi

    DEVICE_API="$(detect_device_api)" || {
        fail "Unable to detect device API for $ACTIVE_SERIAL. Pass --device-api <sdk>"
    }
    validate_device_api "$DEVICE_API"
    log "Detected device API $DEVICE_API"
}

PROJECT_DIR=""
PORT="8206"
PORT_EXPLICIT=0
SERIAL=""
DEVICE_API=""
DEVICE_API_EXPLICIT=0
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

bootstrap_path

while (($# > 0)); do
    case "$1" in
        --project)
            PROJECT_DIR_RAW="${2:-}"
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
        --device-api)
            DEVICE_API="${2:-}"
            DEVICE_API_EXPLICIT=1
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

if [[ ! "$PORT" =~ ^[0-9]+$ ]]; then
    fail "Invalid port '$PORT'. Use a numeric value, e.g. --port 8206"
fi
if ((PORT < 1 || PORT > 65535)); then
    fail "Port '$PORT' is out of range (1-65535)"
fi

if [[ -n "$DEVICE_API" && $DEVICE_API_EXPLICIT -eq 1 ]]; then
    validate_device_api "$DEVICE_API"
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

on_exit() {
    local status=$?

    set +e
    cleanup
    report_finalize "$status"
    set -e
}

trap on_signal INT TERM HUP
trap on_exit EXIT

init_log_dir() {
    local report_file_was_provided=0

    if [[ -n "${IONIC_ANDROID_LIVE_SERVE_INSPECT_REPORT_FILE:-}" ]]; then
        report_file_was_provided=1
        REPORT_FILE="${IONIC_ANDROID_LIVE_SERVE_INSPECT_REPORT_FILE}"
    fi

    REPORT_DIR="${IONIC_ANDROID_LIVE_SERVE_INSPECT_RUN_DIR:-}"
    REPORT_LATEST_DIR="${IONIC_ANDROID_LIVE_SERVE_INSPECT_LATEST_RUN_DIR:-}"
    REPORT_LATEST_FILE="${IONIC_ANDROID_LIVE_SERVE_INSPECT_LATEST_REPORT_FILE:-}"

    if [[ -n "$REPORT_DIR" ]]; then
        mkdir -p "$REPORT_DIR"
    elif [[ -n "$REPORT_FILE" ]]; then
        REPORT_DIR="$(dirname "$REPORT_FILE")"
    else
        REPORT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ionic-android-live-serve-inspect.XXXXXX")"
    fi

    if [[ -z "$REPORT_FILE" ]]; then
        REPORT_FILE="$REPORT_DIR/report.md"
    fi

    LOG_DIR="$REPORT_DIR"
    mkdir -p "$(dirname "$REPORT_FILE")"
    touch "$REPORT_FILE"
    if [[ -n "$REPORT_LATEST_DIR" ]]; then
        mkdir -p "$REPORT_LATEST_DIR"
        if [[ -z "$REPORT_LATEST_FILE" ]]; then
            REPORT_LATEST_FILE="$REPORT_LATEST_DIR/report.md"
        fi
    elif [[ -n "$REPORT_LATEST_FILE" ]]; then
        mkdir -p "$(dirname "$REPORT_LATEST_FILE")"
    fi
    if [[ -n "$REPORT_LATEST_FILE" ]]; then
        touch "$REPORT_LATEST_FILE"
    fi
    REPORT_TARGETS=("$REPORT_FILE")
    if [[ -n "$REPORT_LATEST_FILE" && "$REPORT_LATEST_FILE" != "$REPORT_FILE" ]]; then
        REPORT_TARGETS+=("$REPORT_LATEST_FILE")
    fi
    export IONIC_ANDROID_LIVE_SERVE_INSPECT_REPORT_FILE="$REPORT_FILE"
    if [[ -n "$REPORT_LATEST_FILE" ]]; then
        export IONIC_ANDROID_LIVE_SERVE_INSPECT_LATEST_REPORT_FILE="$REPORT_LATEST_FILE"
    fi

    for target in "${REPORT_TARGETS[@]}"; do
        report_bootstrap_target "$target"
    done

    REPORT_INITIALIZED=1

    if [[ $report_file_was_provided -eq 0 ]]; then
        log "Report file: $REPORT_FILE"
        if [[ "$REPORT_LATEST_FILE" != "$REPORT_FILE" ]]; then
            log "Latest report: $REPORT_LATEST_FILE"
        fi
    fi
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

    report_append_file "$label (exit $status)" "$logfile"

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
    local sdk_root
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
    if sdk_root="$(resolve_android_sdk_root 2>/dev/null)"; then
        candidates+=("${sdk_root}/platform-tools/adb")
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

resolve_android_sdk_root() {
    local candidate
    local sdk_dir

    if [[ -n "${ANDROID_SDK_ROOT:-}" && -d "${ANDROID_SDK_ROOT:-}" ]]; then
        printf '%s\n' "$ANDROID_SDK_ROOT"
        return 0
    fi

    if [[ -n "${ANDROID_HOME:-}" && -d "${ANDROID_HOME:-}" ]]; then
        printf '%s\n' "$ANDROID_HOME"
        return 0
    fi

    if [[ -n "${PROJECT_DIR:-}" && -f "$PROJECT_DIR/android/local.properties" ]]; then
        sdk_dir="$(sed -nE 's/^[[:space:]]*sdk\.dir[[:space:]]*=[[:space:]]*(.+)[[:space:]]*$/\1/p' "$PROJECT_DIR/android/local.properties" | head -n 1)"
        sdk_dir="${sdk_dir//\\:/:}"
        sdk_dir="${sdk_dir//\\\\/\\}"
        if [[ -n "$sdk_dir" && -d "$sdk_dir" ]]; then
            printf '%s\n' "$sdk_dir"
            return 0
        fi
    fi

    local home_dir="${HOME:-}"
    local candidates=()
    if [[ -n "$home_dir" ]]; then
        candidates+=(
            "$home_dir/Android/Sdk"
            "$home_dir/Library/Android/sdk"
            "$home_dir/.android-sdk"
            "$home_dir/Android/sdk"
        )
    fi
    candidates+=(
        "/opt/android-sdk"
        "/usr/local/share/android-sdk"
        "/usr/lib/android-sdk"
    )

    for candidate in "${candidates[@]}"; do
        [[ -d "$candidate" ]] || continue
        printf '%s\n' "$candidate"
        return 0
    done

    return 1
}

ensure_android_sdk_configuration() {
    local sdk_root
    local local_properties_file
    local tmp_file

    sdk_root="$(resolve_android_sdk_root)" || return 1
    ANDROID_SDK_ROOT_RESOLVED="$sdk_root"
    export ANDROID_HOME="$sdk_root"
    export ANDROID_SDK_ROOT="$sdk_root"
    append_path_dir "$sdk_root/platform-tools"
    append_path_dir "$sdk_root/emulator"
    export PATH

    if [[ -n "${PROJECT_DIR:-}" ]]; then
        local_properties_file="$PROJECT_DIR/android/local.properties"
        mkdir -p "$(dirname "$local_properties_file")"
        tmp_file="${local_properties_file}.tmp.$$"
        if [[ -f "$local_properties_file" ]]; then
            if grep -q '^sdk\.dir=' "$local_properties_file"; then
                sed -E "s|^sdk\\.dir=.*$|sdk.dir=$sdk_root|" "$local_properties_file" > "$tmp_file"
            else
                {
                    printf 'sdk.dir=%s\n' "$sdk_root"
                    cat "$local_properties_file"
                } > "$tmp_file"
            fi
            mv "$tmp_file" "$local_properties_file"
        else
            printf 'sdk.dir=%s\n' "$sdk_root" > "$local_properties_file"
        fi
        log "Using Android SDK at $sdk_root"
        log "Ensured Android local.properties at $local_properties_file"
    fi

    return 0
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

    local status=0

    log "Running npm run configure (resilient mode)"
    if run_project_command "npm-run-configure" "npm run configure"; then
        status=0
    else
        status=$?
    fi

    if [[ $status -eq 0 ]]; then
        return 0
    fi

    if search_quiet "spawn pod ENOENT|Updating iOS native dependencies with pod install - failed|AccessDenied|ListObjectsV2 operation: Access Denied" "$LAST_LOG_FILE"; then
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
    search_quiet "$resource_ref" "$manifest_file"
}

android_generated_resources_ready() {
    local strings_file="$PROJECT_DIR/android/app/src/main/res/values/strings.xml"
    local icon_file="$PROJECT_DIR/android/app/src/main/res/drawable/ic_tracking.png"

    if manifest_references_resource '@string/applink_host|@string/applink_host_alternate|@string/branch_key|@string/branch_test_key|@bool/branch_test_mode'; then
        [[ -f "$strings_file" ]] || return 1
        search_quiet '<string name="branch_key">[^<]+' "$strings_file" || return 1
        search_quiet '<string name="applink_host">[^<]+' "$strings_file" || return 1
        search_quiet '<string name="applink_host_alternate">[^<]+' "$strings_file" || return 1
        search_quiet '<string name="branch_test_key">[^<]+' "$strings_file" || return 1
        search_quiet '<bool name="branch_test_mode">[^<]+' "$strings_file" || return 1
    fi

    if manifest_references_resource '@string/default_notification_channel_id|@string/default_notification_channel_name'; then
        [[ -f "$strings_file" ]] || return 1
        search_quiet '<string name="default_notification_channel_id">[^<]+' "$strings_file" || return 1
        search_quiet '<string name="default_notification_channel_name">[^<]+' "$strings_file" || return 1
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
    if ! search_quiet '"capacitor-branch-deep-links"' "$PROJECT_DIR/package.json"; then
        return 0
    fi

    local strings_file="$PROJECT_DIR/android/app/src/main/res/values/strings.xml"
    if [[ ! -f "$strings_file" ]]; then
        return 0
    fi

    if search_quiet '<string name="branch_key">[^<]+' "$strings_file" \
        && search_quiet '<string name="applink_host">[^<]+' "$strings_file" \
        && search_quiet '<string name="applink_host_alternate">[^<]+' "$strings_file"; then
        return 0
    fi

    log "Branch plugin detected but Android Branch strings are missing. Attempting auto-fix."
    run_build_after_if_present
    sync_android_platform

    if ! search_quiet '<string name="branch_key">[^<]+' "$strings_file"; then
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

    for f in "$PROJECT_DIR/android/app/build.gradle.kts" "$PROJECT_DIR/android/app/build.gradle"; do
        if [[ -f "$f" ]]; then
            line="$(search_first_line '^[[:space:]]*applicationId([[:space:]]*=)?[[:space:]]*"[^"]+"' "$f" | cut -d: -f2- || true)"
            if [[ -n "$line" ]]; then
                echo "$line" | sed -E 's/.*"([^"]+)".*/\1/'
                return 0
            fi
        fi
    done

    if [[ -f "$PROJECT_DIR/android/app/src/main/AndroidManifest.xml" ]]; then
        line="$(search_first_line 'package=' "$PROJECT_DIR/android/app/src/main/AndroidManifest.xml" | cut -d: -f2- || true)"
        if [[ -n "$line" ]]; then
            echo "$line" | sed -E 's/.*package="([^"]+)".*/\1/'
            return 0
        fi
    fi

    for f in "$PROJECT_DIR/capacitor.config.ts" "$PROJECT_DIR/capacitor.config.json"; do
        if [[ -f "$f" ]]; then
            line="$(search_first_line "appId[[:space:]]*[:=][[:space:]]*['\"][^'\"]+['\"]" "$f" | cut -d: -f2- || true)"
            if [[ -n "$line" ]]; then
                echo "$line" | sed -E "s/.*appId[[:space:]]*[:=][[:space:]]*['\"]([^'\"]+)['\"].*/\1/"
                return 0
            fi
        fi
    done

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
    local status=0

    if run_android_command "gradlew-install-debug" "./gradlew installDebug --warning-mode all"; then
        status=0
    else
        status=$?
    fi

    if [[ $status -ne 0 ]]; then
        if search_quiet "INSTALL_FAILED_UPDATE_INCOMPATIBLE|INSTALL_FAILED_VERSION_DOWNGRADE" "$LAST_LOG_FILE"; then
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
        if run_gradle_install; then
            install_status=0
        else
            install_status=$?
        fi

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

        if [[ $did_recover_resources -eq 0 ]] && search_quiet "resource string/applink_host|resource string/applink_host_alternate|resource string/branch_key|resource string/branch_test_key|resource bool/branch_test_mode|resource drawable/ic_tracking|resource string/default_notification_channel_id|resource string/default_notification_channel_name" "$LAST_LOG_FILE"; then
            did_recover_resources=1
            recover_android_generated_resources
            continue
        fi

        if [[ $did_repair_native_audio -eq 0 ]] && search_quiet "requestAudioFocusIfNeeded\\(\\) is already defined|abandonAudioFocusIfNeeded\\(\\) is already defined" "$LAST_LOG_FILE"; then
            did_repair_native_audio=1
            repair_native_audio_patch_if_needed
            continue
        fi

        return "$install_status"
    done
}

normalize_component_name() {
    local component="$1"

    if [[ "$component" == */* ]]; then
        printf '%s\n' "$component"
        return 0
    fi

    if [[ "$component" == .* ]]; then
        printf '%s/%s\n' "$PACKAGE_NAME" "$component"
        return 0
    fi

    if [[ "$component" == "$PACKAGE_NAME"* ]]; then
        printf '%s\n' "$component"
        return 0
    fi

    if [[ "$component" == *.* ]]; then
        printf '%s/%s\n' "$PACKAGE_NAME" "$component"
        return 0
    fi

    printf '%s/.%s\n' "$PACKAGE_NAME" "$component"
}

detect_launcher_component_from_manifest() {
    local manifest_file="$PROJECT_DIR/android/app/src/main/AndroidManifest.xml"

    [[ -f "$manifest_file" ]] || return 1

    node - "$manifest_file" <<'NODE'
const fs = require('fs');
const file = process.argv[2];
const xml = fs.readFileSync(file, 'utf8');

function extractName(tag) {
  const match = tag.match(/android:name\s*=\s*"([^"]+)"/);
  return match ? match[1] : null;
}

function hasLauncherIntent(body) {
  return /android\.intent\.action\.MAIN/.test(body) && /android\.intent\.category\.LAUNCHER/.test(body);
}

const patterns = [
  /<(activity|activity-alias)\b([\s\S]*?)>([\s\S]*?)<\/\1>/g,
  /<(activity|activity-alias)\b([\s\S]*?)\/>/g,
];

for (const pattern of patterns) {
  let match;
  while ((match = pattern.exec(xml))) {
    const tag = match[0];
    const attrs = match[2] || '';
    const body = match[3] || '';
    if (!hasLauncherIntent(tag + body)) {
      continue;
    }
    const name = extractName(attrs) || extractName(tag);
    if (name) {
      process.stdout.write(`${name}\n`);
      process.exit(0);
    }
  }
}

process.exit(1);
NODE
}

detect_launcher_component_via_adb() {
    local raw_output component

    raw_output="$("$ADB_BIN" -s "$ACTIVE_SERIAL" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER "$PACKAGE_NAME" 2>/dev/null | tr -d '\r')"
    component="$(printf '%s\n' "$raw_output" | sed -nE 's/.*([[:alnum:]_.$]+\/[[:alnum:]_.$]+).*/\1/p' | head -n 1)"
    [[ -n "$component" ]] || return 1
    printf '%s\n' "$component"
}

resolve_launcher_component() {
    local component=""

    if [[ -n "$ACTIVITY_NAME" ]]; then
        normalize_component_name "$ACTIVITY_NAME"
        return 0
    fi

    if component="$(detect_launcher_component_from_manifest 2>/dev/null)"; then
        normalize_component_name "$component"
        return 0
    fi

    if component="$(detect_launcher_component_via_adb 2>/dev/null)"; then
        printf '%s\n' "$component"
        return 0
    fi

    return 1
}

launch_app() {
    if [[ $SKIP_LAUNCH -eq 1 ]]; then
        log "Launch skipped (--skip-launch)"
        LAUNCH_METHOD="skipped"
        return 0
    fi

    local adb_cmd=("$ADB_BIN" -s "$ACTIVE_SERIAL")
    local logfile status
    local component=""

    if [[ -n "$ACTIVITY_NAME" ]]; then
        component="$(normalize_component_name "$ACTIVITY_NAME")"
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
        LAUNCH_METHOD="activity"
        LAUNCH_COMPONENT="$component"
        return 0
    fi

    if component="$(resolve_launcher_component 2>/dev/null)"; then
        logfile="$(make_log_file "launch-component")"
        LAST_LOG_FILE="$logfile"
        set +e
        "${adb_cmd[@]}" shell am start -W -n "$component" >"$logfile" 2>&1
        status=$?
        set -e

        if [[ $status -eq 0 ]]; then
            log "Launched launcher component: $component"
            LAUNCH_METHOD="component"
            LAUNCH_COMPONENT="$component"
            return 0
        fi

        show_log_excerpt "$logfile"
        warn "Launcher component start failed; falling back to monkey"
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
    LAUNCH_METHOD="monkey"
    LAUNCH_COMPONENT="$PACKAGE_NAME"
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

init_log_dir

if ! command -v node >/dev/null 2>&1; then
    fail "node is required"
fi
if ! command -v npm >/dev/null 2>&1; then
    fail "npm is required"
fi
if ! detect_search_tool; then
    fail "A search tool is required (install ripgrep or ensure grep is available)"
fi
if ! ensure_adb; then
    fail "adb not found in PATH or common Android SDK locations"
fi

resolve_project_dir

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
    run_configure_if_available
    ensure_android_platform
    sync_android_platform
    if ! android_generated_resources_ready; then
        recover_android_generated_resources
    fi
else
    prepare_android_project
fi

if [[ -z "$PACKAGE_NAME" ]]; then
    if ! PACKAGE_NAME="$(detect_package_name)"; then
        fail "Could not detect package name. Pass --package <id>"
    fi
fi

select_usb_device
resolve_device_api

if ((DEVICE_API < 21)); then
    fail "Device API $DEVICE_API does not support adb reverse. Use an API 21+ USB Android device or pass --device-api 21+"
fi

start_ionic_serve
write_native_live_server_config
ensure_android_sdk_configuration || fail "Android SDK not found. Set ANDROID_HOME / ANDROID_SDK_ROOT or install the Android SDK in a standard location"
ensure_android_manifest_allows_cleartext

"$ADB_BIN" -s "$ACTIVE_SERIAL" reverse "tcp:$PORT" "tcp:$PORT"
ADB_REVERSE_SET=1
log "Applied adb reverse tcp:$PORT tcp:$PORT on device $ACTIVE_SERIAL (API $DEVICE_API)"

if attempt_gradle_install_with_recovery; then
    gradle_status=0
else
    gradle_status=$?
fi

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
