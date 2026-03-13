#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _main(argv: list[str]) -> int:
    from simulation_emergency_audit import main as audit_main
    from test_runner import main as test_main

    if len(argv) < 2:
      print("Usage: run.py <audit|test> [...args]", file=sys.stderr)
      return 2

    command = argv[1].strip().lower()
    if command == "audit":
      return audit_main(argv[2:])
    if command == "test":
      return test_main(argv[2:])

    print(f"Unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))

