#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL_DIR=$(cd "${SCRIPT_DIR}/.." && pwd)
REPO_FROM_SKILL=$(cd "${SKILL_DIR}/../../.." && pwd)
RUNTIME_VALIDATOR="${SKILL_DIR}/../.system/skill-runtime-lib/scripts/validate_skills.py"
DEFAULT_REPO_URL="https://github.com/Al3xSy/codexDevAgent.git"
DEFAULT_CACHE_SOURCE="${HOME}/.codex/repos/codexDevAgent"
DEFAULT_TARGET="${HOME}/.codex"
AGENTS_BOUNDARY_TEXT='# Codex Workflow Guide ('
MANAGED_SKILLS_STATE_FILE=".codexDevAgent-managed-skills"
VERSION_STATE_FILE=".codexDevAgent-version"

MODE=""
SOURCE_PATH=""
TARGET_PATH="${DEFAULT_TARGET}"
REPO_URL="${DEFAULT_REPO_URL}"
DRY_RUN=0

declare -a CHANGED_SKILLS=()
declare -a NEW_SKILLS=()
declare -a REMOVED_SKILLS=()
declare -a SOURCE_SKILL_NAMES=()
AGENTS_STATUS="unchanged"
BACKUP_PATH=""
USING_SOURCE=""
STATE_FILE_PATH=""
STATE_FILE_PRESENT=0
VERSION_FILE_PATH=""
SOURCE_VERSION=""
TARGET_VERSION=""

usage() {
  cat <<'EOF'
Usage:
  sync_global_codex_assets.sh check [--source <path>] [--target <path>] [--repo-url <url>]
  sync_global_codex_assets.sh update [--source <path>] [--target <path>] [--repo-url <url>] [--dry-run]
  sync_global_codex_assets.sh apply [--source <path>] [--target <path>] [--repo-url <url>] [--dry-run]
  sync_global_codex_assets.sh clean-install [--source <path>] [--target <path>] [--repo-url <url>] [--dry-run]

Commands:
  check   Refresh the source repo when needed and report whether updates exist.
  update  Backup, merge, and sync the global Codex assets without deleting stale managed skills.
  apply   Alias for update.
  clean-install
          Backup, merge, delete stale managed skills tracked from prior syncs, and then sync the current repo skills.

Options:
  --source <path>   Use a specific codexDevAgent repo checkout.
  --target <path>   Override the target Codex home. Default: ~/.codex
  --repo-url <url>  Override the clone URL for the cached source repo.
  --dry-run         Preview changes without mutating the target.
  -h, --help        Show this help message.
EOF
}

info() {
  printf '[info] %s\n' "$1"
}

warn() {
  printf '[warn] %s\n' "$1" >&2
}

fail() {
  printf '[error] %s\n' "$1" >&2
  exit 1
}

run_cmd() {
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    printf '[dry-run] %s\n' "$*"
    return 0
  fi

  "$@"
}

array_contains() {
  local needle="$1"
  shift
  local value=""

  for value in "$@"; do
    if [[ "${value}" == "${needle}" ]]; then
      return 0
    fi
  done

  return 1
}

is_repo_root() {
  local candidate="$1"

  [[ -f "${candidate}/AGENTS.md" && -d "${candidate}/skills" && -f "${candidate}/README.md" && -f "${candidate}/package.json" ]] || return 1
  grep -q '^# codexDevAgent$' "${candidate}/README.md"
}

read_package_version() {
  local package_json_path="$1"

  node -p "const pkg = require(process.argv[1]); pkg.version || ''" "${package_json_path}"
}

default_branch() {
  local repo_path="$1"
  local origin_head=""

  origin_head=$(git -C "${repo_path}" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null || true)
  if [[ -n "${origin_head}" ]]; then
    printf '%s\n' "${origin_head##*/}"
    return 0
  fi

  printf 'master\n'
}

refresh_cached_repo() {
  local cache_path="$1"
  local branch=""

  if [[ ! -d "${cache_path}/.git" ]]; then
    info "Cloning source repo into ${cache_path}"
    run_cmd mkdir -p "$(dirname "${cache_path}")"
    run_cmd git clone "${REPO_URL}" "${cache_path}"
    return 0
  fi

  if [[ -n "$(git -C "${cache_path}" status --short)" ]]; then
    fail "Cached source repo at ${cache_path} has local changes; aborting refresh."
  fi

  branch=$(default_branch "${cache_path}")
  info "Refreshing cached source repo at ${cache_path}"
  run_cmd git -C "${cache_path}" fetch --prune origin
  run_cmd git -C "${cache_path}" checkout "${branch}"
  run_cmd git -C "${cache_path}" pull --ff-only origin "${branch}"
}

