#!/usr/bin/env bash

set -euo pipefail

ROOT="/home/dm-soft-1/Downloads/lambdas"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  ./fix-github-auth-lambdas.sh [--root <path>] [--dry-run]

What it does:
  1) Normalizes all GitHub remotes in <path> repos to:
     https://github.com/<owner>/<repo>.git
  2) Removes embedded credentials from remote URLs.
  3) Configures git to use GitHub CLI credential helper:
     gh auth setup-git
     gh config set git_protocol https

Examples:
  ./fix-github-auth-lambdas.sh
  ./fix-github-auth-lambdas.sh --root /home/dm-soft-1/Downloads/lambdas --dry-run
EOF
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
}

normalize_github_url() {
  local url="$1"
  local path=""

  if [[ "$url" =~ ^git@github\.com:(.+)$ ]]; then
    path="${BASH_REMATCH[1]}"
    printf 'https://github.com/%s\n' "$path"
    return 0
  fi

  if [[ "$url" =~ ^ssh://git@github\.com/(.+)$ ]]; then
    path="${BASH_REMATCH[1]}"
    printf 'https://github.com/%s\n' "$path"
    return 0
  fi

  if [[ "$url" =~ ^https://[^/]*github\.com/(.+)$ ]]; then
    path="${BASH_REMATCH[1]}"
    printf 'https://github.com/%s\n' "$path"
    return 0
  fi

  printf '%s\n' "$url"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -ge 2 ]] || { echo "Missing value for --root" >&2; exit 1; }
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
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

require_cmd git
require_cmd gh
require_cmd find

if [[ ! -d "$ROOT" ]]; then
  echo "Root path does not exist: $ROOT" >&2
  exit 1
fi

if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run: gh auth login -h github.com" >&2
  exit 1
fi

repo_count=0
repos_changed=0
remotes_changed=0

while IFS= read -r git_dir; do
  repo="${git_dir%/.git}"
  repo_count=$((repo_count + 1))
  repo_changed=0

  while IFS= read -r remote; do
    [[ -n "$remote" ]] || continue
    current_url="$(git -C "$repo" remote get-url "$remote" 2>/dev/null || true)"
    [[ -n "$current_url" ]] || continue

    new_url="$(normalize_github_url "$current_url")"
    if [[ "$new_url" != "$current_url" ]]; then
      if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] $repo :: $remote will be normalized to HTTPS GitHub URL"
      else
        git -C "$repo" remote set-url "$remote" "$new_url"
      fi
      remotes_changed=$((remotes_changed + 1))
      repo_changed=1
    fi
  done < <(git -C "$repo" remote 2>/dev/null || true)

  if [[ "$repo_changed" -eq 1 ]]; then
    repos_changed=$((repos_changed + 1))
  fi
done < <(find "$ROOT" -type d -name .git)

if [[ "$DRY_RUN" -eq 0 ]]; then
  gh auth setup-git >/dev/null
  gh config set git_protocol https >/dev/null
fi

tokenized_left=0
while IFS= read -r git_dir; do
  repo="${git_dir%/.git}"
  while IFS= read -r remote; do
    [[ -n "$remote" ]] || continue
    url="$(git -C "$repo" remote get-url "$remote" 2>/dev/null || true)"
    if [[ "$url" =~ ^https://[^/]+@github\.com/ ]]; then
      tokenized_left=$((tokenized_left + 1))
    fi
  done < <(git -C "$repo" remote 2>/dev/null || true)
done < <(find "$ROOT" -type d -name .git)

echo "Scan root: $ROOT"
echo "Git repos scanned: $repo_count"
echo "Repos changed: $repos_changed"
echo "Remotes changed: $remotes_changed"
echo "Tokenized HTTPS remotes left: $tokenized_left"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry-run mode: no changes were applied."
fi
