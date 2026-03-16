#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("/Users/john/Downloads/lambdas/codeliver_all")
PACKAGE_JSON = "package.json"
LOCKFILES = ("package-lock.json", "npm-shrinkwrap.json")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
NON_REGISTRY_SPEC_PREFIXES = ("file:", "git+", "git://", "http://", "https://", "workspace:", "link:")
PLACEHOLDER_TEST_PATTERNS = (
    "no test specified",
    "console.log('no tests')",
    'console.log("no tests")',
)


class UpgradeError(RuntimeError):
    pass


class DependencyUpgradeError(UpgradeError):
    def __init__(self, message: str, package_report: dict[str, Any]):
        super().__init__(message)
        self.package_report = package_report


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def combined_output(self) -> str:
        if self.stdout and self.stderr:
            return f"{self.stdout.rstrip()}\n{self.stderr.rstrip()}".strip()
        return (self.stdout or self.stderr).strip()


@dataclass
class AttemptRecord:
    version: str
    spec_written: str
    install_ok: bool
    validation_ok: bool
    install_output: str
    validation_output: str
    validator: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upgrade one lambda repo's npm dependencies to the newest compatible versions."
    )
    parser.add_argument("--lambda", dest="lambda_name", required=True, help="Exact lambda repo folder name.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help=f"Lambda root path. Default: {DEFAULT_ROOT}")
    parser.add_argument("--dry-run", action="store_true", help="Run on a temp copy and leave the original repo unchanged.")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable JSON report.")
    return parser.parse_args()


def run_command(command: list[str], cwd: Path, check: bool = False) -> CommandResult:
    completed = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True)
    result = CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if check and result.returncode != 0:
        raise UpgradeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{result.combined_output}"
        )
    return result


def npm_view_json(package_name: str, field: str) -> Any:
    result = run_command(["npm", "view", package_name, field, "--json"], cwd=Path.cwd())
    if result.returncode != 0:
        raise UpgradeError(
            f"npm view failed for {package_name} {field}\n{result.combined_output}"
        )
    raw = result.stdout.strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UpgradeError(f"Unable to parse npm view output for {package_name} {field}: {raw}") from exc


def stable_versions_desc(package_name: str) -> list[str]:
    raw_versions = npm_view_json(package_name, "versions")
    if isinstance(raw_versions, str):
        candidates = [raw_versions]
    elif isinstance(raw_versions, list):
        candidates = [item for item in raw_versions if isinstance(item, str)]
    else:
        raise UpgradeError(f"Unexpected npm versions payload for {package_name}: {raw_versions!r}")

    stable = [version for version in candidates if SEMVER_RE.match(version)]
    if not stable:
        raise UpgradeError(f"No stable semver versions found for {package_name}.")
    stable.sort(key=semver_key, reverse=True)
    return stable


def semver_key(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version)
    if not match:
        raise UpgradeError(f"Invalid semver version: {version}")
    return tuple(int(part) for part in match.groups())


def resolve_repo(root: Path, lambda_name: str) -> Path:
    repo_path = root / lambda_name
    if not repo_path.is_dir():
        raise UpgradeError(f"Lambda repo not found: {repo_path}")
    if not (repo_path / PACKAGE_JSON).is_file():
        raise UpgradeError(f"package.json not found for lambda repo: {repo_path}")
    return repo_path


def make_worktree(repo_path: Path, dry_run: bool) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    if not dry_run:
        return repo_path, None

    temp_dir = tempfile.TemporaryDirectory(prefix=f"{repo_path.name}-dm-upgrade-")
    target = Path(temp_dir.name) / repo_path.name

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        if ".git" in names:
            ignored.add(".git")
        if "node_modules" in names:
            ignored.add("node_modules")
        return ignored

    shutil.copytree(repo_path, target, ignore=ignore)
    return target, temp_dir


def load_package_json(repo_path: Path) -> dict[str, Any]:
    with (repo_path / PACKAGE_JSON).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_package_json(repo_path: Path, payload: dict[str, Any]) -> None:
    with (repo_path / PACKAGE_JSON).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def is_supported_registry_spec(version_spec: str) -> bool:
    stripped = version_spec.strip()
    if not stripped:
        return False
    if stripped.startswith(NON_REGISTRY_SPEC_PREFIXES):
        return False

    normalized = stripped.lstrip("^~")
    return SEMVER_RE.match(normalized) is not None


def collect_upgradeable_dependencies(
    package_json: dict[str, Any],
) -> tuple[list[tuple[str, str, str]], list[dict[str, str]]]:
    found: list[tuple[str, str, str]] = []
    skipped: list[dict[str, str]] = []
    for section in ("dependencies", "devDependencies"):
        dependencies = package_json.get(section) or {}
        if not isinstance(dependencies, dict):
            continue
        for name in sorted(dependencies):
            version = dependencies[name]
            if not isinstance(version, str):
                skipped.append(
                    {
                        "package": name,
                        "section": section,
                        "spec": repr(version),
                        "reason": "Dependency spec is not a string.",
                    }
                )
                continue

            if is_supported_registry_spec(version):
                found.append((section, name, version))
                continue

            skipped.append(
                {
                    "package": name,
                    "section": section,
                    "spec": version,
                    "reason": "Unsupported dependency spec for npm registry version fallback.",
                }
            )
    return found, skipped


