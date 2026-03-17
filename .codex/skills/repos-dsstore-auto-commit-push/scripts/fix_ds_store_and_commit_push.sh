#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOTS="${TARGET_ROOTS:-${HOME}/Downloads/lambdas,${HOME}/Downloads/projects}"
CONCURRENCY="${CONCURRENCY:-8}"
REPORT_DIR="${REPORT_DIR:-${HOME}/Downloads/_dsstore_skill_reports}"
COMMIT_MESSAGE="${COMMIT_MESSAGE:-chore(gitignore): ignore .DS_Store}"
DRY_RUN="${DRY_RUN:-0}"

REPORT_FILE="$(mktemp "${TMPDIR:-/tmp}/dsstore_skill_report.XXXXXX")"
FAILURES_FILE="${REPORT_DIR}/dsstore_skill_failures.txt"
REPORT_LOCK_FILE="${REPORT_FILE}.lock"
FAILURES_LOCK_FILE="${FAILURES_FILE}.lock"
REPO_LIST_FILE="$(mktemp)"
REPO_LIST_NULL_FILE="$(mktemp)"
ROOT_WARNINGS_FILE="$(mktemp)"

mkdir -p "$REPORT_DIR"
find "$REPORT_DIR" -maxdepth 1 -type f \( -name 'dsstore_skill_report_*' -o -name 'dsstore_skill_failures_*' -o -name 'dsstore_skill_failures.txt' -o -name '*.lock' \) -delete 2>/dev/null || true
trap 'rm -f "$REPO_LIST_FILE" "$REPO_LIST_NULL_FILE" "$ROOT_WARNINGS_FILE" "$REPORT_FILE" "$REPORT_LOCK_FILE" "$FAILURES_LOCK_FILE"' EXIT

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
    CANDIDATE_FIXED_COMMITTED_PUSHED|SKIPPED_CLEAN)
      ;;
    *)
      append_failure "$line"
      ;;
  esac
}

path_is_ds_store() {
  local p="$1"
  [[ "$p" == ".DS_Store" || "$p" == */".DS_Store" ]]
}

extract_status_path() {
  local line="$1"
  local path="${line#???}"
  if [[ "$path" == *" -> "* ]]; then
    path="${path##* -> }"
  fi
  printf "%s" "$path"
}

compact_error_file() {
  local source_file="$1"
  tail -n 20 "$source_file" | tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g; s/^ +//; s/ +$//' || true
}

extract_first_https_git_url() {
  local source_file="$1"
  grep -Eo 'https://[^[:space:]]+\.git' "$source_file" | head -n 1 || true
}

build_repo_list() {
  local roots_csv="$1"
  local roots="" root=""

  roots="$roots_csv"
  OLDIFS="$IFS"
  IFS=","
  set -- $roots
  IFS="$OLDIFS"

  for root in "$@"; do
    root="$(printf "%s" "$root" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
    [[ -z "$root" ]] && continue

    if [[ ! -d "$root" ]]; then
      printf "ROOT_NOT_FOUND\t%s\n" "$root" >> "$ROOT_WARNINGS_FILE"
      continue
    fi

    find "$root" -type d -name .git -prune -print 2>/dev/null | sed 's#/\.git$##' >> "$REPO_LIST_FILE"
  done

  if [[ -s "$REPO_LIST_FILE" ]]; then
    sort -u "$REPO_LIST_FILE" > "${REPO_LIST_FILE}.sorted"
    mv "${REPO_LIST_FILE}.sorted" "$REPO_LIST_FILE"
    while IFS= read -r repo; do
      printf "%s\0" "$repo" >> "$REPO_LIST_NULL_FILE"
    done < "$REPO_LIST_FILE"
  fi
}

