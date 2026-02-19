#!/usr/bin/env bash
set -euo pipefail

# Override via env:
#   CONCURRENCY=20 MAX_DEPTH=2 REPORT_FILE=./report.txt WAIT_ON_EXIT=0 ./gitfetchallconcurency_improved.sh /path
CONCURRENCY="${CONCURRENCY:-40}"
MAX_DEPTH="${MAX_DEPTH:-1}"

RUN_ID="${RUN_ID:-$(date +%Y%m%d_%H%M%S)}"

# Human-readable text report (CHANGED repos + detailed failures)
REPORT_FILE="${REPORT_FILE:-./git_sync_report_${RUN_ID}.txt}"
REPORT_LOCK="${REPORT_LOCK:-${REPORT_FILE}.lock}"

# Failures (single-line reasons per repo) + summarized failures report
FAIL_LOG_FILE="${FAIL_LOG_FILE:-./git_sync_failures_${RUN_ID}.tsv}"
FAIL_LOCK="${FAIL_LOCK:-${FAIL_LOG_FILE}.lock}"
FAIL_REPORT_FILE="${FAIL_REPORT_FILE:-./git_sync_failures_${RUN_ID}.txt}"

# If a repo has no commits locally (HEAD is unborn), delete and clone again.
RECLONE_EMPTY_REPOS="${RECLONE_EMPTY_REPOS:-1}"
RECLONE_REMOTE_NAME="${RECLONE_REMOTE_NAME:-origin}"
CLONE_FLAGS="${CLONE_FLAGS:---quiet}"

# Pause at the end so a terminal window doesn’t auto-close (set WAIT_ON_EXIT=0 to disable)
WAIT_ON_EXIT="${WAIT_ON_EXIT:-1}"

ROOTS=("$@")
if [[ "${#ROOTS[@]}" -eq 0 ]]; then
  ROOTS=(".")
fi

append_report_block() {
  local block_text="$1"
  (
    flock -x 200
    printf '%s\n' "$block_text" >> "$REPORT_FILE"
  ) 200>"$REPORT_LOCK"
}

append_failure_entry() {
  local timestamp="$1"
  local repo_name="$2"
  local repo_dir="$3"
  local status="$4"
  local reason="$5"

  local reason_one_line
  reason_one_line="$(printf '%s' "$reason" | tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g; s/^ +//; s/ +$//')"

  (
    flock -x 201
    printf '%s\t%s\t%s\t%s\t%s\n' "$timestamp" "$repo_name" "$repo_dir" "$status" "$reason_one_line" >> "$FAIL_LOG_FILE"
  ) 201>"$FAIL_LOCK"
}

remote_refs_snapshot_to_file() {
  local repo_dir="$1"
  local out_file="$2"
  git -C "$repo_dir" for-each-ref --format='%(refname) %(objectname)' refs/remotes 2>/dev/null \
    | sort > "$out_file" || :
}

count_remote_ref_changes() {
  local before_file="$1"
  local after_file="$2"

  # prints: total<TAB>changed<TAB>added<TAB>deleted
  awk '
    NR==FNR { before[$1]=$2; next }
    { after[$1]=$2 }
    END {
      changed=0; added=0; deleted=0;
      for (k in before) {
        if (!(k in after)) deleted++;
        else if (before[k] != after[k]) changed++;
      }
      for (k in after) {
        if (!(k in before)) added++;
      }
      total = changed + added + deleted;
      printf "%d\t%d\t%d\t%d", total, changed, added, deleted;
    }
  ' "$before_file" "$after_file"
}

