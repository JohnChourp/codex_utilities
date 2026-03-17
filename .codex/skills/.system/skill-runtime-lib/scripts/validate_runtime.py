#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from runtime_support import load_runtime


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: validate_runtime.py <skill-directory>", file=sys.stderr)
        return 2

    skill_dir = Path(argv[0]).expanduser().resolve()
    load_runtime(skill_dir)
    print(f"Runtime is valid: {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
