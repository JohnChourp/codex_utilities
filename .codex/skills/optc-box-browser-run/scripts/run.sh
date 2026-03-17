#!/usr/bin/env bash

set -euo pipefail

REPO_DIR="${REPO_DIR:-${HOME}/Downloads/projects/optc-box-exporter}"

if [ ! -d "$REPO_DIR" ]; then
    echo "Repo not found: $REPO_DIR" >&2
    exit 1
fi

cd "$REPO_DIR"
exec ./tools/run-browser.sh
