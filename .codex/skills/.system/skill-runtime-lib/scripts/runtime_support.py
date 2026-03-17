#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_OS = {"macos", "linux", "windows"}
ALLOWED_EXECUTION_MODES = {"guidance", "python", "python_launcher", "shell"}
ALLOWED_COMMAND_KINDS = {"python", "shell"}
DEFAULT_RECORDING_TEMPLATE = "~/.codex/tmp/skill-runs/{skill}/{timestamp}"


@dataclass(frozen=True)
class Invocation:
    skill_name: str | None
    command_name: str | None
    os_name: str | None
    record: bool
    list_commands: bool
    extra_args: list[str]


@dataclass(frozen=True)
class SkillRuntime:
    skill_dir: Path
    payload: dict[str, Any]


class RuntimeErrorMessage(Exception):
    pass


def detect_os_name() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    return "linux"


def normalize_os_name(value: str | None) -> str:
    if not value:
        return detect_os_name()
    lowered = value.strip().lower()
    if lowered in {"mac", "macos", "darwin", "osx"}:
        return "macos"
    if lowered in {"linux", "ubuntu"}:
        return "linux"
    if lowered in {"windows", "win", "win32"}:
        return "windows"
    raise RuntimeErrorMessage(f"Unsupported OS hint: {value}")


def _candidate_roots(start: Path) -> list[Path]:
    roots = []
    env_root = os.environ.get("CODEX_HOME")
    if env_root:
        roots.append(Path(env_root).expanduser())
    for current in [start, *start.parents]:
        roots.append(current)
        roots.append(current / ".codex")
    roots.append(Path.home() / ".codex")
    return roots


def find_codex_root(start: Path | None = None) -> Path:
    base = (start or Path.cwd()).resolve()
    for candidate in _candidate_roots(base):
        skills_dir = candidate / "skills"
        if skills_dir.is_dir():
            return candidate
    raise RuntimeErrorMessage("Unable to resolve CODEX_HOME / .codex root.")


def skills_root(codex_root: Path) -> Path:
    return codex_root / "skills"


def _iter_skill_dirs(root: Path):
    for child in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if child.is_dir():
            yield child


def resolve_skill_dir(skill_name: str, codex_root: Path) -> Path:
    requested = skill_name.strip()
    if not requested:
        raise RuntimeErrorMessage("Skill name is required.")

    direct_candidates = [
        skills_root(codex_root) / requested,
        skills_root(codex_root) / ".system" / requested,
    ]
    for candidate in direct_candidates:
        if candidate.is_dir():
            return candidate

    folded = requested.lower()
    matches: list[Path] = []
    for scope in [skills_root(codex_root), skills_root(codex_root) / ".system"]:
        if not scope.is_dir():
            continue
        for candidate in _iter_skill_dirs(scope):
            if candidate.name.lower() == folded:
                matches.append(candidate)

    unique = list(dict.fromkeys(matches))
    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        joined = ", ".join(str(path.relative_to(skills_root(codex_root))) for path in unique)
        raise RuntimeErrorMessage(f"Ambiguous skill name '{skill_name}': {joined}")
    raise RuntimeErrorMessage(f"Skill not found: {skill_name}")


def load_runtime(skill_dir: Path) -> SkillRuntime:
    runtime_path = skill_dir / "skill.runtime.json"
    if not runtime_path.is_file():
        raise RuntimeErrorMessage(f"Missing skill.runtime.json in {skill_dir}")
    try:
        payload = json.loads(runtime_path.read_text())
    except json.JSONDecodeError as exc:
        raise RuntimeErrorMessage(f"Invalid JSON in {runtime_path}: {exc}") from exc
    validate_runtime_payload(payload, skill_dir)
    return SkillRuntime(skill_dir=skill_dir, payload=payload)


def _ensure_relative_path(skill_dir: Path, path_value: str, label: str) -> None:
    path = Path(path_value)
    if path.is_absolute():
        raise RuntimeErrorMessage(f"{label} must be relative: {path_value}")
    resolved = (skill_dir / path).resolve()
    try:
        resolved.relative_to(skill_dir.resolve())
    except ValueError as exc:
        raise RuntimeErrorMessage(f"{label} escapes skill directory: {path_value}") from exc


