#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


TEXT_EXTENSIONS = {".js", ".cjs", ".mjs", ".json"}
EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    ".serverless",
    ".webpack",
    "dist",
    "coverage",
}


def iter_text_files(repo_root: Path):
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix in TEXT_EXTENSIONS:
            yield path


def is_test_file(path: Path) -> bool:
    return (
        "tests" in path.parts
        or path.name.endswith(".test.js")
        or path.name.endswith(".spec.js")
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def relative(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root))


def first_match_line(text: str, pattern: re.Pattern[str]):
    for index, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            return index
    return None


def collect_signal_hits(repo_root: Path, files, pattern: re.Pattern[str]):
    hits = []
    for path in files:
        text = read_text(path)
        line = first_match_line(text, pattern)
        if line is not None:
            hits.append({"path": relative(path, repo_root), "line": line})
    return hits


def classify_repo(summary):
    if summary["already_has_origin_logging"]:
        return "already-instrumented"
    if summary["capture_stack_trace"] or summary["uses_custom_error"]:
        return "custom-error-stack-ready"
    if (
        summary["throws_plain_string"]
        or summary["has_handled_error_helper"]
        or summary["has_handled_errors_file"]
    ):
        return "handled-error-needs-stack-wrapper"
    return "manual-review"


def detect_test_command(repo_root: Path):
    package_json_path = repo_root / "package.json"
    if not package_json_path.exists():
        return None
    try:
        package_json = json.loads(read_text(package_json_path))
    except json.JSONDecodeError:
        return None
    scripts = package_json.get("scripts") or {}
    return scripts.get("test")


