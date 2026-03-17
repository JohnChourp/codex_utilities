#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _runtime_support_dir() -> Path:
    script_path = Path(__file__).resolve()
    candidates = [
        script_path.parents[2] / "skill-runtime-lib" / "scripts",
        script_path.parents[3] / ".system" / "skill-runtime-lib" / "scripts",
        script_path.parents[4] / "skills" / ".system" / "skill-runtime-lib" / "scripts",
    ]
    for candidate in candidates:
        if (candidate / "runtime_support.py").is_file():
            return candidate
    raise SystemExit("Unable to locate shared skill runtime support.")


RUNTIME_SUPPORT_DIR = _runtime_support_dir()
if str(RUNTIME_SUPPORT_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SUPPORT_DIR))

from runtime_support import launch_current_skill


if __name__ == "__main__":
    raise SystemExit(launch_current_skill(Path(__file__).resolve(), sys.argv[1:]))
