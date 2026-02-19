#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  run_release.sh [--project <path>] [--bump patch|minor|major] [--version X.Y.Z] [--code N] [--no-push] [--skip-gh-release]
USAGE
}

PROJECT_PATH="/home/john/Downloads/projects/LearnByzantineMusic"
ARGS=()

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
        --no-push|--skip-gh-release)
            ARGS+=("$1")
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

PROJECT_PATH="$(realpath "$PROJECT_PATH")"
if [[ ! -x "$PROJECT_PATH/scripts/release-and-tag.sh" ]]; then
    echo "ERROR: Δεν βρέθηκε το release script στο $PROJECT_PATH/scripts/release-and-tag.sh" >&2
    exit 1
fi

cd "$PROJECT_PATH"
./scripts/release-and-tag.sh "${ARGS[@]}"