resolve_source_repo() {
  if [[ -n "${SOURCE_PATH}" ]]; then
    USING_SOURCE=$(cd "${SOURCE_PATH}" && pwd)
  elif is_repo_root "${PWD}"; then
    USING_SOURCE="${PWD}"
  elif is_repo_root "${REPO_FROM_SKILL}"; then
    USING_SOURCE="${REPO_FROM_SKILL}"
  else
    USING_SOURCE="${DEFAULT_CACHE_SOURCE}"
    refresh_cached_repo "${USING_SOURCE}"
  fi

  is_repo_root "${USING_SOURCE}" || fail "Source repo not valid: ${USING_SOURCE}"
}

validate_source_skills() {
  local source_skills_dir="$1"

  [[ -f "${RUNTIME_VALIDATOR}" ]] || fail "Runtime validator not found at ${RUNTIME_VALIDATOR}"
  command -v python3 >/dev/null 2>&1 || fail "python3 is required to validate skills."

  info "Validating source skills runtime contracts"
  python3 "${RUNTIME_VALIDATOR}" --tree --include-hidden "${source_skills_dir}" || fail "Source skills validation failed."
}

build_merged_agents() {
  local source_agents="$1"
  local target_agents="$2"
  local output_agents="$3"
  local boundary_line=""

  if [[ ! -f "${target_agents}" ]]; then
    cp "${source_agents}" "${output_agents}"
    AGENTS_STATUS="create"
    return 0
  fi

  boundary_line=$(grep -n -m1 -F "${AGENTS_BOUNDARY_TEXT}" "${target_agents}" | cut -d: -f1 || true)
  if [[ -z "${boundary_line}" ]]; then
    fail "Target AGENTS.md exists but does not contain the managed workflow boundary."
  fi

  if (( boundary_line > 1 )); then
    sed -n "1,$((boundary_line - 1))p" "${target_agents}" > "${output_agents}"
  else
    : > "${output_agents}"
  fi

  cat "${source_agents}" >> "${output_agents}"

  if cmp -s "${target_agents}" "${output_agents}"; then
    AGENTS_STATUS="unchanged"
  else
    AGENTS_STATUS="merge"
  fi
}

collect_skill_changes() {
  local source_skills_dir="$1"
  local target_skills_dir="$2"
  local skill_name=""
  local source_skill_path=""
  local target_skill_path=""

  CHANGED_SKILLS=()
  NEW_SKILLS=()
  SOURCE_SKILL_NAMES=()

  while IFS= read -r source_skill_path; do
    skill_name=$(basename "${source_skill_path}")
    target_skill_path="${target_skills_dir}/${skill_name}"
    SOURCE_SKILL_NAMES+=("${skill_name}")

    if [[ ! -d "${target_skill_path}" ]]; then
      NEW_SKILLS+=("${skill_name}")
    elif ! diff -qr "${source_skill_path}" "${target_skill_path}" >/dev/null 2>&1; then
      CHANGED_SKILLS+=("${skill_name}")
    fi
  done < <(find "${source_skills_dir}" -mindepth 1 -maxdepth 1 -type d | sort)
}

collect_removed_skills() {
  local target_skills_dir="$1"
  local managed_skill=""

  REMOVED_SKILLS=()
  STATE_FILE_PRESENT=0

  if [[ ! -f "${STATE_FILE_PATH}" ]]; then
    return 0
  fi

  STATE_FILE_PRESENT=1

  while IFS= read -r managed_skill; do
    [[ -n "${managed_skill}" ]] || continue

    if ! array_contains "${managed_skill}" "${SOURCE_SKILL_NAMES[@]}" && [[ -d "${target_skills_dir}/${managed_skill}" ]]; then
      REMOVED_SKILLS+=("${managed_skill}")
    fi
  done < "${STATE_FILE_PATH}"
}

