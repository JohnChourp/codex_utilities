#!/usr/bin/env bash

set -euo pipefail

DRY_RUN=0
ARGS=()

for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then
    DRY_RUN=1
  else
    ARGS+=("$arg")
  fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_SOURCE_REPO="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SOURCE_REPO="${ARGS[0]:-${DEFAULT_SOURCE_REPO}}"
TARGET_CODEX_DIR="${ARGS[1]:-${HOME}/.codex}"

SOURCE_AGENTS="${SOURCE_REPO}/AGENTS.md"
SOURCE_SKILLS_DIR="${SOURCE_REPO}/skills"
TARGET_AGENTS="${TARGET_CODEX_DIR}/AGENTS.md"
TARGET_SKILLS_DIR="${TARGET_CODEX_DIR}/skills"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
BACKUP_PATH="${TARGET_AGENTS}.bak-${TIMESTAMP}"
WORK_DIR="$(mktemp -d)"
MERGED_AGENTS="${WORK_DIR}/AGENTS.merged.md"

cleanup() {
  rm -rf "${WORK_DIR}"
}

trap cleanup EXIT

require_path() {
  local path="$1"
  local label="$2"

  if [[ ! -e "${path}" ]]; then
    echo "Missing ${label}: ${path}" >&2
    exit 1
  fi
}

require_path "${SOURCE_AGENTS}" "source AGENTS.md"
require_path "${SOURCE_SKILLS_DIR}" "source skills directory"
require_path "${TARGET_AGENTS}" "target global AGENTS.md"

mkdir -p "${TARGET_SKILLS_DIR}"

python3 - <<'PY' "${TARGET_AGENTS}" "${SOURCE_AGENTS}" "${MERGED_AGENTS}"
import pathlib
import re
import sys

target_path = pathlib.Path(sys.argv[1])
source_path = pathlib.Path(sys.argv[2])
merged_path = pathlib.Path(sys.argv[3])

target_text = target_path.read_text()
source_text = source_path.read_text()
pattern = re.compile(r"^# Codex Workflow Guide \(.+$", re.MULTILINE)
match = pattern.search(target_text)

if not match:
    raise SystemExit(f"Workflow boundary heading not found in {target_path}")

merged_text = target_text[:match.start()].rstrip() + "\n\n" + source_text.rstrip() + "\n"
merged_path.write_text(merged_text)
PY

echo "Source repo: ${SOURCE_REPO}"
echo "Target .codex: ${TARGET_CODEX_DIR}"
echo "Workflow overlay source: ${SOURCE_AGENTS}"
echo "Workflow overlay target: ${TARGET_AGENTS}"

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "Dry run enabled."
  echo "Would create backup: ${BACKUP_PATH}"
  echo "Would update workflow overlay in: ${TARGET_AGENTS}"
  echo "Would sync skills:"
  find "${SOURCE_SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type d | sort
  exit 0
fi

cp "${TARGET_AGENTS}" "${BACKUP_PATH}"
cp "${MERGED_AGENTS}" "${TARGET_AGENTS}"

SYNCED_SKILLS=()

while IFS= read -r skill_dir; do
  skill_name="$(basename "${skill_dir}")"
  target_skill_dir="${TARGET_SKILLS_DIR}/${skill_name}"
  rm -rf "${target_skill_dir}"
  cp -R "${skill_dir}" "${target_skill_dir}"
  SYNCED_SKILLS+=("${skill_name}")
done < <(find "${SOURCE_SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type d | sort)

echo "Backup created: ${BACKUP_PATH}"
echo "Skills synced (${#SYNCED_SKILLS[@]}):"
for skill_name in "${SYNCED_SKILLS[@]}"; do
  echo " - ${skill_name}"
done
