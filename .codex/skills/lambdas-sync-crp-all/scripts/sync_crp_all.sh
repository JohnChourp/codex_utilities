#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/Users/john/Downloads/lambdas/crp_all"
ROOT_LABEL="crp_all"

CONCURRENCY="${CONCURRENCY:-20}"
REPORT_DIR="${REPORT_DIR:-/Users/john/Downloads/lambdas/_sync_reports}"
RUN_TS="$(date +%Y%m%d_%H%M%S)"

REPORT_FILE="${REPORT_DIR}/${ROOT_LABEL}_sync_report_${RUN_TS}.txt"
FAILURES_FILE="${REPORT_DIR}/${ROOT_LABEL}_sync_failures_${RUN_TS}.txt"
REPORT_LOCK_FILE="${REPORT_FILE}.lock"
FAILURES_LOCK_FILE="${FAILURES_FILE}.lock"

mkdir -p "$REPORT_DIR"

append_line_locked() {
  local target_file="$1"
  local lock_file="$2"
  local line="$3"

  if command -v flock >/dev/null 2>&1; then
    (
      flock -x 200
      printf "%s\n" "$line" >> "$target_file"
    ) 200>"$lock_file"
    return
  fi

  local lock_dir="${lock_file}.d"
  while ! mkdir "$lock_dir" 2>/dev/null; do
    sleep 0.01
  done

  printf "%s\n" "$line" >> "$target_file"
  rmdir "$lock_dir" || true
}

append_report() {
  append_line_locked "$REPORT_FILE" "$REPORT_LOCK_FILE" "$1"
}

append_failure() {
  append_line_locked "$FAILURES_FILE" "$FAILURES_LOCK_FILE" "$1"
}

log_repo_status() {
  local timestamp="$1"
  local repo_name="$2"
  local status="$3"
  local repo_path="$4"
  local detail="$5"
  local line
  printf -v line "%s\t%s\t%s\t%s\t%s" "$timestamp" "$repo_name" "$status" "$repo_path" "$detail"
  append_report "$line"

  case "$status" in
    FETCH_FAILED|PULL_FAILED|RECLONE_FAILED|SKIPPED_PULL_DIRTY|SKIPPED_PULL_NO_UPSTREAM)
      append_failure "$line"
      ;;
  esac
}