reclone_empty_repo_if_needed() {
  local repo_dir="$1"
  local repo_name="$2"
  local timestamp="$3"

  if [[ "$RECLONE_EMPTY_REPOS" != "1" ]]; then
    return 0
  fi

  # Empty/unborn HEAD -> treat as empty clone/corruption and reclone.
  if git -C "$repo_dir" rev-parse -q --verify HEAD &>/dev/null; then
    return 0
  fi

  local remote_name remote_url
  remote_name="$RECLONE_REMOTE_NAME"
  remote_url=""

  if git -C "$repo_dir" remote get-url "$remote_name" &>/dev/null; then
    remote_url="$(git -C "$repo_dir" remote get-url "$remote_name" 2>/dev/null || true)"
  else
    remote_name="$(git -C "$repo_dir" remote 2>/dev/null | head -n 1 || true)"
    if [[ -n "$remote_name" ]]; then
      remote_url="$(git -C "$repo_dir" remote get-url "$remote_name" 2>/dev/null || true)"
    fi
  fi

  if [[ -z "$remote_url" ]]; then
    append_report_block "$(
      cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: RECLONE_FAILED
Reason: EMPTY_LOCAL_REPO
Remote: NONE
Error:
No remote URL found (cannot reclone).
------------------------------------------------------------
__BLOCK__
    )"

    append_failure_entry "$timestamp" "$repo_name" "$repo_dir" "RECLONE_FAILED" "Empty local repo and no remote URL found"
    echo "✗ ${repo_name} (EMPTY REPO, NO REMOTE URL)" >&2
    return 1
  fi

  local -a tmp_files=()
  local lsremote_out lsremote_err rm_err clone_err
  lsremote_out="$(mktemp)"; tmp_files+=("$lsremote_out")
  lsremote_err="$(mktemp)"; tmp_files+=("$lsremote_err")
  rm_err="$(mktemp)"; tmp_files+=("$rm_err")
  clone_err="$(mktemp)"; tmp_files+=("$clone_err")

  # If we can determine that the REMOTE is empty (no heads), don't loop endlessly.
  if GIT_TERMINAL_PROMPT=0 git ls-remote --heads "$remote_url" >"$lsremote_out" 2>"$lsremote_err"; then
    if [[ ! -s "$lsremote_out" ]]; then
      append_report_block "$(
        cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: REMOTE_EMPTY
Reason: EMPTY_LOCAL_REPO
Remote: ${remote_url}
Note: Remote has no heads; skipping reclone.
------------------------------------------------------------
__BLOCK__
      )"
      echo "↷ ${repo_name} (remote empty; skipping reclone)"
      rm -f "${tmp_files[@]}" || true
      return 0
    fi
  fi

  echo "↻ ${repo_name} (empty repo detected; re-cloning...)"

  if ! rm -rf "$repo_dir" 2>"$rm_err"; then
    local rm_err_tail
    rm_err_tail="$(tail -n 30 "$rm_err" | sed 's/[[:space:]]\+$//' || true)"

    append_report_block "$(
      cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: RECLONE_FAILED
Reason: EMPTY_LOCAL_REPO
Remote: ${remote_url}
Error:
Failed to delete existing directory before reclone.
${rm_err_tail:-<no stderr>}
------------------------------------------------------------
__BLOCK__
    )"

    append_failure_entry "$timestamp" "$repo_name" "$repo_dir" "RECLONE_FAILED" "${rm_err_tail:-Failed to delete existing directory}"
    echo "✗ ${repo_name} (RECLONE FAILED: DELETE ERROR)" >&2
    rm -f "${tmp_files[@]}" || true
    return 1
  fi
  if ! GIT_TERMINAL_PROMPT=0 git clone $CLONE_FLAGS "$remote_url" "$repo_dir" 2>"$clone_err"; then
    local clone_err_tail
    clone_err_tail="$(tail -n 30 "$clone_err" | sed 's/[[:space:]]\+$//' || true)"

    append_report_block "$(
      cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: RECLONE_FAILED