def spec_prefix(version_spec: str) -> str:
    if version_spec.startswith("^"):
        return "^"
    if version_spec.startswith("~"):
        return "~"
    return ""


def format_spec(original_spec: str, version: str) -> str:
    return f"{spec_prefix(original_spec)}{version}"


def capture_repo_state(repo_path: Path) -> dict[str, bytes | None]:
    captured: dict[str, bytes | None] = {}
    files = (PACKAGE_JSON,) + LOCKFILES
    for relative_name in files:
        file_path = repo_path / relative_name
        captured[relative_name] = file_path.read_bytes() if file_path.exists() else None
    return captured


def restore_repo_state(repo_path: Path, state: dict[str, bytes | None]) -> None:
    for relative_name, content in state.items():
        file_path = repo_path / relative_name
        if content is None:
            if file_path.exists():
                file_path.unlink()
            continue
        file_path.write_bytes(content)


def install_dependencies(repo_path: Path) -> CommandResult:
    return run_command(["npm", "install", "--no-audit", "--no-fund"], cwd=repo_path)


def is_meaningful_test(test_script: str | None) -> bool:
    if not test_script or not test_script.strip():
        return False
    lowered = test_script.lower()
    return not any(pattern in lowered for pattern in PLACEHOLDER_TEST_PATTERNS)


def top_level_js_files(repo_path: Path) -> list[Path]:
    patterns = ("*.js", "*.cjs", "*.mjs")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(repo_path.glob(pattern)))
    return [path for path in files if path.is_file()]


def validate_repo(repo_path: Path) -> tuple[str, CommandResult]:
    package_json = load_package_json(repo_path)
    test_script = ((package_json.get("scripts") or {}) or {}).get("test")
    if isinstance(test_script, str) and is_meaningful_test(test_script):
        return "npm test", run_command(["npm", "test"], cwd=repo_path)

    js_files = top_level_js_files(repo_path)
    if not js_files:
        return "no-op", CommandResult(command=[], returncode=0, stdout="No top-level JS files found.", stderr="")

    command = ["node", "--check", *[path.name for path in js_files]]
    return "node --check", run_command(command, cwd=repo_path)


def update_dependency_spec(repo_path: Path, section: str, package_name: str, version_spec: str) -> None:
    package_json = load_package_json(repo_path)
    dependencies = package_json.get(section) or {}
    if package_name not in dependencies:
        raise UpgradeError(f"Dependency {package_name} missing from section {section} during update.")
    dependencies[package_name] = version_spec
    package_json[section] = dependencies
    save_package_json(repo_path, package_json)


def current_dependency_spec(repo_path: Path, section: str, package_name: str) -> str:
    package_json = load_package_json(repo_path)
    dependencies = package_json.get(section) or {}
    current = dependencies.get(package_name)
    if not isinstance(current, str):
        raise UpgradeError(f"Dependency {package_name} missing from section {section}.")
    return current


def truncate_output(output: str, limit: int = 4000) -> str:
    if len(output) <= limit:
        return output
    return output[:limit].rstrip() + "\n...[truncated]"


