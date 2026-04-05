#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  run_release.sh [--project <path>] [--bump patch|minor|major] [--version X.Y.Z] [--code N] [--no-push] [--skip-gh-release]
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd -P)"
PROJECT_PATH=""
ARGS=()
SKIP_GH_RELEASE=0

canonical_path() {
    local target="$1"
    (cd "${target}" && pwd -P)
}

looks_like_repo_root() {
    local candidate="$1"
    [[ -f "${candidate}/package.json" ]] || return 1
    local package_name
    package_name="$(cd "${candidate}" && node -p "require('./package.json').name" 2>/dev/null || true)"
    [[ "${package_name}" == "optc-team-builder" ]]
}

resolve_default_project_path() {
    local git_root=""

    if looks_like_repo_root "$(pwd -P)"; then
        pwd -P
        return
    fi

    git_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "${git_root}" ]] && looks_like_repo_root "${git_root}"; then
        canonical_path "${git_root}"
        return
    fi

    if [[ -d "${HOME}/Downloads/projects/optc-team-builder" ]] && looks_like_repo_root "${HOME}/Downloads/projects/optc-team-builder"; then
        canonical_path "${HOME}/Downloads/projects/optc-team-builder"
        return
    fi

    echo "ERROR: Could not locate the optc-team-builder project. Pass --project <path>." >&2
    exit 1
}

pick_release_bash() {
    local candidate
    local candidates=(
        "${HOME}/.homebrew/bin/bash"
        "/opt/homebrew/bin/bash"
        "/usr/local/bin/bash"
        "$(command -v bash || true)"
    )

    for candidate in "${candidates[@]}"; do
        if [[ -n "${candidate}" && -x "${candidate}" ]]; then
            echo "${candidate}"
            return
        fi
    done

    echo "ERROR: bash was not found in PATH." >&2
    exit 1
}

ensure_release_signing_env() {
    local env_file="${HOME}/.android/optc-team-builder/release-signing.env"
    local setup_script="${PROJECT_PATH}/scripts/setup-release-signing.sh"
    local required_vars=(
        ANDROID_SIGNING_STORE_FILE
        ANDROID_SIGNING_STORE_PASSWORD
        ANDROID_SIGNING_KEY_ALIAS
        ANDROID_SIGNING_KEY_PASSWORD
    )
    local missing=0
    local var_name

    if [[ -f "${env_file}" ]]; then
        # shellcheck disable=SC1090
        source "${env_file}"
    fi

    for var_name in "${required_vars[@]}"; do
        if [[ -z "${!var_name:-}" ]]; then
            missing=1
        fi
    done

    if (( missing == 1 )); then
        if [[ -x "${setup_script}" ]]; then
            "${setup_script}"
        fi

        if [[ -f "${env_file}" ]]; then
            # shellcheck disable=SC1090
            source "${env_file}"
        fi
    fi

    missing=0
    for var_name in "${required_vars[@]}"; do
        if [[ -z "${!var_name:-}" ]]; then
            echo "ERROR: Missing required env var ${var_name}." >&2
            missing=1
        fi
    done

    if (( missing == 1 )); then
        cat >&2 <<EOF
Set up local Android signing first:
  ${PROJECT_PATH}/scripts/setup-release-signing.sh
  source "${env_file}"
EOF
        exit 1
    fi

    if [[ ! -f "${ANDROID_SIGNING_STORE_FILE}" ]]; then
        echo "ERROR: ANDROID_SIGNING_STORE_FILE does not exist: ${ANDROID_SIGNING_STORE_FILE}" >&2
        exit 1
    fi
}

ensure_gh_or_fallback_skip() {
    if (( SKIP_GH_RELEASE == 1 )); then
        return
    fi

    if ! command -v gh >/dev/null 2>&1; then
        echo "[release-skill] gh CLI not found. Falling back to --skip-gh-release." >&2
        ARGS+=("--skip-gh-release")
        return
    fi

    if ! gh auth status >/dev/null 2>&1; then
        echo "[release-skill] gh auth is unavailable. Falling back to --skip-gh-release." >&2
        ARGS+=("--skip-gh-release")
    fi
}

while (($# > 0)); do
    case "$1" in
        --project)
            PROJECT_PATH="${2:-}"
            shift 2
            ;;
        --bump|--version|--code)
            ARGS+=("$1" "${2:-}")
            shift 2
            ;;
        --no-push)
            ARGS+=("$1")
            shift
            ;;
        --skip-gh-release)
            ARGS+=("$1")
            SKIP_GH_RELEASE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if [[ -z "${PROJECT_PATH}" ]]; then
    PROJECT_PATH="$(resolve_default_project_path)"
else
    PROJECT_PATH="$(canonical_path "${PROJECT_PATH}")"
fi

if [[ ! -x "${PROJECT_PATH}/scripts/release-and-tag.sh" ]]; then
    echo "ERROR: Could not find release script at ${PROJECT_PATH}/scripts/release-and-tag.sh" >&2
    exit 1
fi

ensure_release_signing_env
ensure_gh_or_fallback_skip

cd "${PROJECT_PATH}"
RELEASE_BASH="$(pick_release_bash)"
"${RELEASE_BASH}" "${PROJECT_PATH}/scripts/release-and-tag.sh" "${ARGS[@]}"
