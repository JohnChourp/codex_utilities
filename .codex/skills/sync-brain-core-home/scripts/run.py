#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


MANAGED_BEGIN = "<!-- sync-brain-core-home:begin -->"
MANAGED_END = "<!-- sync-brain-core-home:end -->"
SCHEMA_VERSION = 1
MAX_SEARCH_DEPTH = 4


def _stable_path(path: Path) -> str:
    return str(path.expanduser().resolve())


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        resolved = _stable_path(path)
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(Path(resolved))
    return unique


def _collect_search_roots(core_hint: Path | None = None) -> list[Path]:
    cwd = Path.cwd().resolve()
    home = Path.home().resolve()
    roots = [
        cwd,
        *cwd.parents[:3],
        home / "Downloads" / "projects",
        home / "Downloads" / "lambdas",
    ]
    if core_hint is not None:
        roots.extend([core_hint, *core_hint.parents[:3]])
    return [path for path in _dedupe_paths(roots) if path.exists()]


def _repo_root_from_path(candidate: Path) -> Path | None:
    current = candidate if candidate.is_dir() else candidate.parent
    for path in [current, *current.parents]:
        if (path / ".codex").is_dir():
            return path
    return None


def _looks_like_path(raw: str) -> bool:
    return raw.startswith(("~", ".", "/")) or os.sep in raw


def _walk_matches(root: Path, repo_name: str) -> list[Path]:
    matches: list[Path] = []
    target = repo_name.casefold()
    for dirpath, dirnames, _filenames in os.walk(root):
        current = Path(dirpath)
        relative_parts = current.relative_to(root).parts if current != root else ()
        depth = len(relative_parts)
        dirnames.sort()
        if depth > MAX_SEARCH_DEPTH:
            dirnames[:] = []
            continue
        if current.name.casefold() == target and (current / ".codex").is_dir():
            matches.append(current.resolve())
            dirnames[:] = []
    return matches


def resolve_repo(raw: str, search_roots: list[Path]) -> Path:
    candidate = Path(os.path.expandvars(raw)).expanduser()
    if candidate.exists() or _looks_like_path(raw):
        if not candidate.exists():
            raise SystemExit(f"Path does not exist: {candidate}")
        repo_root = _repo_root_from_path(candidate.resolve())
        if repo_root is None:
            raise SystemExit(f"Path is not inside a repo with .codex: {candidate}")
        return repo_root

    matches: list[Path] = []
    for root in search_roots:
        direct = root / raw
        if direct.is_dir() and (direct / ".codex").is_dir():
            matches.append(direct.resolve())
            continue
        matches.extend(_walk_matches(root, raw))

    unique_matches = _dedupe_paths(matches)
    if not unique_matches:
        checked = "\n".join(str(root / raw) for root in search_roots)
        raise SystemExit(f"Repo not found for name '{raw}'. Checked roots:\n{checked}")
    if len(unique_matches) > 1:
        joined = "\n".join(str(path) for path in unique_matches)
        raise SystemExit(f"Multiple repos matched '{raw}'. Be more specific:\n{joined}")
    return unique_matches[0]


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def _resolve_existing_core_from_manifest(
    manifest_path: Path,
    search_roots: list[Path],
) -> Path | None:
    payload = _read_json(manifest_path)
    if not payload:
        return None
    declared = payload.get("declared_core_repo")
    if isinstance(declared, str) and declared.strip():
        try:
            return resolve_repo(declared.strip(), search_roots)
        except SystemExit:
            return None
    return None


def _extract_repo_hint_from_agents(text: str) -> str | None:
    shared_home = re.search(r"Treat `([^`]+?)/\.codex` as a shared home", text)
    if shared_home:
        return shared_home.group(1).strip()

    eslint_path = re.search(
        r"`([^`]+?)/(?:Downloads/projects|Downloads/lambdas)/eslint\.config\.mjs`",
        text,
    )
    if eslint_path:
        return eslint_path.group(1).strip()
    return None


def _resolve_existing_core_from_agents(
    agents_path: Path,
    search_roots: list[Path],
) -> Path | None:
    try:
        text = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    hint = _extract_repo_hint_from_agents(text)
    if not hint:
        return None
    try:
        return resolve_repo(hint, search_roots)
    except SystemExit:
        return None


