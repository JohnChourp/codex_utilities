#!/usr/bin/env python3
"""
Audit a CodeDeliver frontend-facing lambda repo for the canonical
stream-with-buffered-fallback rollout.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


FAMILY_PREFIXES = {
    "codeliver-sap-": "sap",
    "codeliver-panel-": "panel",
    "codeliver-pos-": "pos",
    "codeliver-app-": "app",
}

KNOWN_PROJECTS = {
    "sap": Path.home() / "Downloads/projects/codeliver-sap",
    "panel": Path.home() / "Downloads/projects/codeliver-panel",
    "pos": Path.home() / "Downloads/projects/codeliver-pos",
    "app": Path.home() / "Downloads/projects/codeliver-app",
}

CODE_EXTENSIONS = {".ts", ".js", ".tsx", ".jsx"}
ARRAY_COLLECTION_RESPONSE_RE = re.compile(
    r"(?:class|interface)\s+\w+Response\s*\{[\s\S]{0,400}?\bsuccess\s*:\s*boolean;[\s\S]{0,400}?\b\w+\s*:\s*(?:Array<[^>]+>|[A-Za-z0-9_]+\[\]|any\[\])",
    re.MULTILINE,
)
EMPTY_COLLECTION_TOLERANCE_RE = re.compile(
    r"hasSeenMeta[\s\S]{0,4000}subscriber\.next\(\{[\s\S]{0,400}?success:\s*true[\s\S]{0,400}?(?:\[\]|empty[A-Za-z]+)",
    re.MULTILINE,
)
METHOD_SCOPE_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|static|readonly|async)\s+)*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^;=]*\)\s*(?::\s*[^{]+)?\{\s*$"
)
FUNCTION_SCOPE_RE = re.compile(r"^\s*(?:async\s+)?function\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{\s*$")
ARROW_SCOPE_RE = re.compile(
    r"^\s*(?:const|let|var)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*(?::\s*[^{=]+)?=>\s*\{\s*$"
)
CONTROL_SCOPE_NAMES = {"if", "for", "while", "switch", "catch"}
COLLECTION_LOAD_BEFORE_META_RE = re.compile(r"await\s+[A-Za-z0-9_.]*(?:scan|query|load|fetch|get|list)[A-Za-z0-9_.]*\s*\(", re.IGNORECASE)


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        return ""


def read_lines(path: Path) -> list[str]:
    return read_text(path).splitlines()


def infer_family(repo_name: str) -> str:
    for prefix, family in FAMILY_PREFIXES.items():
        if repo_name.startswith(prefix):
            return family
    return "unknown"


def run_rg(pattern: str, root: Path) -> list[dict]:
    if not root.exists():
        return []

    cmd = [
        "rg",
        "-n",
        "-S",
        "--no-heading",
        "--glob",
        "!node_modules",
        "--glob",
        "!dist",
        "--glob",
        "!www",
        pattern,
        str(root),
    ]

    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []

    hits = []
    for line in result.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        file_path, line_no, text = parts
        hits.append(
            {
                "path": file_path,
                "line": int(line_no),
                "text": text.strip(),
            }
        )
    return hits


def extract_scope_name(line: str) -> str | None:
    for pattern in (FUNCTION_SCOPE_RE, ARROW_SCOPE_RE, METHOD_SCOPE_RE):
        match = pattern.match(line)
        if not match:
            continue
        scope_name = match.group("name")
        if scope_name in CONTROL_SCOPE_NAMES:
            return None
        return scope_name
    return None


def extract_scope_block(lines: list[str], start_index: int) -> tuple[str, int]:
    brace_depth = 0
    saw_opening_brace = False
    collected_lines = []

    for index in range(start_index, len(lines)):
        line = lines[index]
        collected_lines.append(line)
        for char in line:
            if char == "{":
                brace_depth += 1
                saw_opening_brace = True
            elif char == "}":
                brace_depth -= 1
        if saw_opening_brace and brace_depth == 0:
            return "\n".join(collected_lines), index + 1

    return "\n".join(collected_lines), len(lines)


def find_scope_for_line(file_path: Path, line_number: int) -> dict:
    lines = read_lines(file_path)
    if not lines:
        return {
            "name": file_path.stem,
            "line": 1,
            "end_line": 1,
            "text": "",
        }

    search_index = min(max(line_number - 1, 0), len(lines) - 1)
    candidate_scope = None
    for index in range(search_index, -1, -1):
        scope_name = extract_scope_name(lines[index])
        if not scope_name:
            continue
        scope_text, end_line = extract_scope_block(lines, index)
        if end_line < line_number:
            continue
        candidate_scope = {
            "name": scope_name,
            "line": index + 1,
            "end_line": end_line,
            "text": scope_text,
        }

    if candidate_scope:
        return candidate_scope

    return {
        "name": file_path.stem,
        "line": 1,
        "end_line": len(lines),
        "text": "\n".join(lines),
    }


def detect_frontend_features(scope_text: str, file_content: str) -> dict:
    return {
        "uses_accept_ndjson": "application/x-ndjson" in scope_text
        or ("buildStreamRequestHeaders(" in scope_text and "application/x-ndjson" in file_content),
        "uses_fetch_api": bool(re.search(r"\bfetch\s*\(", scope_text)),
        "has_buffered_json_fallback": any(
            token in scope_text
            for token in (
                ".json()",
                "response.json(",
                "response.text()",
                "parseGroupsBufferedResponse",
                "parseAdminsBufferedResponse",
                "isBufferedGroupsResponse",
                "isBufferedAdminsResponse",
                "parseAdminSocketsBufferedResponse",
                "isBufferedAdminSocketsResponse",
            )
        ),
        "has_meta_seen_flag": "hasSeenMeta" in scope_text,
        "has_chunk_received_flag": bool(re.search(r"hasReceived[A-Za-z]+Chunk", scope_text)),
        "has_empty_collection_success_contract": "emitEmptyStreamSuccess" in scope_text
        or "stream_complete_missing_after_meta_empty_success" in scope_text
        or bool(
            re.search(
                r"subscriber\.next\(\{[\s\S]{0,300}?success:\s*true[\s\S]{0,300}?(?:users|groups|sockets)\s*:\s*(?:\[\]|empty[A-Za-z]+|this\.[A-Za-z0-9_]+\(\[\]\))",
                scope_text,
            )
        )
        or bool(ARRAY_COLLECTION_RESPONSE_RE.search(scope_text)),
        "has_empty_collection_tolerance": "stream_complete_missing_after_meta_empty_success" in scope_text
        or "emitEmptyStreamSuccess" in scope_text
        or bool(EMPTY_COLLECTION_TOLERANCE_RE.search(scope_text)),
        "warns_on_missing_complete": "stream_complete_missing_after_chunks" in scope_text
        or "stream_complete_missing_after_meta_empty_success" in scope_text
        or ("console.warn" in scope_text and "complete" in scope_text),
        "mentions_stream_incomplete": "stream_incomplete" in scope_text,
        "has_zero_chunk_buffered_retry": "retryBufferedStreamRequest(" in scope_text
        or "buildStreamRequestHeaders(authUser, false)" in scope_text
        or "stream_zero_chunk_retry_buffered" in scope_text,
    }


def iter_function_scopes(content: str) -> list[dict]:
    lines = content.splitlines()
    scopes = []
    index = 0

    while index < len(lines):
        scope_name = extract_scope_name(lines[index])
        if not scope_name:
            index += 1
            continue

        scope_text, end_line = extract_scope_block(lines, index)
        scopes.append(
            {
                "name": scope_name,
                "line": index + 1,
                "end_line": end_line,
                "text": scope_text,
            }
        )
        index = end_line

    return scopes


def detect_stream_scope(index_text: str) -> dict | None:
    for scope in iter_function_scopes(index_text):
        if 'type: "meta"' in scope["text"] and "writeNdjsonChunk" in scope["text"]:
            return scope
    return None


def has_meta_before_collection_load(scope_text: str) -> bool:
    meta_match = re.search(r'type\s*:\s*["\']meta["\']', scope_text)
    if not meta_match:
        return False

    pre_meta_text = scope_text[: meta_match.start()]
    return not bool(COLLECTION_LOAD_BEFORE_META_RE.search(pre_meta_text))


def build_backend_audit(repo: Path) -> dict:
    index_path = repo / "index.js"
    readme_path = repo / "README.md"
    smoke_path = repo / "stream_smoke.js"
    index_text = read_text(index_path)
    readme_text = read_text(readme_path)
    smoke_text = read_text(smoke_path)
    stream_scope = detect_stream_scope(index_text)

    handler_exports = re.findall(r"exports\.(\w+)\s*=", index_text)
    direct_stream_export = bool(re.search(r"exports\.handler\s*=\s*stream_handler\b", index_text))

    return {
        "repo_path": str(repo),
        "repo_name": repo.name,
        "family": infer_family(repo.name),
        "files_present": {
            "index_js": index_path.exists(),
            "readme_md": readme_path.exists(),
            "stream_smoke_js": smoke_path.exists(),
            "package_json": (repo / "package.json").exists(),
        },
        "backend_features": {
            "has_buffered_handler": "buffered_handler" in handler_exports or "buffered_handler" in index_text,
            "has_stream_handler": "stream_handler" in handler_exports or "stream_handler" in index_text,
            "has_raw_stream_handler": "experimental_stream_handler_raw" in handler_exports
            or "experimental_stream_handler_raw" in index_text,
            "uses_accept_ndjson_negotiation": "application/x-ndjson" in index_text
            and "accept" in index_text.lower(),
            "uses_custom_header_negotiation": "X-Codeliver-Response-Mode" in index_text,
            "has_stream_dispatch_main_handler": not direct_stream_export
            and "exports.handler" in index_text
            and (
                "wantsStreamResponse" in index_text
                or "shouldStreamResponse" in index_text
                or "application/x-ndjson" in index_text
            ),
            "has_awaited_stream_end": "endResponseStream" in index_text or "finished(" in index_text,
            "has_meta_before_collection_load": bool(stream_scope) and has_meta_before_collection_load(stream_scope["text"]),
            "has_ndjson_contract": all(
                re.search(pattern, index_text)
                for pattern in (
                    r"type\s*:\s*[\"']meta[\"']",
                    r"type\s*:\s*[\"']complete[\"']",
                    r"type\s*:\s*[\"']error[\"']",
                )
            ),
        },
        "smoke_features": {
            "has_stream_smoke": smoke_path.exists(),
            "tests_ndjson_content_type": "application/x-ndjson" in smoke_text,
            "tests_buffered_fallback": "buffered" in smoke_text.lower(),
            "tests_error_path": "error" in smoke_text.lower(),
        },
        "readme_features": {
            "mentions_accept_negotiation": "application/x-ndjson" in readme_text,
            "mentions_buffered_fallback": "buffered" in readme_text.lower()
            and "fallback" in readme_text.lower(),
            "mentions_backward_compatibility": "legacy" in readme_text.lower()
            or "backward" in readme_text.lower(),
            "mentions_stream_envs": "STREAM_PAGE_LIMIT" in readme_text
            or "STREAM_DEBUG_DELAY_MS" in readme_text,
        },
    }


def discover_frontend_callers(repo: Path, family: str, explicit_project: str | None) -> list[dict]:
    targets: list[Path] = []

    if explicit_project:
        targets.append(Path(explicit_project).expanduser().resolve())
    else:
        if family in KNOWN_PROJECTS:
            targets.append(KNOWN_PROJECTS[family])
        for root in KNOWN_PROJECTS.values():
            if root not in targets:
                targets.append(root)

    code_callers = []
    fallback_hits = []
    seen = set()
    for project_root in targets:
        for hit in run_rg(repo.name, project_root):
            file_path = Path(hit["path"])
            file_content = read_text(file_path)
            scope = find_scope_for_line(file_path, hit["line"])
            key = (hit["path"], scope["name"], scope["line"])
            if key in seen:
                continue
            seen.add(key)
            caller = {
                "project_root": str(project_root),
                "path": hit["path"],
                "line": hit["line"],
                "text": hit["text"],
                "scope_name": scope["name"],
                "scope_line": scope["line"],
                "scope_end_line": scope["end_line"],
                "features": detect_frontend_features(scope["text"], file_content),
            }
            if file_path.suffix in CODE_EXTENSIONS:
                code_callers.append(caller)
            else:
                fallback_hits.append(caller)
    return code_callers or fallback_hits


def summarize_gaps(audit: dict, callers: list[dict]) -> dict:
    backend = audit["backend_features"]
    smoke = audit["smoke_features"]
    readme = audit["readme_features"]

    backend_gaps = []
    if backend["uses_custom_header_negotiation"]:
        backend_gaps.append("replace custom-header negotiation with Accept: application/x-ndjson")
    if not backend["uses_accept_ndjson_negotiation"]:
        backend_gaps.append("add Accept-based NDJSON negotiation")
    if not backend["has_buffered_handler"]:
        backend_gaps.append("add buffered_handler compatibility path")
    if not backend["has_stream_handler"]:
        backend_gaps.append("add stream_handler path")
    if not backend["has_stream_dispatch_main_handler"]:
        backend_gaps.append("dispatch main handler between buffered and stream modes")
    if not backend["has_awaited_stream_end"]:
        backend_gaps.append("await stream end/flush before returning")
    if not backend["has_meta_before_collection_load"]:
        backend_gaps.append("emit meta before expensive collection load after auth validation")
    if not smoke["has_stream_smoke"]:
        backend_gaps.append("add stream_smoke.js")
    if smoke["has_stream_smoke"] and not smoke["tests_buffered_fallback"]:
        backend_gaps.append("cover buffered fallback in smoke test")
    if smoke["has_stream_smoke"] and not smoke["tests_error_path"]:
        backend_gaps.append("cover error path in smoke test")
    if not readme["mentions_accept_negotiation"]:
        backend_gaps.append("document Accept negotiation in README")
    if not readme["mentions_buffered_fallback"]:
        backend_gaps.append("document buffered fallback in README")

    frontend_gaps = []
    if callers:
        if any(not c["features"]["uses_accept_ndjson"] for c in callers):
            frontend_gaps.append("frontend callers do not request NDJSON via Accept")
        if any(not c["features"]["uses_fetch_api"] for c in callers):
            frontend_gaps.append("frontend callers still look non-streaming; migrate to fetch(...) where needed")
        if any(not c["features"]["has_buffered_json_fallback"] for c in callers):
            frontend_gaps.append("frontend callers are missing buffered JSON fallback")
        if any(not c["features"]["has_chunk_received_flag"] for c in callers):
            frontend_gaps.append("frontend callers are missing tolerant chunk-received completion handling")
        if any(not c["features"]["has_zero_chunk_buffered_retry"] for c in callers):
            frontend_gaps.append("frontend callers do not retry buffered JSON after zero-chunk NDJSON close")
        empty_capable_callers = [caller for caller in callers if caller["features"]["has_empty_collection_success_contract"]]
        if empty_capable_callers:
            if any(not c["features"]["has_meta_seen_flag"] for c in empty_capable_callers):
                frontend_gaps.append("empty-capable collection callers do not track meta-only completion state")
            if any(not c["features"]["has_empty_collection_tolerance"] for c in empty_capable_callers):
                frontend_gaps.append("empty-capable collection callers do not tolerate meta-only clean close as empty success")
        if any(not c["features"]["warns_on_missing_complete"] for c in callers):
            frontend_gaps.append("frontend callers do not warn on missing terminal complete marker")
    else:
        frontend_gaps.append("no real frontend callers were auto-detected; verify search scope before editing frontend code")

    infra_notes = [
        "verify API Gateway route is enabled for response streaming where the backend now streams",
        "verify CORS allowlists stay compatible with the chosen negotiation strategy",
        "do not introduce new custom headers unless API Gateway and browser CORS are updated explicitly",
    ]

    return {
        "backend_gaps": backend_gaps,
        "frontend_gaps": frontend_gaps,
        "infra_notes": infra_notes,
        "overall_status": "already-complete" if not backend_gaps and not frontend_gaps else "needs-rollout",
    }


def audit_repo(repo: Path, explicit_project: str | None = None) -> dict:
    repo = repo.expanduser().resolve()
    audit = build_backend_audit(repo)
    callers = discover_frontend_callers(repo, audit["family"], explicit_project)
    audit["frontend_callers"] = callers
    audit["gaps"] = summarize_gaps(audit, callers)
    return audit


def render_text(audit: dict) -> str:
    lines = [
        f"repo: {audit['repo_name']}",
        f"family: {audit['family']}",
        f"status: {audit['gaps']['overall_status']}",
        "",
        "backend:",
    ]
    for key, value in audit["backend_features"].items():
        lines.append(f"- {key}: {str(value).lower()}")

    lines.append("")
    lines.append("frontend callers:")
    if not audit["frontend_callers"]:
        lines.append("- none detected")
    else:
        for caller in audit["frontend_callers"]:
            lines.append(f"- {caller['path']}:{caller['scope_line']} ({caller['scope_name']})")

    lines.append("")
    lines.append("gaps:")
    for gap in audit["gaps"]["backend_gaps"] + audit["gaps"]["frontend_gaps"]:
        lines.append(f"- {gap}")

    lines.append("")
    lines.append("infra:")
    for note in audit["gaps"]["infra_notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit stream rollout readiness for a CodeDeliver lambda repo.")
    parser.add_argument("--repo", required=True, help="Absolute path to the lambda repo")
    parser.add_argument(
        "--frontend-project",
        help="Optional explicit frontend project root when auto-detection should be narrowed",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    args = parser.parse_args()

    audit = audit_repo(Path(args.repo), args.frontend_project)
    if args.format == "json":
        print(json.dumps(audit, indent=2, sort_keys=True))
        return
    print(render_text(audit))


if __name__ == "__main__":
    main()
