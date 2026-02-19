#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REF_FILE_RE = re.compile(r"^codeliver-(app|pos|panel|sap)-lambdas\.md$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
IGNORED_SECTIONS = {
    "API Ids -> API Names",
    "Πηγές",
    "Sources",
}

CUSTOM_ERROR_PATTERNS = [
    re.compile(r'new\s+CustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'CustomError\s*\([^)]*\|\|\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'throwCustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'makeKnownError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'checkCustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
]

PRESENT_POST_FAILURE_RE = re.compile(r'presentPostFailureAlert\s*\((?s:.*?)["\']([a-z0-9-]+)["\']')
LAMBDA_RESPONSES_KEY_RE = re.compile(r"lambdas_responses\.([a-z0-9-]+)\.")
CONSTANT_LAMBDA_RE = re.compile(
    r'(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:process\.env\.[A-Za-z_][A-Za-z0-9_]*\s*\|\|\s*)?["\']([a-z0-9-]+)["\']'
)
CALL_INVOKE_RE = re.compile(r"\b(?:lambda_invoke|lambdaInvoke|invokeLambda)\s*\(\s*([^\s,)\n]+)")
FUNCTION_NAME_RE = re.compile(r"FunctionName\s*:\s*([^\s,}\n]+)")
STRING_LITERAL_RE = re.compile(r'^["\']([a-z0-9-]+)["\']$')
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def parse_ref_file(path: Path):
    project = path.name.replace("-lambdas.md", "")
    lambdas = []
    seen = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = SECTION_RE.match(line.strip())
        if not match:
            continue
        section = match.group(1).strip()
        if section in IGNORED_SECTIONS:
            continue
        if section.startswith("Observed ") or section.startswith("Σκοπός:"):
            continue
        if section not in seen:
            seen.add(section)
            lambdas.append(section)
    return project, lambdas


def load_frontend_refs(refs_dir: Path):
    project_to_lambdas = {}
    for ref_file in sorted(refs_dir.glob("codeliver-*-lambdas.md")):
        if not REF_FILE_RE.match(ref_file.name):
            continue
        project, lambdas = parse_ref_file(ref_file)
        project_to_lambdas[project] = lambdas
    return project_to_lambdas


def build_lambda_index(lambdas_root: Path):
    index = defaultdict(list)
    for group_dir in sorted(lambdas_root.iterdir()):
        if not group_dir.is_dir():
            continue
        if group_dir.name in {"node_modules", ".git"}:
            continue
        for lambda_dir in sorted(group_dir.iterdir()):
            if lambda_dir.is_dir():
                index[lambda_dir.name].append(str(lambda_dir.resolve()))
    return index


def iter_lambda_code_files(lambda_dir: Path):
    for path in lambda_dir.rglob("*.js"):
        parts = set(path.parts)
        if "node_modules" in parts or "__tests__" in parts or "test" in parts:
            continue
        if path.name.endswith(".test.js"):
            continue
        yield path


def extract_error_codes_from_text(text: str):
    codes = set()
    for pattern in CUSTOM_ERROR_PATTERNS:
        for match in pattern.finditer(text):
            code = match.group(1).strip()
            if code:
                codes.add(code)
    return codes


def extract_response_fields_from_text(text: str):
    fields = set()
    if re.search(r"\bcomment_id\s*:", text):
        fields.add("comment_id")
    if re.search(r"\bcomments\s*:", text):
        fields.add("comments")
    return fields


def resolve_invoked_token(token: str, constants_map: dict):
    token = token.strip()
    string_match = STRING_LITERAL_RE.match(token)
    if string_match:
        return string_match.group(1)
    if IDENTIFIER_RE.match(token):
        return constants_map.get(token)
    return None


def extract_downstream_lambda_names(text: str):
    constants_map = {}
    for match in CONSTANT_LAMBDA_RE.finditer(text):
        constants_map[match.group(1)] = match.group(2)

    names = set()
    for match in CALL_INVOKE_RE.finditer(text):
        name = resolve_invoked_token(match.group(1), constants_map)
        if name:
            names.add(name)

    for match in FUNCTION_NAME_RE.finditer(text):
        name = resolve_invoked_token(match.group(1), constants_map)
        if name:
            names.add(name)

    return {name for name in names if "-" in name}


def detect_project_nested_lambdas(project_root: Path):
    nested_lambdas = set()
    app_root = project_root / "src" / "app"
    if not app_root.exists():
        return nested_lambdas

    for ts_file in app_root.rglob("*.ts"):
        text = ts_file.read_text(encoding="utf-8", errors="ignore")
        for match in PRESENT_POST_FAILURE_RE.finditer(text):
            nested_lambdas.add(match.group(1))
        for match in LAMBDA_RESPONSES_KEY_RE.finditer(text):
            nested_lambdas.add(match.group(1))
    return nested_lambdas


def load_i18n_file(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_i18n_file(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check_translation_exists(i18n_data: dict, translation_kind: str, entry_lambda: str, error_code: str):
    if translation_kind == "root":
        return error_code in i18n_data

    lambdas_responses = i18n_data.get("lambdas_responses")
    if not isinstance(lambdas_responses, dict):
        return False
    lambda_map = lambdas_responses.get(entry_lambda)
    if not isinstance(lambda_map, dict):
        return False
    return error_code in lambda_map


def ensure_translation(
    i18n_data: dict,
    translation_kind: str,
    entry_lambda: str,
    error_code: str,
    placeholder: str,
    apply_changes: bool = True,
):
    if translation_kind == "root":
        if error_code in i18n_data:
            return False, None
        if apply_changes:
            i18n_data[error_code] = placeholder
        return True, None

    lambdas_responses = i18n_data.get("lambdas_responses")
    if lambdas_responses is None:
        if apply_changes:
            i18n_data["lambdas_responses"] = {}
            lambdas_responses = i18n_data["lambdas_responses"]
        else:
            lambdas_responses = {}

    if not isinstance(lambdas_responses, dict):
        return False, "invalid_lambdas_responses_container"

    lambda_map = lambdas_responses.get(entry_lambda)
    if lambda_map is None:
        if apply_changes:
            lambdas_responses[entry_lambda] = {}
            lambda_map = lambdas_responses[entry_lambda]
        else:
            lambda_map = {}

    if not isinstance(lambda_map, dict):
        return False, "invalid_lambda_translation_container"

    if error_code in lambda_map:
        return False, None

    if apply_changes:
        lambda_map[error_code] = placeholder
    return True, None


def md_escape(value):
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def write_markdown_report(path: Path, report: dict):
    rows = report["rows"]
    unresolved = report["unresolved"]
    summary = report["summary"]

    lines = [
        "# Frontend Lambda Error Translation Report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Mode: `{report['mode']}`",
        f"- Languages: `{report['languages']}`",
        f"- Depth: `{report['depth']}`",
        "",
        "## Summary",
        f"- Total rows: `{summary['total_rows']}`",
        f"- found: `{summary['found']}`",
        f"- created: `{summary['created']}`",
        f"- missing: `{summary['missing']}`",
        f"- skipped: `{summary['skipped']}`",
        f"- unresolved mappings: `{summary['unresolved_mappings']}`",
        "",
    ]

    if unresolved:
        lines.append("## Unresolved mappings")
        for item in unresolved:
            lines.append(
                f"- `{item['frontend_project']}` -> `{item['lambda_name']}` ({item['kind']})"
            )
        lines.append("")

    non_found_rows = [row for row in rows if row["status"] != "found"]
    lines.append("## Non-found rows")
    if not non_found_rows:
        lines.append("- None")
        lines.append("")
    else:
        lines.extend(
            [
                "",
                "| frontend_project | entry_lambda | downstream_lambda | error_code | field | translation_path | status | language_file | reason |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in non_found_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_escape(row.get("frontend_project", "")),
                        md_escape(row.get("entry_lambda", "")),
                        md_escape(row.get("downstream_lambda", "")),
                        md_escape(row.get("error_code", "")),
                        md_escape(row.get("field", "")),
                        md_escape(row.get("translation_path", "")),
                        md_escape(row.get("status", "")),
                        md_escape(row.get("language_file", "")),
                        md_escape(row.get("reason", "")),
                    ]
                )
                + " |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_languages_spec(languages: str):
    if languages.strip().lower() == "all":
        return None
    values = [item.strip() for item in languages.split(",") if item.strip()]
    return {f"{value}.json" if not value.endswith(".json") else value for value in values}


def analyze_lambda_folder(lambda_dir: Path):
    all_texts = []
    response_fields = set()
    error_codes = set()
    downstream_names = set()

    for js_file in iter_lambda_code_files(lambda_dir):
        text = js_file.read_text(encoding="utf-8", errors="ignore")
        all_texts.append(text)
        response_fields |= extract_response_fields_from_text(text)
        error_codes |= extract_error_codes_from_text(text)
        downstream_names |= extract_downstream_lambda_names(text)

    return {
        "response_fields": response_fields,
        "error_codes": error_codes,
        "downstream_names": downstream_names,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Audit/autofix frontend-visible lambda error translation coverage."
    )
    parser.add_argument("--mode", choices=["audit", "autofix"], default="autofix")
    parser.add_argument("--languages", default="all", help="all or comma-separated list, e.g. el,en")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--projects-root", default="/home/dm-soft-1/Downloads/projects")
    parser.add_argument("--lambdas-root", default="/home/dm-soft-1/Downloads/lambdas")
    parser.add_argument("--refs-dir", default="/home/dm-soft-1/.codex/refs")
    parser.add_argument(
        "--report-json",
        default="/home/dm-soft-1/.codex/tmp/frontend-lambda-errors-i18n-report.json",
    )
    parser.add_argument(
        "--report-md",
        default="/home/dm-soft-1/.codex/tmp/frontend-lambda-errors-i18n-report.md",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.depth != 1:
        raise SystemExit("Only --depth 1 is supported by policy.")

    projects_root = Path(args.projects_root)
    lambdas_root = Path(args.lambdas_root)
    refs_dir = Path(args.refs_dir)
    report_json_path = Path(args.report_json)
    report_md_path = Path(args.report_md)
    selected_languages = parse_languages_spec(args.languages)

    if not projects_root.exists():
        raise SystemExit(f"projects root not found: {projects_root}")
    if not lambdas_root.exists():
        raise SystemExit(f"lambdas root not found: {lambdas_root}")
    if not refs_dir.exists():
        raise SystemExit(f"refs dir not found: {refs_dir}")

    project_to_entry_lambdas = load_frontend_refs(refs_dir)
    lambda_index = build_lambda_index(lambdas_root)

    unresolved = []
    rows = []
    changed_i18n_files = set()
    i18n_cache = {}
    lambda_analysis_cache = {}

    for frontend_project, entry_lambdas in sorted(project_to_entry_lambdas.items()):
        project_root = projects_root / "codeliver" / frontend_project
        i18n_dir = project_root / "src" / "assets" / "i18n"
        if not i18n_dir.exists():
            unresolved.append(
                {
                    "frontend_project": frontend_project,
                    "lambda_name": "",
                    "kind": "missing_i18n_dir",
                }
            )
            continue

        i18n_files = sorted(i18n_dir.glob("*.json"))
        if selected_languages is not None:
            i18n_files = [path for path in i18n_files if path.name in selected_languages]

        if not i18n_files:
            unresolved.append(
                {
                    "frontend_project": frontend_project,
                    "lambda_name": "",
                    "kind": "no_matching_i18n_files",
                }
            )
            continue

        nested_lambdas = detect_project_nested_lambdas(project_root)

        for entry_lambda in entry_lambdas:
            matches = lambda_index.get(entry_lambda, [])
            if len(matches) != 1:
                kind = "entry_unresolved" if len(matches) == 0 else "entry_ambiguous"
                unresolved.append(
                    {
                        "frontend_project": frontend_project,
                        "lambda_name": entry_lambda,
                        "kind": kind,
                    }
                )
                rows.append(
                    {
                        "frontend_project": frontend_project,
                        "entry_lambda": entry_lambda,
                        "resolved_lambda_path": None,
                        "downstream_lambda": "",
                        "error_code": "",
                        "field": "",
                        "translation_path": "",
                        "status": "skipped",
                        "language_file": "",
                        "reason": kind,
                    }
                )
                continue

            entry_path = Path(matches[0])
            if str(entry_path) not in lambda_analysis_cache:
                lambda_analysis_cache[str(entry_path)] = analyze_lambda_folder(entry_path)
            entry_analysis = lambda_analysis_cache[str(entry_path)]

            entry_fields = entry_analysis["response_fields"] or {"comment_id"}
            entry_error_codes = set(entry_analysis["error_codes"])
            downstream_names = set(entry_analysis["downstream_names"])
            downstream_codes = set()

            for downstream_name in sorted(downstream_names):
                downstream_matches = lambda_index.get(downstream_name, [])
                if len(downstream_matches) != 1:
                    kind = (
                        "downstream_unresolved"
                        if len(downstream_matches) == 0
                        else "downstream_ambiguous"
                    )
                    unresolved.append(
                        {
                            "frontend_project": frontend_project,
                            "lambda_name": downstream_name,
                            "kind": kind,
                        }
                    )
                    continue

                downstream_path = Path(downstream_matches[0])
                if str(downstream_path) not in lambda_analysis_cache:
                    lambda_analysis_cache[str(downstream_path)] = analyze_lambda_folder(
                        downstream_path
                    )
                downstream_analysis = lambda_analysis_cache[str(downstream_path)]
                downstream_codes |= set(downstream_analysis["error_codes"])

            all_error_codes = sorted(entry_error_codes | downstream_codes)
            if not all_error_codes:
                rows.append(
                    {
                        "frontend_project": frontend_project,
                        "entry_lambda": entry_lambda,
                        "resolved_lambda_path": str(entry_path),
                        "downstream_lambda": "",
                        "error_code": "",
                        "field": ",".join(sorted(entry_fields)),
                        "translation_path": "root"
                        if entry_lambda not in nested_lambdas
                        else f"lambdas_responses.{entry_lambda}",
                        "status": "skipped",
                        "language_file": "",
                        "reason": "no_custom_error_codes_detected",
                    }
                )
                continue

            translation_kind = "nested" if entry_lambda in nested_lambdas else "root"
            translation_path = (
                f"lambdas_responses.{entry_lambda}"
                if translation_kind == "nested"
                else "root"
            )

            for i18n_file in i18n_files:
                i18n_key = str(i18n_file.resolve())
                if i18n_key not in i18n_cache:
                    i18n_cache[i18n_key] = load_i18n_file(i18n_file)
                i18n_data = i18n_cache[i18n_key]

                for error_code in all_error_codes:
                    exists = check_translation_exists(
                        i18n_data=i18n_data,
                        translation_kind=translation_kind,
                        entry_lambda=entry_lambda,
                        error_code=error_code,
                    )

                    status = "found" if exists else "missing"
                    reason = ""

                    if not exists and args.mode == "autofix":
                        created, collision_reason = ensure_translation(
                            i18n_data=i18n_data,
                            translation_kind=translation_kind,
                            entry_lambda=entry_lambda,
                            error_code=error_code,
                            placeholder=f"TODO({error_code})",
                            apply_changes=not args.dry_run,
                        )
                        if collision_reason:
                            status = "skipped"
                            reason = collision_reason
                        elif created:
                            if args.dry_run:
                                status = "missing"
                                reason = "dry_run"
                            else:
                                status = "created"
                                changed_i18n_files.add(i18n_key)

                    downstream_lambda = ""
                    if error_code in downstream_codes and error_code not in entry_error_codes:
                        downstream_lambda = "one-hop-downstream"

                    for field in sorted(entry_fields):
                        rows.append(
                            {
                                "frontend_project": frontend_project,
                                "entry_lambda": entry_lambda,
                                "resolved_lambda_path": str(entry_path),
                                "downstream_lambda": downstream_lambda,
                                "error_code": error_code,
                                "field": field,
                                "translation_path": translation_path,
                                "status": status,
                                "language_file": i18n_key,
                                "reason": reason,
                            }
                        )

    if args.mode == "autofix" and not args.dry_run:
        for path_str in sorted(changed_i18n_files):
            save_i18n_file(Path(path_str), i18n_cache[path_str])

    status_counts = Counter(row["status"] for row in rows)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "languages": args.languages,
        "depth": args.depth,
        "projects_root": str(projects_root.resolve()),
        "lambdas_root": str(lambdas_root.resolve()),
        "refs_dir": str(refs_dir.resolve()),
        "rows": rows,
        "unresolved": unresolved,
        "summary": {
            "total_rows": len(rows),
            "found": status_counts.get("found", 0),
            "created": status_counts.get("created", 0),
            "missing": status_counts.get("missing", 0),
            "skipped": status_counts.get("skipped", 0),
            "unresolved_mappings": len(unresolved),
            "changed_i18n_files": len(changed_i18n_files),
        },
    }

    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_markdown_report(report_md_path, report)

    print(
        "summary",
        json.dumps(
            {
                "report_json": str(report_json_path),
                "report_md": str(report_md_path),
                **report["summary"],
            },
            ensure_ascii=False,
        ),
    )


if __name__ == "__main__":
    main()
