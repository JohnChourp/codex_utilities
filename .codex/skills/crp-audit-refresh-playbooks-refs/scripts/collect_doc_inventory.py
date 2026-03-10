#!/usr/bin/env python3
import argparse
from pathlib import Path


PLAYBOOK_PATTERNS = ["crp-*.md"]
REF_PATTERNS = [
    "crp-*.md",
    "cloud-repos-panel-lambdas*.md",
    "crp-refs-frontend-index.generated.md",
]


def list_matching(path: Path, patterns: list[str]):
    if not path.exists():
        return []

    names = set()
    for pattern in patterns:
        for entry in path.glob(pattern):
            if entry.is_file():
                names.add(entry.name)
    return sorted(names)


def main():
    parser = argparse.ArgumentParser(description="List CRP playbooks/refs inventory.")
    parser.add_argument("--root", default="/Users/john", help="Workspace root (default: /Users/john)")
    args = parser.parse_args()

    root = Path(args.root)
    playbooks = root / ".codex" / "playbooks"
    refs = root / ".codex" / "refs"

    playbook_list = list_matching(playbooks, PLAYBOOK_PATTERNS)
    refs_list = list_matching(refs, REF_PATTERNS)

    print("Playbooks:")
    if playbook_list:
        for name in playbook_list:
            print(f"- {name}")
    else:
        print("- (none)")

    print("\nRefs:")
    if refs_list:
        for name in refs_list:
            print(f"- {name}")
    else:
        print("- (none)")


if __name__ == "__main__":
    main()
