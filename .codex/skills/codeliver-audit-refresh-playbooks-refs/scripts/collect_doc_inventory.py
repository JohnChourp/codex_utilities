#!/usr/bin/env python3
import argparse
from pathlib import Path


def list_md(path: Path):
    if not path.exists():
        return []
    return sorted([p.name for p in path.glob("*.md")])


def main():
    parser = argparse.ArgumentParser(description="List CodeDeliver playbooks/refs inventory.")
    parser.add_argument("--root", default="/home/dm-soft-1", help="Workspace root (default: /home/dm-soft-1)")
    args = parser.parse_args()

    root = Path(args.root)
    playbooks = root / ".codex" / "playbooks"
    refs = root / ".codex" / "refs"

    playbook_list = list_md(playbooks)
    refs_list = list_md(refs)

    print("Playbooks:")
    for name in playbook_list:
        print(f"- {name}")

    print("\nRefs:")
    for name in refs_list:
        print(f"- {name}")


if __name__ == "__main__":
    main()
