#!/bin/bash

USERNAME="JohnChourp"

set -euo pipefail

# ---------- config -------------
USERNAME="JohnChourp"
GITHUB_TOKEN="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"

# All the top-level lambda folders you want to process (add/remove freely)
ROOTS=(
  "/home/dm-soft-1/Downloads/lambdas/codeliver_all"
  "/home/dm-soft-1/Downloads/lambdas/crp_all"
)
# Or: ROOTS=("$@")   # pass them as CLI args instead
# --------------------------------

process_repo () {
  local repo_dir="$1"
  local repo_name
  repo_name="$(basename "$repo_dir")"

  echo "  → $repo_name"

  # Skip if it’s not a git repo
  if ! git -C "$repo_dir" rev-parse --is-inside-work-tree &>/dev/null; then
    echo "    (not a git repo, skipping)"
    return
  fi

  # Build the new URL (no token printed to screen)
  local new_url="https://$USERNAME:${GITHUB_TOKEN}@github.com/dmngr/${repo_name}.git"

  # Only update if different (idempotent)
  local current_url
  current_url="$(git -C "$repo_dir" remote get-url origin 2>/dev/null || echo '')"

  if [[ "$current_url" == "$new_url" ]]; then
    echo "    already set, skipping"
  else
    git -C "$repo_dir" remote set-url origin "$new_url"
    echo "    remote updated"
  fi
}

for root in "${ROOTS[@]}"; do
  if [[ ! -d "$root" ]]; then
    echo "Directory not found: $root"
    continue
  fi
  echo "Processing root: $root"
  # one level deep dirs
  while IFS= read -r -d '' dir; do
    process_repo "$dir"
  done < <(find "$root" -mindepth 1 -maxdepth 1 -type d -print0)
done

echo "All done!"
read -r -p "Done. Press Enter to close..." _

