#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PROJECTS_ROOT = str(Path.home() / "Downloads" / "projects")
DEFAULT_LAMBDAS_ROOT = str(Path.home() / "Downloads" / "lambdas" / "crp_all")

API_LAMBDA_RE = re.compile(r"/prod/(crp-[a-z0-9-]+)")
LOG_NAME_RE = re.compile(r'logName\s*:\s*["\'](crp-[a-z0-9-]+)["\']')


def find_entry_lambdas(frontend_files):
    lambda_sources = defaultdict(set)

    for file_path in frontend_files:
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        for match in API_LAMBDA_RE.finditer(text):
            lambda_sources[match.group(1)].add(f"{file_path}:api_path")

        for match in LOG_NAME_RE.finditer(text):
            lambda_sources[match.group(1)].add(f"{file_path}:logName")

    return lambda_sources


def build_lambda_index(lambdas_root: Path):
    index = defaultdict(list)
    ignored_names = {"node_modules", ".git", "__pycache__"}

    if not lambdas_root.exists():
        return index

    for first in sorted(lambdas_root.iterdir()):
        if not first.is_dir() or first.name in ignored_names:
            continue

        # Normal CRP layout: lambdas are direct children under crp_all.
        if (first / "index.js").exists() or (first / "package.json").exists() or (first / "cloudformation").exists():
            index[first.name].append(str(first.resolve()))
            continue

        # Fallback for grouped layouts.
        for second in sorted(first.iterdir()):
            if not second.is_dir() or second.name in ignored_names:
                continue
            index[second.name].append(str(second.resolve()))

    return index


def collect_entries(projects_root: Path, frontend_project: str, lambdas_root: Path):
    project_root = projects_root / frontend_project
    frontend_files = [
        project_root / "src" / "app" / "shared" / "data-storage.service.ts",
        project_root / "src" / "app" / "shared" / "auth" / "auth.service.ts",
    ]

    lambda_sources = find_entry_lambdas(frontend_files)
    lambda_index = build_lambda_index(lambdas_root)

    entries = []
    unresolved = []
    ambiguous = []

    for entry_lambda in sorted(lambda_sources.keys()):
        matches = lambda_index.get(entry_lambda, [])
        item = {
            "frontend_project": frontend_project,
            "entry_lambda": entry_lambda,
            "discovered_from": sorted(lambda_sources[entry_lambda]),
            "resolved_lambda_path": None,
        }

        if len(matches) == 1:
            item["status"] = "resolved"
            item["resolved_lambda_path"] = matches[0]
        elif len(matches) == 0:
            item["status"] = "unresolved"
            unresolved.append(
                {
                    "frontend_project": frontend_project,
                    "entry_lambda": entry_lambda,
                    "kind": "entry_unresolved",
                }
            )
        else:
            item["status"] = "ambiguous"
            item["candidates"] = matches
            ambiguous.append(
                {
                    "frontend_project": frontend_project,
                    "entry_lambda": entry_lambda,
                    "kind": "entry_ambiguous",
                    "candidates": matches,
                }
            )

        entries.append(item)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projects_root": str(projects_root.resolve()),
        "frontend_project": frontend_project,
        "frontend_files": [str(path.resolve()) for path in frontend_files],
        "lambdas_root": str(lambdas_root.resolve()),
        "entries": entries,
        "summary": {
            "total_entries": len(entries),
            "resolved": sum(1 for item in entries if item["status"] == "resolved"),
            "unresolved": len(unresolved),
            "ambiguous": len(ambiguous),
        },
        "unresolved": unresolved,
        "ambiguous": ambiguous,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Collect frontend-reachable CRP lambdas from cloud-repos-panel service files."
    )
    parser.add_argument("--projects-root", default=DEFAULT_PROJECTS_ROOT)
    parser.add_argument("--frontend-project", default="cloud-repos-panel")
    parser.add_argument("--lambdas-root", default=DEFAULT_LAMBDAS_ROOT)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    projects_root = Path(args.projects_root)
    lambdas_root = Path(args.lambdas_root)

    if not projects_root.exists():
        raise SystemExit(f"projects root not found: {projects_root}")
    if not lambdas_root.exists():
        raise SystemExit(f"lambdas root not found: {lambdas_root}")

    result = collect_entries(projects_root=projects_root, frontend_project=args.frontend_project, lambdas_root=lambdas_root)
    json_output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_output + "\n", encoding="utf-8")
        print(f"wrote: {output_path}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
