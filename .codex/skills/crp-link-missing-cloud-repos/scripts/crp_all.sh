#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="${SCRIPT_DIR}/sync_crp_all.sh"
CRP_CLOUD_SCRIPT="${SCRIPT_DIR}/sync_crp_cloud_repos.py"
DEFAULT_TARGET_REPOS_FILE="/Users/john/Downloads/lambdas/crp_all/current-crp-target-repos.txt"
DEFAULT_CLOUD_REPORT_FILE="/Users/john/Downloads/lambdas/crp_all/crp-cloud-repos-sync-report.json"
DEFAULT_PROJECT_REPOS_LIST_TXT="/Users/john/Downloads/lambdas/crp_all/current-crp-project-repos-full-list.txt"
DEFAULT_PROJECT_REPOS_LIST_JSON="/Users/john/Downloads/lambdas/crp_all/current-crp-project-repos-full-list.json"

temp_files=()
temp_dirs=()

cleanup_temp_artifacts() {
  local f d

  for f in "${temp_files[@]:-}"; do
    [[ -n "$f" ]] && rm -f "$f" 2>/dev/null || true
  done

  for d in "${temp_dirs[@]:-}"; do
    [[ -n "$d" ]] && rm -rf "$d" 2>/dev/null || true
  done
}

cleanup_legacy_outputs() {
  rm -f "$DEFAULT_TARGET_REPOS_FILE" "$DEFAULT_CLOUD_REPORT_FILE" "$DEFAULT_PROJECT_REPOS_LIST_TXT" 2>/dev/null || true
  rm -f /Users/john/Downloads/lambdas/_sync_reports/crp_all_sync_report_*.txt 2>/dev/null || true
  rm -f /Users/john/Downloads/lambdas/_sync_reports/crp_all_sync_failures_*.txt 2>/dev/null || true
}

trap 'cleanup_temp_artifacts' EXIT

usage() {
  cat <<'USAGE'
Usage:
  crp_all.sh [--only-sync | --only-cloud-link-clone] [--repos-file <path>] [cloud-link-args...]

Modes:
  --only-sync                 Run only git sync for target repos.
  --only-cloud-link-clone     Run only CRP cloud-link + local clone/sync stage.

Default:
  Run CRP cloud-link + local clone/sync stage first, then run git sync stage for the same target repo list.

Additional args are passed to:
  scripts/sync_crp_cloud_repos.py

Examples:
  crp_all.sh
  crp_all.sh --dry-run
  crp_all.sh --only-sync
  crp_all.sh --only-cloud-link-clone --clone-prefer https
USAGE
}

python_tls_probe() {
  local py="$1"
  "$py" - <<'PY'
import sys
import urllib.error
import urllib.request

url = "https://mpq5pzhhv2.execute-api.eu-west-1.amazonaws.com/prod"
try:
    urllib.request.urlopen(url, timeout=8)
except urllib.error.HTTPError:
    sys.exit(0)
except Exception as exc:
    msg = str(exc)
    if "CERTIFICATE_VERIFY_FAILED" in msg:
        sys.exit(2)
    sys.exit(1)

sys.exit(0)
PY
}

select_python() {
  local candidates=()
  local seen=":"
  local first_available=""
  local cert_fail=0

  if [[ -n "${PYTHON_BIN:-}" ]]; then
    candidates+=("${PYTHON_BIN}")
  fi
  candidates+=("python3" "/usr/bin/python3")

  for candidate in "${candidates[@]}"; do
    local resolved=""

    if [[ "${seen}" == *":${candidate}:"* ]]; then
      continue
    fi
    seen+="${candidate}:"

    if [[ -x "${candidate}" ]]; then
      resolved="${candidate}"
    else
      resolved="$(command -v "${candidate}" 2>/dev/null || true)"
    fi

    if [[ -z "${resolved}" ]]; then
      continue
    fi

    if [[ -z "${first_available}" ]]; then
      first_available="${resolved}"
    fi

    if python_tls_probe "${resolved}"; then
      printf "%s\n" "${resolved}"
      return 0
    fi

    local rc=$?
    if [[ ${rc} -eq 2 ]]; then
      cert_fail=1
    fi
  done

  if [[ ${cert_fail} -eq 1 && -x "/usr/bin/python3" ]]; then
    printf "%s\n" "/usr/bin/python3"
    return 0
  fi

  if [[ -n "${first_available}" ]]; then
    printf "%s\n" "${first_available}"
    return 0
  fi

  echo "ERROR: No python interpreter found (tried PYTHON_BIN, python3, /usr/bin/python3)." >&2
  return 2
}

