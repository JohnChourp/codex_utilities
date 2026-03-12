#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


DEFAULT_ROOT = "/home/dm-soft-1/Downloads/lambdas/codeliver_all"
DEFAULT_OUT = "/home/dm-soft-1/.codex/refs/codeliver-dynamodb-index-audit.md"

STRING_LITERAL_RE = re.compile(r"""^(['"])(.*)\1$""", re.S)
IDENTIFIER_RE = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
CONST_DECL_RE = re.compile(
    r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(.+?);",
    re.S,
)


@dataclass(frozen=True)
class Evidence:
    lambda_name: str
    file_path: str
    line: int


@dataclass
class RawUsage:
    lambda_name: str
    file_path: str
    line: int
    table_expr: str
    index_expr: str
    table_value: Optional[str]
    index_value: Optional[str]
    table_reason: Optional[str]
    index_reason: Optional[str]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit DynamoDB TableName/IndexName usage across CodeDeliver lambdas.",
    )
    parser.add_argument(
        "--root",
        default=DEFAULT_ROOT,
        help=f"Lambdas root (default: {DEFAULT_ROOT})",
    )
    parser.add_argument(
        "--mode",
        choices=["code-only", "live"],
        default="live",
        help="Audit mode: code-only extracts usage, live also verifies DynamoDB tables/indexes.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "md", "json"],
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--out",
        nargs="?",
        const=DEFAULT_OUT,
        default=None,
        help=f"Write output to file (default path when flag is present without value: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Optional AWS CLI profile override for live mode. Defaults to the active CLI identity.",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="Optional AWS region override for live mode. Defaults to the active AWS CLI configuration.",
    )
    return parser


def iter_js_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.js"):
        if "node_modules" in path.parts:
            continue
        yield path


def find_lambda_name(root: Path, file_path: Path) -> str:
    relative = file_path.relative_to(root)
    return relative.parts[0] if relative.parts else file_path.parent.name


def strip_inline_comment(expr: str) -> str:
    in_string: Optional[str] = None
    escape = False
    for idx, ch in enumerate(expr):
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
        if ch == "/" and idx + 1 < len(expr) and expr[idx + 1] == "/":
            return expr[:idx].rstrip()
    return expr.strip()


def collect_constants(text: str) -> Dict[str, str]:
    constants: Dict[str, str] = {}
    for match in CONST_DECL_RE.finditer(text):
        name = match.group(1)
        value = strip_inline_comment(match.group(2).strip())
        constants[name] = value
    return constants


def resolve_value(expr: str, constants: Dict[str, str], seen: Optional[set] = None) -> Tuple[Optional[str], Optional[str]]:
    normalized = strip_inline_comment(expr.strip()).rstrip(",")
    if not normalized:
        return None, "empty expression"

    literal_match = STRING_LITERAL_RE.match(normalized)
    if literal_match:
        return literal_match.group(2), None

    if IDENTIFIER_RE.match(normalized):
        seen = seen or set()
        if normalized in seen:
            return None, f"constant cycle: {normalized}"
        target = constants.get(normalized)
        if target is None:
            return None, f"unresolved identifier: {normalized}"
        seen.add(normalized)
        return resolve_value(target, constants, seen)

    return None, f"dynamic expression: {normalized}"


def iter_object_spans(text: str) -> Iterable[Tuple[int, int]]:
    stack: List[int] = []
    in_string: Optional[str] = None
    in_line_comment = False
    in_block_comment = False
    escape = False
    for idx, ch in enumerate(text):
        nxt = text[idx + 1] if idx + 1 < len(text) else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
            continue
        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
            continue
        if escape:
            escape = False
            continue
        if in_string:
            if ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            continue
        if ch == "/" and nxt == "/":
            in_line_comment = True
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            continue
        if ch in ("'", '"', "`"):
            in_string = ch
            continue
        if ch == "{":
            stack.append(idx)
        elif ch == "}" and stack:
            start = stack.pop()
            yield start, idx + 1