process_repo() {
  local repo="$1"
  local timestamp repo_name status lines line
  local xy path only_ds tracked_paths tracked_unique
  local gitignore changed_gitignore
  local post_status post_line post_path safe_paths
  local commit_err push_err

  timestamp="$(date -Iseconds)"
  repo_name="$(basename "$repo")"

  if ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    log_repo_status "$timestamp" "$repo_name" "REPO_SCAN_FAILED" "$repo" "Not a git work tree"
    return 1
  fi

  if [[ "$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null || true)" != "$repo" ]]; then
    log_repo_status "$timestamp" "$repo_name" "REPO_SCAN_FAILED" "$repo" "Path is not git toplevel"
    return 1
  fi

  status="$(git -C "$repo" status --porcelain 2>/dev/null || true)"
  if [[ -z "$status" ]]; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_CLEAN" "$repo" "Working tree is clean"
    return 0
  fi

  only_ds=1
  tracked_paths=""
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    path="$(extract_status_path "$line")"
    if ! path_is_ds_store "$path"; then
      only_ds=0
      break
    fi

    xy="${line:0:2}"
    if [[ "$xy" != "??" ]]; then
      tracked_paths="${tracked_paths}${path}"$'\n'
    fi
  done <<EOF
$status
EOF

  if [[ "$only_ds" != "1" ]]; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_NON_DS_CHANGES" "$repo" "Repository has non-.DS_Store uncommitted changes"
    return 0
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    log_repo_status "$timestamp" "$repo_name" "DRY_RUN_CANDIDATE" "$repo" "Would update .gitignore, untrack tracked .DS_Store, then commit and push"
    return 0
  fi

  gitignore="$repo/.gitignore"
  changed_gitignore=0

  if [[ ! -f "$gitignore" ]]; then
    : > "$gitignore"
    changed_gitignore=1
  fi

  if ! rg -n '^\.DS_Store$' "$gitignore" >/dev/null 2>&1; then
    if [[ -s "$gitignore" ]] && [[ "$(tail -c 1 "$gitignore" 2>/dev/null || true)" != "" ]]; then
      printf "\n" >> "$gitignore"
    fi
    printf ".DS_Store\n" >> "$gitignore"
    changed_gitignore=1
  fi

  if [[ "$changed_gitignore" == "1" ]]; then
    git -C "$repo" add .gitignore >/dev/null 2>&1 || {
      log_repo_status "$timestamp" "$repo_name" "REPO_SCAN_FAILED" "$repo" "Failed to stage .gitignore"
      return 1
    }
  fi

  if [[ -n "$tracked_paths" ]]; then
    tracked_unique="$(printf "%s" "$tracked_paths" | sed '/^$/d' | sort -u || true)"
    while IFS= read -r path; do
      [[ -z "$path" ]] && continue
      if ! git -C "$repo" rm --cached --quiet -- "$path" >/dev/null 2>&1; then
        log_repo_status "$timestamp" "$repo_name" "REPO_SCAN_FAILED" "$repo" "Failed to untrack $path"
        return 1
      fi
    done <<EOF
$tracked_unique
EOF
  fi

  post_status="$(git -C "$repo" status --porcelain 2>/dev/null || true)"
  if [[ -z "$post_status" ]]; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_NOTHING_TO_COMMIT" "$repo" "No changes left after fix"
    return 0
  fi

  safe_paths=1
  while IFS= read -r post_line; do
    [[ -z "$post_line" ]] && continue
    post_path="$(extract_status_path "$post_line")"
    if [[ "$post_path" != ".gitignore" ]] && ! path_is_ds_store "$post_path"; then
      safe_paths=0
      break
    fi
  done <<EOF
$post_status
EOF

  if [[ "$safe_paths" != "1" ]]; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_SAFETY_UNEXPECTED_CHANGES" "$repo" "Unexpected paths found after fix; skipping commit/push"
    return 0
  fi

  if git -C "$repo" diff --cached --quiet >/dev/null 2>&1; then
    log_repo_status "$timestamp" "$repo_name" "SKIPPED_NOTHING_TO_COMMIT" "$repo" "No staged changes for commit"
    return 0
  fi

  commit_err="$(mktemp)"
  push_err="$(mktemp)"

  if ! git -C "$repo" commit -m "$COMMIT_MESSAGE" --quiet 2>"$commit_err"; then
    log_repo_status "$timestamp" "$repo_name" "COMMIT_FAILED" "$repo" "$(compact_error_file "$commit_err")"
    rm -f "$commit_err" "$push_err"
    return 1
  fi

  if ! git -C "$repo" push --quiet 2>"$push_err"; then
    local push_raw_error recovery_notes did_recovery new_origin_url pull_err
    push_raw_error="$(compact_error_file "$push_err")"
    recovery_notes=""
    did_recovery=0

    if rg -qi 'repository moved|new location' "$push_err"; then
      new_origin_url="$(extract_first_https_git_url "$push_err")"
      if [[ -n "$new_origin_url" ]]; then
        if git -C "$repo" remote set-url origin "$new_origin_url" >/dev/null 2>&1; then
          did_recovery=1
          recovery_notes="${recovery_notes}updated origin URL; "
        else
          recovery_notes="${recovery_notes}failed to update origin URL; "
        fi
      fi
    fi

    if rg -qi 'non-fast-forward|tip of your current branch is behind|fetch first|cannot lock ref' "$push_err"; then
      pull_err="$(mktemp)"
      if git -C "$repo" pull --rebase --autostash --quiet 2>"$pull_err"; then
        did_recovery=1
        recovery_notes="${recovery_notes}pull --rebase succeeded; "
      else
        recovery_notes="${recovery_notes}pull --rebase failed: $(compact_error_file "$pull_err"); "
      fi
      rm -f "$pull_err"
    fi

    if [[ "$did_recovery" == "1" ]]; then
      if git -C "$repo" push --quiet 2>"$push_err"; then
        rm -f "$commit_err" "$push_err"
        log_repo_status "$timestamp" "$repo_name" "CANDIDATE_FIXED_COMMITTED_PUSHED" "$repo" "Applied DS_Store fix and pushed successfully (recovery: ${recovery_notes% ;})"
        return 0
      fi
      recovery_notes="${recovery_notes}retry push failed: $(compact_error_file "$push_err"); "
    fi

    log_repo_status "$timestamp" "$repo_name" "PUSH_FAILED" "$repo" "${push_raw_error}${recovery_notes:+ | recovery: ${recovery_notes}}"
    rm -f "$commit_err" "$push_err"
    return 1
  fi

  rm -f "$commit_err" "$push_err"
  log_repo_status "$timestamp" "$repo_name" "CANDIDATE_FIXED_COMMITTED_PUSHED" "$repo" "Applied DS_Store fix and pushed successfully"
  return 0
}

