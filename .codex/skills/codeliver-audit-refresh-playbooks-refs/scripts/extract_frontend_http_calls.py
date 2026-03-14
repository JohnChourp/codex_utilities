#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Optional

from path_resolution import resolve_paths

TARGET_PROJECTS = [
    "codeliver-app",
    "codeliver-pos",
    "codeliver-panel",
    "codeliver-sap",
]

METHODS = ["get", "post", "put", "delete", "patch"]
INDEX_FILENAME_DEFAULT = "refs-frontend-index.generated.md"

CALL_RE = re.compile(
    r"(?P<client>this\.http|CapacitorHttp)\s*\.\s*(?P<method>get|post|put|delete|patch)\s*(?:<[^()]*>)?\s*\(",
    re.IGNORECASE | re.MULTILINE,
)
EXECUTE_API_RE = re.compile(
    r"https?://([a-z0-9]+)\.execute-api\.[^/]+/([^/\s\"'`]+)(/[^\s\"'`]+)?",
    re.IGNORECASE,
)
DIRECT_ASSIGNMENT_RE = re.compile(
    r"(?:^|[;\n])\s*(?:(?:const|let|var|private|public|protected|readonly|static)\s+)*"
    r"(?:(?:this\.)?(?P<name>[A-Za-z_$][A-Za-z0-9_$]*))\s*=\s*(?P<expr>.+?);",
    re.MULTILINE | re.DOTALL,
)
PIPE_CALLBACK_RE = re.compile(
    r"\b(?:tap|map|switchMap|mergeMap|concatMap|catchError)\s*\(\s*(?:async\s*)?\(\s*([A-Za-z_$][A-Za-z0-9_$]*)",
    re.MULTILINE,
)
IN_OPERATOR_RE = r"""["']([A-Za-z_$][A-Za-z0-9_$]*)["']\s+in\s+{param}\b"""


def iter_service_files(root: Path):
    for project in TARGET_PROJECTS:
        base = root / "codeliver" / project / "src" / "app"
        if not base.exists():
            continue
        for path in base.rglob("*.service.ts"):
            yield path


def detect_project(path: Path):
    parts = path.parts
    for idx, part in enumerate(parts):
        if part == "codeliver" and idx + 1 < len(parts):
            candidate = parts[idx + 1]
            if candidate in TARGET_PROJECTS:
                return candidate
    return None