refresh_crp_project_repo_lists() {
  local cfg="${HOME}/.crp/config.json"
  local api="https://mpq5pzhhv2.execute-api.eu-west-1.amazonaws.com/prod"
  local token project_id project_name tmp_json

  if [[ ! -f "$cfg" ]]; then
    echo "WARN: CRP config not found, skipping project repo list refresh." >&2
    return 0
  fi

  token="$(jq -r '.api.auth.token // ""' "$cfg")"
  if [[ -z "$token" ]]; then
    echo "WARN: CRP token missing, skipping project repo list refresh." >&2
    return 0
  fi

  project_id="$(curl -sS -X POST "$api/crp-fetch-projects" \
    -H 'content-type: application/json' \
    -H "authorization: $token" \
    -H 'origin: http://localhost' \
    --data '{"type":"fetch-projects","page":0,"searchTerm":"crp","project_id":"","nextContinuationToken":""}' \
    | jq -r '.data[] | select((.project_name // "") | ascii_downcase == "crp") | .project_id' | head -n1)"

  if [[ -z "$project_id" ]]; then
    echo "WARN: Could not resolve project_id for project 'crp'. Skipping project repo list refresh." >&2
    return 0
  fi

  project_name="$(curl -sS -X POST "$api/crp-fetch-projects" \
    -H 'content-type: application/json' \
    -H "authorization: $token" \
    -H 'origin: http://localhost' \
    --data '{"type":"fetch-projects","page":0,"searchTerm":"crp","project_id":"","nextContinuationToken":""}' \
    | jq -r '.data[] | select((.project_name // "") | ascii_downcase == "crp") | .project_name' | head -n1)"

  tmp_json="$(mktemp)"

  curl -sS -X POST "$api/crp-fetch-cloud-repos" \
    -H 'content-type: application/json' \
    -H "authorization: $token" \
    -H 'origin: http://localhost' \
    --data "{\"type\":\"fetch-cloud-repos-by-project-id\",\"project_id\":\"$project_id\"}" \
    > "$tmp_json"

  jq --arg pn "$project_name" '{project_id: .data[0].project_id, project_name: $pn, repo_count: (.data | map(.repo_id) | unique | length), repos: (.data | map(.repo_id) | unique | sort)}' \
    "$tmp_json" > "$DEFAULT_PROJECT_REPOS_LIST_JSON"

  rm -f "$tmp_json"

  echo "Wrote: $DEFAULT_PROJECT_REPOS_LIST_JSON"
}

mode_sync=1
mode_cloud_link_clone=1
seen_only_sync=0
seen_only_cloud_link_clone=0
target_repos_file="$DEFAULT_TARGET_REPOS_FILE"
cloud_report_out="$DEFAULT_CLOUD_REPORT_FILE"
user_provided_repos_file=0
user_provided_cloud_out=0
cloud_args=()

has_cloud_arg() {
  local wanted="$1"
  local arg
  if [[ ${#cloud_args[@]} -eq 0 ]]; then
    return 1
  fi
  for arg in "${cloud_args[@]}"; do
    if [[ "$arg" == "$wanted" || "$arg" == "$wanted="* ]]; then
      return 0
    fi
  done
  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only-sync)
      mode_cloud_link_clone=0
      seen_only_sync=1
      shift
      ;;
    --only-cloud-link-clone)
      mode_sync=0
      seen_only_cloud_link_clone=1
      shift
      ;;
    --repos-file)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --repos-file requires a value." >&2
        exit 2
      fi
      target_repos_file="$2"
      user_provided_repos_file=1
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      cloud_args+=("$1")
      shift
      ;;
  esac
done

if [[ ${seen_only_sync} -eq 1 && ${seen_only_cloud_link_clone} -eq 1 ]]; then
  echo "ERROR: --only-sync and --only-cloud-link-clone are mutually exclusive." >&2
  exit 2
fi

if [[ ! -x "${SYNC_SCRIPT}" ]]; then
  echo "ERROR: Sync script not found or not executable: ${SYNC_SCRIPT}" >&2
  exit 2
fi

if [[ ! -f "${CRP_CLOUD_SCRIPT}" ]]; then
  echo "ERROR: Required script not found: ${CRP_CLOUD_SCRIPT}" >&2
  exit 2
fi

if has_cloud_arg "--out"; then
  user_provided_cloud_out=1
fi

if [[ ${user_provided_repos_file} -eq 0 && ${mode_cloud_link_clone} -eq 1 ]]; then
  target_repos_file="$(mktemp -t crp-target-repos.XXXXXX)"
  temp_files+=("$target_repos_file")
fi

if [[ ${user_provided_cloud_out} -eq 0 ]]; then
  cloud_report_out="$(mktemp -t crp-cloud-report.XXXXXX.json)"
  temp_files+=("$cloud_report_out")
fi

if [[ ${mode_cloud_link_clone} -eq 1 ]]; then
  py_bin="$(select_python)"
  echo "Using python interpreter: ${py_bin}"
  cloud_cmd=("${py_bin}" "${CRP_CLOUD_SCRIPT}" --repos-list-out "$target_repos_file")
  if [[ ${user_provided_cloud_out} -eq 0 ]]; then
    cloud_cmd+=(--out "$cloud_report_out")
  fi
  if [[ ${#cloud_args[@]} -gt 0 ]]; then
    cloud_cmd+=("${cloud_args[@]}")
  fi
  "${cloud_cmd[@]}"
fi

if [[ ${mode_sync} -eq 1 ]]; then
  sync_report_dir="$(mktemp -d -t crp-sync-reports.XXXXXX)"
  temp_dirs+=("$sync_report_dir")
  REPORT_DIR="$sync_report_dir" "${SYNC_SCRIPT}" --repos-file "$target_repos_file"
fi

refresh_crp_project_repo_lists
cleanup_legacy_outputs