export -f append_line_locked
export -f append_report
export -f append_failure
export -f log_repo_status
export -f path_is_ds_store
export -f extract_status_path
export -f compact_error_file
export -f extract_first_https_git_url
export -f process_repo
export REPORT_FILE FAILURES_FILE REPORT_LOCK_FILE FAILURES_LOCK_FILE COMMIT_MESSAGE DRY_RUN

{
  echo "DS_Store auto-fix commit/push report"
  echo "Generated: $(date -Iseconds)"
  echo "Target roots: $TARGET_ROOTS"
  echo "Concurrency: $CONCURRENCY"
  echo "Dry run: $DRY_RUN"
  echo "Format: timestamp<TAB>repo<TAB>status<TAB>path<TAB>detail"
  echo "------------------------------------------------------------------"
} > "$REPORT_FILE"

{
  echo "DS_Store auto-fix failures/skip report"
  echo "Generated: $(date -Iseconds)"
  echo "Target roots: $TARGET_ROOTS"
  echo "Format: timestamp<TAB>repo<TAB>status<TAB>path<TAB>detail"
  echo "------------------------------------------------------------------"
} > "$FAILURES_FILE"

build_repo_list "$TARGET_ROOTS"

if [[ -s "$ROOT_WARNINGS_FILE" ]]; then
  while IFS= read -r warning; do
    append_failure "$warning"
  done < "$ROOT_WARNINGS_FILE"
fi

if [[ ! -s "$REPO_LIST_FILE" ]]; then
  append_report "SUMMARY\trepos-dsstore\tNO_REPOS_FOUND\t-\tNo repositories discovered under target roots"
  append_failure "SUMMARY\trepos-dsstore\tNO_REPOS_FOUND\t-\tNo repositories discovered under target roots"
  echo "Failures: $FAILURES_FILE"
  exit 0
fi

overall_exit=0

if ! xargs -0 -I {} -P "$CONCURRENCY" bash -c 'set -euo pipefail; process_repo "$1"' _ {} < "$REPO_LIST_NULL_FILE"; then
  overall_exit=1
fi

status_counts="$(awk -F "\t" 'NF>=3 && $1!="SUMMARY" {c[$3]++} END{for (k in c) printf "%s=%d ", k, c[k]}' "$REPORT_FILE")"
failure_count="$(awk -F "\t" 'NF>=3 && $1!="SUMMARY" {c++} END{print c+0}' "$FAILURES_FILE")"

printf -v summary_counts_line "%s\t%s\t%s\t%s\t%s" "SUMMARY" "repos-dsstore" "COUNTS" "-" "${status_counts:-none}"
printf -v summary_fail_line "%s\t%s\t%s\t%s\t%s" "SUMMARY" "repos-dsstore" "FAILURES_OR_SKIPS" "-" "${failure_count}"

append_report "------------------------------------------------------------------"
append_report "$summary_counts_line"
append_report "$summary_fail_line"

append_failure "------------------------------------------------------------------"
append_failure "$summary_fail_line"

echo "Failures: $FAILURES_FILE"
exit "$overall_exit"
