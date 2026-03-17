#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import runtime_support


RUNNER_TEMPLATE = """#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _runtime_support_dir() -> Path:
    script_path = Path(__file__).resolve()
    candidates = [
        script_path.parents[2] / '.system' / 'skill-runtime-lib' / 'scripts',
        script_path.parents[2] / 'skill-runtime-lib' / 'scripts',
        script_path.parents[3] / '.system' / 'skill-runtime-lib' / 'scripts',
    ]
    for candidate in candidates:
        if (candidate / 'runtime_support.py').is_file():
            return candidate
    raise SystemExit('Unable to locate shared skill runtime support.')


RUNTIME_SUPPORT_DIR = _runtime_support_dir()
if str(RUNTIME_SUPPORT_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SUPPORT_DIR))

from runtime_support import launch_current_skill


if __name__ == '__main__':
    raise SystemExit(launch_current_skill(Path(__file__).resolve(), sys.argv[1:]))
"""


PYTHON_MAIN = """#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


if __name__ == "__main__":
    payload = {
        "argv": sys.argv[1:],
        "cwd": str(Path.cwd()),
    }
    print(json.dumps(payload))
"""

SHELL_MAIN = """#!/usr/bin/env bash
set -euo pipefail
printf 'shell:%s\\n' "$*"
"""


class RuntimeSupportTests(unittest.TestCase):
    def _create_skill(self, root: Path, name: str, supported_os: list[str] | None = None) -> Path:
        skill_dir = root / "skills" / name
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: test skill\n---\n"
        )
        (scripts_dir / "run.py").write_text(RUNNER_TEMPLATE)
        (scripts_dir / "main.py").write_text(PYTHON_MAIN)
        runtime = {
            "schema_version": 2,
            "skill_name": name,
            "execution_mode": "python_launcher",
            "supported_os": supported_os or ["macos", "linux", "windows"],
            "unsupported_behavior": "fail_fast",
            "preflight": {"cache_ttl_seconds": 600, "checks": []},
            "entrypoint": {"kind": "python", "path": "scripts/run.py"},
            "tooling": {
                "python": {
                    "macos": ["python3"],
                    "linux": ["python3"],
                    "windows": ["py", "-3"],
                }
            },
            "default_command": "main",
            "commands": [
                {
                    "name": "main",
                    "description": "main command",
                    "kind": "python",
                    "path": "scripts/main.py",
                    "args": [],
                }
            ],
            "recording": {
                "enabled_by_default": False,
                "output_dir_template": str(root / "records" / "{skill}" / "{timestamp}"),
                "artifacts": ["run.json", "command.txt", "stdout.log", "stderr.log"],
            },
        }
        (skill_dir / "skill.runtime.json").write_text(json.dumps(runtime, indent=2) + "\n")
        return skill_dir

    def _create_shell_skill(self, root: Path, name: str) -> Path:
        skill_dir = root / "skills" / name
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: shell test skill\n---\n"
        )
        (scripts_dir / "run.py").write_text(RUNNER_TEMPLATE)
        shell_script = scripts_dir / "main.sh"
        shell_script.write_text(SHELL_MAIN)
        shell_script.chmod(0o755)
        runtime = {
            "schema_version": 2,
            "skill_name": name,
            "execution_mode": "python_launcher",
            "supported_os": ["macos", "linux"],
            "unsupported_behavior": "fail_fast",
            "preflight": {
                "cache_ttl_seconds": 600,
                "checks": [{"type": "tool", "name": "bash", "install_hint": {"linux": "Install bash."}}],
            },
            "entrypoint": {"kind": "python", "path": "scripts/run.py"},
            "tooling": {"bash": {"macos": ["bash"], "linux": ["bash"]}},
            "default_command": "main",
            "commands": [
                {
                    "name": "main",
                    "description": "shell main",
                    "kind": "shell",
                    "path": "scripts/main.sh",
                    "args": [],
                }
            ],
            "recording": {
                "enabled_by_default": False,
                "output_dir_template": str(root / "records" / "{skill}" / "{timestamp}"),
                "artifacts": ["run.json", "command.txt", "stdout.log", "stderr.log"],
            },
        }
        (skill_dir / "skill.runtime.json").write_text(json.dumps(runtime, indent=2) + "\n")
        return skill_dir

    def test_load_runtime_validates(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_dir = self._create_skill(root, "demo-skill")
            runtime = runtime_support.load_runtime(skill_dir)
            self.assertEqual(runtime.payload["schema_version"], 2)

    def test_unsupported_os_fails_fast(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_dir = self._create_skill(root, "mac-only", ["macos"])
            runtime = runtime_support.load_runtime(skill_dir)
            with self.assertRaises(runtime_support.RuntimeErrorMessage):
                runtime_support.execute_skill(runtime, None, [], os_name="linux", record=False)

    def test_recording_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_dir = self._create_skill(root, "record-skill")
            runtime = runtime_support.load_runtime(skill_dir)
            exit_code = runtime_support.execute_skill(
                runtime,
                None,
                ["--flag", "value"],
                os_name="linux",
                record=True,
            )
            self.assertEqual(exit_code, 0)
            record_root = root / "records" / "record-skill"
            runs = list(record_root.iterdir())
            self.assertEqual(len(runs), 1)
            run_dir = runs[0]
            self.assertTrue((run_dir / "run.json").is_file())
            self.assertTrue((run_dir / "stdout.log").is_file())
            payload = json.loads((run_dir / "run.json").read_text())
            self.assertEqual(payload["exit_code"], 0)

    def test_shell_command_invocation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_dir = self._create_shell_skill(root, "shell-skill")
            runtime = runtime_support.load_runtime(skill_dir)
            exit_code = runtime_support.execute_skill(
                runtime,
                None,
                ["hello", "world"],
                os_name="linux",
                record=False,
            )
            self.assertEqual(exit_code, 0)

    def test_main_runner_resolves_default_command(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self._create_skill(root, "runner-skill")
            env = dict(os.environ)
            env["CODEX_HOME"] = str(root)
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parent / "run_skill.py"),
                    "runner-skill",
                    "--",
                    "--hello",
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout.strip())
            self.assertEqual(payload["argv"], ["--hello"])


if __name__ == "__main__":
    raise SystemExit(unittest.main())
