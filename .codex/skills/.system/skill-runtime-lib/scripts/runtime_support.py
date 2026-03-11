#!/usr/bin/env python3
"""Shared runtime and validation helpers for global Codex skills."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any


SCHEMA_VERSION = 1
RUNTIME_FILENAME = "skill.runtime.json"
SUPPORTED_OS = ("macos", "linux", "windows")
EXECUTION_MODES = ("guidance", "python_launcher")
COMMAND_KINDS = ("python", "shell", "exec")
CHECK_TYPES = ("tool", "env", "path")
UNSUPPORTED_BEHAVIOR = "fail_fast"
DEFAULT_CACHE_TTL_SECONDS = 600
JUNK_FILE_NAMES = {".DS_Store"}
JUNK_DIR_NAMES = {"__pycache__"}
JUNK_SUFFIXES = {".pyc"}
OS_PATH_ANTI_PATTERNS = (
    re.compile(r"/Users/"),
    re.compile(r"~/Library/"),
    re.compile(r"/Applications/"),
    re.compile(r"\\Users\\"),
)


@dataclass
class ValidationIssue:
    level: str
    message: str
    path: str | None = None

    def format(self) -> str:
        if self.path:
            return f"{self.level}: {self.path}: {self.message}"
        return f"{self.level}: {self.message}"


class RuntimeErrorBase(Exception):
    """Base exception for runtime failures."""


class ValidationError(RuntimeErrorBase):
    """Raised when skill structure or runtime metadata is invalid."""


def detect_os() -> str:
    current = platform.system()
    if current == "Darwin":
        return "macos"
    if current == "Linux":
        return "linux"
    if current == "Windows":
        return "windows"
    return current.lower()


def skill_dir_from_any_path(any_path: str | Path) -> Path:
    resolved = Path(any_path).resolve()
    if resolved.name == RUNTIME_FILENAME:
        return resolved.parent
    if resolved.name == "SKILL.md":
        return resolved.parent
    if resolved.name == "run.py" and resolved.parent.name == "scripts":
        return resolved.parent.parent
    if resolved.is_dir():
        return resolved
    return resolved.parent


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_runtime(skill_dir: str | Path) -> dict[str, Any]:
    runtime_path = skill_dir_from_any_path(skill_dir) / RUNTIME_FILENAME
    if not runtime_path.is_file():
        raise ValidationError(f"Missing {RUNTIME_FILENAME}")
    return load_json(runtime_path)


def parse_skill_frontmatter(skill_md_path: Path) -> dict[str, Any]:
    if not skill_md_path.is_file():
        raise ValidationError("Missing SKILL.md")
    content = skill_md_path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise ValidationError("No YAML frontmatter found in SKILL.md")
    loaded: dict[str, Any] = {}
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith((" ", "\t")):
            continue
        key_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw_line)
        if not key_match:
            continue
        key = key_match.group(1)
        value = key_match.group(2).strip()
        if value.startswith(("\"", "'")) and value.endswith(("\"", "'")) and len(value) >= 2:
            value = value[1:-1]
        loaded[key] = value
    if not loaded:
        raise ValidationError("Frontmatter must be a YAML-like mapping")
    return loaded


def _validate_supported_os(values: Any, issues: list[ValidationIssue], path: str) -> list[str]:
    if not isinstance(values, list) or not values:
        issues.append(ValidationIssue("ERROR", "supported_os must be a non-empty array", path))
        return []
    normalized: list[str] = []
    for value in values:
        if value not in SUPPORTED_OS:
            issues.append(
                ValidationIssue("ERROR", f"Unsupported OS value '{value}'", path)
            )
            continue
        normalized.append(value)
    if len(set(normalized)) != len(normalized):
        issues.append(ValidationIssue("ERROR", "supported_os contains duplicates", path))
    return normalized


def _validate_preflight(
    preflight: Any,
    issues: list[ValidationIssue],
    base_path: str,
) -> None:
    if not isinstance(preflight, dict):
        issues.append(ValidationIssue("ERROR", "preflight must be an object", base_path))
        return
    ttl = preflight.get("cache_ttl_seconds", DEFAULT_CACHE_TTL_SECONDS)
    if not isinstance(ttl, int) or ttl <= 0:
        issues.append(
            ValidationIssue("ERROR", "preflight.cache_ttl_seconds must be a positive integer", base_path)
        )
    checks = preflight.get("checks", [])
    if not isinstance(checks, list):
        issues.append(ValidationIssue("ERROR", "preflight.checks must be an array", base_path))
        return
    for index, check in enumerate(checks):
        path = f"{base_path}.checks[{index}]"
        if not isinstance(check, dict):
            issues.append(ValidationIssue("ERROR", "check must be an object", path))
            continue
        check_type = check.get("type")
        if check_type not in CHECK_TYPES:
            issues.append(
                ValidationIssue("ERROR", f"Unsupported check type '{check_type}'", path)
            )
            continue
        if check_type == "tool" and not isinstance(check.get("name"), str):
            issues.append(ValidationIssue("ERROR", "tool check requires string 'name'", path))
        if check_type == "env" and not isinstance(check.get("name"), str):
            issues.append(ValidationIssue("ERROR", "env check requires string 'name'", path))
        if check_type == "path" and not isinstance(check.get("path"), str):
            issues.append(ValidationIssue("ERROR", "path check requires string 'path'", path))
        if "install_hint" in check and not isinstance(check["install_hint"], dict):
            issues.append(ValidationIssue("ERROR", "install_hint must be an object", path))


def _validate_tooling(
    tooling: Any,
    issues: list[ValidationIssue],
    base_path: str,
) -> None:
    if not isinstance(tooling, dict):
        issues.append(ValidationIssue("ERROR", "tooling must be an object", base_path))
        return
    for tool_name, mapping in tooling.items():
        tool_path = f"{base_path}.{tool_name}"
        if not isinstance(mapping, dict):
            issues.append(ValidationIssue("ERROR", "tool definition must be an object", tool_path))
            continue
        for os_name, command in mapping.items():
            if os_name not in SUPPORTED_OS:
                issues.append(
                    ValidationIssue("ERROR", f"Unsupported OS value '{os_name}'", tool_path)
                )
                continue
            if not isinstance(command, list) or not command or not all(
                isinstance(item, str) and item for item in command
            ):
                issues.append(
                    ValidationIssue("ERROR", "tool command must be a non-empty string array", tool_path)
                )


def _validate_commands(
    commands: Any,
    issues: list[ValidationIssue],
    base_path: str,
) -> list[str]:
    if not isinstance(commands, list) or not commands:
        issues.append(ValidationIssue("ERROR", "commands must be a non-empty array", base_path))
        return []
    names: list[str] = []
    for index, command in enumerate(commands):
        path = f"{base_path}[{index}]"
        if not isinstance(command, dict):
            issues.append(ValidationIssue("ERROR", "command must be an object", path))
            continue
        name = command.get("name")
        if not isinstance(name, str) or not name:
            issues.append(ValidationIssue("ERROR", "command requires non-empty string 'name'", path))
        else:
            names.append(name)
        kind = command.get("kind")
        if kind not in COMMAND_KINDS:
            issues.append(ValidationIssue("ERROR", f"Unsupported command kind '{kind}'", path))
        script_path = command.get("path")
        if not isinstance(script_path, str) or not script_path:
            issues.append(ValidationIssue("ERROR", "command requires non-empty string 'path'", path))
        args = command.get("args", [])
        if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            issues.append(ValidationIssue("ERROR", "command.args must be a string array", path))
        if "supported_os" in command:
            _validate_supported_os(command["supported_os"], issues, f"{path}.supported_os")
        executor_tool = command.get("executor_tool")
        if executor_tool is not None and not isinstance(executor_tool, str):
            issues.append(ValidationIssue("ERROR", "executor_tool must be a string", path))
    if len(set(names)) != len(names):
        issues.append(ValidationIssue("ERROR", "commands contain duplicate names", base_path))
    return names


def _validate_entrypoint(
    entrypoint: Any,
    execution_mode: str,
    issues: list[ValidationIssue],
    base_path: str,
) -> None:
    if execution_mode == "guidance":
        if entrypoint not in (None, {}):
            issues.append(ValidationIssue("ERROR", "guidance skills must not define an entrypoint", base_path))
        return
    if not isinstance(entrypoint, dict):
        issues.append(ValidationIssue("ERROR", "python_launcher skills require an entrypoint object", base_path))
        return
    path = entrypoint.get("path")
    if path != "scripts/run.py":
        issues.append(
            ValidationIssue("ERROR", "entrypoint.path must be 'scripts/run.py'", base_path)
        )
    kind = entrypoint.get("kind")
    if kind != "python":
        issues.append(ValidationIssue("ERROR", "entrypoint.kind must be 'python'", base_path))


def _scan_junk_files(skill_dir: Path, issues: list[ValidationIssue]) -> None:
    for path in skill_dir.rglob("*"):
        if path.name in JUNK_FILE_NAMES or path.suffix in JUNK_SUFFIXES:
            issues.append(ValidationIssue("ERROR", "junk file must be removed", str(path)))
        elif path.is_dir() and path.name in JUNK_DIR_NAMES:
            issues.append(ValidationIssue("ERROR", "junk directory must be removed", str(path)))


def _scan_launcher_portability(skill_dir: Path, runtime: dict[str, Any], issues: list[ValidationIssue]) -> None:
    if runtime.get("execution_mode") != "python_launcher":
        return
    launcher_path = skill_dir / "scripts" / "run.py"
    if not launcher_path.is_file():
        return
    content = launcher_path.read_text(encoding="utf-8")
    patterns = [pattern.pattern for pattern in OS_PATH_ANTI_PATTERNS if pattern.search(content)]
    if patterns:
        issues.append(
            ValidationIssue(
                "ERROR",
                "launcher contains hardcoded OS-specific path patterns",
                str(launcher_path),
            )
        )


def validate_skill(skill_dir: str | Path) -> list[ValidationIssue]:
    resolved = skill_dir_from_any_path(skill_dir)
    issues: list[ValidationIssue] = []
    skill_md_path = resolved / "SKILL.md"
    runtime_path = resolved / RUNTIME_FILENAME

    frontmatter: dict[str, Any] | None = None
    try:
        frontmatter = parse_skill_frontmatter(skill_md_path)
    except ValidationError as exc:
        issues.append(ValidationIssue("ERROR", str(exc), str(skill_md_path)))

    runtime: dict[str, Any] | None = None
    if not runtime_path.is_file():
        issues.append(ValidationIssue("ERROR", f"Missing {RUNTIME_FILENAME}", str(runtime_path)))
    else:
        try:
            runtime = load_json(runtime_path)
        except json.JSONDecodeError as exc:
            issues.append(
                ValidationIssue("ERROR", f"Invalid JSON: {exc.msg}", str(runtime_path))
            )

    _scan_junk_files(resolved, issues)

    if runtime is None:
        return issues

    if runtime.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            ValidationIssue("ERROR", f"schema_version must be {SCHEMA_VERSION}", str(runtime_path))
        )

    skill_name = runtime.get("skill_name")
    if not isinstance(skill_name, str) or not skill_name:
        issues.append(ValidationIssue("ERROR", "skill_name must be a non-empty string", str(runtime_path)))
    elif frontmatter and frontmatter.get("name") != skill_name:
        issues.append(
            ValidationIssue("ERROR", "skill_name must match SKILL.md frontmatter name", str(runtime_path))
        )

    execution_mode = runtime.get("execution_mode")
    if execution_mode not in EXECUTION_MODES:
        issues.append(
            ValidationIssue(
                "ERROR",
                f"execution_mode must be one of {', '.join(EXECUTION_MODES)}",
                str(runtime_path),
            )
        )
        execution_mode = "guidance"

    if runtime.get("unsupported_behavior") != UNSUPPORTED_BEHAVIOR:
        issues.append(
            ValidationIssue(
                "ERROR",
                f"unsupported_behavior must be '{UNSUPPORTED_BEHAVIOR}'",
                str(runtime_path),
            )
        )

    _validate_supported_os(runtime.get("supported_os"), issues, f"{runtime_path}:supported_os")
    _validate_preflight(runtime.get("preflight", {}), issues, f"{runtime_path}:preflight")
    _validate_tooling(runtime.get("tooling", {}), issues, f"{runtime_path}:tooling")
    _validate_entrypoint(runtime.get("entrypoint"), execution_mode, issues, f"{runtime_path}:entrypoint")

    command_names: list[str] = []
    if execution_mode == "python_launcher":
        command_names = _validate_commands(
            runtime.get("commands"),
            issues,
            f"{runtime_path}:commands",
        )
        launcher = resolved / "scripts" / "run.py"
        if not launcher.is_file():
            issues.append(ValidationIssue("ERROR", "Missing scripts/run.py", str(launcher)))
        for command in runtime.get("commands", []):
            if not isinstance(command, dict):
                continue
            command_path = command.get("path")
            if isinstance(command_path, str):
                candidate = resolved / command_path
                if not candidate.is_file():
                    issues.append(
                        ValidationIssue("ERROR", "command path does not exist", str(candidate))
                    )
    else:
        if runtime.get("commands"):
            issues.append(
                ValidationIssue("ERROR", "guidance skills must not declare commands", str(runtime_path))
            )

    if command_names and runtime.get("default_command") and runtime.get("default_command") not in command_names:
        issues.append(
            ValidationIssue(
                "ERROR",
                "default_command must match one of the command names",
                str(runtime_path),
            )
        )

    _scan_launcher_portability(resolved, runtime, issues)
    return issues


def validate_tree(root_dir: str | Path, include_hidden: bool = False) -> list[ValidationIssue]:
    root = Path(root_dir).resolve()
    issues: list[ValidationIssue] = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        skill_dir = skill_md.parent
        relative = skill_dir.relative_to(root)
        if not include_hidden and any(part.startswith(".") for part in relative.parts):
            continue
        issues.extend(validate_skill(skill_dir))
    return issues


def cache_file_path() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    cache_dir = codex_home / "tmp"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "skill-runtime-cache.json"


def load_cache() -> dict[str, Any]:
    path = cache_file_path()
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def save_cache(payload: dict[str, Any]) -> None:
    path = cache_file_path()
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def resolve_tool_command(runtime: dict[str, Any], tool_name: str, current_os: str) -> list[str]:
    tooling = runtime.get("tooling", {})
    mapping = tooling.get(tool_name)
    if not isinstance(mapping, dict):
        raise RuntimeErrorBase(f"Tool '{tool_name}' is not defined in tooling")
    command = mapping.get(current_os)
    if not isinstance(command, list) or not command:
        raise RuntimeErrorBase(f"Tool '{tool_name}' is not configured for {current_os}")
    return command


def _install_hint(check: dict[str, Any], current_os: str) -> str:
    install_hint = check.get("install_hint", {})
    if isinstance(install_hint, dict):
        return install_hint.get(current_os) or install_hint.get("default") or ""
    return ""


def _cache_key(skill_dir: Path, runtime: dict[str, Any], current_os: str, check: dict[str, Any]) -> str:
    explicit = check.get("cache_key")
    if isinstance(explicit, str) and explicit:
        return explicit
    check_label = check.get("name") or check.get("path") or check.get("type")
    return f"{skill_dir}:{runtime.get('skill_name')}:{current_os}:{check_label}"


def run_preflight(skill_dir: Path, runtime: dict[str, Any], current_os: str) -> None:
    supported = runtime.get("supported_os", [])
    if current_os not in supported:
        supported_label = ", ".join(supported)
        raise RuntimeErrorBase(
            f"Unsupported OS '{current_os}' for skill '{runtime.get('skill_name')}'. Supported: {supported_label}"
        )

    preflight = runtime.get("preflight", {})
    checks = preflight.get("checks", [])
    ttl = preflight.get("cache_ttl_seconds", DEFAULT_CACHE_TTL_SECONDS)
    cache = load_cache()
    cache_updated = False
    now = int(time.time())

    for check in checks:
        cache_key = _cache_key(skill_dir, runtime, current_os, check)
        cached = cache.get(cache_key)
        if isinstance(cached, dict) and cached.get("expires_at", 0) >= now:
            continue

        check_type = check["type"]
        if check_type == "tool":
            resolved = resolve_tool_command(runtime, check["name"], current_os)
            if shutil.which(resolved[0]) is None:
                hint = _install_hint(check, current_os)
                suffix = f" {hint}" if hint else ""
                raise RuntimeErrorBase(
                    f"Missing required tool '{check['name']}' ({resolved[0]}).{suffix}"
                )
        elif check_type == "env":
            if not os.environ.get(check["name"]):
                hint = _install_hint(check, current_os)
                suffix = f" {hint}" if hint else ""
                raise RuntimeErrorBase(
                    f"Missing required environment variable '{check['name']}'.{suffix}"
                )
        elif check_type == "path":
            raw_path = check["path"]
            candidate = Path(os.path.expandvars(os.path.expanduser(raw_path)))
            if not candidate.is_absolute():
                candidate = skill_dir / raw_path
            if not candidate.exists():
                hint = _install_hint(check, current_os)
                suffix = f" {hint}" if hint else ""
                raise RuntimeErrorBase(
                    f"Missing required path '{candidate}'.{suffix}"
                )

        cache[cache_key] = {"expires_at": now + ttl}
        cache_updated = True

    if cache_updated:
        save_cache(cache)


def list_commands(runtime: dict[str, Any], current_os: str) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for command in runtime.get("commands", []):
        supported = command.get("supported_os", runtime.get("supported_os", []))
        if current_os in supported:
            commands.append(command)
    return commands


def resolve_execution_plan(
    skill_dir: Path,
    runtime: dict[str, Any],
    command: dict[str, Any],
    current_os: str,
    passthrough_args: list[str],
) -> list[str]:
    command_path = skill_dir / command["path"]
    default_args = command.get("args", [])
    kind = command["kind"]
    if kind == "python":
        executor = command.get("executor_tool", "python")
        prefix = resolve_tool_command(runtime, executor, current_os)
        return prefix + [str(command_path)] + default_args + passthrough_args
    if kind == "shell":
        executor = command.get("executor_tool", "bash")
        prefix = resolve_tool_command(runtime, executor, current_os)
        return prefix + [str(command_path)] + default_args + passthrough_args
    if kind == "exec":
        return [str(command_path)] + default_args + passthrough_args
    raise RuntimeErrorBase(f"Unsupported command kind '{kind}'")


def _select_command(runtime: dict[str, Any], current_os: str, argv: list[str]) -> tuple[dict[str, Any], list[str]]:
    commands = list_commands(runtime, current_os)
    if not commands:
        raise RuntimeErrorBase("No commands are available for the current OS.")
    command_map = {command["name"]: command for command in commands}
    if not argv:
        default_name = runtime.get("default_command")
        if default_name:
            command = command_map.get(default_name)
            if command:
                return command, []
        if len(commands) == 1:
            return commands[0], []
        raise RuntimeErrorBase(
            "Multiple commands are available. Use one of: " + ", ".join(sorted(command_map))
        )
    command_name = argv[0]
    if command_name == "list":
        for command in commands:
            description = command.get("description", "")
            suffix = f" - {description}" if description else ""
            print(f"{command['name']}{suffix}")
        raise SystemExit(0)
    if command_name not in command_map:
        if len(commands) == 1:
            return commands[0], argv
        raise RuntimeErrorBase(
            f"Unknown command '{command_name}'. Available: {', '.join(sorted(command_map))}"
        )
    return command_map[command_name], argv[1:]


def _print_plan(runtime: dict[str, Any], current_os: str, command: dict[str, Any], plan: list[str]) -> None:
    print(f"[skill-runtime] skill={runtime.get('skill_name')}")
    print(f"[skill-runtime] os={current_os}")
    print(f"[skill-runtime] command={command['name']}")
    print(f"[skill-runtime] exec={' '.join(plan)}")


def launch_skill(skill_dir: str | Path, argv: list[str]) -> int:
    resolved = skill_dir_from_any_path(skill_dir)
    runtime = load_runtime(resolved)
    current_os = detect_os()
    if runtime.get("execution_mode") != "python_launcher":
        raise RuntimeErrorBase("This skill is guidance-only and has no executable launcher.")
    run_preflight(resolved, runtime, current_os)
    command, passthrough_args = _select_command(runtime, current_os, argv)
    plan = resolve_execution_plan(resolved, runtime, command, current_os, passthrough_args)
    _print_plan(runtime, current_os, command, plan)
    completed = subprocess.run(plan)
    return completed.returncode


def launch_current_skill(script_path: str | Path, argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    skill_dir = skill_dir_from_any_path(script_path)
    return launch_skill(skill_dir, args)


def validation_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate skill runtime metadata.")
    parser.add_argument("paths", nargs="+", help="Skill directory or root to validate")
    parser.add_argument("--tree", action="store_true", help="Treat paths as roots containing multiple skills")
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden directories such as .system",
    )
    args = parser.parse_args(argv)

    issues: list[ValidationIssue] = []
    for raw_path in args.paths:
        if args.tree:
            issues.extend(validate_tree(raw_path, include_hidden=args.include_hidden))
        else:
            issues.extend(validate_skill(raw_path))

    if not issues:
        print("Skill runtime validation passed.")
        return 0

    for issue in issues:
        print(issue.format(), file=sys.stderr)
    return 1


__all__ = [
    "RuntimeErrorBase",
    "ValidationError",
    "launch_current_skill",
    "launch_skill",
    "load_runtime",
    "parse_skill_frontmatter",
    "validate_skill",
    "validate_tree",
    "validation_cli",
]
