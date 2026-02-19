#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
REPORT_FILE="${2:-./dirty-repos.txt}"

if [[ ! -d "$ROOT" ]]; then
  echo "Invalid path: $ROOT" >&2
  exit 2
fi

# Find directories that contain a .git directory OR a .git file (worktrees/submodules).
mapfile -t REPOS < <(
  find "$ROOT" \
    -type d \( -name node_modules -o -name dist -o -name build -o -name out -o -name .next -o -name .cache -o -name .venv -o -name venv \) -prune -o \
    \( -type d -name .git -print -o -type f -name .git -print \) \
  | sed 's|/\.git$||' \
  | sort -u
)

{
  echo "Git dirty repo scan report"
  echo "Root: $(cd "$ROOT" && pwd)"
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Repos detected: ${#REPOS[@]}"
  echo
} > "$REPORT_FILE"

if [[ ${#REPOS[@]} -eq 0 ]]; then
  echo "No Git repositories found under: $ROOT" | tee -a "$REPORT_FILE"
  exit 0
fi

DIRTY_COUNT=0

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
    } >> "$REPORT_FILE"
  fi
done

if [[ $DIRTY_COUNT -eq 0 ]]; then
  echo "All clean. Checked ${#REPOS[@]} repo(s). Report: $REPORT_FILE"
  echo "All repositories are clean." >> "$REPORT_FILE"
  exit 0
fi

echo "Found $DIRTY_COUNT dirty repo(s). Report: $REPORT_FILE"
exit 1

