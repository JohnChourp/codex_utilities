#!/usr/bin/env python3
from __future__ import annotations

import sys
import runpy
from pathlib import Path


def _runtime_support_dir() -> Path:
    script_path = Path(__file__).resolve()
    candidates = [
        script_path.parents[2] / ".system" / "skill-runtime-lib" / "scripts",
        script_path.parents[2] / "skill-runtime-lib" / "scripts",
        script_path.parents[3] / ".system" / "skill-runtime-lib" / "scripts",
    ]
    for candidate in candidates:
        if (candidate / "runtime_support.py").is_file():
            return candidate
    return Path()


RUNTIME_SUPPORT_DIR = _runtime_support_dir()
if str(RUNTIME_SUPPORT_DIR) not in sys.path and RUNTIME_SUPPORT_DIR != Path():
    sys.path.insert(0, str(RUNTIME_SUPPORT_DIR))

if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    if RUNTIME_SUPPORT_DIR != Path():
        from runtime_support import launch_current_skill

        raise SystemExit(launch_current_skill(script_path, sys.argv[1:]))

    main_script = script_path.parent / "main.py"
    sys.argv = [str(main_script), *sys.argv[1:]]
    runpy.run_path(str(main_script), run_name="__main__")
