#!/usr/bin/env python3
"""Validate a skill using the shared runtime validator."""

from __future__ import annotations

from pathlib import Path
import sys

RUNTIME_SUPPORT_DIR = (
    Path(__file__).resolve().parents[2] / "skill-runtime-lib" / "scripts"
)
if str(RUNTIME_SUPPORT_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SUPPORT_DIR))

from runtime_support import validate_skill


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: python quick_validate.py <skill_directory>")
        return 1

    issues = validate_skill(argv[0])
    if not issues:
        print("Skill runtime validation passed.")
        return 0

    for issue in issues:
        print(issue.format(), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
