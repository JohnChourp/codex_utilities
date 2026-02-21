#!/usr/bin/env bash

## This script was auto-generated to clone the selected repositories.
## Keep it secret – it contains your GitHub token.
## Place this script in the folder where you want the repos to live and run it there.

# Default concurrency (override via env: CONCURRENCY=20 ./clone_selected_repos.sh)
CONCURRENCY="${CONCURRENCY:-10}"

githubHost="github.com"
GITHUB_TOKEN="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"

if [ -z "$GITHUB_TOKEN" ]; then
  echo "⛔ GITHUB_TOKEN is empty. Edit this script and set it to a valid GitHub token."
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
cd "$script_dir" || exit 1

echo "⚙️ Using concurrency: ${CONCURRENCY}"

repos=(
  "codeliver-sap"
  "codeliver-app"
  "codeliver-panel"
  "codeliver-pos"
)

clone_repo() {
  local fullName="$1"
  local repoDir="${fullName##*/}"

  if [ -d "$repoDir/.git" ]; then
    echo "✅ Skipping ${fullName}: already cloned in ${repoDir}"
    return 0
  fi
  if [ -d "$repoDir" ]; then
    echo "⚠️ Skipping ${fullName}: directory ${repoDir} exists but is not a git repo."
    return 0
  fi

  echo "🌀 Cloning ${fullName} ..."
  if git clone "https://${GITHUB_TOKEN}@${githubHost}/dmngr/${fullName}.git"; then
    echo "✅ Done ${fullName}"
  else
    echo "⛔ Failed ${fullName}" >&2
    return 1
  fi
}

export -f clone_repo
export githubHost
export GITHUB_TOKEN

printf "%s\0" "${repos[@]}" | xargs -0 -n 1 -P "$CONCURRENCY" -I {} bash -c 'clone_repo "$1"' _ {}

echo "All done!"