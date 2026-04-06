#!/usr/bin/env bash

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FILE="${ROOT_DIR}/harden-status-report.txt"
FAMILY_FILTER=""

print_usage() {
  cat <<EOF
Usage: ./report-harden-status.sh [--family FAMILY_NAME] [--output OUTPUT_FILE]
EOF
}

fail() {
  echo "$1" >&2
  exit 1
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --family)
        [[ $# -ge 2 ]] || fail "Missing value for --family"
        FAMILY_FILTER="$2"
        shift 2
        ;;
      --output)
        [[ $# -ge 2 ]] || fail "Missing value for --output"
        OUTPUT_FILE="$2"
        shift 2
        ;;
      --help|-h)
        print_usage
        exit 0
        ;;
      *)
        fail "Unknown argument: $1"
        ;;
    esac
  done
}

append_entries() {
  local title="$1"
  shift

  {
    echo "${title}:"

    if [[ $# -eq 0 ]]; then
      echo "(none)"
    else
      local entry
      for entry in "$@"; do
        echo "$entry"
      done
    fi
  } >>"$REPORT_TMP"
}

parse_args "$@"

mapfile -t FAMILY_NAMES < <(
  find "$ROOT_DIR" -mindepth 1 -maxdepth 1 -type d -name '*_all' -printf '%f\n' | sort
)

[[ ${#FAMILY_NAMES[@]} -gt 0 ]] || fail "No *_all families found under $ROOT_DIR"

if [[ -n "$FAMILY_FILTER" ]]; then
  FAMILY_FOUND=0
  for family_name in "${FAMILY_NAMES[@]}"; do
    if [[ "$family_name" == "$FAMILY_FILTER" ]]; then
      FAMILY_FOUND=1
      FAMILY_NAMES=("$FAMILY_FILTER")
      break
    fi
  done

  [[ $FAMILY_FOUND -eq 1 ]] || fail "Family not found: $FAMILY_FILTER"
fi

repos=0
package_json=0
hardened=0
not_hardened=0
missing_package_json=0
errors=()
not_hardened_entries=()
missing_package_entries=()

for family_name in "${FAMILY_NAMES[@]}"; do
  family_dir="${ROOT_DIR}/${family_name}"

  mapfile -t repo_names < <(
    find "$family_dir" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort
  )

  for repo_name in "${repo_names[@]}"; do
    repo_label="${family_name}/${repo_name}"
    package_json_path="${family_dir}/${repo_name}/package.json"

    repos=$((repos + 1))

    if [[ ! -f "$package_json_path" ]]; then
      missing_package_json=$((missing_package_json + 1))
      missing_package_entries+=("$repo_label")
      continue
    fi

    package_json=$((package_json + 1))

    parse_result="$(
      node - "$package_json_path" 2>&1 <<'NODE'
const fs = require("fs");

const packageJsonPath = process.argv[2];

try {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
  const value = Object.prototype.hasOwnProperty.call(packageJson, "harden_deploy_timestamp")
    ? String(packageJson.harden_deploy_timestamp ?? "").trim()
    : "";

  console.log(value.length > 0 ? "hardened" : "not_hardened");
} catch (error) {
  console.error(error.message);
  process.exit(2);
}
NODE
    )"
    parse_status=$?

    if [[ $parse_status -ne 0 ]]; then
      errors+=("${repo_label}: ${parse_result}")
      continue
    fi

    if [[ "$parse_result" == "hardened" ]]; then
      hardened=$((hardened + 1))
      continue
    fi

    not_hardened=$((not_hardened + 1))
    not_hardened_entries+=("$repo_label")
  done
done

REPORT_TMP="$(mktemp "${ROOT_DIR}/harden-status-report.XXXXXX.tmp")"
trap 'rm -f "$REPORT_TMP"' EXIT

{
  echo "Scanned root: ${ROOT_DIR}"
  echo "Scanned families: ${FAMILY_NAMES[*]}"
  echo "Summary:"
  echo "repos=${repos}"
  echo "package_json=${package_json}"
  echo "hardened=${hardened}"
  echo "not_hardened=${not_hardened}"
  echo "missing_package_json=${missing_package_json}"
  echo "errors=${#errors[@]}"
  echo
} >"$REPORT_TMP"

append_entries "Not hardened" "${not_hardened_entries[@]}"
echo >>"$REPORT_TMP"
append_entries "Missing package.json" "${missing_package_entries[@]}"

if [[ ${#errors[@]} -gt 0 ]]; then
  echo >>"$REPORT_TMP"
  append_entries "Errors" "${errors[@]}"
fi

mv "$REPORT_TMP" "$OUTPUT_FILE"
trap - EXIT

echo "Report written to: ${OUTPUT_FILE}"
echo "repos=${repos} package_json=${package_json} hardened=${hardened} not_hardened=${not_hardened} missing_package_json=${missing_package_json} errors=${#errors[@]}"

if [[ ${#errors[@]} -gt 0 ]]; then
  exit 1
fi
