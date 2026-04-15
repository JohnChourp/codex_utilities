#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


SEMVER_CHARS = set("0123456789.")


def parse_semver(value: str) -> tuple[int, int, int] | None:
    raw = str(value or "").strip()
    if raw.startswith("v"):
        raw = raw[1:]
    if "-" in raw or "+" in raw:
        return None
    parts = raw.split(".")
    if len(parts) != 3:
        return None
    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        return None


def parse_supported_spec(spec: str) -> tuple[str, str, tuple[int, int, int]] | None:
    raw = str(spec or "").strip()
    if not raw:
        return None

    prefix = ""
    version_text = raw
    if raw[0] in {"^", "~"}:
        prefix = raw[0]
        version_text = raw[1:]

    if any(ch not in SEMVER_CHARS for ch in version_text):
        return None

    parsed = parse_semver(version_text)
    if parsed is None:
        return None
    return prefix, version_text, parsed


def npm_versions(package_name: str) -> list[str]:
    command = ["npm", "view", package_name, "versions", "--json", "--silent"]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip() or f"npm exited {completed.returncode}"
        raise RuntimeError(detail)

    payload = (completed.stdout or "").strip()
    if not payload:
        return []

    parsed = json.loads(payload)
    if isinstance(parsed, str):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, str)]
    return []


def latest_stable_version(package_name: str) -> tuple[str, tuple[int, int, int]] | None:
    stable = []
    for version in npm_versions(package_name):
        parsed = parse_semver(version)
        if parsed is not None:
            stable.append((parsed, version))
    if not stable:
        return None
    stable.sort(key=lambda item: item[0])
    parsed, version = stable[-1]
    return version, parsed


def scan_repo(repo_dir: Path) -> dict | None:
    package_json_path = repo_dir / "package.json"
    try:
        package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "repo": repo_dir.name,
            "path": str(repo_dir),
            "error": f"failed_to_read_package_json: {exc}",
        }

    repo_result = {
        "repo": repo_dir.name,
        "path": str(repo_dir),
        "outdated": {"dependencies": [], "devDependencies": []},
        "skipped": [],
    }

    for section in ("dependencies", "devDependencies"):
        dependencies = package_json.get(section) or {}
        if not isinstance(dependencies, dict):
            continue

        for package_name in sorted(dependencies):
            spec = str(dependencies[package_name])
            parsed_spec = parse_supported_spec(spec)
            if parsed_spec is None:
                repo_result["skipped"].append(
                    {
                        "name": package_name,
                        "section": section,
                        "spec": spec,
                        "reason": "unsupported_spec",
                    }
                )
                continue

            prefix, current_version_text, current_version = parsed_spec
            try:
                latest = latest_stable_version(package_name)
            except Exception as exc:
                repo_result["skipped"].append(
                    {
                        "name": package_name,
                        "section": section,
                        "spec": spec,
                        "reason": "registry_lookup_failed",
                        "detail": str(exc),
                    }
                )
                continue

            if latest is None:
                repo_result["skipped"].append(
                    {
                        "name": package_name,
                        "section": section,
                        "spec": spec,
                        "reason": "no_stable_registry_version",
                    }
                )
                continue

            latest_version_text, latest_version = latest
            if latest_version <= current_version:
                continue

            repo_result["outdated"][section].append(
                {
                    "name": package_name,
                    "spec": spec,
                    "range_style": prefix or "exact",
                    "current_version": current_version_text,
                    "latest_stable_version": latest_version_text,
                }
            )

    if repo_result["outdated"]["dependencies"] or repo_result["outdated"]["devDependencies"] or repo_result["skipped"]:
        return repo_result
    return None


def build_parser(default_root: str, default_output: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan direct child lambda repos and write a JSON report for outdated npm dependencies."
    )
    parser.add_argument("--root", default=default_root, help="Root folder that contains direct child lambda repos.")
    parser.add_argument("--output", default=default_output, help="JSON report output path.")
    return parser


def main(default_root: str, default_output: str, argv: list[str]) -> int:
    args = build_parser(default_root, default_output).parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()

    if not root.is_dir():
        raise SystemExit(f"root not found: {root}")

    repos = []
    errors = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "package.json").is_file():
            continue
        result = scan_repo(child)
        if result is None:
            continue
        if "error" in result:
            errors.append(result)
        else:
            repos.append(result)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "repos": repos,
        "errors": errors,
        "summary": {
            "scanned_repos": len([child for child in root.iterdir() if child.is_dir() and (child / "package.json").is_file()]),
            "repos_with_findings": len(repos),
            "repos_with_errors": len(errors),
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "repos_with_findings": len(repos), "repos_with_errors": len(errors)}))
    return 0
