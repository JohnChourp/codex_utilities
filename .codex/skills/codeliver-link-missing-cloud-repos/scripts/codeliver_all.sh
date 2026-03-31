#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="${SCRIPT_DIR}/sync_codeliver_all.sh"
CODELIVER_CLOUD_SCRIPT="${SCRIPT_DIR}/sync_codeliver_cloud_repos.py"
DOWNLOADS_DIR="${DOWNLOADS_DIR:-${HOME}/Downloads}"
DEFAULT_CLONE_ROOT="${DOWNLOADS_DIR}/lambdas/codeliver_all"
DEFAULT_TARGET_REPOS_FILE="${DEFAULT_CLONE_ROOT}/current-codeliver-target-repos.txt"
DEFAULT_CLOUD_REPORT_FILE="${DEFAULT_CLONE_ROOT}/codeliver-cloud-repos-sync-report.json"
DEFAULT_PROJECT_REPOS_LIST_TXT="${DEFAULT_CLONE_ROOT}/current-codeliver-project-repos-full-list.txt"
DEFAULT_PROJECT_REPOS_LIST_JSON="${DEFAULT_CLONE_ROOT}/current-codeliver-project-repos-full-list.json"
DEFAULT_API_ROUTE_PREFIX="crp"
DEFAULT_PROJECTS_ROOT="${DOWNLOADS_DIR}/projects"
DEFAULT_PROJECTS_CODELIVER_ROOT="${DEFAULT_PROJECTS_ROOT}/codeliver"
DEFAULT_SYNC_REPORT_DIR="${DOWNLOADS_DIR}/lambdas/_sync_reports"
DEFAULT_CODELIVER_CONFIG_PATH="${HOME}/.codeliver/config.json"
DEFAULT_CRP_CONFIG_PATH="${HOME}/.crp/config.json"

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
  rm -f "${DEFAULT_SYNC_REPORT_DIR}"/codeliver_all_sync_report_*.txt 2>/dev/null || true
  rm -f "${DEFAULT_SYNC_REPORT_DIR}"/codeliver_all_sync_failures_*.txt 2>/dev/null || true
}

trap 'cleanup_temp_artifacts' EXIT

usage() {
  cat <<'USAGE'
Usage:
  codeliver_all.sh [--only-sync | --only-cloud-link-clone] [--repos-file <path>] [cloud-link-args...]

Modes:
  --only-sync                 Run only git sync for target repos.
  --only-cloud-link-clone     Run only Codeliver cloud-link + local clone/sync stage.

Default:
  Run Codeliver cloud-link + local clone/sync stage first, then run git sync stage for the same target repo list.

Additional args are passed to:
  scripts/sync_codeliver_cloud_repos.py

Examples:
  codeliver_all.sh
  codeliver_all.sh --dry-run
  codeliver_all.sh --only-sync
  codeliver_all.sh --only-cloud-link-clone --clone-prefer https
USAGE
}

resolve_projects_root() {
  if [[ -d "$DEFAULT_PROJECTS_CODELIVER_ROOT" ]]; then
    printf "%s\n" "$DEFAULT_PROJECTS_CODELIVER_ROOT"
    return 0
  fi
  printf "%s\n" "$DEFAULT_PROJECTS_ROOT"
}

normalize_api_route_prefix() {
  local prefix="${1:-$DEFAULT_API_ROUTE_PREFIX}"
  prefix="${prefix,,}"
  if [[ -z "$prefix" ]]; then
    prefix="$DEFAULT_API_ROUTE_PREFIX"
  fi
  printf "%s\n" "$prefix"
}

resolve_api_config_path() {
  local route_prefix
  route_prefix="$(normalize_api_route_prefix "${1:-}")"

  if [[ "$route_prefix" == "crp" ]]; then
    printf "%s\n" "$DEFAULT_CRP_CONFIG_PATH"
    return 0
  fi

  printf "%s\n" "$DEFAULT_CODELIVER_CONFIG_PATH"
}

