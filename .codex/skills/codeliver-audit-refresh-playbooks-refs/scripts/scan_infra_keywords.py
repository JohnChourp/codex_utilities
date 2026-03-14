#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from path_resolution import resolve_paths

KEYWORDS = [
    "httpApi",
    "events:",
    "Schedule",
    "SQS",
    "SNS",
    "EventBridge",
    "DynamoDB",
    "S3",
    "CloudFront",
    "ApiGateway",
    "API Gateway",
]

DEFAULT_OUT_NAME = "infra-scan.md"
DEFAULT_SUFFIXES = {".js", ".ts", ".yaml", ".yml", ".json"}
DOC_SUFFIXES = {".md"}


def iter_files(root: Path, include_docs: bool):
    suffixes = set(DEFAULT_SUFFIXES)
    if include_docs:
        suffixes |= DOC_SUFFIXES
    for path in root.rglob("*"):
        if "node_modules" in path.parts:
            continue
        if path.name in {"package-lock.json", ".package-lock.json"}:
            continue
        if path.is_file() and path.suffix in suffixes:
            yield path


def scan(root: Path, limit: int, include_docs: bool):
    pattern = re.compile("|".join(re.escape(k) for k in KEYWORDS))
    results = []
    for path in iter_files(root, include_docs):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                results.append({"path": str(path), "line": i, "text": line.strip()})
                if len(results) >= limit:
                    return results
    return results


def render_text(results):
    return "\n".join([f"{r['path']}:{r['line']}: {r['text']}" for r in results])


def render_md(results, root: Path, limit: int):
    lines = [
        "# Infra keyword scan",
        "",
        f"- Root: `{root}`",
        f"- Limit: `{limit}`",
        "",
        "## Matches",
    ]
    if not results:
        lines.append("- (no matches)")
        return "\n".join(lines) + "\n"
    for item in results:
        lines.append(f"- `{item['path']}:{item['line']}` `{item['text']}`")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Scan lambdas for infra keyword hints.")
    parser.add_argument("--root", default=None, help="Backward-compatible lambdas root override.")
    parser.add_argument("--lambdas-root", default=None, help="Lambdas root override.")
    parser.add_argument("--codex-root", default=None, help="Canonical .codex root override.")
    parser.add_argument("--projects-root", default=None, help="Projects root override.")
    parser.add_argument("--os", default=None, help="Optional OS hint: macos, ubuntu, linux, windows.")
    parser.add_argument("--limit", type=int, default=200, help="Max matches to print")
    parser.add_argument("--format", choices=["text", "md", "json"], default="text")
    parser.add_argument("--include-docs", action="store_true", help="Include README/ROADMAP/docs noise in the scan.")
    parser.add_argument(
        "--out",
        nargs="?",
        const="__DEFAULT__",
        default=None,
        help="Write output to file. Default path is <codex-root>/refs/infra-scan.md.",
    )
    args = parser.parse_args()

    resolved = resolve_paths(
        os_hint=args.os,
        codex_root=Path(args.codex_root) if args.codex_root else None,
        projects_root=Path(args.projects_root) if args.projects_root else None,
        lambdas_root=Path(args.lambdas_root or args.root) if (args.lambdas_root or args.root) else None,
    )
    root = resolved.lambdas_root

    results = scan(root, args.limit, args.include_docs)

    if args.format == "json":
        output = json.dumps(results, indent=2)
    elif args.format == "md":
        output = render_md(results, root, args.limit)
    else:
        output = render_text(results)

    if args.out:
        out_path = (
            resolved.codex_root / "refs" / DEFAULT_OUT_NAME
            if args.out == "__DEFAULT__"
            else Path(args.out)
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