def _validate_command_spec(command: dict[str, Any], skill_dir: Path, label: str) -> None:
    if not isinstance(command.get("name"), str) or not command["name"].strip():
        raise RuntimeErrorMessage(f"{label} missing a valid name")
    kind = command.get("kind")
    if kind not in ALLOWED_COMMAND_KINDS:
        raise RuntimeErrorMessage(f"{label} has unsupported kind: {kind}")
    path_value = command.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        raise RuntimeErrorMessage(f"{label} missing a valid path")
    _ensure_relative_path(skill_dir, path_value, f"{label}.path")
    if not (skill_dir / path_value).is_file():
        raise RuntimeErrorMessage(f"{label}.path not found: {path_value}")
    args = command.get("args", [])
    if args is not None and (not isinstance(args, list) or not all(isinstance(item, str) for item in args)):
        raise RuntimeErrorMessage(f"{label}.args must be an array of strings")

    os_entrypoints = command.get("os_entrypoints", {})
    if os_entrypoints is not None:
        if not isinstance(os_entrypoints, dict):
            raise RuntimeErrorMessage(f"{label}.os_entrypoints must be an object")
        for os_name, override in os_entrypoints.items():
            if os_name not in ALLOWED_OS:
                raise RuntimeErrorMessage(f"{label}.os_entrypoints has unsupported OS: {os_name}")
            if not isinstance(override, dict):
                raise RuntimeErrorMessage(f"{label}.os_entrypoints.{os_name} must be an object")
            override_copy = {
                key: value
                for key, value in command.items()
                if key not in {"os_entrypoints", "wrappers"}
            }
            override_copy.update(override)
            _validate_command_spec(override_copy, skill_dir, f"{label}.os_entrypoints.{os_name}")


def validate_runtime_payload(payload: dict[str, Any], skill_dir: Path) -> None:
    if not isinstance(payload, dict):
        raise RuntimeErrorMessage("skill.runtime.json must contain an object")

    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise RuntimeErrorMessage("schema_version must be an integer >= 1")

    execution_mode = payload.get("execution_mode")
    if execution_mode not in ALLOWED_EXECUTION_MODES:
        raise RuntimeErrorMessage(f"Unsupported execution_mode: {execution_mode}")

    supported_os = payload.get("supported_os")
    if not isinstance(supported_os, list) or not supported_os:
        raise RuntimeErrorMessage("supported_os must be a non-empty array")
    invalid_os = [item for item in supported_os if item not in ALLOWED_OS]
    if invalid_os:
        raise RuntimeErrorMessage(f"Unsupported OS values in supported_os: {', '.join(invalid_os)}")

    entrypoint = payload.get("entrypoint")
    if entrypoint is not None:
        if not isinstance(entrypoint, dict):
            raise RuntimeErrorMessage("entrypoint must be an object or null")
        if entrypoint.get("kind") not in ALLOWED_COMMAND_KINDS:
            raise RuntimeErrorMessage("entrypoint.kind must be python or shell")
        path_value = entrypoint.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            raise RuntimeErrorMessage("entrypoint.path must be a non-empty string")
        _ensure_relative_path(skill_dir, path_value, "entrypoint.path")
        if not (skill_dir / path_value).is_file():
            raise RuntimeErrorMessage(f"entrypoint.path not found: {path_value}")

    commands = payload.get("commands", [])
    if commands is None:
        commands = []
    if not isinstance(commands, list):
        raise RuntimeErrorMessage("commands must be an array")
    for index, command in enumerate(commands):
        if not isinstance(command, dict):
            raise RuntimeErrorMessage(f"commands[{index}] must be an object")
        _validate_command_spec(command, skill_dir, f"commands[{index}]")

    if execution_mode != "guidance" and not commands and entrypoint is None:
        raise RuntimeErrorMessage("Executable skills require commands[] or entrypoint")

    default_command = payload.get("default_command")
    if default_command is not None:
        if not isinstance(default_command, str) or not default_command.strip():
            raise RuntimeErrorMessage("default_command must be a non-empty string when present")
        names = {command["name"] for command in commands}
        if names and default_command not in names:
            raise RuntimeErrorMessage(f"default_command '{default_command}' is not present in commands[]")

    preflight = payload.get("preflight", {})
    if preflight is not None:
        if not isinstance(preflight, dict):
            raise RuntimeErrorMessage("preflight must be an object")
        checks = preflight.get("checks", [])
        if checks is not None:
            if not isinstance(checks, list):
                raise RuntimeErrorMessage("preflight.checks must be an array")
            for index, check in enumerate(checks):
                if not isinstance(check, dict):
                    raise RuntimeErrorMessage(f"preflight.checks[{index}] must be an object")
                if check.get("type") != "tool":
                    raise RuntimeErrorMessage(f"preflight.checks[{index}] only supports type=tool")
                if not isinstance(check.get("name"), str) or not check["name"].strip():
                    raise RuntimeErrorMessage(f"preflight.checks[{index}] requires a tool name")

    recording = payload.get("recording", {})
    if recording is not None:
        if not isinstance(recording, dict):
            raise RuntimeErrorMessage("recording must be an object")
        template = recording.get("output_dir_template")
        if template is not None and (not isinstance(template, str) or not template.strip()):
            raise RuntimeErrorMessage("recording.output_dir_template must be a non-empty string")
        artifacts = recording.get("artifacts", [])
        if artifacts is not None and (not isinstance(artifacts, list) or not all(isinstance(item, str) for item in artifacts)):
            raise RuntimeErrorMessage("recording.artifacts must be an array of strings")