apply_agents_update() {
  local merged_agents="$1"
  local target_agents="$2"

  if [[ "${AGENTS_STATUS}" == "unchanged" ]]; then
    return 0
  fi

  run_cmd mkdir -p "$(dirname "${target_agents}")"

  if [[ -f "${target_agents}" ]]; then
    BACKUP_PATH="${target_agents}.bak-$(date +%Y%m%d%H%M%S)"
    run_cmd cp "${target_agents}" "${BACKUP_PATH}"
  fi

  run_cmd cp "${merged_agents}" "${target_agents}"
}

apply_skill_sync() {
  local source_skills_dir="$1"
  local target_skills_dir="$2"
  local skill_name=""

  run_cmd mkdir -p "${target_skills_dir}"

  if [[ "${MODE}" == "clean-install" ]]; then
    for skill_name in "${REMOVED_SKILLS[@]}"; do
      run_cmd rm -rf "${target_skills_dir:?}/${skill_name}"
    done
  fi

  for skill_name in "${NEW_SKILLS[@]}"; do
    run_cmd cp -R "${source_skills_dir}/${skill_name}" "${target_skills_dir}/${skill_name}"
  done

  for skill_name in "${CHANGED_SKILLS[@]}"; do
    run_cmd rm -rf "${target_skills_dir:?}/${skill_name}"
    run_cmd cp -R "${source_skills_dir}/${skill_name}" "${target_skills_dir}/${skill_name}"
  done
}

write_managed_skills_state() {
  local skill_name=""

  if [[ "${MODE}" == "check" ]]; then
    return 0
  fi

  run_cmd mkdir -p "$(dirname "${STATE_FILE_PATH}")"

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    printf '[dry-run] write managed skills state to %s\n' "${STATE_FILE_PATH}"
    return 0
  fi

  : > "${STATE_FILE_PATH}"
  for skill_name in "${SOURCE_SKILL_NAMES[@]}"; do
    printf '%s\n' "${skill_name}" >> "${STATE_FILE_PATH}"
  done
}

read_target_version() {
  if [[ -f "${VERSION_FILE_PATH}" ]]; then
    TARGET_VERSION=$(tr -d '[:space:]' < "${VERSION_FILE_PATH}")
  else
    TARGET_VERSION=""
  fi
}

write_target_version() {
  if [[ -z "${SOURCE_VERSION}" || "${MODE}" == "check" ]]; then
    return 0
  fi

  run_cmd mkdir -p "$(dirname "${VERSION_FILE_PATH}")"

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    printf '[dry-run] write installed version %s to %s\n' "${SOURCE_VERSION}" "${VERSION_FILE_PATH}"
    return 0
  fi

  printf '%s\n' "${SOURCE_VERSION}" > "${VERSION_FILE_PATH}"
}

