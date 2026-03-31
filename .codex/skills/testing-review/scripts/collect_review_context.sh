#!/usr/bin/env bash
set -euo pipefail

BASE_REF="master"

usage() {
  cat <<'EOF'
Usage:
  collect_review_context.sh [--base <branch>]

Options:
  --base <branch>  Base branch or ref to diff against. Default: master
  -h, --help       Show this help message.
EOF
}

fail() {
  printf '[error] %s\n' "$1" >&2
  exit 1
}

resolve_ref() {
  local ref="$1"

  if git rev-parse --verify --quiet "${ref}" >/dev/null; then
    printf '%s\n' "${ref}"
    return 0
  fi

  if git rev-parse --verify --quiet "origin/${ref}" >/dev/null; then
    printf '%s\n' "origin/${ref}"
    return 0
  fi

  fail "Could not resolve base ref: ${ref}"
}

while (($# > 0)); do
  case "$1" in
    --base)
      shift
      [[ $# -gt 0 ]] || fail "--base requires a ref."
      BASE_REF="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "Current directory is not a git repository."

REPO_ROOT=$(git rev-parse --show-toplevel)
CURRENT_BRANCH=$(git branch --show-current || true)
[[ -n "${CURRENT_BRANCH}" ]] || CURRENT_BRANCH="DETACHED_HEAD"
RESOLVED_BASE=$(resolve_ref "${BASE_REF}")
MERGE_BASE=$(git merge-base HEAD "${RESOLVED_BASE}")

printf 'Repo: %s\n' "${REPO_ROOT}"
printf 'Current branch: %s\n' "${CURRENT_BRANCH}"
printf 'Base ref: %s\n' "${RESOLVED_BASE}"
printf 'Merge base: %s\n' "${MERGE_BASE}"
printf '\nDiff stat:\n'
git diff --stat "${MERGE_BASE}...HEAD"
printf '\nChanged files:\n'
git diff --name-only "${MERGE_BASE}...HEAD"
