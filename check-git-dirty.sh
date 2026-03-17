#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_FILE_DEFAULT="$SCRIPT_DIR/dirty-repos.txt"
REPORT_FILE="$REPORT_FILE_DEFAULT"
QUIET_TERMINAL="${CHECK_GIT_DIRTY_QUIET_TERMINAL:-1}"
AUTO_CLOSE_TERMINAL="${CHECK_GIT_DIRTY_AUTO_CLOSE_TERMINAL:-1}"

if [[ "$QUIET_TERMINAL" == "1" ]]; then
  exec >/dev/null 2>&1
fi

close_terminal_window_if_requested() {
  if [[ "$AUTO_CLOSE_TERMINAL" != "1" ]]; then
    return
  fi
  if [[ "${TERM_PROGRAM:-}" != "Apple_Terminal" ]]; then
    return
  fi

  (sleep 0.2
   osascript -e 'tell application "Terminal" to if (count windows) > 0 then close front window' >/dev/null 2>&1 || true
  ) &
}

finish_and_exit() {
  local code="$1"
  close_terminal_window_if_requested
  exit "$code"
}

resolve_downloads_root() {
  local dir="$SCRIPT_DIR"
  while [[ "$dir" != "/" ]]; do
    if [[ "$(basename "$dir")" == "Downloads" ]]; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

DOWNLOADS_ROOT="$(resolve_downloads_root || true)"
if [[ -z "$DOWNLOADS_ROOT" ]]; then
  finish_and_exit 2
fi

TARGET_ROOTS_DEFAULT=(
  "$DOWNLOADS_ROOT/projects"
  "$DOWNLOADS_ROOT/projects/codeliver"
  "$DOWNLOADS_ROOT/lambdas/codeliver_all"
  "$DOWNLOADS_ROOT/lambdas/crp_all"
)
TARGET_ROOTS=("${TARGET_ROOTS_DEFAULT[@]}")

# Backward-compatible args:
# - check-git-dirty.sh                       -> scan default roots, default report
# - check-git-dirty.sh /path/report.txt      -> scan default roots, custom report
# - check-git-dirty.sh /path/root            -> scan only that root, default report
# - check-git-dirty.sh /path/root report.txt -> scan only that root, custom report
if [[ $# -ge 1 ]]; then
  if [[ -d "${1:-}" ]]; then
    TARGET_ROOTS=("${1}")
    if [[ $# -ge 2 ]]; then
      REPORT_FILE="${2}"
    fi
  else
    REPORT_FILE="${1}"
  fi
fi

if [[ "$REPORT_FILE" != /* ]]; then
  REPORT_FILE="$PWD/$REPORT_FILE"
fi
mkdir -p "$(dirname "$REPORT_FILE")"
# Always recreate the report from scratch for each run.
rm -f "$REPORT_FILE"

REPOS=()
SCAN_ROOTS=()
NON_REPO_DIRS=()

for root in "${TARGET_ROOTS[@]}"; do
  if [[ -d "$root" ]]; then
    SCAN_ROOTS+=("$(cd "$root" && pwd)")
  fi
done

if [[ ${#SCAN_ROOTS[@]} -eq 0 ]]; then
  finish_and_exit 2
fi

while IFS= read -r candidate_dir; do
  [[ -n "$candidate_dir" ]] || continue

  if git -C "$candidate_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    continue
  fi

  NON_REPO_DIRS+=("$candidate_dir")
done < <(
  for root in "${SCAN_ROOTS[@]}"; do
    find "$root" \
      -mindepth 1 -maxdepth 1 \
      -type d \
      ! -name node_modules \
      ! -name dist \
      ! -name build \
      ! -name out \
      ! -name .next \
      ! -name .cache \
      ! -name .venv \
      ! -name venv \
      2>/dev/null
  done | sort -u
)

while IFS= read -r repo; do
  REPOS+=("$repo")
done < <(
  for root in "${SCAN_ROOTS[@]}"; do
    find "$root" \
      -type d \( -name node_modules -o -name dist -o -name build -o -name out -o -name .next -o -name .cache -o -name .venv -o -name venv \) -prune -o \
      \( -type d -name .git -print -o -type f -name .git -print \) \
      2>/dev/null \
      | sed 's|/\.git$||'
  done | sort -u
)

if [[ ${#REPOS[@]} -eq 0 ]]; then
  {
    echo "Git dirty repo scan report"
    echo "Downloads root: $DOWNLOADS_ROOT"
    echo "Scan roots:"
    for root in "${SCAN_ROOTS[@]}"; do
      echo "- $root"
    done
    echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "Repos detected: 0"
    echo "Dirty repos detected: 0"
    echo "Non-repo folders detected: ${#NON_REPO_DIRS[@]}"
    echo
    echo "No Git repositories found under scan roots."
    if [[ ${#NON_REPO_DIRS[@]} -gt 0 ]]; then
      echo
      echo "Non-repo folders:"
      for dir in "${NON_REPO_DIRS[@]}"; do
        echo "- $dir"
      done
    fi
  } > "$REPORT_FILE"
  finish_and_exit 0
fi

DIRTY_COUNT=0
DIRTY_DETAILS_FILE="$(mktemp)"
trap 'rm -f "$DIRTY_DETAILS_FILE"' EXIT

for repo in "${REPOS[@]}"; do
  if ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    continue
  fi

  STATUS="$(git -C "$repo" status --porcelain || true)"
  if [[ -n "$STATUS" ]]; then
    DIRTY_COUNT=$((DIRTY_COUNT + 1))
    {
      echo "- $repo"
      echo "$STATUS" | sed 's/^/  /'
      echo
    } >> "$DIRTY_DETAILS_FILE"
  fi
done

{
  echo "Git dirty repo scan report"
  echo "Downloads root: $DOWNLOADS_ROOT"
  echo "Scan roots:"
  for root in "${SCAN_ROOTS[@]}"; do
    echo "- $root"
  done
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Repos detected: ${#REPOS[@]}"
  echo "Dirty repos detected: $DIRTY_COUNT"
  echo "Non-repo folders detected: ${#NON_REPO_DIRS[@]}"
  echo
} > "$REPORT_FILE"

if [[ ${#NON_REPO_DIRS[@]} -gt 0 ]]; then
  {
    echo "Non-repo folders:"
    for dir in "${NON_REPO_DIRS[@]}"; do
      echo "- $dir"
    done
    echo
  } >> "$REPORT_FILE"
fi

if [[ $DIRTY_COUNT -eq 0 ]]; then
  echo "All repositories are clean." >> "$REPORT_FILE"
  finish_and_exit 0
fi

cat "$DIRTY_DETAILS_FILE" >> "$REPORT_FILE"
echo "Dirty repos total: $DIRTY_COUNT" >> "$REPORT_FILE"
finish_and_exit 1
