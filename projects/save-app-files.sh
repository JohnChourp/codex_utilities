#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="${1:-"$script_dir/src/app"}"
prettier_bin="${FORMATTER_BIN:-"$script_dir/node_modules/.bin/prettier"}"
require_formatter="${REQUIRE_FORMATTER:-0}"

if [[ ! -d "$root" ]]; then
  echo "Root directory not found: $root" >&2
  exit 1
fi

formatter=()
if [[ -x "$prettier_bin" ]]; then
  formatter=("$prettier_bin")
elif command -v prettier >/dev/null 2>&1; then
  formatter=(prettier)
fi

if [[ ${#formatter[@]} -eq 0 ]]; then
  if [[ "$require_formatter" == "1" ]]; then
    echo "Formatter not found. Install prettier or set FORMATTER_BIN, or unset REQUIRE_FORMATTER." >&2
    exit 1
  fi
  echo "Warning: Prettier not found. Files will be rewritten without formatting." >&2
fi

find "$root" -path "$root/.git" -prune -o -type f -print0 | while IFS= read -r -d '' f; do
  printf '%s\n' "$f"
  case "$f" in
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.html|*.css|*.scss|*.sass|*.less|*.json|*.md|*.yml|*.yaml)
      if [[ ${#formatter[@]} -gt 0 ]]; then
        "${formatter[@]}" --write --loglevel warn "$f"
      fi
      ;;
  esac
  python3 - "$f" <<'PY'
import sys

path = sys.argv[1]
with open(path, "rb") as fh:
    data = fh.read()
with open(path, "wb") as fh:
    fh.write(data)
PY
done