looks_like_github_pat() {
  local token="${1:-}"
  [[ "$token" == ghp_* || "$token" == github_pat_* ]]
}

extract_config_token() {
  local cfg="$1"
  local token=""
  local py=""

  if [[ ! -f "$cfg" ]]; then
    return 1
  fi

  if command -v jq >/dev/null 2>&1; then
    token="$(jq -r '.api.auth.token // ""' "$cfg" 2>/dev/null || true)"
  else
    for py in "${PYTHON_BIN:-}" python3 /usr/bin/python3; do
      [[ -n "$py" ]] || continue
      if [[ -x "$py" || -n "$(command -v "$py" 2>/dev/null || true)" ]]; then
        token="$("$py" - "$cfg" <<'PY'
import json
import sys
from pathlib import Path

cfg = Path(sys.argv[1])
try:
    data = json.loads(cfg.read_text(encoding="utf-8"))
except Exception:
    print("")
    raise SystemExit(0)
print((((data.get("api") or {}).get("auth") or {}).get("token") or "").strip())
PY
)"
        break
      fi
    done
  fi

  if [[ -z "$token" ]]; then
    return 1
  fi
  printf "%s\n" "$token"
  return 0
}

bootstrap_codeliver_config_if_possible() {
  local cfg="$1"
  local token="${CODELIVER_AUTH_TOKEN:-}"
  local py=""

  if [[ "$cfg" != "$DEFAULT_CODELIVER_CONFIG_PATH" ]]; then
    return 1
  fi

  if extract_config_token "$cfg" >/dev/null 2>&1; then
    return 0
  fi

  if [[ -z "$token" ]]; then
    return 1
  fi
  if looks_like_github_pat "$token"; then
    return 1
  fi

  mkdir -p "${HOME}/.codeliver"

  for py in "${PYTHON_BIN:-}" python3 /usr/bin/python3; do
    [[ -n "$py" ]] || continue
    if [[ -x "$py" || -n "$(command -v "$py" 2>/dev/null || true)" ]]; then
      "$py" - "$cfg" <<'PY'
import json
import os
import sys
from pathlib import Path

cfg_path = Path(sys.argv[1])
token = os.getenv("CODELIVER_AUTH_TOKEN", "").strip()
if not token:
    raise SystemExit(1)

data = {}
if cfg_path.exists():
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        data = {}

api = data.setdefault("api", {})
auth = api.setdefault("auth", {})
auth["token"] = token
auth.setdefault("user", {})
data.setdefault("currentProject", {})
data.setdefault("github", {})

cfg_path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
PY
      if extract_config_token "$cfg" >/dev/null 2>&1; then
        echo "Bootstrapped ~/.codeliver/config.json from CODELIVER_AUTH_TOKEN"
        return 0
      fi
      break
    fi
  done

  return 1
}

build_local_target_repo_list() {
  local out_file="$1"
  {
    find "$DEFAULT_CLONE_ROOT" -mindepth 1 -maxdepth 1 -type d -name 'codeliver-*' -exec basename {} \; 2>/dev/null || true
    find "$DEFAULT_PROJECTS_ROOT" -mindepth 1 -maxdepth 1 -type d -name 'codeliver-*' -exec basename {} \; 2>/dev/null || true
    find "$DEFAULT_PROJECTS_CODELIVER_ROOT" -mindepth 1 -maxdepth 1 -type d -name 'codeliver-*' -exec basename {} \; 2>/dev/null || true
  } | sort -u > "$out_file"
}