def find_matching_paren(text: str, open_idx: int) -> int:
    depth = 0
    in_string = None
    escape = False
    for i in range(open_idx, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if in_string:
            if ch == in_string:
                in_string = None
            continue
        if ch in ("'", '"', "`"):
            in_string = ch
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def split_top_level(args: str):
    parts = []
    buf = []
    depth = 0
    in_string = None
    escape = False
    for ch in args:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == "\\":
            buf.append(ch)
            escape = True
            continue
        if in_string:
            buf.append(ch)
            if ch == in_string:
                in_string = None
            continue
        if ch in ("'", '"', "`"):
            buf.append(ch)
            in_string = ch
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


def split_property(chunk: str) -> Optional[tuple[str, str]]:
    normalized = chunk.strip().rstrip(",")
    if re.match(r"^(?:this\.)?[A-Za-z_$][A-Za-z0-9_$]*$", normalized):
        key = normalized.split(".")[-1]
        return key, normalized

    depth_curly = 0
    depth_square = 0
    depth_paren = 0
    in_string = None
    escape = False
    for idx, ch in enumerate(chunk):
        if escape:
            escape = False
            continue
        if in_string:
            if ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            continue
        if ch in ("'", '"', "`"):
            in_string = ch
            continue
        if ch == "{":
            depth_curly += 1
        elif ch == "}":
            depth_curly -= 1
        elif ch == "[":
            depth_square += 1
        elif ch == "]":
            depth_square -= 1
        elif ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
        elif ch == ":" and depth_curly == 0 and depth_square == 0 and depth_paren == 0:
            key = chunk[:idx].strip().strip("'\"")
            value = chunk[idx + 1 :].strip()
            return key, value
    return None


def line_for_index(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def load_api_map(path: Path):
    mapping = {}
    if not path.exists():
        return mapping
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("### "):
            continue
        match = re.match(r"###\s+(.+?)\s+\(([^)]+)\)", line)
        if match:
            mapping[match.group(2).strip()] = match.group(1).strip()
    return mapping


def collect_assignments(text: str):
    assignments = {}
    for match in DIRECT_ASSIGNMENT_RE.finditer(text):
        name = match.group("name")
        expr = match.group("expr").strip()
        assignments[name] = expr
        assignments[f"this.{name}"] = expr
    return assignments


def extract_execute_api_url(expr: str):
    if "execute-api" in expr:
        match = EXECUTE_API_RE.search(expr)
        if match:
            return match.group(0)
    literals = re.findall(r"['\"]([^'\"]+)['\"]", expr)
    for literal in literals:
        if "execute-api" in literal:
            match = EXECUTE_API_RE.search(literal)
            if match:
                return match.group(0)
    return None


def combine_base_url(base_expr: str, suffix: str, assignments: dict, depth: int):
    base_value = resolve_url_expression(base_expr, assignments, depth + 1)
    if not base_value:
        return None
    base_url = extract_execute_api_url(base_value) or base_value.strip("'\"")
    separator = "" if base_url.endswith("/") or suffix.startswith("/") else "/"
    return f'"{base_url}{separator}{suffix}"'


def resolve_url_expression(expr: str, assignments: dict, depth: int = 0):
    normalized = expr.strip()
    if not normalized or depth > 5:
        return normalized
    if extract_execute_api_url(normalized):
        return normalized
    if normalized in assignments:
        return resolve_url_expression(assignments[normalized], assignments, depth + 1)
    if normalized.startswith("this.") and normalized in assignments:
        return resolve_url_expression(assignments[normalized], assignments, depth + 1)

    concat_match = re.match(
        r"""^(this\.[A-Za-z_$][A-Za-z0-9_$]*|[A-Za-z_$][A-Za-z0-9_$]*)\s*\+\s*['"]([^'"]+)['"]$""",
        normalized,
    )
    if concat_match:
        return combine_base_url(concat_match.group(1), concat_match.group(2), assignments, depth)

    return normalized


def extract_route_literal(expr: str):
    literals = re.findall(r"['\"]([^'\"]+)['\"]", expr)
    if literals:
        return literals[-1]
    return None


def parse_url(expr: str, api_map: dict):
    api_id = None
    api_name = None
    stage = None
    route = None
    url = extract_execute_api_url(expr)
    if url:
        match = EXECUTE_API_RE.search(url)
        if match:
            api_id = match.group(1)
            stage = match.group(2)
            route = (match.group(3) or "").lstrip("/")
    if route:
        route = route.split("?")[0]
    if not route:
        route_literal = extract_route_literal(expr)
        if route_literal:
            route = route_literal.lstrip("/").split("?")[0]
    if api_id:
        api_name = api_map.get(api_id)
    return api_id, api_name, stage, route


def normalized_path(api_name: str, stage: str, route: str):
    if api_name and stage and route:
        return f"{api_name}/{stage}/{route}"
    return None


def find_calls(text: str):
    results = []
    for match in CALL_RE.finditer(text):
        method = match.group("method").lower()
        client = match.group("client")
        open_idx = match.end() - 1
        args_end = find_matching_paren(text, open_idx)
        if args_end == -1:
            continue
        args = text[open_idx + 1 : args_end].strip()
        results.append(
            {
                "method": method,
                "client": client,
                "idx": match.start(),
                "args": args,
                "args_end": args_end,
            }
        )
    return results


def extract_object_properties(expr: str):
    normalized = expr.strip()
    if not normalized.startswith("{") or not normalized.endswith("}"):
        return {}
    body = normalized[1:-1]
    properties = {}
    for chunk in split_top_level(body):
        parsed = split_property(chunk)
        if parsed:
            properties[parsed[0]] = parsed[1]
    return properties


def extract_call_payload(call: dict, assignments: dict):
    parts = split_top_level(call["args"])
    if call["client"] == "CapacitorHttp":
        properties = extract_object_properties(parts[0]) if parts else {}
        raw_url = properties.get("url", "")
        url = resolve_url_expression(raw_url, assignments)
        body = properties.get("data") or properties.get("body") or ""
        return url, body

    raw_url = parts[0] if parts else ""
    url = resolve_url_expression(raw_url, assignments)
    if call["method"] in {"post", "put", "patch"}:
        body = parts[1] if len(parts) > 1 else ""
    else:
        body = ""
    return url, body


def extract_response_fields(text: str, args_end: int):
    tail = text[args_end:]
    boundary_match = re.search(r"\n\s{2}[A-Za-z_$][A-Za-z0-9_$]*\s*\(", tail[1:])
    if boundary_match:
        snippet = tail[: boundary_match.start() + 1]
    else:
        snippet = tail[:2200]
    fields = []
    for param in PIPE_CALLBACK_RE.findall(snippet):
        direct_pattern = re.compile(rf"\b{re.escape(param)}(?:\?\.|\.)\s*([A-Za-z_$][A-Za-z0-9_$]*)")
        for match in direct_pattern.finditer(snippet):
            field = match.group(1)
            if field not in fields:
                fields.append(field)
        in_pattern = re.compile(IN_OPERATOR_RE.format(param=re.escape(param)))
        for match in in_pattern.finditer(snippet):
            field = match.group(1)
            if field not in fields:
                fields.append(field)
    return fields[:12]


def format_response_example(fields: list[str]) -> str:
    if not fields:
        return "Response example not observed in service code."
    joined = ", ".join(fields)
    return "{ " + joined + " }"


def to_markdown_table(rows):
    lines = ["| File | Line | Method | URL | Body | Response |", "| --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        lines.append(
            f"| `{row['file']}` | {row['line']} | {row['method']} | `{row.get('url', '')}` | "
            f"`{row.get('body', '')}` | `{', '.join(row.get('response_fields', [])) or 'not-observed'}` |"
        )
    return "\n".join(lines)


def render_summary(rows: list[dict]) -> str:
    lines = [
        f"calls={len(rows)}",
        f"resolved={sum(1 for row in rows if row.get('normalized'))}",
        f"unresolved={sum(1 for row in rows if not row.get('normalized'))}",
    ]
    by_project = OrderedDict()
    for project in TARGET_PROJECTS:
        project_rows = [row for row in rows if row.get("project") == project]
        if not project_rows:
            continue
        unique_routes = OrderedDict()
        for row in project_rows:
            key = row.get("normalized") or row.get("route") or f"{row['method']}:{row['line']}"
            unique_routes[key] = True
        lines.append(
            f"{project}: calls={len(project_rows)} unique={len(unique_routes)} observed_response={sum(1 for row in project_rows if row.get('response_fields'))}"
        )
    return "\n".join(lines) + "\n"


def render_refs_markdown(project: str, calls: list):
    title = f"# {project} frontend -> HTTP lambdas"
    purpose = (
        "Purpose: Document HTTP lambdas called from the frontend (from *.service.ts) "
        "with normalized paths and observed payloads/responses."
    )

    api_ids = OrderedDict()
    sources = OrderedDict()
    for call in calls:
        if call.get("api_id") and call.get("api_name"):
            api_ids[call["api_id"]] = call["api_name"]
        sources[call["file"]] = True

    lines = [title, "", purpose, "", "## API Ids -> API Names"]
    if api_ids:
        for api_id, api_name in api_ids.items():
            lines.append(f"- `{api_id}` -> `{api_name}`")
    else:
        lines.append("- (no API ids resolved)")

    lines.extend(["", "## Sources"])
    for path in sources.keys():
        lines.append(f"- `{path}`")

    grouped = OrderedDict()
    for call in calls:
        route_key = call.get("route") or f"unresolved-{call['method']}-{call['line']}"
        grouped.setdefault(route_key, []).append(call)

    for route_key, group_calls in grouped.items():
        primary = group_calls[0]
        lines.extend(["", f"## {route_key}", ""])
        lines.append(f"- Normalized: `{primary.get('normalized') or '(unresolved)'}`")
        lines.append(f"- Method: `{primary['method'].upper()}`")
        lines.append(f"- Route: `/{primary.get('route') or '(unresolved)'}`")
        lines.append(f"- URL: `{primary.get('url') or '(unresolved)'}`")
        lines.extend(["", "Observed request payload/options", ""])
        for call in group_calls:
            lines.append(f"Source: `{call['file']}:{call['line']}`")
            lines.append("```ts")
            lines.append(call.get("body") or "(none)")
            lines.append("```")
        lines.extend(["", "Observed response", ""])
        response_fields = []
        for call in group_calls:
            for field in call.get("response_fields", []):
                if field not in response_fields:
                    response_fields.append(field)
        if response_fields:
            lines.append("```ts")
            lines.append(format_response_example(response_fields))
            lines.append("```")
        else:
            lines.append("Response example not observed in service code.")

    return "\n".join(lines) + "\n"


def write_index(refs_dir: Path, generated_files: list):
    lines = ["# Frontend refs index", "", "Generated refs:"]
    for path in generated_files:
        rel = Path(path).relative_to(refs_dir)
        lines.append(f"- `{rel}`")
    out_path = refs_dir / INDEX_FILENAME_DEFAULT
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(out_path)


def write_ref_files(rows: list[dict], refs_dir: Path):
    by_project = defaultdict(list)
    for row in rows:
        if row.get("project"):
            by_project[row["project"]].append(row)

    refs_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for project, calls in by_project.items():
        out_path = refs_dir / f"{project}-lambdas.generated.md"
        out_path.write_text(render_refs_markdown(project, calls), encoding="utf-8")
        written.append(str(out_path))
    index_path = write_index(refs_dir, written)
    return written, index_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract frontend HTTP calls from CodeDeliver services.")
    parser.add_argument("--root", default=None, help="Backward-compatible projects root override.")
    parser.add_argument("--projects-root", default=None, help="Projects root override.")
    parser.add_argument("--codex-root", default=None, help="Canonical .codex root override.")
    parser.add_argument("--lambdas-root", default=None, help="Lambdas root override.")
    parser.add_argument("--os", default=None, help="Optional OS hint: macos, ubuntu, linux, windows.")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument("--summary", action="store_true", help="Print compact audit-first summary output.")
    parser.add_argument("--api-gateways", default=None, help="API gateways playbook path override.")
    parser.add_argument("--write", action="store_true", help="Write markdown refs into .codex/refs")
    parser.add_argument("--refs-dir", default=None, help="Refs output dir override")
    args = parser.parse_args()

    resolved = resolve_paths(
        os_hint=args.os,
        codex_root=Path(args.codex_root) if args.codex_root else None,
        projects_root=Path(args.projects_root or args.root) if (args.projects_root or args.root) else None,
        lambdas_root=Path(args.lambdas_root) if args.lambdas_root else None,
    )

    api_gateway_path = Path(args.api_gateways) if args.api_gateways else resolved.codex_root / "playbooks" / "codeliver-api-gateways.md"
    refs_dir = Path(args.refs_dir) if args.refs_dir else resolved.codex_root / "refs"
    api_map = load_api_map(api_gateway_path)

    rows = []
    for path in iter_service_files(resolved.projects_root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        assignments = collect_assignments(text)
        project = detect_project(path)
        for call in find_calls(text):
            url, body = extract_call_payload(call, assignments)
            api_id, api_name, stage, route = parse_url(url, api_map)
            rows.append(
                {
                    "project": project,
                    "file": str(path),
                    "line": line_for_index(text, call["idx"]),
                    "method": call["method"],
                    "client": call["client"],
                    "url": url,
                    "body": body,
                    "api_id": api_id,
                    "api_name": api_name,
                    "stage": stage,
                    "route": route,
                    "normalized": normalized_path(api_name, stage, route),
                    "response_fields": extract_response_fields(text, call["args_end"]),
                }
            )

    if args.write:
        written, index_path = write_ref_files(rows, refs_dir)
        print(json.dumps({"written": written, "index": index_path, "count": len(written)}, indent=2))
        return 0

    if args.summary:
        print(render_summary(rows), end="")
        return 0

    if args.format == "md":
        print(to_markdown_table(rows))
    else:
        print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
