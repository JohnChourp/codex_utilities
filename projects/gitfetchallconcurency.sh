#!/usr/bin/env bash
set -euo pipefail

# Default concurrency (override via env: CONCURRENCY=20 ./fetch_repos_parallel.sh ...)
CONCURRENCY="${CONCURRENCY:-10}"

# Scan one level deep by default (override via env: MAX_DEPTH=3 ...)
MAX_DEPTH="${MAX_DEPTH:-1}"

# Usage:
#   ./fetch_repos_parallel.sh /path/to/folder/with/repos
#   ./fetch_repos_parallel.sh /path/to/folder1 /path/to/folder2
ROOTS=("$@")
if [[ "${#ROOTS[@]}" -eq 0 ]]; then
  ROOTS=(".")
fi

fetch_repo() {
  local repo_dir="$1"
  local repo_name
  repo_name="$(basename "$repo_dir")"

  # Skip if not a git repo
  if ! git -C "$repo_dir" rev-parse --is-inside-work-tree &>/dev/null; then
    return 0
  fi

  echo "→ ${repo_name} (fetching...)"

  # Fetch all remotes, prune deleted branches; keep output quiet-ish
  if git -C "$repo_dir" fetch --all --prune --quiet; then
    echo "✓ ${repo_name} (done)"
  else
    echo "✗ ${repo_name} (FAILED)" >&2
    return 1
  fi
}

export -f fetch_repo

for root in "${ROOTS[@]}"; do
  if [[ ! -d "$root" ]]; then
    echo "Directory not found: $root" >&2
    continue
  fi

  echo "Processing root: $root (max depth: $MAX_DEPTH, concurrency: $CONCURRENCY)"

  # Find directories up to MAX_DEPTH and fetch in parallel
  find "$root" -mindepth 1 -maxdepth "$MAX_DEPTH" -type d -print0 \
    | xargs -0 -n 1 -P "$CONCURRENCY" -I {} bash -c 'fetch_repo "$1"' _ {}
done

echo "All done!"

