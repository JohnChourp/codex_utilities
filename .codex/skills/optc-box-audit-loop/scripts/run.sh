#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-${HOME}/Downloads/projects/optc-box-exporter}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <case-folder> [image-size]" >&2
  exit 64
fi

CASE_FOLDER="$1"
IMAGE_SIZE="${2:-64}"

if [[ ! -d "$CASE_FOLDER" ]]; then
  echo "Case folder does not exist: $CASE_FOLDER" >&2
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
