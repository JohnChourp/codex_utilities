#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from path_resolution import resolve_paths


def list_md(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted([p.name for p in path.glob("*.md")])


def main() -> int:
    parser = argparse.ArgumentParser(description="List CodeDeliver playbooks/refs inventory.")
    parser.add_argument("--root", default=None, help="Backward-compatible workspace root override.")
    parser.add_argument("--codex-root", default=None, help="Canonical .codex root override.")
    parser.add_argument("--projects-root", default=None, help="Projects root override.")
    parser.add_argument("--lambdas-root", default=None, help="Lambdas root override.")
    parser.add_argument("--os", default=None, help="Optional OS hint: macos, ubuntu, linux, windows.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--verbose", action="store_true", help="Print full playbook/ref file lists.")
    args = parser.parse_args()

    explicit_codex = Path(args.codex_root) if args.codex_root else None
    if not explicit_codex and args.root:
        explicit_codex = Path(args.root) / ".codex"

    resolved = resolve_paths(
        os_hint=args.os,
        codex_root=explicit_codex,
        projects_root=Path(args.projects_root) if args.projects_root else None,
        lambdas_root=Path(args.lambdas_root) if args.lambdas_root else None,
    )

    playbooks = resolved.codex_root / "playbooks"
    refs = resolved.codex_root / "refs"
    playbook_list = list_md(playbooks)
    refs_list = list_md(refs)

    payload = {
        "codex_root": str(resolved.codex_root),
        "playbook_count": len(playbook_list),
        "ref_count": len(refs_list),
        "playbooks": playbook_list if args.verbose else [],
        "refs": refs_list if args.verbose else [],
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Codex root: {resolved.codex_root}")
    print(f"Playbooks: {len(playbook_list)}")
    print(f"Refs: {len(refs_list)}")
    if args.verbose:
        print("")
        print("Playbooks:")
        for name in playbook_list:
            print(f"- {name}")
        print("")
        print("Refs:")
        for name in refs_list:
            print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
