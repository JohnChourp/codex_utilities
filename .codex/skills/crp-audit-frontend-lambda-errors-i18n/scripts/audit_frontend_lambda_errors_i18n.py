#!/usr/bin/env python3
import argparse
import json
import os
import re
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

API_LAMBDA_RE = re.compile(r"/prod/(crp-[a-z0-9-]+)")
LOG_NAME_RE = re.compile(r'logName\s*:\s*["\'](crp-[a-z0-9-]+)["\']')

PRESENT_POST_FAILURE_RE = re.compile(r'presentPostFailureAlert\s*\((?s:.*?)["\']([a-z0-9-]+)["\']')
LAMBDA_RESPONSES_KEY_RE = re.compile(r"lambdas_responses\.([a-z0-9-]+)\.")

CUSTOM_ERROR_PATTERNS = [
    re.compile(r'new\s+CustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'CustomError\s*\([^)]*\|\|\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'throwCustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'makeKnownError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'checkCustomError\s*\(\s*["\']([A-Za-z0-9_.-]+)["\']'),
    re.compile(r'comment_id\s*:\s*["\']([A-Za-z0-9_.-]+)["\']'),
]

CONSTANT_LAMBDA_RE = re.compile(
    r'(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:process\.env\.[A-Za-z_][A-Za-z0-9_]*\s*\|\|\s*)?["\']([a-z0-9-]+)["\']'
)
CALL_INVOKE_RE = re.compile(r"\b(?:lambda_invoke|lambdaInvoke|invokeLambda)\s*\(\s*([^\s,)\n]+)")
FUNCTION_NAME_RE = re.compile(r"FunctionName\s*:\s*([^\s,}\n]+)")
STRING_LITERAL_RE = re.compile(r'^["\']([a-z0-9-]+)["\']$')
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PLACEHOLDER_RE = re.compile(r"{{\s*[^{}]+\s*}}")
TODO_PLACEHOLDER_RE = re.compile(r"^\s*TODO\([^)]+\)\s*$", re.IGNORECASE)
SUPPORTED_LOCALE_FILES = {"el.json", "en.json"}


def find_entry_lambdas(project_root: Path):
    frontend_files = [
        project_root / "src" / "app" / "shared" / "data-storage.service.ts",
        project_root / "src" / "app" / "shared" / "auth" / "auth.service.ts",
    ]

    lambda_sources = defaultdict(set)
    for file_path in frontend_files:
        if not file_path.exists():
            continue

        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for match in API_LAMBDA_RE.finditer(text):
            lambda_sources[match.group(1)].add(f"{file_path}:api_path")

        for match in LOG_NAME_RE.finditer(text):
            lambda_sources[match.group(1)].add(f"{file_path}:logName")

    return lambda_sources, frontend_files


def build_lambda_index(lambdas_root: Path):
    index = defaultdict(list)
    ignored_names = {"node_modules", ".git", "__pycache__"}

    for first in sorted(lambdas_root.iterdir()):
        if not first.is_dir() or first.name in ignored_names:
            continue

        if (first / "index.js").exists() or (first / "package.json").exists() or (first / "cloudformation").exists():
            index[first.name].append(str(first.resolve()))
            continue

        for second in sorted(first.iterdir()):
            if not second.is_dir() or second.name in ignored_names:
                continue
            index[second.name].append(str(second.resolve()))

    return index


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


def analyze_lambda_folder(lambda_dir: Path):
    response_fields = set()
    error_codes = set()
    downstream_names = set()

    for js_file in iter_lambda_code_files(lambda_dir):
        text = js_file.read_text(encoding="utf-8", errors="ignore")
        response_fields |= extract_response_fields_from_text(text)
        error_codes |= extract_error_codes_from_text(text)
        downstream_names |= extract_downstream_lambda_names(text)

    return {
        "response_fields": response_fields,
        "error_codes": error_codes,
        "downstream_names": downstream_names,
    }


def parse_languages_spec(languages: str):
    if languages.strip().lower() == "all":
        return set(SUPPORTED_LOCALE_FILES)
    values = [item.strip() for item in languages.split(",") if item.strip()]
    selected = {f"{value}.json" if not value.endswith(".json") else value for value in values}
    unsupported = sorted(selected - SUPPORTED_LOCALE_FILES)
    if unsupported:
        raise SystemExit(f"unsupported locales requested: {unsupported}. Only el,en are allowed.")
    return selected