def discover_existing_brain_core(brain_repo: Path, search_roots: list[Path]) -> Path | None:
    brain_codex = brain_repo / ".codex"
    manifest_match = _resolve_existing_core_from_manifest(brain_codex / "core-home.json", search_roots)
    if manifest_match is not None:
        return manifest_match
    return _resolve_existing_core_from_agents(brain_codex / "AGENTS.md", search_roots)


def build_fallback_chain(
    declared_core_repo: Path,
    existing_brain_core_repo: Path | None,
) -> list[dict[str, Any]]:
    chain: list[dict[str, Any]] = []

    def add_repo_entry(kind: str, repo_path: Path) -> None:
        chain.append(
            {
                "kind": kind,
                "repo_path": _stable_path(repo_path),
                "codex_path": _stable_path(repo_path / ".codex"),
                "exists": (repo_path / ".codex").is_dir(),
            }
        )

    add_repo_entry("declared_core", declared_core_repo)
    if existing_brain_core_repo is not None:
        add_repo_entry("brain_defined_core", existing_brain_core_repo)

    global_codex = Path.home() / ".codex"
    if global_codex.is_dir():
        chain.append(
            {
                "kind": "global_codex",
                "repo_path": None,
                "codex_path": _stable_path(global_codex),
                "exists": True,
            }
        )

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in chain:
        key = entry["codex_path"]
        if key in seen or not entry["exists"]:
            continue
        seen.add(key)
        deduped.append(entry)
    return deduped


def resolve_shared_assets(fallback_chain: list[dict[str, Any]]) -> dict[str, Any]:
    assets = {
        "projects": Path("Downloads/projects/eslint.config.mjs"),
        "lambdas": Path("Downloads/lambdas/eslint.config.mjs"),
    }
    resolved: dict[str, Any] = {}
    for asset_name, relative_path in assets.items():
        candidates: list[dict[str, Any]] = []
        selected_path: str | None = None
        selected_from: str | None = None
        for entry in fallback_chain:
            repo_path = entry.get("repo_path")
            if repo_path is None:
                continue
            candidate = Path(repo_path) / relative_path
            exists = candidate.is_file()
            candidate_entry = {
                "from": entry["kind"],
                "path": _stable_path(candidate),
                "exists": exists,
            }
            candidates.append(candidate_entry)
            if selected_path is None and exists:
                selected_path = candidate_entry["path"]
                selected_from = entry["kind"]
        resolved[asset_name] = {
            "selected_path": selected_path,
            "selected_from": selected_from,
            "candidates": candidates,
        }
    return {"eslint": resolved}


def build_manifest(
    brain_repo: Path,
    declared_core_repo: Path,
    fallback_chain: list[dict[str, Any]],
    resolved_shared_assets: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "brain_repo": _stable_path(brain_repo),
        "declared_core_repo": _stable_path(declared_core_repo),
        "fallback_chain": fallback_chain,
        "resolved_shared_assets": resolved_shared_assets,
    }