def _normalize_tool_vectors(raw_value: Any, tool_name: str) -> list[list[str]]:
    if raw_value is None:
        return [[tool_name]]
    if isinstance(raw_value, list) and raw_value and all(isinstance(item, str) for item in raw_value):
        return [raw_value]
    if isinstance(raw_value, list) and all(isinstance(item, list) and item and all(isinstance(part, str) for part in item) for item in raw_value):
        return raw_value
    raise RuntimeErrorMessage(f"Invalid tooling entry for {tool_name}")


def resolve_tool_command(runtime: SkillRuntime, tool_name: str, os_name: str) -> list[str]:
    tooling = runtime.payload.get("tooling", {})
    tool_entry = tooling.get(tool_name, {})
    raw_value = None
    if isinstance(tool_entry, dict):
        raw_value = tool_entry.get(os_name, tool_entry.get("default"))
    elif tool_entry:
        raw_value = tool_entry
    for vector in _normalize_tool_vectors(raw_value, tool_name):
        binary = shutil.which(vector[0])
        if binary:
            return [binary, *vector[1:]]
    raise RuntimeErrorMessage(f"Required tool not found in PATH: {tool_name}")


def run_preflight(runtime: SkillRuntime, os_name: str) -> None:
    if os_name not in runtime.payload.get("supported_os", []):
        supported = ", ".join(runtime.payload.get("supported_os", []))
        raise RuntimeErrorMessage(
            f"Skill '{runtime.skill_dir.name}' does not support {os_name}. Supported OS: {supported}"
        )

    checks = runtime.payload.get("preflight", {}).get("checks", [])
    for check in checks:
        tool_name = check["name"]
        try:
            resolve_tool_command(runtime, tool_name, os_name)
        except RuntimeErrorMessage as exc:
            install_hint = check.get("install_hint", {})
            hint = ""
            if isinstance(install_hint, dict):
                hint = install_hint.get(os_name) or install_hint.get("default") or ""
            message = str(exc)
            if hint:
                message = f"{message}. {hint}"
            raise RuntimeErrorMessage(message) from exc


def _resolve_command_override(command: dict[str, Any], os_name: str) -> dict[str, Any]:
    resolved = dict(command)
    os_entrypoints = command.get("os_entrypoints", {})
    if isinstance(os_entrypoints, dict) and os_name in os_entrypoints:
        resolved.update(os_entrypoints[os_name])
    wrappers = command.get("wrappers", {})
    if isinstance(wrappers, dict) and os_name in wrappers:
        resolved.update(wrappers[os_name])
    return resolved


