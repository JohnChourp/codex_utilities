#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from path_resolution import resolve_paths


def list_md(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(item.name for item in path.glob("*.md"))


def run_script(script_path: Path, *args: str) -> str:
    command = [sys.executable, str(script_path), *args]
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        stderr = process.stderr.strip() or process.stdout.strip() or f"{script_path.name} failed"
        raise SystemExit(stderr)
    return process.stdout.strip()


def parse_summary_block(text: str) -> dict[str, str]:
    payload = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        payload[key.strip()] = value.strip()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a compact CodeDeliver audit fast path.")
    parser.add_argument("--os", default=None, help="Optional OS hint: macos, ubuntu, linux, windows.")
    parser.add_argument("--codex-root", default=None, help="Canonical .codex root override.")
    parser.add_argument("--projects-root", default=None, help="Projects root override.")
    parser.add_argument("--lambdas-root", default=None, help="Lambdas root override.")
    parser.add_argument("--include-dynamodb", action="store_true", help="Include DynamoDB index audit.")
    parser.add_argument("--dynamodb-mode", choices=["code-only", "live"], default="code-only")
    parser.add_argument("--include-infra", action="store_true", help="Include infra keyword scan.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    resolved = resolve_paths(
        os_hint=args.os,
        codex_root=Path(args.codex_root) if args.codex_root else None,
        projects_root=Path(args.projects_root) if args.projects_root else None,
        lambdas_root=Path(args.lambdas_root) if args.lambdas_root else None,
    )

    frontend_summary = parse_summary_block(
        run_script(
            script_dir / "extract_frontend_http_calls.py",
            "--summary",
            "--os",
            resolved.os_name,
            "--codex-root",
            str(resolved.codex_root),
            "--projects-root",
            str(resolved.projects_root),
            "--lambdas-root",
            str(resolved.lambdas_root),
        )
    )

    payload = {
        "mode": "audit-fast",
        "os": resolved.os_name,
        "codex_root": str(resolved.codex_root),
        "projects_root": str(resolved.projects_root),
        "lambdas_root": str(resolved.lambdas_root),
        "playbooks": len(list_md(resolved.codex_root / "playbooks")),
        "refs": len(list_md(resolved.codex_root / "refs")),
        "frontend_summary": frontend_summary,
        "dynamodb": "skipped",
        "infra": "skipped",
    }

    if args.include_dynamodb:
        payload["dynamodb"] = run_script(
            script_dir / "audit_dynamodb_indexes.py",
            "--mode",
            args.dynamodb_mode,
            "--os",
            resolved.os_name,
            "--codex-root",
            str(resolved.codex_root),
            "--projects-root",
            str(resolved.projects_root),
            "--lambdas-root",
            str(resolved.lambdas_root),
        )

    if args.include_infra:
        payload["infra"] = run_script(
            script_dir / "scan_infra_keywords.py",
            "--os",
            resolved.os_name,
            "--codex-root",
            str(resolved.codex_root),
            "--projects-root",
            str(resolved.projects_root),
            "--lambdas-root",
            str(resolved.lambdas_root),
            "--limit",
            "50",
        )

    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return 0

    print("mode=audit-fast")
    print(f"os={payload['os']}")
    print(f"codex_root={payload['codex_root']}")
    print(f"projects_root={payload['projects_root']}")
    print(f"lambdas_root={payload['lambdas_root']}")
    print(f"playbooks={payload['playbooks']}")
    print(f"refs={payload['refs']}")
    for key, value in payload["frontend_summary"].items():
        print(f"frontend.{key}={value}")
    if args.include_dynamodb:
        print("")
        print(payload["dynamodb"])
    else:
        print("dynamodb=skipped")
    if args.include_infra:
        print("")
        print(payload["infra"])
    else:
        print("infra=skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