Reason: EMPTY_LOCAL_REPO
Remote: ${remote_url}
Error:
${clone_err_tail:-<no stderr>}
------------------------------------------------------------
__BLOCK__
    )"

    append_failure_entry "$timestamp" "$repo_name" "$repo_dir" "RECLONE_FAILED" "${clone_err_tail:-Clone failed (no stderr)}"
    echo "✗ ${repo_name} (RECLONE FAILED)" >&2
    rm -f "${tmp_files[@]}" || true
    return 1
  fi

  # If it is still empty after clone, treat it as remote-empty or unusual state.
  if ! git -C "$repo_dir" rev-parse -q --verify HEAD &>/dev/null; then
    append_report_block "$(
      cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: RECLONED_BUT_EMPTY
Reason: EMPTY_LOCAL_REPO
Remote: ${remote_url}
Note: Clone succeeded, but HEAD is still unborn (remote may be empty or default branch is not set).
------------------------------------------------------------
__BLOCK__
    )"
    echo "✓ ${repo_name} (re-cloned; still empty)"
    rm -f "${tmp_files[@]}" || true
    return 0
  fi

  append_report_block "$(
    cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: RECLONED
Reason: EMPTY_LOCAL_REPO
Remote: ${remote_url}
------------------------------------------------------------
__BLOCK__
  )"

  echo "✓ ${repo_name} (re-cloned)"
  rm -f "${tmp_files[@]}" || true
  return 0
}

sync_repo() {
  local repo_dir="$1"
  local repo_name timestamp

  if ! git -C "$repo_dir" rev-parse --is-inside-work-tree &>/dev/null; then
    return 0
  fi

  # Only operate on actual repo root; prevents accidental reclone inside subdirectories.
  local toplevel
  toplevel="$(git -C "$repo_dir" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -z "$toplevel" || "$toplevel" != "$repo_dir" ]]; then
    return 0
  fi

  repo_name="$(basename "$repo_dir")"
  timestamp="$(date -Iseconds)"

  # Empty repo handling
  if ! reclone_empty_repo_if_needed "$repo_dir" "$repo_name" "$timestamp"; then
    return 1
  fi

  local current_branch upstream_ref
  current_branch="$(git -C "$repo_dir" symbolic-ref --short -q HEAD 2>/dev/null || true)"
  upstream_ref=""
  if [[ -n "$current_branch" ]]; then
    upstream_ref="$(git -C "$repo_dir" rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>/dev/null || true)"
  fi

  local before_head after_head
  before_head="$(git -C "$repo_dir" rev-parse -q HEAD 2>/dev/null || true)"
  after_head="$before_head"

  local before_upstream after_upstream
  before_upstream=""
  after_upstream=""
  if [[ -n "$upstream_ref" ]]; then
    before_upstream="$(git -C "$repo_dir" rev-parse -q "@{u}" 2>/dev/null || true)"
  fi

  local -a tmp_files=()
  local before_remotes_file after_remotes_file fetch_err_file pull_err_file
  before_remotes_file="$(mktemp)"; tmp_files+=("$before_remotes_file")
  after_remotes_file="$(mktemp)"; tmp_files+=("$after_remotes_file")
  fetch_err_file="$(mktemp)"; tmp_files+=("$fetch_err_file")
  pull_err_file="$(mktemp)"; tmp_files+=("$pull_err_file")

  cleanup() { rm -f "${tmp_files[@]}" 2>/dev/null || true; }
  trap cleanup RETURN

  remote_refs_snapshot_to_file "$repo_dir" "$before_remotes_file"

  echo "→ ${repo_name} (fetching...)"
  if ! GIT_TERMINAL_PROMPT=0 git -C "$repo_dir" fetch --all --prune --quiet 2>"$fetch_err_file"; then
    local fetch_err
    fetch_err="$(tail -n 30 "$fetch_err_file" | sed 's/[[:space:]]\+$//' || true)"

    append_report_block "$(
      cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: FETCH_FAILED
Branch: ${current_branch:-DETACHED}
Upstream: ${upstream_ref:-NONE}
Error:
${fetch_err:-<no stderr>}
------------------------------------------------------------
__BLOCK__
    )"

    append_failure_entry "$timestamp" "$repo_name" "$repo_dir" "FETCH_FAILED" "${fetch_err:-Fetch failed (no stderr)}"
    echo "✗ ${repo_name} (FETCH FAILED)" >&2
    return 1
  fi

  remote_refs_snapshot_to_file "$repo_dir" "$after_remotes_file"

  local fetch_counts fetch_total fetch_changed fetch_added fetch_deleted
  fetch_counts="$(count_remote_ref_changes "$before_remotes_file" "$after_remotes_file")"
  fetch_total="$(cut -f1 <<<"$fetch_counts")"
  fetch_changed="$(cut -f2 <<<"$fetch_counts")"
  fetch_added="$(cut -f3 <<<"$fetch_counts")"
  fetch_deleted="$(cut -f4 <<<"$fetch_counts")"

  local upstream_new_commits="0"
  if [[ -n "$upstream_ref" ]]; then
    after_upstream="$(git -C "$repo_dir" rev-parse -q "@{u}" 2>/dev/null || true)"
    if [[ -n "$before_upstream" && -n "$after_upstream" && "$before_upstream" != "$after_upstream" ]]; then
      upstream_new_commits="$(git -C "$repo_dir" rev-list --count "${before_upstream}..${after_upstream}" 2>/dev/null || echo 0)"
    fi
  fi

  local pull_new_commits="0"
  local pull_attempted="0"
  if [[ -n "$current_branch" && -n "$upstream_ref" ]]; then
    pull_attempted="1"
    echo "→ ${repo_name} (pulling...)"
    if ! GIT_TERMINAL_PROMPT=0 git -C "$repo_dir" pull --ff-only --quiet 2>"$pull_err_file"; then
      local pull_err
      pull_err="$(tail -n 30 "$pull_err_file" | sed 's/[[:space:]]\+$//' || true)"

      append_report_block "$(
        cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: PULL_FAILED
