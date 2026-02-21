#!/usr/bin/env bash
# count_projects_chars.sh
#
# Counts total characters per Git project under a root folder, excluding anything ignored by that project's .gitignore
# (via: git ls-files --exclude-standard). Writes a Markdown report file + prints a highlighted console summary.
#
# Usage:
#   ./count_projects_chars.sh
#   ./count_projects_chars.sh /path/to/root
#   ./count_projects_chars.sh /path/to/root --report /path/to/report.md
#   ./count_projects_chars.sh /path/to/root --depth 1

set -euo pipefail
IFS=$'\n\t'

ROOT_DIR=""
REPORT_PATH=""
SCAN_DEPTH="2"

print_usage() {
  cat <<EOF
Usage:
  $0 [root_dir] [--report /path/to/report.md] [--depth N]

Options:
  --report PATH   Where to write the Markdown report
  --depth N       Scan repo roots up to N directory levels under root (default: 1)
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  print_usage
  exit 0
fi

if [[ "${1:-}" != "" && "${1:-}" != --* ]]; then
  ROOT_DIR="$1"
  shift
else
  ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --report)
      REPORT_PATH="${2:-}"
      [[ -n "$REPORT_PATH" ]] || { echo "Error: --report requires a path" >&2; exit 1; }
      shift 2
      ;;
    --depth)
      SCAN_DEPTH="${2:-}"
      [[ -n "$SCAN_DEPTH" && "$SCAN_DEPTH" =~ ^[0-9]+$ && "$SCAN_DEPTH" -ge 1 ]] || {
        echo "Error: --depth requires a positive integer" >&2
        exit 1
      }
      shift 2
      ;;
    *)
      echo "Error: Unknown argument: $1" >&2
      print_usage >&2
      exit 1
      ;;
  esac
done