def upgrade_one_dependency(repo_path: Path, section: str, package_name: str, original_spec: str) -> dict[str, Any]:
    baseline_state = capture_repo_state(repo_path)
    available_versions = stable_versions_desc(package_name)
    attempts: list[AttemptRecord] = []
    chosen_version: str | None = None
    chosen_spec: str | None = None
    validator_used: str | None = None

    for version in available_versions:
        candidate_spec = format_spec(original_spec, version)
        update_dependency_spec(repo_path, section, package_name, candidate_spec)

        install_result = install_dependencies(repo_path)
        if install_result.returncode != 0:
            attempts.append(
                AttemptRecord(
                    version=version,
                    spec_written=candidate_spec,
                    install_ok=False,
                    validation_ok=False,
                    install_output=truncate_output(install_result.combined_output),
                    validation_output="Skipped because npm install failed.",
                    validator="not-run",
                )
            )
            restore_repo_state(repo_path, baseline_state)
            restore_result = install_dependencies(repo_path)
            if restore_result.returncode != 0:
                raise UpgradeError(
                    f"Failed to restore repo after npm install failure for {package_name} {candidate_spec}\n"
                    f"{restore_result.combined_output}"
                )
            continue

        validator_name, validation_result = validate_repo(repo_path)
        validation_ok = validation_result.returncode == 0
        attempts.append(
            AttemptRecord(
                version=version,
                spec_written=candidate_spec,
                install_ok=True,
                validation_ok=validation_ok,
                install_output=truncate_output(install_result.combined_output),
                validation_output=truncate_output(validation_result.combined_output),
                validator=validator_name,
            )
        )

        if validation_ok:
            chosen_version = version
            chosen_spec = candidate_spec
            validator_used = validator_name
            break

        restore_repo_state(repo_path, baseline_state)
        restore_result = install_dependencies(repo_path)
        if restore_result.returncode != 0:
            raise UpgradeError(
                f"Failed to restore repo after validation failure for {package_name} {candidate_spec}\n"
                f"{restore_result.combined_output}"
            )

    package_report = {
        "package": package_name,
        "section": section,
        "original_spec": original_spec,
        "current_spec": current_dependency_spec(repo_path, section, package_name),
        "available_versions": available_versions,
        "chosen_version": chosen_version,
        "chosen_spec": chosen_spec,
        "validator": validator_used,
        "attempts": [
            {
                "version": attempt.version,
                "spec_written": attempt.spec_written,
                "install_ok": attempt.install_ok,
                "validation_ok": attempt.validation_ok,
                "install_output": attempt.install_output,
                "validation_output": attempt.validation_output,
                "validator": attempt.validator,
            }
            for attempt in attempts
        ],
        "status": "upgraded" if chosen_spec and original_spec != chosen_spec else "unchanged",
    }

    if chosen_version is None or chosen_spec is None or validator_used is None:
        restore_repo_state(repo_path, baseline_state)
        restore_result = install_dependencies(repo_path)
        if restore_result.returncode != 0:
            raise UpgradeError(
                f"Failed to restore repo after exhausting versions for {package_name}\n{restore_result.combined_output}"
            )
        package_report["status"] = "failed"
        package_report["current_spec"] = current_dependency_spec(repo_path, section, package_name)
        raise DependencyUpgradeError(
            f"No compatible version found for {package_name}. Tried: {', '.join(version for version in available_versions)}",
            package_report,
        )

    package_report["current_spec"] = current_dependency_spec(repo_path, section, package_name)
    package_report["status"] = "upgraded" if original_spec != chosen_spec else "unchanged"
    return package_report


def build_human_summary(report: dict[str, Any]) -> str:
    lines = [
        f"Lambda: {report['lambda']}",
        f"Root: {report['root']}",
        f"Worktree: {report['worktree']}",
        f"Dry run: {'yes' if report['dry_run'] else 'no'}",
        f"Status: {report['status']}",
        f"Packages eligible: {report.get('packages_discovered', len(report['packages']))}",
        f"Packages skipped: {report.get('packages_skipped', 0)}",
    ]
    if report.get("error"):
        lines.append(f"Error: {report['error']}")
    for package in report["packages"]:
        lines.append(
            f"- {package['package']}: {package['original_spec']} -> {package.get('chosen_spec', package['original_spec'])} "
            f"[{package.get('status', 'pending')}]"
        )
        attempts = package.get("attempts") or []
        if attempts:
            tried = ", ".join(
                f"{attempt['spec_written']} ({'ok' if attempt['validation_ok'] else 'fail'})" for attempt in attempts
            )
            lines.append(f"  attempts: {tried}")
    for skipped in report.get("skipped_packages", []):
        lines.append(
            f"- {skipped['package']}: {skipped['spec']} [skipped: {skipped['reason']}]"
        )
    return "\n".join(lines)


def execute_upgrade(lambda_name: str, root: Path, dry_run: bool) -> dict[str, Any]:
    repo_path = resolve_repo(root, lambda_name)
    worktree, temp_dir = make_worktree(repo_path, dry_run)
    report: dict[str, Any] = {
        "lambda": lambda_name,
        "root": str(root),
        "repo": str(repo_path),
        "worktree": str(worktree),
        "dry_run": dry_run,
        "status": "success",
        "packages_discovered": 0,
        "packages_skipped": 0,
        "skipped_packages": [],
        "packages": [],
    }

    try:
        package_json = load_package_json(worktree)
        dependencies, skipped_packages = collect_upgradeable_dependencies(package_json)
        report["packages_discovered"] = len(dependencies)
        report["packages_skipped"] = len(skipped_packages)
        report["skipped_packages"] = skipped_packages
        for section, package_name, version_spec in dependencies:
            package_report = upgrade_one_dependency(worktree, section, package_name, version_spec)
            report["packages"].append(package_report)
    except DependencyUpgradeError as exc:
        report["packages"].append(exc.package_report)
        report["status"] = "failed"
        report["error"] = str(exc)
    except UpgradeError as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

    return report


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()

    try:
        report = execute_upgrade(args.lambda_name, root, args.dry_run)
    except UpgradeError as exc:
        report = {
            "lambda": args.lambda_name,
            "root": str(root),
            "repo": None,
            "worktree": None,
            "dry_run": args.dry_run,
            "status": "failed",
            "packages": [],
            "error": str(exc),
        }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(build_human_summary(report))

    return 0 if report["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
