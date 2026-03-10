#!/usr/bin/env python3
import argparse
from collections import OrderedDict, defaultdict
import json
import re
from pathlib import Path

TARGET_PROJECT = "cloud-repos-panel"
METHODS = ["get", "post", "put", "delete", "patch"]

API_GATEWAYS_DEFAULT = "/Users/john/.codex/playbooks/crp-api-gateways.md"
REFS_DIR_DEFAULT = "/Users/john/.codex/refs"
INDEX_FILENAME_DEFAULT = "crp-refs-frontend-index.generated.md"

EXECUTE_API_RE = re.compile(
    r"https?://([a-z0-9]+)\.execute-api\.[^/]+/([^/\s\"'`]+)(/[^\s\"'`]+)?",
    re.IGNORECASE,
)
THIS_URL_RE = re.compile(r"""this\.(\w+)\s*\+\s*['"]([^'"]+)['"]""")
ASSIGN_URL_RE = re.compile(r"""(\w+)\s*=\s*['"](https?://[^'"]+)['"]""")


def iter_service_files(root: Path):
    base = root / TARGET_PROJECT / "src" / "app"
    if not base.exists():
        return
    for path in base.rglob("*.service.ts"):
        yield path


def detect_project(path: Path):
    return TARGET_PROJECT if TARGET_PROJECT in path.parts else None


def find_calls(text: str):
    results = []
    for method in METHODS:
        needle = f"http.{method}("
        start = 0
        while True:
            idx = text.find(needle, start)
            if idx == -1:
                break
            args_start = idx + len(needle)
            args_end = find_matching_paren(text, args_start - 1)
            if args_end == -1:
                start = args_start
                continue
            args = text[args_start:args_end].strip()
            results.append((method, idx, args))
            start = args_end + 1
    return results


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
            name = match.group(1).strip()
            api_id = match.group(2).strip()
            mapping[api_id] = name
    return mapping


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


def extract_base_url_assignments(text: str):
    base_urls = {}
    for name, value in ASSIGN_URL_RE.findall(text):
        if "execute-api" in value:
            base_urls[name] = value
    return base_urls


def resolve_url_expression(expr: str, base_urls: dict):
    if "execute-api" in expr:
        return expr
    match = THIS_URL_RE.search(expr)
    if not match:
        return expr
    var_name, suffix = match.groups()
    base_url = base_urls.get(var_name)
    if not base_url:
        return expr
    separator = "" if base_url.endswith("/") else "/"
    return f'"{base_url}{separator}{suffix}"'


def normalized_path(api_name: str, stage: str, route: str):
    if api_name and stage and route:
        return f"{api_name}/{stage}/{route}"
    return None


def to_markdown_table(rows):
    lines = ["| File | Line | Method | URL | Body |", "| --- | --- | --- | --- | --- |"]
    for row in rows:
        url = row.get("url", "")
        body = row.get("body", "")
        lines.append(
            f"| `{row['file']}` | {row['line']} | {row['method']} | `{url}` | `{body}` |"
        )
    return "\n".join(lines)


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
        if route_key not in grouped:
            grouped[route_key] = []
        grouped[route_key].append(call)

    for route_key, group_calls in grouped.items():
        heading = route_key
        lines.extend(["", f"## {heading}", ""])
        primary = group_calls[0]
        normalized = primary.get("normalized") or "(unresolved)"
        route = primary.get("route") or "(unresolved)"
        url_expr = primary.get("url") or "(unresolved)"
        lines.append(f"- Normalized: `{normalized}`")
        lines.append(f"- Method: `{primary['method'].upper()}`")
        lines.append(f"- Route: `/{route}`")
        lines.append(f"- URL: `{url_expr}`")
        lines.extend(["", "Observed request payload/options", ""])
        for call in group_calls:
            lines.append(f"Source: `{call['file']}:{call['line']}`")
            body = call.get("body") or "(none)"
            lines.append("```ts")
            lines.append(body)
            lines.append("```")
        lines.extend(["", "Observed response", "", "Response example not observed in service code."])

    return "\n".join(lines) + "\n"


def write_index(refs_dir: Path, generated_files: list):
    lines = ["# CRP frontend refs index", "", "Generated refs:"]
    for path in generated_files:
        rel = Path(path).relative_to(refs_dir)
        lines.append(f"- `{rel}`")
    content = "\n".join(lines) + "\n"
    out_path = refs_dir / INDEX_FILENAME_DEFAULT
    out_path.write_text(content, encoding="utf-8")
    return str(out_path)


def write_ref_files(rows: list, refs_dir: Path):
    by_project = defaultdict(list)
    for row in rows:
        project = row.get("project")
        if not project:
            continue
        by_project[project].append(row)

    refs_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for project, calls in by_project.items():
        output = render_refs_markdown(project, calls)
        out_path = refs_dir / f"{project}-lambdas.generated.md"
        out_path.write_text(output, encoding="utf-8")
        written.append(str(out_path))

    index_path = write_index(refs_dir, written)
    return written, index_path


def main():
    parser = argparse.ArgumentParser(
        description="Extract HttpClient calls from cloud-repos-panel services."
    )
    parser.add_argument("--root", default="/Users/john/Downloads/projects", help="Projects root")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument("--api-gateways", default=API_GATEWAYS_DEFAULT, help="API gateways playbook path")
    parser.add_argument("--write", action="store_true", help="Write markdown refs into .codex/refs")
    parser.add_argument("--refs-dir", default=REFS_DIR_DEFAULT, help="Refs output dir")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")

    api_map = load_api_map(Path(args.api_gateways))

    rows = []
    for path in iter_service_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        base_urls = extract_base_url_assignments(text)
        project = detect_project(path)
        for method, idx, args_str in find_calls(text):
            parts = split_top_level(args_str)
            raw_url = parts[0] if parts else ""
            url = resolve_url_expression(raw_url, base_urls)
            body = parts[1] if len(parts) > 1 else ""
            api_id, api_name, stage, route = parse_url(url, api_map)
            rows.append(
                {
                    "project": project,
                    "file": str(path),
                    "line": line_for_index(text, idx),
                    "method": method,
                    "url": url,
                    "body": body,
                    "raw_args": args_str,
                    "api_id": api_id,
                    "api_name": api_name,
                    "stage": stage,
                    "route": route,
                    "normalized": normalized_path(api_name, stage, route),
                }
            )

    if args.write:
        written, index_path = write_ref_files(rows, Path(args.refs_dir))
        print(json.dumps({"written": written, "index": index_path, "count": len(written)}, indent=2))
        return

    if args.format == "md":
        print(to_markdown_table(rows))
    else:
        print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
