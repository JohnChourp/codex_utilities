#!/usr/bin/env python3
from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class ResolvedPaths:
    os_name: str
    codex_root: Path
    projects_root: Path
    lambdas_root: Path


def normalize_os_hint(value: Optional[str]) -> str:
    if not value:
        return detect_os_name()
    lowered = value.strip().lower()
    if lowered in {"mac", "macos", "osx", "darwin"}:
        return "macos"
    if lowered in {"ubuntu", "linux"}:
        return "linux"
    if lowered in {"windows", "win", "win32"}:
        return "windows"
    return detect_os_name()


def detect_os_name() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    return "linux"


def is_canonical_codex_root(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "playbooks").is_dir()
        and (path / "refs").is_dir()
        and (path / "playbooks" / "codeliver-api-gateways.md").is_file()
    )


def is_projects_root(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "codeliver" / "codeliver-app").is_dir()
        and (path / "codeliver" / "codeliver-panel").is_dir()
    )


def is_lambdas_root(path: Path) -> bool:
    return path.is_dir() and (path / "codeliver-app-sync-actions").is_dir()


def _unique_existing(paths: Iterable[Path]) -> list[Path]:
    seen = set()
    ordered: list[Path] = []
    for path in paths:
        key = str(path)
        if key in seen or not path.exists():
            continue
        seen.add(key)
        ordered.append(path)
    return ordered


def _parent_chain(path: Path) -> list[Path]:
    return [path, *path.parents]


def _downloads_candidates(home: Path, os_name: str) -> list[Path]:
    downloads = home / "Downloads"
    candidates = [
        downloads / "projects" / "codex_utilities" / ".codex",
        home / ".codex",
        downloads / "projects",
        downloads / "lambdas" / "codeliver_all",
    ]
    if os_name == "windows":
        candidates.extend(
            [
                home / "projects" / "codex_utilities" / ".codex",
                home / "projects",
                home / "lambdas" / "codeliver_all",
            ]
        )
    return candidates


def _codex_candidates(cwd: Path, home: Path, os_name: str) -> list[Path]:
    candidates: list[Path] = []
    for base in _parent_chain(cwd):
        candidates.append(base / ".codex")
        candidates.append(base / "projects" / "codex_utilities" / ".codex")
        candidates.append(base.parent / "projects" / "codex_utilities" / ".codex")
    candidates.extend(_downloads_candidates(home, os_name))
    return _unique_existing(candidates)


def _projects_candidates(cwd: Path, home: Path, os_name: str, codex_root: Optional[Path]) -> list[Path]:
    candidates: list[Path] = []
    if codex_root is not None and codex_root.parent.parent.exists():
        candidates.append(codex_root.parent.parent)
    for base in _parent_chain(cwd):
        candidates.append(base / "projects")
        candidates.append(base)
    candidates.extend(_downloads_candidates(home, os_name))
    return _unique_existing(candidates)


def _lambdas_candidates(cwd: Path, home: Path, os_name: str, projects_root: Optional[Path]) -> list[Path]:
    candidates: list[Path] = []
    if projects_root is not None:
        candidates.append(projects_root.parent / "lambdas" / "codeliver_all")
    for base in _parent_chain(cwd):
        candidates.append(base / "lambdas" / "codeliver_all")
        candidates.append(base)
    candidates.extend(_downloads_candidates(home, os_name))
    return _unique_existing(candidates)


def find_codex_root(cwd: Optional[Path] = None, os_hint: Optional[str] = None, explicit: Optional[Path] = None) -> Path:
    if explicit is not None:
        candidate = explicit.expanduser().resolve()
        if is_canonical_codex_root(candidate):
            return candidate
        raise SystemExit(f"Canonical .codex root not found: {candidate}")

    os_name = normalize_os_hint(os_hint)
    current = (cwd or Path.cwd()).resolve()
    home = Path.home()
    for candidate in _codex_candidates(current, home, os_name):
        if is_canonical_codex_root(candidate):
            return candidate
    raise SystemExit("Unable to resolve canonical .codex root.")


def find_projects_root(
    cwd: Optional[Path] = None,
    os_hint: Optional[str] = None,
    explicit: Optional[Path] = None,
    codex_root: Optional[Path] = None,
) -> Path:
    if explicit is not None:
        candidate = explicit.expanduser().resolve()
        if is_projects_root(candidate):
            return candidate
        raise SystemExit(f"Projects root not found: {candidate}")

    os_name = normalize_os_hint(os_hint)
    current = (cwd or Path.cwd()).resolve()
    home = Path.home()
    for candidate in _projects_candidates(current, home, os_name, codex_root):
        if is_projects_root(candidate):
            return candidate
    raise SystemExit("Unable to resolve projects root.")


def find_lambdas_root(
    cwd: Optional[Path] = None,
    os_hint: Optional[str] = None,
    explicit: Optional[Path] = None,
    projects_root: Optional[Path] = None,
) -> Path:
    if explicit is not None:
        candidate = explicit.expanduser().resolve()
        if is_lambdas_root(candidate):
            return candidate
        raise SystemExit(f"Lambdas root not found: {candidate}")

    os_name = normalize_os_hint(os_hint)
    current = (cwd or Path.cwd()).resolve()
    home = Path.home()
    for candidate in _lambdas_candidates(current, home, os_name, projects_root):
        if is_lambdas_root(candidate):
            return candidate
    raise SystemExit("Unable to resolve lambdas root.")


def resolve_paths(
    *,
    cwd: Optional[Path] = None,
    os_hint: Optional[str] = None,
    codex_root: Optional[Path] = None,
    projects_root: Optional[Path] = None,
    lambdas_root: Optional[Path] = None,
) -> ResolvedPaths:
    current = (cwd or Path.cwd()).resolve()
    os_name = normalize_os_hint(os_hint or os.environ.get("CODEX_SKILL_OS"))
    resolved_codex = find_codex_root(current, os_name, codex_root)
    resolved_projects = find_projects_root(current, os_name, projects_root, resolved_codex)
    resolved_lambdas = find_lambdas_root(current, os_name, lambdas_root, resolved_projects)
    return ResolvedPaths(
        os_name=os_name,
        codex_root=resolved_codex,
        projects_root=resolved_projects,
        lambdas_root=resolved_lambdas,
    )