report() {
  local mode_label="$1"
  local total_updates=0
  local skill_name=""

  printf 'Mode: %s\n' "${mode_label}"
  printf 'Source repo: %s\n' "${USING_SOURCE}"
  printf 'Target Codex home: %s\n' "${TARGET_PATH}"
  if [[ -n "${SOURCE_VERSION}" || -n "${TARGET_VERSION}" ]]; then
    printf 'Version: installed=%s source=%s\n' "${TARGET_VERSION:-unknown}" "${SOURCE_VERSION:-unknown}"
  fi

  if [[ "${AGENTS_STATUS}" == "unchanged" ]]; then
    printf 'AGENTS.md: up to date\n'
  elif [[ "${AGENTS_STATUS}" == "create" ]]; then
    printf 'AGENTS.md: will be created\n'
    total_updates=$((total_updates + 1))
  else
    printf 'AGENTS.md: will be merged\n'
    total_updates=$((total_updates + 1))
  fi

  if [[ -n "${BACKUP_PATH}" ]]; then
    printf 'Backup: %s\n' "${BACKUP_PATH}"
  elif [[ ("${MODE}" == "update" || "${MODE}" == "clean-install") && "${AGENTS_STATUS}" != "unchanged" && -f "${TARGET_PATH}/AGENTS.md" ]]; then
    printf 'Backup: %s.bak-<timestamp>\n' "${TARGET_PATH}/AGENTS.md"
  fi

  if (( ${#NEW_SKILLS[@]} == 0 && ${#CHANGED_SKILLS[@]} == 0 )); then
    printf 'Skills: up to date\n'
  else
    if (( ${#NEW_SKILLS[@]} > 0 )); then
      total_updates=$((total_updates + ${#NEW_SKILLS[@]}))
      printf 'Skills to add:\n'
      for skill_name in "${NEW_SKILLS[@]}"; do
        printf '  - %s\n' "${skill_name}"
      done
    fi

    if (( ${#CHANGED_SKILLS[@]} > 0 )); then
      total_updates=$((total_updates + ${#CHANGED_SKILLS[@]}))
      printf 'Skills to update:\n'
      for skill_name in "${CHANGED_SKILLS[@]}"; do
        printf '  - %s\n' "${skill_name}"
      done
    fi
  fi

  if (( ${#REMOVED_SKILLS[@]} > 0 )); then
    total_updates=$((total_updates + ${#REMOVED_SKILLS[@]}))
    if [[ "${MODE}" == "clean-install" ]]; then
      printf 'Skills to remove:\n'
    else
      printf 'Stale managed skills removable by clean-install:\n'
    fi

    for skill_name in "${REMOVED_SKILLS[@]}"; do
      printf '  - %s\n' "${skill_name}"
    done
  elif [[ "${MODE}" == "clean-install" && "${STATE_FILE_PRESENT}" -eq 0 ]]; then
    printf 'Managed state: no prior managed skill state found; no stale managed skills removed\n'
  fi

  if (( total_updates == 0 )); then
    printf 'Result: no updates available\n'
  elif [[ "${MODE}" == "check" ]]; then
    printf 'Result: updates available\n'
  elif [[ "${DRY_RUN}" -eq 1 ]]; then
    printf 'Result: dry-run completed\n'
  else
    printf 'Result: update applied\n'
  fi
}

while (($# > 0)); do
  case "$1" in
    check|update|apply|clean-install)
      [[ -z "${MODE}" ]] || fail "Only one command may be provided."
      if [[ "$1" == "apply" ]]; then
        MODE="update"
      else
        MODE="$1"
      fi
      shift
      ;;
    --source)
      shift
      [[ $# -gt 0 ]] || fail "--source requires a path."
      SOURCE_PATH="$1"
      shift
      ;;
    --target)
      shift
      [[ $# -gt 0 ]] || fail "--target requires a path."
      TARGET_PATH="$1"
      shift
      ;;
    --repo-url)
      shift
      [[ $# -gt 0 ]] || fail "--repo-url requires a URL."
      REPO_URL="$1"
      shift
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
      fail "Unknown argument: $1"
      ;;
  esac
done

[[ -n "${MODE}" ]] || {
  usage
  exit 1
}

tmp_dir=$(mktemp -d)
trap 'rm -rf "${tmp_dir}"' EXIT

resolve_source_repo

SOURCE_AGENTS="${USING_SOURCE}/AGENTS.md"
SOURCE_SKILLS="${USING_SOURCE}/skills"
TARGET_AGENTS="${TARGET_PATH}/AGENTS.md"
TARGET_SKILLS="${TARGET_PATH}/skills"
MERGED_AGENTS="${tmp_dir}/AGENTS.merged.md"
STATE_FILE_PATH="${TARGET_PATH}/${MANAGED_SKILLS_STATE_FILE}"
VERSION_FILE_PATH="${TARGET_PATH}/${VERSION_STATE_FILE}"

[[ -f "${SOURCE_AGENTS}" ]] || fail "Source AGENTS.md not found at ${SOURCE_AGENTS}"
[[ -d "${SOURCE_SKILLS}" ]] || fail "Source skills directory not found at ${SOURCE_SKILLS}"
[[ -f "${USING_SOURCE}/package.json" ]] || fail "Source package.json not found at ${USING_SOURCE}/package.json"
grep -q -m1 -F "${AGENTS_BOUNDARY_TEXT}" "${SOURCE_AGENTS}" || fail "Source AGENTS.md does not contain the managed workflow boundary."
SOURCE_VERSION=$(read_package_version "${USING_SOURCE}/package.json")
read_target_version
validate_source_skills "${SOURCE_SKILLS}"

build_merged_agents "${SOURCE_AGENTS}" "${TARGET_AGENTS}" "${MERGED_AGENTS}"
collect_skill_changes "${SOURCE_SKILLS}" "${TARGET_SKILLS}"
collect_removed_skills "${TARGET_SKILLS}"

if [[ "${MODE}" == "update" || "${MODE}" == "clean-install" ]]; then
  apply_agents_update "${MERGED_AGENTS}" "${TARGET_AGENTS}"
  apply_skill_sync "${SOURCE_SKILLS}" "${TARGET_SKILLS}"
  write_managed_skills_state
  write_target_version
fi

report "${MODE}"
