#!/usr/bin/env bash
set -euo pipefail

# Override via env:
#   CONCURRENCY=20 MAX_DEPTH=2 REPORT_FILE=./report.txt WAIT_ON_EXIT=0 ./gitfetchallconcurency.sh /path
CONCURRENCY="${CONCURRENCY:-10}"
MAX_DEPTH="${MAX_DEPTH:-1}"

# Human-readable text report
REPORT_FILE="${REPORT_FILE:-./git_sync_report_$(date +%Y%m%d_%H%M%S).txt}"
REPORT_LOCK="${REPORT_LOCK:-${REPORT_FILE}.lock}"

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

sync_repo() {
  local repo_dir="$1"
  local repo_name timestamp
  repo_name="$(basename "$repo_dir")"
  timestamp="$(date -Iseconds)"

  if ! git -C "$repo_dir" rev-parse --is-inside-work-tree &>/dev/null; then
    return 0
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

  local before_remotes_file after_remotes_file fetch_err_file pull_err_file
  before_remotes_file="$(mktemp)"
  after_remotes_file="$(mktemp)"
  fetch_err_file="$(mktemp)"
  pull_err_file="$(mktemp)"
  trap 'rm -f "$before_remotes_file" "$after_remotes_file" "$fetch_err_file" "$pull_err_file"' RETURN

  remote_refs_snapshot_to_file "$repo_dir" "$before_remotes_file"

  echo "→ ${repo_name} (fetching...)"
  if ! GIT_TERMINAL_PROMPT=0 git -C "$repo_dir" fetch --all --prune --quiet 2>"$fetch_err_file"; then
    local fetch_err
    fetch_err="$(tail -n 20 "$fetch_err_file" | sed 's/[[:space:]]\+$//' || true)"

    append_report_block "$(
      cat <<EOF
[$timestamp] ${repo_name}
Path: ${repo_dir}
Status: FETCH_FAILED
Branch: ${current_branch:-DETACHED}
Upstream: ${upstream_ref:-NONE}
Error:
${fetch_err:-<no stderr>}
------------------------------------------------------------
EOF
    )"

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
      pull_err="$(tail -n 20 "$pull_err_file" | sed 's/[[:space:]]\+$//' || true)"

      append_report_block "$(
        cat <<EOF
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
EOF
      )"

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
      cat <<EOF
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
EOF
    )"
  fi

  echo "✓ ${repo_name} (done)"
}

export -f sync_repo
export -f append_report_block
export -f remote_refs_snapshot_to_file
export -f count_remote_ref_changes
export REPORT_FILE REPORT_LOCK

mkdir -p "$(dirname "$REPORT_FILE")"

{
  printf 'Git sync report\n'
  printf 'Generated: %s\n' "$(date -Iseconds)"
  printf 'Roots: %s\n' "${ROOTS[*]}"
  printf 'Max depth: %s | Concurrency: %s\n' "$MAX_DEPTH" "$CONCURRENCY"
  printf 'This report includes:\n'
  printf '  - CHANGED repos (fetch/pull caused updates)\n'
  printf '  - FAILED repos (fetch or pull failed)\n'
  printf '============================================================\n'
} > "$REPORT_FILE"

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

echo
echo "All done!"
echo "Text report written to: $REPORT_FILE"

if [[ "$WAIT_ON_EXIT" == "1" && -t 0 ]]; then
  echo
  read -r -p "Finished (exit code: ${overall_exit}). Press Enter to close..." _
fi

exit "$overall_exit"