Branch: ${current_branch:-DETACHED}
Upstream: ${upstream_ref:-NONE}
Fetch changes (refs/remotes): total=${fetch_total} (changed=${fetch_changed}, added=${fetch_added}, deleted=${fetch_deleted})
Upstream new commits (after fetch): ${upstream_new_commits}
Error:
${pull_err:-<no stderr>}
------------------------------------------------------------
__BLOCK__
      )"

      append_failure_entry "$timestamp" "$repo_name" "$repo_dir" "PULL_FAILED" "${pull_err:-Pull failed (no stderr)}"
      echo "✗ ${repo_name} (PULL FAILED)" >&2
      return 1
    fi

    after_head="$(git -C "$repo_dir" rev-parse -q HEAD 2>/dev/null || true)"
    if [[ -n "$before_head" && -n "$after_head" && "$before_head" != "$after_head" ]]; then
      pull_new_commits="$(git -C "$repo_dir" rev-list --count "${before_head}..${after_head}" 2>/dev/null || echo 0)"
    fi
  fi

  # Write report ONLY if changed (fetch refs changed OR upstream moved OR pull advanced HEAD)
  if [[ "$fetch_total" -gt 0 || "$upstream_new_commits" != "0" || "$pull_new_commits" != "0" ]]; then
    append_report_block "$(
      cat <<__BLOCK__
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: CHANGED
Branch: ${current_branch:-DETACHED}
Upstream: ${upstream_ref:-NONE}
Fetch changes (refs/remotes): total=${fetch_total} (changed=${fetch_changed}, added=${fetch_added}, deleted=${fetch_deleted})
Upstream new commits (after fetch): ${upstream_new_commits}
Pull attempted: ${pull_attempted}
Pulled new commits (local HEAD advanced): ${pull_new_commits}
------------------------------------------------------------
__BLOCK__
    )"
  fi

  echo "✓ ${repo_name} (done)"
}

