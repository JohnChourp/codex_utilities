#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


SEMVER_SPEC_RE = re.compile(
    r"^(?P<prefix>\^|~)?(?P<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)$"
)
SEMVER_VERSION_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)


@dataclass(frozen=True)
class VersionLookup:
    latest_stable: str | None
    error: str | None = None


def _discover_userconfig() -> str | None:
    if os.environ.get("NODE_AUTH_TOKEN") or os.environ.get("NPM_TOKEN"):
        return None

    candidates = [
        Path.home() / ".npmrc.automation",
        Path.home() / ".npmrc",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def _npm_env() -> dict[str, str]:
    env = os.environ.copy()
    userconfig = _discover_userconfig()
    if userconfig:
        env["NPM_CONFIG_USERCONFIG"] = userconfig
    return env


def _parse_semver(version: str) -> tuple[int, int, int, tuple[tuple[int, int | str], ...] | None] | None:
    match = SEMVER_VERSION_RE.match(version)
    if not match:
        return None

    prerelease = match.group("prerelease")
    prerelease_key: tuple[tuple[int, int | str], ...] | None = None
    if prerelease:
        parts: list[tuple[int, int | str]] = []
        for part in prerelease.split("."):
            if part.isdigit():
                parts.append((0, int(part)))
            else:
                parts.append((1, part))
        prerelease_key = tuple(parts)

    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        prerelease_key,
    )


def _compare_semver(left: str, right: str) -> int:
    left_key = _parse_semver(left)
    right_key = _parse_semver(right)
    if left_key is None or right_key is None:
        raise ValueError(f"Unsupported semver comparison: {left!r} vs {right!r}")

    left_core = left_key[:3]
    right_core = right_key[:3]
    if left_core < right_core:
        return -1
    if left_core > right_core:
        return 1

    left_pre = left_key[3]
    right_pre = right_key[3]
    if left_pre is None and right_pre is None:
        return 0
    if left_pre is None:
        return 1
    if right_pre is None:
        return -1

    for left_part, right_part in zip(left_pre, right_pre):
        if left_part == right_part:
            continue
        if left_part[0] != right_part[0]:
            return -1 if left_part[0] < right_part[0] else 1
        return -1 if left_part[1] < right_part[1] else 1

    if len(left_pre) < len(right_pre):
        return -1
    if len(left_pre) > len(right_pre):
        return 1
    return 0


def _latest_stable_from_versions(versions: list[str]) -> str | None:
    latest: str | None = None
    for version in versions:
        parsed = _parse_semver(version)
        if parsed is None or parsed[3] is not None:
            continue
        if latest is None or _compare_semver(version, latest) > 0:
            latest = version
    return latest


def _lookup_versions(package_name: str, env: dict[str, str]) -> VersionLookup:
    npm_path = "npm"
    command = [npm_path, "view", package_name, "versions", "--json"]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
    except FileNotFoundError:
        raise SystemExit("npm is required for outdated dependency scanning but was not found in PATH.")

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "npm view failed"
        return VersionLookup(latest_stable=None, error=stderr.splitlines()[-1])

    stdout = completed.stdout.strip()
    if not stdout:
        return VersionLookup(latest_stable=None, error="npm view returned no versions")

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return VersionLookup(latest_stable=None, error=f"invalid npm response: {exc}")

    if isinstance(data, str):
        versions = [data]
    elif isinstance(data, list) and all(isinstance(item, str) for item in data):
        versions = data
    else:
        return VersionLookup(latest_stable=None, error="unexpected npm response format")

    latest_stable = _latest_stable_from_versions(versions)
    if latest_stable is None:
        return VersionLookup(latest_stable=None, error="no stable npm version found")
    return VersionLookup(latest_stable=latest_stable)


def _load_package_json(package_json_path: Path) -> dict[str, Any]:
    return json.loads(package_json_path.read_text())


def _iter_repositories(root: Path) -> list[Path]:
    return sorted(
        child for child in root.iterdir()
        if child.is_dir() and (child / "package.json").is_file()
    )


def _normalize_spec(spec: Any) -> tuple[str | None, str | None]:
    if not isinstance(spec, str):
        return None, "spec is not a string"

    match = SEMVER_SPEC_RE.match(spec.strip())
    if not match:
        return None, "unsupported spec (supported: exact, ^, ~)"
    return match.group("version"), None


def _scan_repo(repo_path: Path, env: dict[str, str], cache: dict[str, VersionLookup]) -> dict[str, Any] | None:
    package_json = _load_package_json(repo_path / "package.json")
    outdated: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []

    for section in ("dependencies", "devDependencies"):
        section_dependencies = package_json.get(section)
        if not isinstance(section_dependencies, dict):
            continue

        for dependency_name, spec in section_dependencies.items():
            current_version, spec_error = _normalize_spec(spec)
            if spec_error:
                skipped.append(
                    {
                        "name": dependency_name,
                        "section": section,
                        "spec": str(spec),
                        "reason": spec_error,
                    }
                )
                continue

            cached = cache.get(dependency_name)
            if cached is None:
                cached = _lookup_versions(dependency_name, env)
                cache[dependency_name] = cached

            if cached.error:
                skipped.append(
                    {
                        "name": dependency_name,
                        "section": section,
                        "spec": str(spec),
                        "reason": cached.error,
                    }
                )
                continue

            latest = cached.latest_stable
            if latest is None or current_version is None:
                continue

            if _compare_semver(current_version, latest) < 0:
                outdated.append(
                    {
                        "name": dependency_name,
                        "section": section,
                        "spec": str(spec),
                        "current": current_version,
                        "latest": latest,
                    }
                )

    if not outdated and not skipped:
        return None

    return {
        "repo": repo_path.name,
        "outdated": outdated,
        "skipped": skipped,
    }


def _build_report(root: Path) -> dict[str, Any]:
    env = _npm_env()
    repositories = _iter_repositories(root)
    cache: dict[str, VersionLookup] = {}
    findings: list[dict[str, Any]] = []

    for repo_path in repositories:
        repo_report = _scan_repo(repo_path, env, cache)
        if repo_report is not None:
            findings.append(repo_report)

    return {
        "generated_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "root": str(root),
        "repositories_scanned": len(repositories),
        "repositories_with_findings": len(findings),
        "outdated_dependencies": sum(len(repo["outdated"]) for repo in findings),
        "skipped_dependencies": sum(len(repo["skipped"]) for repo in findings),
        "repositories": findings,
    }


def _parse_args(default_root: str, default_output: str, argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan lambda repos for outdated direct dependencies.")
    parser.add_argument("--root", default=default_root, help="Root directory containing lambda repos.")
    parser.add_argument("--output", default=default_output, help="Path to the JSON report file.")
    return parser.parse_args(argv)


def main(default_root: str, default_output: str, argv: list[str] | None = None) -> int:
    args = _parse_args(default_root, default_output, argv or [])
    root = Path(args.root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()

    if not root.is_dir():
        raise SystemExit(f"Root path does not exist or is not a directory: {root}")

    report = _build_report(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main("", "", sys.argv[1:]))