def pick_command(runtime: SkillRuntime, command_name: str | None, extra_args: list[str]) -> tuple[dict[str, Any], list[str], str]:
    commands = runtime.payload.get("commands", [])
    by_name = {command["name"]: command for command in commands}

    if command_name and command_name.startswith("-"):
        extra_args = [command_name, *extra_args]
        command_name = None

    if command_name:
        selected = by_name.get(command_name)
        if selected is None:
            available = ", ".join(sorted(by_name))
            raise RuntimeErrorMessage(f"Unknown command '{command_name}'. Available: {available}")
        return selected, extra_args, command_name

    if extra_args:
        possible_name = extra_args[0]
        if possible_name in by_name:
            return by_name[possible_name], extra_args[1:], possible_name

    default_name = runtime.payload.get("default_command")
    if default_name:
        selected = by_name.get(default_name)
        if selected is None:
            raise RuntimeErrorMessage(f"default_command '{default_name}' is not configured")
        return selected, extra_args, default_name

    entrypoint = runtime.payload.get("entrypoint")
    if entrypoint:
        return dict(entrypoint, name="entrypoint", args=entrypoint.get("args", [])), extra_args, "entrypoint"

    raise RuntimeErrorMessage("No default command available for this skill.")


def build_process_argv(runtime: SkillRuntime, command: dict[str, Any], os_name: str, extra_args: list[str]) -> list[str]:
    resolved_command = _resolve_command_override(command, os_name)
    kind = resolved_command["kind"]
    command_path = runtime.skill_dir / resolved_command["path"]
    base_args = list(resolved_command.get("args", []))

    if kind == "python":
        python_key = "python"
        if "python3" in runtime.payload.get("tooling", {}) and "python" not in runtime.payload.get("tooling", {}):
            python_key = "python3"
        python_command = resolve_tool_command(runtime, python_key, os_name)
        return [*python_command, str(command_path), *base_args, *extra_args]

    if kind == "shell":
        suffix = command_path.suffix.lower()
        if suffix == ".sh":
            shell_command = resolve_tool_command(runtime, "bash", os_name)
            return [*shell_command, str(command_path), *base_args, *extra_args]
        if suffix in {".cmd", ".bat"}:
            if os_name == "windows":
                return [str(command_path), *base_args, *extra_args]
            shell_command = resolve_tool_command(runtime, "bash", os_name)
            return [*shell_command, str(command_path), *base_args, *extra_args]
        return [str(command_path), *base_args, *extra_args]

    raise RuntimeErrorMessage(f"Unsupported command kind: {kind}")


def _record_dir(runtime: SkillRuntime, timestamp: str) -> Path:
    recording = runtime.payload.get("recording", {})
    template = recording.get("output_dir_template") or DEFAULT_RECORDING_TEMPLATE
    expanded = template.format(skill=runtime.skill_dir.name, timestamp=timestamp)
    return Path(expanded).expanduser()


def _write_recording(
    runtime: SkillRuntime,
    record_dir: Path,
    process_argv: list[str],
    os_name: str,
    command_name: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    started_at: str,
    ended_at: str,
) -> None:
    record_dir.mkdir(parents=True, exist_ok=True)
    (record_dir / "stdout.log").write_text(stdout)
    (record_dir / "stderr.log").write_text(stderr)
    (record_dir / "command.txt").write_text(shlex.join(process_argv) + "\n")
    payload = {
        "skill": runtime.skill_dir.name,
        "command": command_name,
        "os": os_name,
        "cwd": str(runtime.skill_dir),
        "started_at": started_at,
        "ended_at": ended_at,
        "exit_code": exit_code,
        "argv": process_argv,
        "artifacts": {
            "stdout": str(record_dir / "stdout.log"),
            "stderr": str(record_dir / "stderr.log"),
            "command": str(record_dir / "command.txt"),
        },
    }
    (record_dir / "run.json").write_text(json.dumps(payload, indent=2) + "\n")