def split_top_level_chunks(body: str, absolute_body_start: int) -> List[Tuple[str, int]]:
    chunks: List[Tuple[str, int]] = []
    depth_curly = 0
    depth_square = 0
    depth_paren = 0
    in_string: Optional[str] = None
    in_line_comment = False
    in_block_comment = False
    escape = False
    chunk_start = 0

    for idx, ch in enumerate(body):
        nxt = body[idx + 1] if idx + 1 < len(body) else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
            continue
        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
            continue
        if escape:
            escape = False
            continue
        if in_string:
            if ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            continue
        if ch == "/" and nxt == "/":
            in_line_comment = True
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
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
        elif ch == "," and depth_curly == 0 and depth_square == 0 and depth_paren == 0:
            chunk = body[chunk_start:idx].strip()
            if chunk:
                chunks.append((chunk, absolute_body_start + chunk_start))
            chunk_start = idx + 1

    tail = body[chunk_start:].strip()
    if tail:
        chunks.append((tail, absolute_body_start + chunk_start))
    return chunks


def split_property(chunk: str) -> Optional[Tuple[str, str]]:
    depth_curly = 0
    depth_square = 0
    depth_paren = 0
    in_string: Optional[str] = None
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


def extract_usages(root: Path) -> Tuple[List[RawUsage], int, int]:
    usages: List[RawUsage] = []
    files = list(iter_js_files(root))
    lambda_names = {find_lambda_name(root, path) for path in files}

    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        constants = collect_constants(text)
        relative_file = str(path.relative_to(root))
        lambda_name = find_lambda_name(root, path)

        for start, end in iter_object_spans(text):
            body = text[start + 1 : end - 1]
            props: Dict[str, Tuple[str, int]] = {}
            for chunk, chunk_offset in split_top_level_chunks(body, start + 1):
                parsed = split_property(chunk)
                if not parsed:
                    continue
                key, value = parsed
                if key in {"TableName", "IndexName"} and key not in props:
                    props[key] = (value, chunk_offset)
            if "TableName" not in props or "IndexName" not in props:
                continue

            table_expr, table_offset = props["TableName"]
            index_expr, _index_offset = props["IndexName"]
            table_value, table_reason = resolve_value(table_expr, constants)
            index_value, index_reason = resolve_value(index_expr, constants)
            line = text.count("\n", 0, table_offset) + 1
            usages.append(
                RawUsage(
                    lambda_name=lambda_name,
                    file_path=relative_file,
                    line=line,
                    table_expr=table_expr,
                    index_expr=index_expr,
                    table_value=table_value,
                    index_value=index_value,
                    table_reason=table_reason,
                    index_reason=index_reason,
                )
            )

    return usages, len(lambda_names), len(files)


def run_aws_json(command: List[str], profile: Optional[str], region: Optional[str]) -> dict:
    env = os.environ.copy()
    if profile:
        env["AWS_PROFILE"] = profile
    if region:
        env["AWS_REGION"] = region
        env["AWS_DEFAULT_REGION"] = region

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "AWS CLI command failed")
    return json.loads(process.stdout)