[[ -d "$ROOT_DIR" ]] || { echo "Error: Root folder does not exist: $ROOT_DIR" >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo "Error: git is required." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required." >&2; exit 1; }

STAMP="$(date +"%Y%m%d-%H%M%S")"
NOW_UTC="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"

if [[ -z "$REPORT_PATH" ]]; then
  REPORT_PATH="${ROOT_DIR%/}/char-count-report-${STAMP}.md"
fi

mkdir -p "$(dirname "$REPORT_PATH")"

# ---- color helpers (console only) ----
USE_COLOR=0
[[ -t 1 ]] && USE_COLOR=1
if [[ "$USE_COLOR" -eq 1 ]]; then
  BOLD="$(printf '\033[1m')"
  GREEN="$(printf '\033[32m')"
  DIM="$(printf '\033[2m')"
  RESET="$(printf '\033[0m')"
else
  BOLD=""; GREEN=""; DIM=""; RESET=""
fi

is_git_repo_root() {
  [[ -d "$1/.git" || -f "$1/.git" ]]
}

count_chars_git_repo() {
  local project_dir="$1"

  python3 - "$project_dir" <<'PY'
import os, subprocess, sys

project_dir = sys.argv[1]

p = subprocess.run(
    ["git", "-C", project_dir, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    check=False,
)
data = p.stdout
if not data:
    print(0)
    raise SystemExit(0)

paths = data.split(b"\0")
total = 0

for raw in paths:
    if not raw:
        continue
    rel = raw.decode("utf-8", errors="surrogateescape")
    full = os.path.join(project_dir, rel)

    try:
        with open(full, "rb") as f:
            blob = f.read()
    except Exception:
        continue

    try:
        total += len(blob.decode("utf-8"))
    except Exception:
        total += len(blob)

print(total)
PY
}

format_number() {
  local n="$1"
  python3 - "$n" <<'PY'
import sys
try:
  v = int(sys.argv[1])
  print(f"{v:,}")
except Exception:
  print(sys.argv[1])
PY
}

tmp_results="$(mktemp)"
cleanup() { rm -f "$tmp_results"; }
trap cleanup EXIT

declare -A seen_repos=()
repo_count=0

# Include root itself if it's a repo root
if is_git_repo_root "$ROOT_DIR"; then
  seen_repos["$ROOT_DIR"]=1
fi

max_git_depth=$((SCAN_DEPTH + 1))

# Find .git entries up to depth, convert to repo root dirs (unique)
while IFS= read -r -d '' git_entry; do
  repo_dir="$(dirname "$git_entry")"
  if [[ -z "${seen_repos["$repo_dir"]+x}" ]]; then
    seen_repos["$repo_dir"]=1
  fi
done < <(find "$ROOT_DIR" -mindepth 1 -maxdepth "$max_git_depth" \
  \( -type d -name .git -o -type f -name .git \) -print0)

# Count each repo root (but skip ROOT_DIR itself if user likely wants subprojects? keep it if present)
for repo_dir in "${!seen_repos[@]}"; do
  # Only consider repos that are within scan depth from root (repo dir depth <= SCAN_DEPTH)
  # Compute depth by counting slashes relative to root.
  rel="${repo_dir#"$ROOT_DIR"/}"
  if [[ "$repo_dir" == "$ROOT_DIR" ]]; then
    depth=0
  else
    depth=$(( $(awk -F'/' '{print NF}' <<<"$rel") ))
  fi
  [[ "$depth" -le "$SCAN_DEPTH" ]] || continue

  project_name="$(basename "$repo_dir")"
  chars="$(count_chars_git_repo "$repo_dir" | tr -d '[:space:]')"
  printf "%s\t%s\t%s\n" "$chars" "$project_name" "$repo_dir" >>"$tmp_results"
  repo_count=$((repo_count + 1))
done

if [[ "$repo_count" -eq 0 ]]; then
  echo "No Git projects found under: $ROOT_DIR (depth=$SCAN_DEPTH)"
  echo "No report written."
  exit 0
fi

# Sort descending by count
sorted="$(sort -t $'\t' -k1,1nr "$tmp_results")"

max_chars="$(printf "%s\n" "$sorted" | head -n 1 | awk -F $'\t' '{print $1}')"

# Collect winners (handle ties)
winners=""
while IFS=$'\t' read -r chars name path; do
  [[ -z "${chars:-}" ]] && continue
  if [[ "$chars" == "$max_chars" ]]; then
    winners+="${name} (${path})"$'\n'
  else
    break
  fi
done <<<"$sorted"

# ---------------- write report (Markdown) ----------------
{
  echo "# Character Count Report"
  echo
  echo "- **Generated:** ${NOW_UTC}"
  echo "- **Root:** \`${ROOT_DIR}\`"
  echo "- **Scan depth:** \`${SCAN_DEPTH}\`"
  echo "- **Projects scanned:** \`${repo_count}\`"
  echo
  echo "## Results (descending)"
  echo
  echo "| Rank | Project | Characters | Path |"
  echo "|---:|---|---:|---|"

  rank=0
  while IFS=$'\t' read -r chars name path; do
    [[ -z "${chars:-}" ]] && continue
    rank=$((rank + 1))
    # IMPORTANT: single-quoted format string so backticks stay literal (no command substitution)
    printf '| %d | %s | %s | `%s` |\n' "$rank" "$name" "$(format_number "$chars")" "$path"
  done <<<"$sorted"

  echo
  echo "## Winner(s)"
  echo
  echo "**Most characters:** $(format_number "$max_chars")"
  echo
  echo '```'
  printf "%s" "$winners"
  echo '```'
} >"$REPORT_PATH"

# ---------------- console output ----------------
echo "Root: $ROOT_DIR"
echo "Depth: $SCAN_DEPTH"
echo "Report: $REPORT_PATH"
echo
echo "${BOLD}Results (largest highlighted):${RESET}"
printf "%-3s  %-5s  %-12s  %s\n" " " "Rank" "Chars" "Project"
printf "%-3s  %-5s  %-12s  %s\n" "---" "-----" "------------" "------------------------------"

rank=0
while IFS=$'\t' read -r chars name path; do
  [[ -z "${chars:-}" ]] && continue
  rank=$((rank + 1))
  if [[ "$chars" == "$max_chars" ]]; then
    printf "%s%-3s  %-5s  %-12s  %s%s\n" "${BOLD}${GREEN}" "★" "$rank" "$(format_number "$chars")" "$name" "${RESET}"
  else
    printf "%-3s  %-5s  %-12s  %s\n" " " "$rank" "$(format_number "$chars")" "$name"
  fi
done <<<"$sorted"

echo
echo "${BOLD}Winner:${RESET} ${GREEN}$(printf "%s\n" "$sorted" | head -n 1 | awk -F $'\t' '{print $2}')${RESET} (${BOLD}$(format_number "$max_chars")${RESET} chars)"
echo "${DIM}(Full report written to: $REPORT_PATH)${RESET}"

