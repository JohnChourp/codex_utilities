#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re

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

DEFAULT_OUT = "/Users/john/.codex/refs/crp-infra-scan.generated.md"


def iter_files(root: Path):
    for path in root.rglob("*"):
        if "node_modules" in path.parts:
            continue
        if path.name in {"package-lock.json", ".package-lock.json"}:
            continue
        if path.is_file() and path.suffix in {".js", ".ts", ".yaml", ".yml", ".md", ".json"}:
            yield path


def scan(root: Path, limit: int):
    pattern = re.compile("|".join(re.escape(keyword) for keyword in KEYWORDS))
    results = []
    for path in iter_files(root):
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
    return "\n".join(f"{item['path']}:{item['line']}: {item['text']}" for item in results)


def render_md(results, root: Path, limit: int):
    lines = [
        "# CRP infra keyword scan",
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
    parser = argparse.ArgumentParser(description="Scan CRP lambdas for infra keyword hints.")
    parser.add_argument("--root", default="/Users/john/Downloads/lambdas/crp_all", help="CRP lambdas root")
    parser.add_argument("--limit", type=int, default=200, help="Max matches to print")
    parser.add_argument("--format", choices=["text", "md", "json"], default="text")
    parser.add_argument(
        "--out",
        nargs="?",
        const=DEFAULT_OUT,
        default=None,
        help=f"Write output to file (default: {DEFAULT_OUT})",
    )
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")

    results = scan(root, args.limit)

    if args.format == "json":
        output = json.dumps(results, indent=2)
    elif args.format == "md":
        output = render_md(results, root, args.limit)
    else:
        output = render_text(results)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