def build_report(
    usages: List[RawUsage],
    lambda_count: int,
    file_count: int,
    mode: str,
    profile: Optional[str],
    region: Optional[str],
) -> dict:
    resolved_pairs: Dict[Tuple[str, str], List[Evidence]] = defaultdict(list)
    unresolved: List[dict] = []

    for usage in usages:
        evidence = Evidence(
            lambda_name=usage.lambda_name,
            file_path=usage.file_path,
            line=usage.line,
        )
        if usage.table_value and usage.index_value:
            resolved_pairs[(usage.table_value, usage.index_value)].append(evidence)
            continue

        unresolved.append(
            {
                "lambda": usage.lambda_name,
                "file_path": usage.file_path,
                "line": usage.line,
                "table_expr": usage.table_expr,
                "index_expr": usage.index_expr,
                "resolved_table": usage.table_value,
                "resolved_index": usage.index_value,
                "reason": "; ".join(
                    part
                    for part in [usage.table_reason, usage.index_reason]
                    if part
                ),
            }
        )

    report = {
        "mode": mode,
        "account_id": None,
        "profile": profile,
        "region": region,
        "scanned_lambdas": lambda_count,
        "scanned_js_files": file_count,
        "resolved_pair_count": len(resolved_pairs),
        "unique_tables": sorted({table for table, _index in resolved_pairs}),
        "resolved_table_index_pairs": [
            {
                "table": table,
                "index": index,
                "evidence": [
                    {
                        "lambda": ev.lambda_name,
                        "file_path": ev.file_path,
                        "line": ev.line,
                    }
                    for ev in sorted(
                        evidences,
                        key=lambda item: (item.lambda_name, item.file_path, item.line),
                    )
                ],
            }
            for (table, index), evidences in sorted(resolved_pairs.items())
        ],
        "confirmed_present": [],
        "missing_in_dynamodb": [],
        "unresolved_needs_manual_review": sorted(
            unresolved,
            key=lambda item: (item["lambda"], item["file_path"], item["line"]),
        ),
        "table_errors": [],
    }

    if mode == "code-only":
        return report

    try:
        identity = run_aws_json(["aws", "sts", "get-caller-identity", "--output", "json"], profile, region)
    except RuntimeError as exc:
        raise SystemExit(
            "Live mode requires a working AWS CLI identity. "
            f"Failed to resolve caller identity: {exc}. "
            "Re-run with valid AWS auth or use --mode code-only."
        ) from exc

    report["account_id"] = identity.get("Account")
    table_cache: Dict[str, dict] = {}
    for table in sorted({table for table, _index in resolved_pairs}):
        try:
            table_cache[table] = run_aws_json(
                ["aws", "dynamodb", "describe-table", "--table-name", table, "--output", "json"],
                profile,
                region,
            )
        except RuntimeError as exc:
            report["table_errors"].append({"table": table, "error": str(exc)})

    table_error_names = {item["table"] for item in report["table_errors"]}
    for (table, index), evidences in sorted(resolved_pairs.items()):
        rendered_evidence = [
            {
                "lambda": ev.lambda_name,
                "file_path": ev.file_path,
                "line": ev.line,
            }
            for ev in sorted(evidences, key=lambda item: (item.lambda_name, item.file_path, item.line))
        ]
        if table in table_error_names:
            continue
        table_data = table_cache[table]["Table"]
        live_indexes = {
            item["IndexName"] for item in table_data.get("GlobalSecondaryIndexes", [])
        } | {
            item["IndexName"] for item in table_data.get("LocalSecondaryIndexes", [])
        }
        target = {
            "table": table,
            "index": index,
            "evidence": rendered_evidence,
        }
        if index in live_indexes:
            report["confirmed_present"].append(target)
        else:
            report["missing_in_dynamodb"].append(target)

    return report