generate_failures_report() {
  local now total=0
  now="$(date -Iseconds)"

  if [[ -f "$FAIL_LOG_FILE" ]]; then
    local lines
    lines="$(wc -l < "$FAIL_LOG_FILE" | tr -d ' ')"
    if [[ "$lines" =~ ^[0-9]+$ && "$lines" -gt 1 ]]; then
      total=$((lines - 1))
    fi
  fi

  local fetch_failed=0 pull_failed=0 reclone_failed=0
  if [[ "$total" -gt 0 ]]; then
    fetch_failed="$(awk -F'\t' 'NR>1 && $4=="FETCH_FAILED" {c++} END{print c+0}' "$FAIL_LOG_FILE")"
    pull_failed="$(awk -F'\t' 'NR>1 && $4=="PULL_FAILED" {c++} END{print c+0}' "$FAIL_LOG_FILE")"
    reclone_failed="$(awk -F'\t' 'NR>1 && $4=="RECLONE_FAILED" {c++} END{print c+0}' "$FAIL_LOG_FILE")"
  fi

  {
    printf 'Git sync failures summary\n'
    printf 'Generated: %s\n' "$now"
    printf 'Total failures: %s\n' "$total"
    printf 'By type: FETCH_FAILED=%s, PULL_FAILED=%s, RECLONE_FAILED=%s\n' "$fetch_failed" "$pull_failed" "$reclone_failed"
    printf '============================================================\n'

    if [[ "$total" -eq 0 ]]; then
      printf 'No failures.\n'
    else
      printf 'Timestamp\tRepo\tStatus\tPath\tReason\n'
      awk -F'\t' 'NR>1 {printf "%s\t%s\t%s\t%s\t%s\n", $1, $2, $4, $3, $5}' "$FAIL_LOG_FILE"
    fi
  } > "$FAIL_REPORT_FILE"
}

export -f sync_repo
export -f reclone_empty_repo_if_needed
export -f append_report_block
export -f append_failure_entry
export -f remote_refs_snapshot_to_file
export -f count_remote_ref_changes
export REPORT_FILE REPORT_LOCK FAIL_LOG_FILE FAIL_LOCK FAIL_REPORT_FILE RECLONE_EMPTY_REPOS RECLONE_REMOTE_NAME CLONE_FLAGS

mkdir -p "$(dirname "$REPORT_FILE")"
mkdir -p "$(dirname "$FAIL_LOG_FILE")"

{
  printf 'Git sync report\n'
  printf 'Generated: %s\n' "$(date -Iseconds)"
  printf 'Roots: %s\n' "${ROOTS[*]}"
  printf 'Max depth: %s | Concurrency: %s\n' "$MAX_DEPTH" "$CONCURRENCY"
  printf 'This report includes:\n'
  printf '  - CHANGED repos (fetch/pull caused updates)\n'
  printf '  - FAILED repos (fetch/pull/reclone failures, with details)\n'
  printf '  - RECLONED repos (empty local repo was re-cloned)\n'
  printf '============================================================\n'
} > "$REPORT_FILE"

# Initialize failures log
{
  printf 'timestamp\trepo\tpath\tstatus\treason\n'
} > "$FAIL_LOG_FILE"

overall_exit=0

for root in "${ROOTS[@]}"; do
  if [[ ! -d "$root" ]]; then
    echo "Directory not found: $root" >&2
    overall_exit=1
    continue
  fi

  echo "Processing root: $root (max depth: $MAX_DEPTH, concurrency: $CONCURRENCY)"
  if ! find "$root" -mindepth 1 -maxdepth "$MAX_DEPTH" -type d -print0 \
    | xargs -0 -P "$CONCURRENCY" -I {} bash -c 'set -euo pipefail; sync_repo "$1"' _ {}; then
    overall_exit=1
  fi
done

generate_failures_report

echo
echo "All done!"
echo "Text report written to: $REPORT_FILE"
echo "Failures summary written to: $FAIL_REPORT_FILE"

if [[ "$WAIT_ON_EXIT" == "1" && -t 0 ]]; then
  echo
  read -r -p "Finished (exit code: ${overall_exit}). Press Enter to close..." _
fi

exit "$overall_exit"
