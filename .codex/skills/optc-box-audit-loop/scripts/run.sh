#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-${HOME}/Downloads/projects/optc-box-exporter}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ $# -gt 2 ]]; then
  echo "Usage: $0 [case-folder] [image-size]" >&2
  echo "Required layout:" >&2
  echo "  <case-folder>/input/<one-screenshot>" >&2
  echo "  <case-folder>/output/<one-or-more-character-images>" >&2
  echo "  <case-folder>/meta/corrected.json" >&2
  echo "Default <case-folder>: ${SKILL_DIR}" >&2
  exit 64
fi

CASE_FOLDER="${1:-${SKILL_DIR}}"
IMAGE_SIZE="${2:-64}"

if [[ ! -d "$CASE_FOLDER" ]]; then
  echo "Case folder does not exist: $CASE_FOLDER" >&2
  exit 66
fi

if [[ ! -d "$CASE_FOLDER/input" ]]; then
  echo "Missing required directory: $CASE_FOLDER/input" >&2
  exit 66
fi

if [[ ! -d "$CASE_FOLDER/output" ]]; then
  echo "Missing required directory: $CASE_FOLDER/output" >&2
  exit 66
fi

if [[ ! -d "$CASE_FOLDER/meta" ]]; then
  echo "Missing required directory: $CASE_FOLDER/meta" >&2
  exit 66
fi

if [[ ! -f "$CASE_FOLDER/meta/corrected.json" ]]; then
  echo "Missing required file: $CASE_FOLDER/meta/corrected.json" >&2
  exit 66
fi

PYTHON_BIN=""
for candidate in \
  "$REPO_DIR/.venv/bin/python" \
  "$REPO_DIR/.venv39/bin/python" \
  "$(command -v python3)"; do
  if [[ -x "$candidate" ]] && "$candidate" - <<'PY' >/dev/null 2>&1
import cv2
from PIL import Image
PY
  then
    PYTHON_BIN="$candidate"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "No compatible Python environment found for OPTCbx audit-case." >&2
  exit 69
fi

cd "$REPO_DIR"
"$PYTHON_BIN" -m optcbx audit-case "$CASE_FOLDER" --image-size "$IMAGE_SIZE" --write-artifacts