sync_repo() {
  local repo_dir="$1"
  local timestamp repo_name toplevel
  local origin_url current_branch upstream_ref
  local fetch_err_file pull_err_file fetch_err pull_err

  timestamp="$(date -Iseconds)"
  repo_name="$(basename "$repo_dir")"
  fetch_err_file="$(mktemp)"
  pull_err_file="$(mktemp)"

  if ! git -C "$repo_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_NOT_GIT_TOPLEVEL" "$repo_dir" "Directory is not a git repository"
    rm -f "$fetch_err_file" "$pull_err_file"
    return 0
  fi

  toplevel="$(git -C "$repo_dir" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ "$toplevel" != "$repo_dir" ]]; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_NOT_GIT_TOPLEVEL" "$repo_dir" "Directory is not git toplevel"
    rm -f "$fetch_err_file" "$pull_err_file"
    return 0
  fi

  if ! git -C "$repo_dir" rev-parse -q --verify HEAD >/dev/null 2>&1; then
    origin_url="$(git -C "$repo_dir" remote get-url origin 2>/dev/null || true)"

    if [[ -z "$origin_url" ]]; then
      log_repo_status "$timestamp" "$repo_name" "RECLONE_FAILED" "$repo_dir" "Empty repo and missing origin remote"
      rm -f "$fetch_err_file" "$pull_err_file"
      return 1
    fi

    case "$repo_dir" in
      "$ROOT_DIR"/*) ;;
      *)
        log_repo_status "$timestamp" "$repo_name" "RECLONE_FAILED" "$repo_dir" "Safety guard blocked rm -rf outside root"
        rm -f "$fetch_err_file" "$pull_err_file"
        return 1
        ;;
    esac

    if ! rm -rf "$repo_dir"; then
      log_repo_status "$timestamp" "$repo_name" "RECLONE_FAILED" "$repo_dir" "Failed to delete empty repo before reclone"
      rm -f "$fetch_err_file" "$pull_err_file"
      return 1
    fi

    if ! GIT_TERMINAL_PROMPT=0 git clone --quiet "$origin_url" "$repo_dir" 2>"$fetch_err_file"; then
      fetch_err="$(tail -n 20 "$fetch_err_file" 2>/dev/null | tr "\n" " " | sed -E "s/[[:space:]]+/ /g; s/^ +//; s/ +$//" || true)"
      log_repo_status "$timestamp" "$repo_name" "RECLONE_FAILED" "$repo_dir" "${fetch_err:-git clone failed from origin}"
      rm -f "$fetch_err_file" "$pull_err_file"
      return 1
    fi

    if ! git -C "$repo_dir" rev-parse -q --verify HEAD >/dev/null 2>&1; then
      log_repo_status "$timestamp" "$repo_name" "RECLONED_BUT_EMPTY" "$repo_dir" "Repo recloned but HEAD is still unborn"
      rm -f "$fetch_err_file" "$pull_err_file"
      return 0
    fi

    log_repo_status "$timestamp" "$repo_name" "RECLONED" "$repo_dir" "Empty repo deleted and recloned from origin"
  fi

  if ! GIT_TERMINAL_PROMPT=0 git -C "$repo_dir" fetch --all --prune --quiet 2>"$fetch_err_file"; then
    fetch_err="$(tail -n 20 "$fetch_err_file" 2>/dev/null | tr "\n" " " | sed -E "s/[[:space:]]+/ /g; s/^ +//; s/ +$//" || true)"
    log_repo_status "$timestamp" "$repo_name" "FETCH_FAILED" "$repo_dir" "${fetch_err:-git fetch failed}"
    rm -f "$fetch_err_file" "$pull_err_file"
    return 1
  fi

  if [[ -n "$(git -C "$repo_dir" status --porcelain 2>/dev/null || true)" ]]; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_PULL_DIRTY" "$repo_dir" "Skipped pull because local uncommitted changes exist"
    rm -f "$fetch_err_file" "$pull_err_file"
    return 0
  fi

  current_branch="$(git -C "$repo_dir" symbolic-ref --short -q HEAD 2>/dev/null || true)"
  upstream_ref=""
  if [[ -n "$current_branch" ]]; then
    upstream_ref="$(git -C "$repo_dir" rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>/dev/null || true)"
  fi

  if [[ -z "$current_branch" || -z "$upstream_ref" ]]; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_PULL_NO_UPSTREAM" "$repo_dir" "Skipped pull because branch/upstream is missing"
    rm -f "$fetch_err_file" "$pull_err_file"
    return 0
  fi

  if ! GIT_TERMINAL_PROMPT=0 git -C "$repo_dir" pull --ff-only --quiet 2>"$pull_err_file"; then
    pull_err="$(tail -n 20 "$pull_err_file" 2>/dev/null | tr "\n" " " | sed -E "s/[[:space:]]+/ /g; s/^ +//; s/ +$//" || true)"
    log_repo_status "$timestamp" "$repo_name" "PULL_FAILED" "$repo_dir" "${pull_err:-git pull failed}"
    rm -f "$fetch_err_file" "$pull_err_file"
    return 1
  fi

  log_repo_status "$timestamp" "$repo_name" "SYNCED" "$repo_dir" "Fetch and pull completed"
  rm -f "$fetch_err_file" "$pull_err_file"
  return 0
}

export -f append_line_locked
export -f append_report
export -f append_failure
export -f log_repo_status
export -f sync_repo
export ROOT_DIR ROOT_LABEL REPORT_FILE FAILURES_FILE REPORT_LOCK_FILE FAILURES_LOCK_FILE

{
  echo "Git sync report"
  echo "Generated: $(date -Iseconds)"
  echo "Root: $ROOT_DIR"
  echo "Concurrency: $CONCURRENCY"
  echo "Format: timestamp<TAB>repo<TAB>status<TAB>path<TAB>detail"
  echo "------------------------------------------------------------------"
} > "$REPORT_FILE"

{
  echo "Git sync failures/skipped-pull report"
  echo "Generated: $(date -Iseconds)"
  echo "Root: $ROOT_DIR"
  echo "Format: timestamp<TAB>repo<TAB>status<TAB>path<TAB>detail"
  echo "------------------------------------------------------------------"
} > "$FAILURES_FILE"

overall_exit=0

if [[ ! -d "$ROOT_DIR" ]]; then
  echo "Root directory not found: $ROOT_DIR" >&2
  exit 1
fi

if ! find "$ROOT_DIR" -mindepth 1 -maxdepth 1 -type d -print0 \
  | xargs -0 -P "$CONCURRENCY" -I {} bash -c 'set -euo pipefail; sync_repo "$1"' _ {}; then
  overall_exit=1
fi

status_counts="$(awk -F "\t" 'NF>=3 {c[$3]++} END{for (k in c) printf "%s=%d ", k, c[k]}' "$REPORT_FILE")"
fail_count="$(awk -F "\t" 'NF>=3 {c++} END{print c+0}' "$FAILURES_FILE")"

printf -v summary_counts_line "%s\t%s\t%s\t%s\t%s" "SUMMARY" "$ROOT_LABEL" "COUNTS" "$ROOT_DIR" "${status_counts:-none}"
printf -v summary_fail_line "%s\t%s\t%s\t%s\t%s" "SUMMARY" "$ROOT_LABEL" "FAILED_OR_SKIPPED_PULL" "$ROOT_DIR" "${fail_count}"

append_report "------------------------------------------------------------------"
append_report "$summary_counts_line"
append_report "$summary_fail_line"

append_failure "------------------------------------------------------------------"
append_failure "$summary_fail_line"

echo "Report: $REPORT_FILE"
echo "Failures: $FAILURES_FILE"
exit "$overall_exit"
