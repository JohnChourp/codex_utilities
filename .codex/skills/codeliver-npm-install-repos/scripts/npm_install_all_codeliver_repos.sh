#!/usr/bin/env bash
set -uo pipefail

ROOT="/Users/john/Downloads/lambdas/codeliver_all"
DRY_RUN=0

usage() {
  cat <<'USAGE'
Usage:
  npm_install_all_codeliver_repos.sh [--root <path>] [--dry-run]

Options:
  --root <path>   Root folder with local repos (default: /Users/john/Downloads/lambdas/codeliver_all)
  --dry-run       Print planned npm installs without executing
  -h, --help      Show help
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

if [[ $DRY_RUN -eq 0 ]] && ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm is not available in PATH." >&2
  exit 2
fi

total=0
installed=0
failed=0
skipped=0

while IFS= read -r repo_dir; do
  [[ -d "$repo_dir" ]] || continue

  if [[ ! -f "$repo_dir/package.json" ]]; then
    skipped=$((skipped + 1))
    continue
  fi

  total=$((total + 1))
  repo_name="$(basename "$repo_dir")"
  echo "[$repo_name] npm i"

  if [[ $DRY_RUN -eq 1 ]]; then
    installed=$((installed + 1))
    continue
  fi

  if (cd "$repo_dir" && npm i); then
    installed=$((installed + 1))
  else
    failed=$((failed + 1))
    echo "[$repo_name] FAILED" >&2
  fi
done < <(find "$ROOT" -mindepth 1 -maxdepth 1 -type d | sort)

echo
echo "Summary:"
echo "  root: $ROOT"
echo "  repos_with_package_json: $total"
echo "  installed: $installed"
echo "  failed: $failed"
echo "  skipped_no_package_json: $skipped"

if [[ $failed -gt 0 ]]; then
  exit 1
fi

exit 0