restore_cached_target_repo_list() {
  local out_file="$1"

  if [[ -s "$DEFAULT_TARGET_REPOS_FILE" ]]; then
    if [[ "$out_file" == "$DEFAULT_TARGET_REPOS_FILE" ]]; then
      return 0
    fi
    cp "$DEFAULT_TARGET_REPOS_FILE" "$out_file"
    return 0
  fi

  return 1
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

refresh_codeliver_project_repo_lists() {
  local cfg="$1"
  local api="https://mpq5pzhhv2.execute-api.eu-west-1.amazonaws.com/prod"
  local token project_id project_name tmp_json tmp_projects projects_response

  if [[ ! -f "$cfg" ]]; then
    echo "WARN: Codeliver config not found (~/.codeliver/config.json), skipping project repo list refresh." >&2
    return 0
  fi

  token="$(jq -r '.api.auth.token // ""' "$cfg")"
  if [[ -z "$token" ]]; then
    echo "WARN: Codeliver token missing, skipping project repo list refresh." >&2
    return 0
  fi
  if looks_like_github_pat "$token"; then
    echo "WARN: Config token looks like GitHub PAT, skipping project repo list refresh." >&2
    return 0
  fi

  local api_route_prefix="${API_ROUTE_PREFIX:-crp}"

  tmp_projects="$(mktemp)"
  curl -sS -X POST "$api/${api_route_prefix}-fetch-projects" \
    -H 'content-type: application/json' \
    -H "authorization: $token" \
    -H 'origin: http://localhost' \
    --data '{"type":"fetch-projects","page":0,"searchTerm":"codeliver","project_id":"","nextContinuationToken":""}' \
    > "$tmp_projects"

  projects_response="$(cat "$tmp_projects")"
  if ! echo "$projects_response" | jq -e . >/dev/null 2>&1; then
    echo "WARN: Invalid JSON from ${api_route_prefix}-fetch-projects; skipping project repo list refresh." >&2
    rm -f "$tmp_projects"
    return 0
  fi

  project_id="$(jq -r '((.data // []) | map(select((.project_name // "") | ascii_downcase == "codeliver")) | .[0].project_id) // ""' "$tmp_projects")"

  if [[ -z "$project_id" ]]; then
    echo "WARN: Could not resolve project_id for project 'codeliver' via ${api_route_prefix}-fetch-projects. Skipping project repo list refresh." >&2
    rm -f "$tmp_projects"
    return 0
  fi

  project_name="$(jq -r '((.data // []) | map(select((.project_name // "") | ascii_downcase == "codeliver")) | .[0].project_name) // "codeliver"' "$tmp_projects")"
  rm -f "$tmp_projects"

  tmp_json="$(mktemp)"

  curl -sS -X POST "$api/${api_route_prefix}-fetch-cloud-repos" \
    -H 'content-type: application/json' \
    -H "authorization: $token" \
    -H 'origin: http://localhost' \
    --data "{\"type\":\"fetch-cloud-repos-by-project-id\",\"project_id\":\"$project_id\"}" \
    > "$tmp_json"

  jq --arg pn "$project_name" '{project_id: (((.data // [])[0].project_id) // ""), project_name: $pn, repo_count: ((.data // []) | map(.repo_id) | unique | length), repos: ((.data // []) | map(.repo_id) | unique | sort)}' \
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
generated_feature_cloud_repos_file=0
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

get_cloud_arg_value() {
  local wanted="$1"
  local fallback="$2"
  local idx arg next_idx

  for (( idx=0; idx<${#cloud_args[@]}; idx++ )); do
    arg="${cloud_args[$idx]}"
    if [[ "$arg" == "$wanted" ]]; then
      next_idx=$((idx + 1))
      if [[ $next_idx -lt ${#cloud_args[@]} ]]; then
        printf "%s\n" "${cloud_args[$next_idx]}"
        return 0
      fi
      break
    fi
    if [[ "$arg" == "$wanted="* ]]; then
      printf "%s\n" "${arg#*=}"
      return 0
    fi
  done

  printf "%s\n" "$fallback"
  return 0
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

if [[ ! -f "${CODELIVER_CLOUD_SCRIPT}" ]]; then
  echo "ERROR: Required script not found: ${CODELIVER_CLOUD_SCRIPT}" >&2
  exit 2
fi

if has_cloud_arg "--out"; then
  user_provided_cloud_out=1
fi

if [[ ${user_provided_repos_file} -eq 0 && ${mode_cloud_link_clone} -eq 1 ]]; then
  target_repos_file="$(mktemp -t codeliver-target-repos.XXXXXX)"
  temp_files+=("$target_repos_file")
fi

if [[ ${user_provided_cloud_out} -eq 0 ]]; then
  cloud_report_out="$(mktemp -t codeliver-cloud-report.XXXXXX.json)"
  temp_files+=("$cloud_report_out")
fi

resolved_projects_root="$(resolve_projects_root)"
effective_api_route_prefix="$(get_cloud_arg_value "--api-route-prefix" "${API_ROUTE_PREFIX:-crp}")"
API_ROUTE_PREFIX="$effective_api_route_prefix"
export API_ROUTE_PREFIX
resolved_config_path="$(resolve_api_config_path "$effective_api_route_prefix")"

if [[ ${mode_cloud_link_clone} -eq 1 ]]; then
  cfg="$resolved_config_path"
  bootstrap_codeliver_config_if_possible "$cfg" || true

  if extract_config_token "$cfg" >/dev/null 2>&1; then
    py_bin="$(select_python)"
    echo "Using python interpreter: ${py_bin}"
    cloud_cmd=("${py_bin}" "${CODELIVER_CLOUD_SCRIPT}" --config "$cfg" --repos-list-out "$target_repos_file")
    if [[ ${user_provided_cloud_out} -eq 0 ]]; then
      cloud_cmd+=(--out "$cloud_report_out")
    fi
    if ! has_cloud_arg "--all-cloud-repos-out"; then
      cloud_cmd+=(--all-cloud-repos-out "$DEFAULT_PROJECT_REPOS_LIST_JSON")
    fi
    if ! has_cloud_arg "--projects-root"; then
      cloud_cmd+=(--projects-root "$resolved_projects_root")
    fi
    if [[ ${#cloud_args[@]} -gt 0 ]]; then
      cloud_cmd+=("${cloud_args[@]}")
    fi
    if "${cloud_cmd[@]}"; then
      feature_cloud_out="$(get_cloud_arg_value "--all-cloud-repos-out" "$DEFAULT_PROJECT_REPOS_LIST_JSON")"
      if [[ -s "$feature_cloud_out" ]]; then
        generated_feature_cloud_repos_file=1
      fi
    else
      if [[ ${seen_only_cloud_link_clone} -eq 1 ]]; then
        exit 1
      fi
      echo "WARN: Cloud-link stage failed. Falling back to local-only sync using cached/local target repos." >&2
      if ! restore_cached_target_repo_list "$target_repos_file"; then
        build_local_target_repo_list "$target_repos_file"
      fi
    fi
  else
    if [[ ${seen_only_cloud_link_clone} -eq 1 ]]; then
      echo "ERROR: Missing valid auth token in ${cfg}. Cloud-link stage requires authentication." >&2
      exit 2
    fi
    echo "WARN: Missing valid auth token in ${cfg}. Skipping cloud-link stage and falling back to local-only sync." >&2
    build_local_target_repo_list "$target_repos_file"
  fi
fi

if [[ ${mode_sync} -eq 1 ]]; then
  sync_report_dir="$(mktemp -d -t codeliver-sync-reports.XXXXXX)"
  temp_dirs+=("$sync_report_dir")
  if [[ ! -s "$target_repos_file" ]]; then
    echo "WARN: Target repos list is empty; rebuilding from local directories." >&2
    build_local_target_repo_list "$target_repos_file"
  fi
  REPORT_DIR="$sync_report_dir" PROJECTS_DIR="$resolved_projects_root" "${SYNC_SCRIPT}" --repos-file "$target_repos_file"
fi

if [[ ${generated_feature_cloud_repos_file} -eq 0 ]]; then
  refresh_codeliver_project_repo_lists "$resolved_config_path"
else
  echo "Wrote: $DEFAULT_PROJECT_REPOS_LIST_JSON"
fi
cleanup_legacy_outputs
