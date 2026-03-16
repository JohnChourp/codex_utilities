#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
import re


SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
NON_REGISTRY_SPEC_PREFIXES = (
    "file:",
    "git+",
    "git://",
    "http://",
    "https://",
    "workspace:",
    "link:",
    "github:",
)


class ScanError(RuntimeError):
    pass


@dataclass(frozen=True)
class OutdatedEntry:
    repo_name: str
    section: str
    package_name: str
    current_spec: str
    current_version: str
    latest_version: str


@dataclass(frozen=True)
class SkippedEntry:
    repo_name: str
    section: str
    package_name: str
    spec: str
    reason: str


def parse_args(default_root: str, default_output: str, argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find outdated npm dependencies across lambda repos and write a text report."
    )
    parser.add_argument("--root", default=default_root, help=f"Lambda root path. Default: {default_root}")
    parser.add_argument(
        "--output",
        default=default_output,
        help=f"Output report path. Default: {default_output}",
    )
    return parser.parse_args(list(argv))


def stable_semver_from_spec(version_spec: str) -> str | None:
    stripped = version_spec.strip()
    if not stripped:
        return None
    if stripped.startswith(NON_REGISTRY_SPEC_PREFIXES):
        return None
    normalized = stripped.lstrip("^~")
    if SEMVER_RE.match(normalized):
        return normalized
    return None


def semver_key(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version)
    if not match:
        raise ScanError(f"Invalid semver value: {version}")
    return tuple(int(part) for part in match.groups())


def npm_view_versions(package_name: str) -> list[str]:
    completed = subprocess.run(
        ["npm", "view", package_name, "versions", "--json"],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "Unknown npm error"
        raise ScanError(f"npm lookup failed for {package_name}: {message}")
    raw = completed.stdout.strip()
    if not raw:
        raise ScanError(f"npm lookup returned no data for {package_name}")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ScanError(f"Unable to parse npm versions for {package_name}: {raw}") from exc

    if isinstance(payload, str):
        versions = [payload]
    elif isinstance(payload, list):
        versions = [item for item in payload if isinstance(item, str)]
    else:
        raise ScanError(f"Unexpected npm versions payload for {package_name}: {payload!r}")
    return versions


def latest_stable_version(package_name: str, cache: dict[str, str]) -> str:
    if package_name in cache:
        return cache[package_name]

    versions = npm_view_versions(package_name)
    stable_versions = [version for version in versions if SEMVER_RE.match(version)]
    if not stable_versions:
        raise ScanError(f"No stable semver releases found for {package_name}")
    stable_versions.sort(key=semver_key)
    latest = stable_versions[-1]
    cache[package_name] = latest
    return latest


def load_package_json(package_json_path: Path) -> dict[str, Any]:
    try:
        with package_json_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise ScanError(f"Missing package.json: {package_json_path}") from exc
    except json.JSONDecodeError as exc:
        raise ScanError(f"Invalid package.json: {package_json_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ScanError(f"package.json must contain an object: {package_json_path}")
    return payload


def scan_root(root: Path) -> tuple[list[OutdatedEntry], list[SkippedEntry], int]:
    if not root.exists():
        raise ScanError(f"Root path does not exist: {root}")
    if not root.is_dir():
        raise ScanError(f"Root path is not a directory: {root}")

    outdated_entries: list[OutdatedEntry] = []
    skipped_entries: list[SkippedEntry] = []
    version_cache: dict[str, str] = {}
    scanned_repos = 0

    for child in sorted(root.iterdir(), key=lambda path: path.name.lower()):
        if not child.is_dir():
            continue

        package_json_path = child / "package.json"
        if not package_json_path.is_file():
            continue

        scanned_repos += 1
        package_json = load_package_json(package_json_path)

        for section in ("dependencies", "devDependencies"):
            dependencies = package_json.get(section) or {}
            if not isinstance(dependencies, dict):
                raise ScanError(f"{section} must be an object in {package_json_path}")

            for package_name in sorted(dependencies):
                spec = dependencies[package_name]
                if not isinstance(spec, str):
                    skipped_entries.append(
                        SkippedEntry(
                            repo_name=child.name,
                            section=section,
                            package_name=package_name,
                            spec=repr(spec),
                            reason="Dependency spec is not a string.",
                        )
                    )
                    continue

                current_version = stable_semver_from_spec(spec)
                if not current_version:
                    skipped_entries.append(
                        SkippedEntry(
                            repo_name=child.name,
                            section=section,
                            package_name=package_name,
                            spec=spec,
                            reason="Unsupported dependency spec for stable semver comparison.",
                        )
                    )
                    continue

                latest_version = latest_stable_version(package_name, version_cache)
                if semver_key(current_version) < semver_key(latest_version):
                    outdated_entries.append(
                        OutdatedEntry(
                            repo_name=child.name,
                            section=section,
                            package_name=package_name,
                            current_spec=spec,
                            current_version=current_version,
                            latest_version=latest_version,
                        )
                    )

    return outdated_entries, skipped_entries, scanned_repos


def render_report(
    root: Path,
    output: Path,
    scanned_repos: int,
    outdated_entries: list[OutdatedEntry],
    skipped_entries: list[SkippedEntry],
) -> str:
    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    repos_with_updates = len({entry.repo_name for entry in outdated_entries})

    lines = [
        "Outdated npm dependency report",
        f"Generated at: {generated_at}",
        f"Root: {root}",
        f"Output: {output}",
        f"Scanned repos: {scanned_repos}",
        f"Repos with updates: {repos_with_updates}",
        f"Total outdated entries: {len(outdated_entries)}",
        f"Skipped dependency specs: {len(skipped_entries)}",
        "",
        "Outdated dependencies",
        "=====================",
    ]

    if outdated_entries:
        current_repo: str | None = None
        for entry in sorted(
            outdated_entries,
            key=lambda item: (item.repo_name.lower(), item.section, item.package_name.lower()),
        ):
            if entry.repo_name != current_repo:
                if current_repo is not None:
                    lines.append("")
                current_repo = entry.repo_name
                lines.append(f"[{entry.repo_name}]")
            lines.append(f"- {entry.section} :: {entry.package_name}")
            lines.append(f"  current spec: {entry.current_spec}")
            lines.append(f"  resolved current: {entry.current_version}")
            lines.append(f"  latest stable: {entry.latest_version}")
    else:
        lines.append("No outdated dependencies found.")

    lines.extend(["", "Skipped dependency specs", "========================"])
    if skipped_entries:
        for entry in sorted(
            skipped_entries,
            key=lambda item: (item.repo_name.lower(), item.section, item.package_name.lower()),
        ):
            lines.append(
                f"- {entry.repo_name} :: {entry.section} :: {entry.package_name} :: {entry.spec} :: {entry.reason}"
            )
    else:
        lines.append("No skipped dependency specs.")

    lines.append("")
    return "\n".join(lines)


def write_report(output_path: Path, report: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def main(default_root: str, default_output: str, argv: Sequence[str] | None = None) -> int:
    args = parse_args(default_root, default_output, argv or sys.argv[1:])
    root = Path(args.root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()

    try:
        outdated_entries, skipped_entries, scanned_repos = scan_root(root)
        report = render_report(root, output, scanned_repos, outdated_entries, skipped_entries)
        write_report(output, report)
    except ScanError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(
        f"Wrote report to {output} "
        f"(scanned_repos={scanned_repos}, repos_with_updates={len({entry.repo_name for entry in outdated_entries})}, "
        f"outdated_entries={len(outdated_entries)}, skipped_specs={len(skipped_entries)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main("", ""))
