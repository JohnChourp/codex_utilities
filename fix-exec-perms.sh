#!/usr/bin/env bash
# fix-exec-perms.sh
# Scans a target folder (and all subfolders) and makes executable:
#   - all *.sh files
#   - any file that has a shebang (#!...) on the first line
#
# Usage:
#   ./fix-exec-perms.sh                 # scans current folder
#   ./fix-exec-perms.sh /path/to/folder # scans that folder

set -euo pipefail

TARGET="${1:-.}"

if [[ ! -d "$TARGET" ]]; then
  echo "Error: '$TARGET' is not a folder"
  exit 1
fi

echo "Scanning: $TARGET"

# Find candidate files:
# - regular files
# - not in .git
# - either name ends with .sh OR first two bytes are "#!"
# Note: macOS 'find' doesn't support -printf; keep it POSIX-ish.
files=()
while IFS= read -r file; do
  files+=("$file")
done < <(
  find "$TARGET" -type d -name .git -prune -o \
    -type f \( -name "*.sh" -o -exec sh -c 'head -c 2 "$1" 2>/dev/null | grep -q "^#!"' _ {} \; \) \
    -print
)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "No matching scripts found."
  exit 0
fi

changed=0
skipped=0

for f in "${files[@]}"; do
  # Fix Windows CRLF endings if present (prevents /bin/bash^M issues)
  if LC_ALL=C grep -q $'\r' "$f" 2>/dev/null; then
    sed -i '' $'s/\r$//' "$f"
  fi

  # Add execute bit
  if chmod +x "$f" 2>/dev/null; then
    ((changed++))
  else
    echo "Could not chmod (permission?): $f"
    ((skipped++))
    continue
  fi

  # Remove macOS quarantine attribute if present (best-effort)
  if xattr -p com.apple.quarantine "$f" >/dev/null 2>&1; then
    xattr -d com.apple.quarantine "$f" >/dev/null 2>&1 || true
  fi
done

echo "Done."
echo "Executable set on: $changed file(s)"
echo "Skipped: $skipped file(s)"