def parse_locale_priority(spec: str):
    values = [item.strip() for item in spec.split(",") if item.strip()]
    parsed = [f"{value}.json" if not value.endswith(".json") else value for value in values]
    return [item for item in parsed if item in SUPPORTED_LOCALE_FILES]


def load_i18n_file(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_i18n_file(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_placeholder_translation(value: str):
    return bool(TODO_PLACEHOLDER_RE.match(value.strip()))


def get_translation_value(i18n_data: dict, translation_kind: str, entry_lambda: str, error_code: str):
    if translation_kind == "root":
        value = i18n_data.get(error_code)
        if not isinstance(value, str) or not value.strip():
            return None
        return None if is_placeholder_translation(value) else value

    lambdas_responses = i18n_data.get("lambdas_responses")
    if not isinstance(lambdas_responses, dict):
        return None
    lambda_map = lambdas_responses.get(entry_lambda)
    if not isinstance(lambda_map, dict):
        return None
    value = lambda_map.get(error_code)
    if not isinstance(value, str) or not value.strip():
        return None
    return None if is_placeholder_translation(value) else value


def check_translation_exists(i18n_data: dict, translation_kind: str, entry_lambda: str, error_code: str):
    return get_translation_value(i18n_data, translation_kind, entry_lambda, error_code) is not None


def ensure_translation(i18n_data: dict, translation_kind: str, entry_lambda: str, error_code: str, translated_text: str, apply_changes: bool = True):
    if translation_kind == "root":
        existing_value = i18n_data.get(error_code)
        if isinstance(existing_value, str) and existing_value.strip() and not is_placeholder_translation(existing_value):
            return False, None
        if apply_changes:
            i18n_data[error_code] = translated_text
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

    existing_value = lambda_map.get(error_code)
    if isinstance(existing_value, str) and existing_value.strip() and not is_placeholder_translation(existing_value):
        return False, None

    if apply_changes:
        lambda_map[error_code] = translated_text

    return True, None


def extract_output_text(response_json: dict):
    output_text = response_json.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    chunks = []
    for item in response_json.get("output", []):
        if not isinstance(item, dict):
            continue
        for content_item in item.get("content", []):
            if not isinstance(content_item, dict):
                continue
            text_value = content_item.get("text")
            if isinstance(text_value, str) and text_value:
                chunks.append(text_value)

    return "\n".join(chunks).strip()


def locale_to_language_name(locale_file: str):
    locale = locale_file.lower().replace(".json", "")
    if locale in {"en", "eng"}:
        return "English"
    if locale in {"el", "gr", "greek"}:
        return "Greek"
    return f"language locale '{locale}'"


def placeholders_signature(text: str):
    return Counter(PLACEHOLDER_RE.findall(text or ""))


def call_openai_translate_batch(texts, target_locale_file: str, model: str):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None, "missing_openai_api_key"

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    target_language = locale_to_language_name(target_locale_file)

    system_prompt = (
        "You are a professional translator. "
        "Translate each input item to the target language with natural, production-ready quality. "
        "Preserve placeholders exactly (example: {{count}}), keep markdown/code tokens unchanged, "
        "and do not add commentary. Return only a JSON array of strings with the same item count and order."
    )

    user_payload = {
        "target_language": target_language,
        "items": texts,
    }

    body = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": system_prompt,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(user_payload, ensure_ascii=False),
                    }
                ],
            },
        ],
    }

    request = urllib.request.Request(
        f"{base_url}/responses",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            payload = json.loads(raw)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="ignore")
        return None, f"openai_http_error_{error.code}:{detail[:300]}"
    except Exception as error:  # noqa: BLE001
        return None, f"openai_request_failed:{error}"

    output_text = extract_output_text(payload)
    if not output_text:
        return None, "openai_empty_output"

    try:
        translated = json.loads(output_text)
    except Exception:  # noqa: BLE001
        return None, "openai_invalid_json_output"

    if not isinstance(translated, list):
        return None, "openai_output_not_list"
    if len(translated) != len(texts):
        return None, "openai_output_count_mismatch"

    normalized = []
    for value in translated:
        normalized.append(value if isinstance(value, str) else str(value))

    return normalized, None


def humanize_key(error_code: str):
    text = re.sub(r"[_\-.]+", " ", error_code).strip()
    if not text:
        return error_code
    return f"{text.capitalize()}."