def main():
    parser = argparse.ArgumentParser(
        description="Audit a lambda repo for compact origin logging rollout."
    )
    parser.add_argument("--repo", required=True, help="Absolute or relative repo path")
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo).expanduser().resolve()
    if not repo_root.exists():
        raise SystemExit(f"Repo not found: {repo_root}")
    if not repo_root.is_dir():
        raise SystemExit(f"Repo path is not a directory: {repo_root}")

    files = list(iter_text_files(repo_root))
    js_files = [path for path in files if path.suffix in {".js", ".cjs", ".mjs"}]
    source_js_files = [path for path in js_files if not is_test_file(path)]
    test_js_files = [path for path in js_files if is_test_file(path)]

    handled_errors_file = next(
        (path for path in source_js_files if path.name == "handled_errors.js"),
        None,
    )
    errors_file = next(
        (path for path in source_js_files if path.name == "errors.js"),
        None,
    )

    handled_error_pattern = re.compile(r"handled_custom_error|ACTION:SLACK_HANDLED_ERROR_HE1=")
    request_success_pattern = re.compile(r"RequestId SUCCESS")
    origin_logging_pattern = re.compile(
        r"\berror_origin\b|\bbuildErrorOriginLogLine\b"
    )
    custom_error_pattern = re.compile(r"\bCustomError\b")
    capture_stack_trace_pattern = re.compile(r"Error\.captureStackTrace")
    plain_string_throw_pattern = re.compile(r"""throw\s+['"][^'"]+['"]""")
    handled_helper_pattern = re.compile(
        r"\bHandledError\b|\bmarkHandledError\b|\bcheckHandledError\b"
    )
    direct_comment_error_assignment_pattern = re.compile(
        r"\b(comment_id|hard_error_comment_id|first_failed_comment_id)\s*=\s*error\s*;"
    )
    raw_error_string_compare_pattern = re.compile(
        r"(?<!typeof )\berror\s*(===|!==)\s*['\"][^'\"]+['\"]"
    )

    handler_hits = collect_signal_hits(repo_root, source_js_files, handled_error_pattern)
    request_success_hits = collect_signal_hits(
        repo_root, source_js_files, request_success_pattern
    )
    origin_logging_hits = collect_signal_hits(
        repo_root, source_js_files, origin_logging_pattern
    )
    custom_error_hits = collect_signal_hits(repo_root, source_js_files, custom_error_pattern)
    plain_string_throw_hits = collect_signal_hits(
        repo_root, source_js_files, plain_string_throw_pattern
    )
    handled_helper_hits = collect_signal_hits(
        repo_root, source_js_files, handled_helper_pattern
    )
    direct_comment_error_assignment_hits = collect_signal_hits(
        repo_root, source_js_files, direct_comment_error_assignment_pattern
    )
    raw_error_string_compare_hits = collect_signal_hits(
        repo_root, source_js_files, raw_error_string_compare_pattern
    )

    capture_stack_trace = False
    if errors_file:
        capture_stack_trace = bool(
            capture_stack_trace_pattern.search(read_text(errors_file))
        )

    suggested_files_to_read = []
    for candidate in [
        relative(handled_errors_file, repo_root) if handled_errors_file else None,
        relative(errors_file, repo_root) if errors_file else None,
        *sorted({hit["path"] for hit in handler_hits}),
        *sorted({hit["path"] for hit in direct_comment_error_assignment_hits}),
        *sorted({hit["path"] for hit in raw_error_string_compare_hits}),
    ]:
        if candidate and candidate not in suggested_files_to_read:
            suggested_files_to_read.append(candidate)

    summary = {
        "repo_root": str(repo_root),
        "has_handled_errors_file": handled_errors_file is not None,
        "handled_errors_file": (
            relative(handled_errors_file, repo_root) if handled_errors_file else None
        ),
        "errors_file": relative(errors_file, repo_root) if errors_file else None,
        "uses_custom_error": bool(custom_error_hits),
        "capture_stack_trace": capture_stack_trace,
        "throws_plain_string": bool(plain_string_throw_hits),
        "has_handled_error_helper": bool(handled_helper_hits),
        "already_has_origin_logging": bool(origin_logging_hits),
        "has_handled_error_normalization_warnings": bool(
            direct_comment_error_assignment_hits or raw_error_string_compare_hits
        ),
        "has_requestid_success_log": bool(request_success_hits),
        "has_slack_handled_error_marker": bool(handler_hits),
        "candidate_handler_files": sorted(
            {hit["path"] for hit in handler_hits + request_success_hits}
        ),
        "test_files": sorted(relative(path, repo_root) for path in test_js_files),
        "test_command": detect_test_command(repo_root),
        "suggested_files_to_read": suggested_files_to_read,
        "signal_hits": {
            "handled_error_flow": handler_hits,
            "requestid_success": request_success_hits,
            "origin_logging": origin_logging_hits,
            "custom_error": custom_error_hits,
            "plain_string_throw": plain_string_throw_hits,
            "handled_error_helper": handled_helper_hits,
            "direct_comment_error_assignment": direct_comment_error_assignment_hits,
            "raw_error_string_compare": raw_error_string_compare_hits,
        },
    }
    summary["pattern"] = classify_repo(summary)

    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    print(f"Repo: {summary['repo_root']}")
    print(f"Pattern: {summary['pattern']}")
    print(f"handled_errors.js: {summary['handled_errors_file'] or 'missing'}")
    print(f"errors.js: {summary['errors_file'] or 'missing'}")
    print(f"origin logging present: {summary['already_has_origin_logging']}")
    print(f"CustomError usage: {summary['uses_custom_error']}")
    print(f"Error.captureStackTrace: {summary['capture_stack_trace']}")
    print(f"Plain string throws: {summary['throws_plain_string']}")
    print(f"Handled-error helper: {summary['has_handled_error_helper']}")
    print(
        "Handled-error normalization warnings: "
        f"{summary['has_handled_error_normalization_warnings']}"
    )
    print(f"Candidate handler files: {', '.join(summary['candidate_handler_files']) or 'none'}")
    print(f"Suggested files to read: {', '.join(summary['suggested_files_to_read']) or 'none'}")
    print(f"Test files: {', '.join(summary['test_files']) or 'none'}")
    print(f"Test command: {summary['test_command'] or 'missing'}")


if __name__ == "__main__":
    main()