def execute_skill(
    runtime: SkillRuntime,
    command_name: str | None,
    extra_args: list[str],
    os_name: str | None = None,
    record: bool = False,
) -> int:
    resolved_os = normalize_os_name(os_name)
    if runtime.payload["execution_mode"] == "guidance":
        raise RuntimeErrorMessage(
            f"Skill '{runtime.skill_dir.name}' is guidance-only and cannot be executed via run-skill."
        )

    run_preflight(runtime, resolved_os)
    command, command_extra_args, resolved_command_name = pick_command(runtime, command_name, extra_args)
    process_argv = build_process_argv(runtime, command, resolved_os, command_extra_args)

    if not record:
        completed = subprocess.run(process_argv, cwd=runtime.skill_dir)
        return completed.returncode

    started_at = datetime.now(timezone.utc).isoformat()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    record_dir = _record_dir(runtime, timestamp)
    completed = subprocess.run(
        process_argv,
        cwd=runtime.skill_dir,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    ended_at = datetime.now(timezone.utc).isoformat()
    _write_recording(
        runtime=runtime,
        record_dir=record_dir,
        process_argv=process_argv,
        os_name=resolved_os,
        command_name=resolved_command_name,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        started_at=started_at,
        ended_at=ended_at,
    )
    return completed.returncode


def list_commands(runtime: SkillRuntime) -> list[str]:
    commands = runtime.payload.get("commands", [])
    return [command["name"] for command in commands]


def parse_invocation(argv: list[str], require_skill_name: bool) -> Invocation:
    skill_name: str | None = None
    positionals: list[str] = []
    extra_args: list[str] = []
    os_name: str | None = None
    record = False
    list_commands_flag = False

    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--":
            extra_args = argv[index + 1 :]
            break
        if token in {"-h", "--help"}:
            raise RuntimeErrorMessage("help")
        if token == "--record":
            record = True
            index += 1
            continue
        if token == "--list-commands":
            list_commands_flag = True
            index += 1
            continue
        if token == "--os":
            if index + 1 >= len(argv):
                raise RuntimeErrorMessage("--os requires a value")
            os_name = argv[index + 1]
            index += 2
            continue
        positionals.append(token)
        index += 1

    if require_skill_name:
        if not positionals:
            raise RuntimeErrorMessage("Skill name is required.")
        skill_name = positionals[0]
        positionals = positionals[1:]

    command_name = positionals[0] if positionals else None
    if not extra_args and len(positionals) > 1:
        extra_args = positionals[1:]

    return Invocation(
        skill_name=skill_name,
        command_name=command_name,
        os_name=os_name,
        record=record,
        list_commands=list_commands_flag,
        extra_args=extra_args,
    )


def launch_current_skill(script_path: Path, argv: list[str]) -> int:
    runtime = load_runtime(script_path.resolve().parents[1])
    invocation = parse_invocation(argv, require_skill_name=False)
    if invocation.list_commands:
        for name in list_commands(runtime):
            print(name)
        return 0
    return execute_skill(
        runtime=runtime,
        command_name=invocation.command_name,
        extra_args=invocation.extra_args,
        os_name=invocation.os_name,
        record=invocation.record,
    )


def print_run_skill_help() -> None:
    print(
        "Usage:\n"
        "  run-skill <skill-name> [command] [--os <macos|linux|windows>] [--record] [-- <extra-args>]\n"
        "  run-skill <skill-name> --list-commands\n"
    )


def main(argv: list[str]) -> int:
    try:
        invocation = parse_invocation(argv, require_skill_name=True)
    except RuntimeErrorMessage as exc:
        if str(exc) == "help":
            print_run_skill_help()
            return 0
        print(str(exc), file=sys.stderr)
        print_run_skill_help()
        return 2

    try:
        codex_root = find_codex_root()
        skill_dir = resolve_skill_dir(invocation.skill_name or "", codex_root)
        runtime = load_runtime(skill_dir)
        if invocation.list_commands:
            for name in list_commands(runtime):
                print(name)
            return 0
        return execute_skill(
            runtime=runtime,
            command_name=invocation.command_name,
            extra_args=invocation.extra_args,
            os_name=invocation.os_name,
            record=invocation.record,
        )
    except RuntimeErrorMessage as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