def select_source_text(error_code: str, i18n_cache_by_file: dict, locale_priority: list):
    for locale_file in locale_priority:
        data = i18n_cache_by_file.get(locale_file)
        if isinstance(data, dict):
            value = get_translation_value(data, "root", "", error_code)
            if value:
                return value, locale_file

    for locale_file, data in i18n_cache_by_file.items():
        if isinstance(data, dict):
            value = get_translation_value(data, "root", "", error_code)
            if value:
                return value, locale_file

    return humanize_key(error_code), "generated"


def md_escape(value):
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def write_markdown_report(path: Path, report: dict):
    rows = report.get("rows", [])
    unresolved = report.get("unresolved", [])
    summary = report.get("summary", {})

    lines = [
        "# CRP Frontend Lambda Error Translation Report",
        "",
        f"- Generated at: `{report.get('generated_at', '')}`",
        f"- Mode: `{report.get('mode', '')}`",
        f"- Languages: `{report.get('languages', '')}`",
        f"- Depth: `{report.get('depth', '')}`",
        f"- Translation provider: `{report.get('translation_provider', '')}`",
        f"- Translation model: `{report.get('translation_model', '')}`",
        "",
        "## Summary",
        f"- Total rows: `{summary.get('total_rows', 0)}`",
        f"- found: `{summary.get('found', 0)}`",
        f"- created: `{summary.get('created', 0)}`",
        f"- missing: `{summary.get('missing', 0)}`",
        f"- skipped: `{summary.get('skipped', 0)}`",
        f"- unresolved mappings: `{summary.get('unresolved_mappings', 0)}`",
        f"- changed_i18n_files: `{summary.get('changed_i18n_files', 0)}`",
        "",
    ]

    if unresolved:
        lines.append("## Unresolved mappings")
        for item in unresolved:
            lines.append(
                f"- `{item.get('frontend_project', '')}` -> `{item.get('lambda_name', item.get('entry_lambda', ''))}` ({item.get('kind', '')})"
            )
        lines.append("")

    non_found_rows = [row for row in rows if row.get("status") != "found"]
    lines.append("## Non-found rows")
    if not non_found_rows:
        lines.append("- None")
        lines.append("")
    else:
        lines.extend(
            [
                "",
                "| frontend_project | entry_lambda | downstream_lambda | error_code | field | translation_path | status | language_file | reason | translation_status | translation_reason |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
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
                        md_escape(row.get("translation_status", "")),
                        md_escape(row.get("translation_reason", "")),
                    ]
                )
                + " |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Audit/autofix frontend-visible CRP lambda error translation coverage."
    )
    parser.add_argument("--mode", choices=["audit", "autofix"], default="autofix")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--projects-root", default="/Users/john/Downloads/projects")
    parser.add_argument("--frontend-project", default="cloud-repos-panel")
    parser.add_argument("--lambdas-root", default="/Users/john/Downloads/lambdas/crp_all")
    parser.add_argument("--languages", default="el,en", help="comma-separated list, supported only: el,en")
    parser.add_argument("--translation-provider", choices=["openai", "none"], default="openai")
    parser.add_argument("--translation-model", default="gpt-4.1-mini")
    parser.add_argument("--translation-source-locale-priority", default="en,el")
    parser.add_argument(
        "--report-json",
        default="/Users/john/.codex/tmp/crp-frontend-lambda-errors-i18n-report.json",
    )
    parser.add_argument(
        "--report-md",
        default="/Users/john/.codex/tmp/crp-frontend-lambda-errors-i18n-report.md",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.depth != 1:
        raise SystemExit("Only --depth 1 is supported by policy.")

    projects_root = Path(args.projects_root)
    project_root = projects_root / args.frontend_project
    lambdas_root = Path(args.lambdas_root)
    report_json_path = Path(args.report_json)
    report_md_path = Path(args.report_md)
    selected_languages = parse_languages_spec(args.languages)
    locale_priority = parse_locale_priority(args.translation_source_locale_priority)
    if not locale_priority:
        locale_priority = ["en.json", "el.json"]

    if not projects_root.exists():
        raise SystemExit(f"projects root not found: {projects_root}")
    if not project_root.exists():
        raise SystemExit(f"frontend project not found: {project_root}")
    if not lambdas_root.exists():
        raise SystemExit(f"lambdas root not found: {lambdas_root}")

    lambda_sources, frontend_files = find_entry_lambdas(project_root)
    entry_lambdas = sorted(lambda_sources.keys())
    lambda_index = build_lambda_index(lambdas_root)
    nested_lambdas = detect_project_nested_lambdas(project_root)

    i18n_dir = project_root / "src" / "assets" / "i18n"
    if not i18n_dir.exists():
        raise SystemExit(f"i18n directory not found: {i18n_dir}")

    i18n_files = sorted(i18n_dir.glob("*.json"))
    if selected_languages is not None:
        i18n_files = [path for path in i18n_files if path.name in selected_languages]

    if not i18n_files:
        raise SystemExit(f"no matching i18n files found in: {i18n_dir}")

    unresolved = []
    rows = []
    changed_i18n_files = set()
    i18n_cache = {}
    lambda_analysis_cache = {}

    # Cache locale data by filename for source-text fallback selection.
    i18n_cache_by_file = {}

    for i18n_file in i18n_files:
        i18n_key = str(i18n_file.resolve())
        data = load_i18n_file(i18n_file)
        i18n_cache[i18n_key] = data
        i18n_cache_by_file[i18n_file.name] = data

    for entry_lambda in entry_lambdas:
        matches = lambda_index.get(entry_lambda, [])
        if len(matches) != 1:
            kind = "entry_unresolved" if len(matches) == 0 else "entry_ambiguous"
            unresolved.append(
                {
                    "frontend_project": args.frontend_project,
                    "lambda_name": entry_lambda,
                    "kind": kind,
                }
            )
            rows.append(
                {
                    "frontend_project": args.frontend_project,
                    "entry_lambda": entry_lambda,
                    "resolved_lambda_path": None,
                    "downstream_lambda": "",
                    "error_code": "",
                    "field": "",
                    "translation_path": "",
                    "status": "skipped",
                    "language_file": "",
                    "reason": kind,
                    "translation_provider": args.translation_provider,
                    "translation_model": args.translation_model,
                    "translation_source_locale": "",
                    "translation_status": "skipped",
                    "translation_reason": kind,
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
                kind = "downstream_unresolved" if len(downstream_matches) == 0 else "downstream_ambiguous"
                unresolved.append(
                    {
                        "frontend_project": args.frontend_project,
                        "lambda_name": downstream_name,
                        "kind": kind,
                    }
                )
                continue

            downstream_path = Path(downstream_matches[0])
            if str(downstream_path) not in lambda_analysis_cache:
                lambda_analysis_cache[str(downstream_path)] = analyze_lambda_folder(downstream_path)
            downstream_analysis = lambda_analysis_cache[str(downstream_path)]
            downstream_codes |= set(downstream_analysis["error_codes"])

        all_error_codes = sorted(entry_error_codes | downstream_codes)
        translation_kind = "nested" if entry_lambda in nested_lambdas else "root"
        translation_path = f"lambdas_responses.{entry_lambda}" if translation_kind == "nested" else "root"

        if not all_error_codes:
            rows.append(
                {
                    "frontend_project": args.frontend_project,
                    "entry_lambda": entry_lambda,
                    "resolved_lambda_path": str(entry_path),
                    "downstream_lambda": "",
                    "error_code": "",
                    "field": ",".join(sorted(entry_fields)),
                    "translation_path": translation_path,
                    "status": "skipped",
                    "language_file": "",
                    "reason": "no_custom_error_codes_detected",
                    "translation_provider": args.translation_provider,
                    "translation_model": args.translation_model,
                    "translation_source_locale": "",
                    "translation_status": "skipped",
                    "translation_reason": "no_custom_error_codes_detected",
                }
            )
            continue

        for i18n_file in i18n_files:
            i18n_key = str(i18n_file.resolve())
            i18n_data = i18n_cache[i18n_key]

            per_code = {}
            missing_codes = []
            source_text_by_code = {}
            source_locale_by_code = {}

            for error_code in all_error_codes:
                exists = check_translation_exists(
                    i18n_data=i18n_data,
                    translation_kind=translation_kind,
                    entry_lambda=entry_lambda,
                    error_code=error_code,
                )
                if exists:
                    per_code[error_code] = {
                        "status": "found",
                        "reason": "",
                        "translation_status": "found",
                        "translation_reason": "",
                        "translation_source_locale": "",
                    }
                else:
                    per_code[error_code] = {
                        "status": "missing",
                        "reason": "",
                        "translation_status": "missing",
                        "translation_reason": "",
                        "translation_source_locale": "",
                    }
                    missing_codes.append(error_code)

            if missing_codes and args.mode == "autofix":
                if args.dry_run:
                    for error_code in missing_codes:
                        per_code[error_code]["reason"] = "dry_run"
                        per_code[error_code]["translation_reason"] = "dry_run"
                else:
                    source_texts = []
                    for error_code in missing_codes:
                        source_text, source_locale = select_source_text(error_code, i18n_cache_by_file, locale_priority)
                        source_text_by_code[error_code] = source_text
                        source_locale_by_code[error_code] = source_locale
                        source_texts.append(source_text)

                    translated_texts = None
                    translation_batch_reason = ""
                    if args.translation_provider == "openai":
                        translated_texts, translation_batch_reason = call_openai_translate_batch(
                            source_texts,
                            target_locale_file=i18n_file.name,
                            model=args.translation_model,
                        )

                    for idx, error_code in enumerate(missing_codes):
                        source_text = source_text_by_code[error_code]
                        source_locale = source_locale_by_code[error_code]

                        translated_text = source_text
                        translation_status = "fallback_copied"
                        translation_reason = (
                            translation_batch_reason
                            if args.translation_provider == "openai"
                            else "translation_provider_none"
                        )

                        if translated_texts is not None:
                            candidate = translated_texts[idx]
                            if placeholders_signature(candidate) == placeholders_signature(source_text):
                                translated_text = candidate
                                translation_status = "created"
                                translation_reason = "openai_translated"
                            else:
                                translation_status = "fallback_copied"
                                translation_reason = "placeholder_mismatch"

                        created, collision_reason = ensure_translation(
                            i18n_data=i18n_data,
                            translation_kind=translation_kind,
                            entry_lambda=entry_lambda,
                            error_code=error_code,
                            translated_text=translated_text,
                            apply_changes=True,
                        )

                        if collision_reason:
                            per_code[error_code]["status"] = "skipped"
                            per_code[error_code]["reason"] = collision_reason
                            per_code[error_code]["translation_status"] = "skipped"
                            per_code[error_code]["translation_reason"] = collision_reason
                            per_code[error_code]["translation_source_locale"] = source_locale
                        elif created:
                            per_code[error_code]["status"] = "created"
                            per_code[error_code]["reason"] = ""
                            per_code[error_code]["translation_status"] = translation_status
                            per_code[error_code]["translation_reason"] = translation_reason
                            per_code[error_code]["translation_source_locale"] = source_locale
                            changed_i18n_files.add(i18n_key)

            for error_code in all_error_codes:
                downstream_lambda = ""
                if error_code in downstream_codes and error_code not in entry_error_codes:
                    downstream_lambda = "one-hop-downstream"

                for field in sorted(entry_fields):
                    rows.append(
                        {
                            "frontend_project": args.frontend_project,
                            "entry_lambda": entry_lambda,
                            "resolved_lambda_path": str(entry_path),
                            "downstream_lambda": downstream_lambda,
                            "error_code": error_code,
                            "field": field,
                            "translation_path": translation_path,
                            "status": per_code[error_code]["status"],
                            "language_file": i18n_key,
                            "reason": per_code[error_code]["reason"],
                            "translation_provider": args.translation_provider,
                            "translation_model": args.translation_model,
                            "translation_source_locale": per_code[error_code]["translation_source_locale"],
                            "translation_status": per_code[error_code]["translation_status"],
                            "translation_reason": per_code[error_code]["translation_reason"],
                        }
                    )

    if args.mode == "autofix" and not args.dry_run:
        for path_str in sorted(changed_i18n_files):
            save_i18n_file(Path(path_str), i18n_cache[path_str])

    status_counts = Counter(row.get("status", "") for row in rows)
    translation_status_counts = Counter(row.get("translation_status", "") for row in rows)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "languages": args.languages,
        "depth": args.depth,
        "projects_root": str(projects_root.resolve()),
        "frontend_project": args.frontend_project,
        "frontend_files": [str(path.resolve()) for path in frontend_files],
        "lambdas_root": str(lambdas_root.resolve()),
        "translation_provider": args.translation_provider,
        "translation_model": args.translation_model,
        "translation_source_locale_priority": locale_priority,
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
            "translation_found": translation_status_counts.get("found", 0),
            "translation_created": translation_status_counts.get("created", 0),
            "translation_fallback_copied": translation_status_counts.get("fallback_copied", 0),
            "translation_missing": translation_status_counts.get("missing", 0),
            "translation_skipped": translation_status_counts.get("skipped", 0),
        },
    }

    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
