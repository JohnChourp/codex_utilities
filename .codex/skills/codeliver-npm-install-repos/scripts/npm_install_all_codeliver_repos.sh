#!/usr/bin/env bash
set -uo pipefail

ROOT="${HOME}/Downloads/lambdas/codeliver_all"
DRY_RUN=0
CONCURRENCY="${CONCURRENCY:-20}"
temp_files=()

cleanup_temp_artifacts() {
  local f
  for f in "${temp_files[@]:-}"; do
    [[ -n "$f" ]] && rm -f "$f" 2>/dev/null || true
  done
}

trap 'cleanup_temp_artifacts' EXIT

usage() {
  cat <<'USAGE'
Usage:
  npm_install_all_codeliver_repos.sh [--root <path>] [--dry-run]

Options:
  --root <path>   Root folder with local repos (default: ~/Downloads/lambdas/codeliver_all)
  --dry-run       Print planned npm installs without executing
  -h, --help      Show help

Environment:
  CONCURRENCY     Parallel npm install workers (default: 20)
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --root requires a value." >&2
        exit 2
      fi
      ROOT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$ROOT" ]]; then
  echo "ERROR: Root path not found: $ROOT" >&2
  exit 2
fi

if [[ ! "$CONCURRENCY" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: CONCURRENCY must be a positive integer." >&2
  exit 2
fi

if [[ $DRY_RUN -eq 0 ]] && ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm is not available in PATH." >&2
  exit 2
fi

append_line_locked() {
  local target_file="$1"
  local lock_file="$2"
  local line="$3"

  if command -v flock >/dev/null 2>&1; then
    (
      flock -x 200
      printf "%s\n" "$line" >> "$target_file"
    ) 200>"$lock_file"
    return
  fi

  local lock_dir="${lock_file}.d"
  while ! mkdir "$lock_dir" 2>/dev/null; do
    sleep 0.01
  done

  printf "%s\n" "$line" >> "$target_file"
  rmdir "$lock_dir" || true
}

record_result() {
  local repo_name="$1"
  local status="$2"
  local line
  printf -v line "%s\t%s" "$repo_name" "$status"
  append_line_locked "$RESULTS_FILE" "$RESULTS_LOCK_FILE" "$line"
}

install_repo() {
  local repo_dir="$1"
  local repo_name

  repo_name="$(basename "$repo_dir")"
  echo "[$repo_name] npm i"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    record_result "$repo_name" "INSTALLED"
    return 0
  fi

  if (cd "$repo_dir" && npm i); then
    record_result "$repo_name" "INSTALLED"
    return 0
  fi

  record_result "$repo_name" "FAILED"
  echo "[$repo_name] FAILED" >&2
  return 1
}

RESULTS_FILE="$(mktemp)"
RESULTS_LOCK_FILE="${RESULTS_FILE}.lock"
temp_files+=("$RESULTS_FILE" "$RESULTS_LOCK_FILE")

export -f append_line_locked
export -f record_result
export -f install_repo
export RESULTS_FILE RESULTS_LOCK_FILE DRY_RUN

ALL_REPO_DIRS=()
while IFS= read -r repo_dir; do
  ALL_REPO_DIRS+=("$repo_dir")
done < <(find "$ROOT" -mindepth 1 -maxdepth 1 -type d | sort)

TARGET_REPOS=()
skipped=0

for repo_dir in "${ALL_REPO_DIRS[@]}"; do
  [[ -d "$repo_dir" ]] || continue

  if [[ ! -f "$repo_dir/package.json" ]]; then
    skipped=$((skipped + 1))
    continue
  fi

  TARGET_REPOS+=("$repo_dir")
done

total="${#TARGET_REPOS[@]}"
installed=0
failed=0
overall_exit=0

if [[ "$total" -gt 0 ]]; then
  if ! printf "%s\0" "${TARGET_REPOS[@]}" | xargs -0 -P "$CONCURRENCY" -I {} bash -c 'set -euo pipefail; install_repo "$1"' _ {}; then
    overall_exit=1
  fi

  installed="$(awk -F '\t' '$2=="INSTALLED" {c++} END {print c+0}' "$RESULTS_FILE")"
  failed="$(awk -F '\t' '$2=="FAILED" {c++} END {print c+0}' "$RESULTS_FILE")"
fi

echo
echo "Summary:"
echo "  root: $ROOT"
echo "  concurrency: $CONCURRENCY"
echo "  repos_with_package_json: $total"
echo "  installed: $installed"
echo "  failed: $failed"
echo "  skipped_no_package_json: $skipped"

if [[ $failed -gt 0 ]]; then
  exit 1
fi

exit "$overall_exit"