def render_text(report: dict) -> str:
    lines = [
        f"Mode: {report['mode']}",
        f"Account ID: {report['account_id'] or 'n/a'}",
        f"Profile: {report['profile'] or 'active AWS CLI profile'}",
        f"Region: {report['region'] or 'active AWS CLI region'}",
        f"Scanned lambdas: {report['scanned_lambdas']}",
        f"Scanned JS files: {report['scanned_js_files']}",
        f"Unique tables: {len(report['unique_tables'])}",
        f"Resolved table/index pairs: {report['resolved_pair_count']}",
        f"Confirmed present: {len(report['confirmed_present'])}",
        f"Missing in DynamoDB: {len(report['missing_in_dynamodb'])}",
        f"Unresolved needs manual review: {len(report['unresolved_needs_manual_review'])}",
        f"Table errors: {len(report['table_errors'])}",
        "",
    ]

    if report["missing_in_dynamodb"]:
        lines.append("Missing in DynamoDB:")
        for item in report["missing_in_dynamodb"]:
            evidence = ", ".join(
                f"{ev['file_path']}:{ev['line']}" for ev in item["evidence"][:3]
            )
            lines.append(f"- {item['table']} -> {item['index']} ({evidence})")
        lines.append("")

    if report["unresolved_needs_manual_review"]:
        lines.append("Unresolved needs manual review:")
        for item in report["unresolved_needs_manual_review"]:
            lines.append(
                f"- {item['file_path']}:{item['line']} table={item['table_expr']} "
                f"index={item['index_expr']} reason={item['reason']}"
            )
        lines.append("")

    if report["table_errors"]:
        lines.append("Table errors:")
        for item in report["table_errors"]:
            lines.append(f"- {item['table']}: {item['error']}")
        lines.append("")

    lines.append("Resolved table/index pairs:")
    for item in report["resolved_table_index_pairs"]:
        lines.append(f"- {item['table']} -> {item['index']}")
    return "\n".join(lines) + "\n"


def render_md(report: dict, root: Path) -> str:
    lines = [
        "# CodeDeliver DynamoDB index audit",
        "",
        f"- Root: `{root}`",
        f"- Mode: `{report['mode']}`",
        f"- Account ID: `{report['account_id'] or 'n/a'}`",
        f"- Profile: `{report['profile'] or 'active AWS CLI profile'}`",
        f"- Region: `{report['region'] or 'active AWS CLI region'}`",
        f"- Scanned lambdas: `{report['scanned_lambdas']}`",
        f"- Scanned JS files: `{report['scanned_js_files']}`",
        f"- Unique tables: `{len(report['unique_tables'])}`",
        f"- Resolved table/index pairs: `{report['resolved_pair_count']}`",
        f"- Confirmed present: `{len(report['confirmed_present'])}`",
        f"- Missing in DynamoDB: `{len(report['missing_in_dynamodb'])}`",
        f"- Unresolved needs manual review: `{len(report['unresolved_needs_manual_review'])}`",
        f"- Table errors: `{len(report['table_errors'])}`",
        "",
        "## Confirmed present",
    ]

    if report["confirmed_present"]:
        for item in report["confirmed_present"]:
            lines.append(f"- `{item['table']} -> {item['index']}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Missing in DynamoDB"])
    if report["missing_in_dynamodb"]:
        for item in report["missing_in_dynamodb"]:
            lines.append(f"- `{item['table']} -> {item['index']}`")
            for ev in item["evidence"]:
                lines.append(f"  - `{ev['file_path']}:{ev['line']}` ({ev['lambda']})")
    else:
        lines.append("- None")

    lines.extend(["", "## Unresolved needs manual review"])
    if report["unresolved_needs_manual_review"]:
        for item in report["unresolved_needs_manual_review"]:
            lines.append(
                f"- `{item['file_path']}:{item['line']}` "
                f"`table={item['table_expr']}` `index={item['index_expr']}`"
            )
            lines.append(f"  - Reason: `{item['reason']}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Table errors"])
    if report["table_errors"]:
        for item in report["table_errors"]:
            lines.append(f"- `{item['table']}`")
            lines.append(f"  - Error: `{item['error']}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Resolved table/index pairs"])
    for item in report["resolved_table_index_pairs"]:
        lines.append(f"- `{item['table']} -> {item['index']}`")
        for ev in item["evidence"][:5]:
            lines.append(f"  - `{ev['file_path']}:{ev['line']}` ({ev['lambda']})")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")

    usages, lambda_count, file_count = extract_usages(root)
    report = build_report(
        usages=usages,
        lambda_count=lambda_count,
        file_count=file_count,
        mode=args.mode,
        profile=args.profile,
        region=args.region,
    )

    if args.format == "json":
        output = json.dumps(report, indent=2)
    elif args.format == "md":
        output = render_md(report, root)
    else:
        output = render_text(report)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