def _generated_ref_text(manifest: dict[str, Any]) -> str:
    lines = [
        "# Shared Core Resolution (Generated)",
        "",
        "Generated by `sync-brain-core-home`. Do not edit manually.",
        "",
        "## Resolution Order",
        "",
    ]
    for index, entry in enumerate(manifest["fallback_chain"], start=1):
        label = entry["kind"]
        path_label = entry["repo_path"] or entry["codex_path"]
        lines.append(f"{index}. `{label}` -> `{path_label}`")

    eslint = manifest["resolved_shared_assets"]["eslint"]
    lines.extend(
        [
            "",
            "## Shared ESLint",
            "",
        ]
    )
    for asset_name in ("projects", "lambdas"):
        asset = eslint[asset_name]
        selected = asset["selected_path"] or "not found"
        lines.append(f"### {asset_name.title()}")
        lines.append(f"- Selected: `{selected}`")
        if asset["selected_from"]:
            lines.append(f"- Selected from: `{asset['selected_from']}`")
        else:
            lines.append("- Selected from: `none`")
        lines.append("- Candidates in order:")
        for candidate in asset["candidates"]:
            exists_text = "yes" if candidate["exists"] else "no"
            lines.append(
                f"  - `{candidate['from']}`: `{candidate['path']}` (exists: {exists_text})"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _managed_block_text() -> str:
    return (
        f"{MANAGED_BEGIN}\n"
        "## Shared Core Resolution\n\n"
        "- Use `.codex/refs/shared-core-resolution.generated.md` as the canonical shared-core lookup for general/shared Codex assets.\n"
        "- Resolve shared assets in this order: declared core repo, existing brain-defined core, then global `~/.codex` when present.\n"
        "- Keep domain-specific policies, playbooks, refs, and skills under the local brain `.codex` as the canonical source.\n"
        "- When the user asks to run ESLint across projects, use the first existing shared config from the resolved core chain documented in `.codex/refs/shared-core-resolution.generated.md`.\n"
        f"{MANAGED_END}\n"
    )


def _remove_managed_block(text: str) -> str:
    pattern = re.compile(
        rf"\n?{re.escape(MANAGED_BEGIN)}.*?{re.escape(MANAGED_END)}\n?",
        re.DOTALL,
    )
    return re.sub(pattern, "\n", text)


def _remove_hardcoded_shared_lines(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    skip_eslint_block = False

    for line in lines:
        stripped = line.strip()
        if skip_eslint_block:
            if line.startswith("  - ") or line.startswith("\t- "):
                continue
            skip_eslint_block = False

        if re.search(r"Treat `[^`]+/\.codex` as a shared home", line):
            continue

        if stripped.startswith("- When the user asks to run ESLint across projects"):
            skip_eslint_block = True
            continue

        output.append(line)

    text = "\n".join(output).strip() + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def update_agents_content(original_text: str) -> str:
    text = _remove_managed_block(original_text)
    text = _remove_hardcoded_shared_lines(text)
    managed = _managed_block_text()

    header = "## Working rules"
    if header in text:
        before, after = text.split(header, 1)
        before = before.rstrip() + "\n\n"
        after = header + after
        result = before + managed + "\n" + after.lstrip()
    else:
        result = text.rstrip() + "\n\n" + managed

    result = re.sub(r"\n{3,}", "\n\n", result).rstrip() + "\n"
    return result


def build_write_plan(
    brain_repo: Path,
    manifest: dict[str, Any],
) -> dict[Path, str]:
    brain_codex = brain_repo / ".codex"
    refs_dir = brain_codex / "refs"

    agents_path = brain_codex / "AGENTS.md"
    try:
        original_agents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing AGENTS.md in brain repo: {agents_path}") from exc

    updated_agents = update_agents_content(original_agents)
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    resolution_text = _generated_ref_text(manifest)

    return {
        agents_path: updated_agents,
        brain_codex / "core-home.json": manifest_text,
        refs_dir / "shared-core-resolution.generated.md": resolution_text,
    }


def _write_changes(write_plan: dict[Path, str], dry_run: bool) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for path, new_text in write_plan.items():
        old_text = path.read_text(encoding="utf-8") if path.exists() else None
        changed = old_text != new_text
        changes.append({"path": str(path), "changed": changed})
        if not dry_run and changed:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new_text, encoding="utf-8")
    return changes


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync a brain repo to a declared shared core home.")
    parser.add_argument("--core", required=True, help="Absolute path or repo name for the shared core repo.")
    parser.add_argument("--brain", required=True, help="Absolute path or repo name for the brain repo.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing files.")
    parser.add_argument(
        "--print-resolution",
        action="store_true",
        help="Print resolved manifest JSON to stdout.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    preliminary_roots = _collect_search_roots()
    declared_core_repo = resolve_repo(args.core, preliminary_roots)
    search_roots = _collect_search_roots(declared_core_repo)
    brain_repo = resolve_repo(args.brain, search_roots)

    for label, repo_path in (("core", declared_core_repo), ("brain", brain_repo)):
        if not (repo_path / ".codex").is_dir():
            raise SystemExit(f"Resolved {label} repo is missing .codex: {repo_path}")

    existing_brain_core = discover_existing_brain_core(brain_repo, search_roots)
    fallback_chain = build_fallback_chain(declared_core_repo, existing_brain_core)
    resolved_shared_assets = resolve_shared_assets(fallback_chain)
    manifest = build_manifest(brain_repo, declared_core_repo, fallback_chain, resolved_shared_assets)
    write_plan = build_write_plan(brain_repo, manifest)
    changes = _write_changes(write_plan, args.dry_run)

    print(f"core_repo={_stable_path(declared_core_repo)}")
    print(f"brain_repo={_stable_path(brain_repo)}")
    print(f"existing_brain_core={_stable_path(existing_brain_core) if existing_brain_core else 'none'}")
    print(f"dry_run={'yes' if args.dry_run else 'no'}")
    for change in changes:
        print(f"file={change['path']} changed={'yes' if change['changed'] else 'no'}")

    if args.print_resolution:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
