#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


DEFAULT_ROOT = str(Path.home() / "Downloads" / "lambdas" / "crp_all")
DEFAULT_OUTPUT = str(Path.home() / "Downloads" / "lambdas" / "crp_all" / "outdated-dependencies-report.json")


def _shared_scripts_dir() -> Path:
    script_path = Path(__file__).resolve()
    candidate = script_path.parents[2] / ".system" / "outdated-lambda-deps-shared" / "scripts"
    if (candidate / "outdated_lambda_deps.py").is_file():
        return candidate
    raise SystemExit("Unable to locate shared outdated dependency scanner.")


SHARED_SCRIPTS_DIR = _shared_scripts_dir()
if str(SHARED_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_SCRIPTS_DIR))

from outdated_lambda_deps import main as shared_main


if __name__ == "__main__":
    raise SystemExit(shared_main(DEFAULT_ROOT, DEFAULT_OUTPUT, sys.argv[1:]))
