#!/usr/bin/env python3
"""
Build a scoped validation checklist for a CodeDeliver stream-fallback rollout.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path

from audit_stream_rollout_target import audit_repo


def build_validation(repo: Path, explicit_project: str | None = None) -> dict:
    audit = audit_repo(repo, explicit_project)
    repo = repo.expanduser().resolve()

    lambda_commands = []
    if (repo / "stream_smoke.js").exists():
        lambda_commands.append(
            {
                "label": "lambda smoke test",
                "cwd": str(repo),
                "cmd": "node stream_smoke.js",
            }
        )

    eslint_targets = []
    for rel_path in ("index.js", "dynamo_db_functions.js", "stream_smoke.js"):
        if (repo / rel_path).exists():
            eslint_targets.append(rel_path)

    if eslint_targets:
        lambda_commands.append(
            {
                "label": "lambda eslint",
                "cwd": str(repo),
                "cmd": "npx eslint " + " ".join(shlex.quote(path) for path in eslint_targets),
            }
        )

    frontend_commands = []
    frontend_roots = {}
    for caller in audit["frontend_callers"]:
        project_root = caller["project_root"]
        frontend_roots.setdefault(project_root, set()).add(caller["path"])

    for project_root, caller_paths in sorted(frontend_roots.items()):
        project_root_path = Path(project_root)
        relative_paths = []
        for caller_path in sorted(caller_paths):
            try:
                relative_paths.append(str(Path(caller_path).resolve().relative_to(project_root_path.resolve())))
            except ValueError:
                relative_paths.append(caller_path)

        if relative_paths:
            frontend_commands.append(
                {
                    "label": f"frontend eslint ({project_root_path.name})",
                    "cwd": str(project_root_path),
                    "cmd": "npx eslint " + " ".join(shlex.quote(path) for path in relative_paths),
                }
            )

        if project_root_path.exists() and (project_root_path / "angular.json").exists():
            frontend_commands.append(
                {
                    "label": f"angular debug trace audit ({project_root_path.name})",
                    "cwd": str(project_root_path),
                    "cmd": f"{Path.home()}/.codex/scripts/audit_angular_debug_traces.py --project {shlex.quote(str(project_root_path))}",
                }
            )

    manual_checks = list(audit["gaps"]["infra_notes"])
    if audit["frontend_callers"]:
        manual_checks.append(
            "verify a zero-chunk NDJSON browser close retries buffered JSON instead of surfacing a stream_incomplete error"
        )
    if any(caller["features"].get("has_empty_collection_success_contract") for caller in audit["frontend_callers"]):
        manual_checks.append(
            "verify the real browser path succeeds when a valid empty collection response loses the terminal complete marker after meta"
        )

    return {
        "repo": str(repo),
        "status": audit["gaps"]["overall_status"],
        "lambda_commands": lambda_commands,
        "frontend_commands": frontend_commands,
        "manual_checks": manual_checks,
    }


def render_text(validation: dict) -> str:
    lines = [
        f"repo: {validation['repo']}",
        f"status: {validation['status']}",
        "",
        "lambda commands:",
    ]

    if not validation["lambda_commands"]:
        lines.append("- none")
    else:
        for item in validation["lambda_commands"]:
            lines.append(f"- ({item['cwd']}) {item['cmd']}")

    lines.append("")
    lines.append("frontend commands:")
    if not validation["frontend_commands"]:
        lines.append("- none")
    else:
        for item in validation["frontend_commands"]:
            lines.append(f"- ({item['cwd']}) {item['cmd']}")

    lines.append("")
    lines.append("manual checks:")
    for item in validation["manual_checks"]:
        lines.append(f"- {item}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build validation commands for a stream rollout.")
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

    validation = build_validation(Path(args.repo), args.frontend_project)
    if args.format == "json":
        print(json.dumps(validation, indent=2, sort_keys=True))
        return
    print(render_text(validation))


if __name__ == "__main__":
    main()
