#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REF_FILE_RE = re.compile(r"^codeliver-(app|pos|panel|sap)-lambdas\.md$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
IGNORED_SECTIONS = {
    "API Ids -> API Names",
    "Πηγές",
    "Sources",
}


def parse_ref_file(path: Path):
    project = path.name.replace("-lambdas.md", "")
    lambdas = []
    seen = set()

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = SECTION_RE.match(line.strip())
        if not match:
            continue
        section = match.group(1).strip()
        if section in IGNORED_SECTIONS:
            continue
        if section.startswith("Observed ") or section.startswith("Σκοπός:"):
            continue
        if section not in seen:
            seen.add(section)
            lambdas.append(section)

    return project, lambdas


def load_frontend_refs(refs_dir: Path):
    project_to_lambdas = {}
    for ref_file in sorted(refs_dir.glob("codeliver-*-lambdas.md")):
        if not REF_FILE_RE.match(ref_file.name):
            continue
        project, lambdas = parse_ref_file(ref_file)
        project_to_lambdas[project] = lambdas
    return project_to_lambdas


def build_lambda_index(lambdas_root: Path):
    index = defaultdict(list)
    for group_dir in sorted(lambdas_root.iterdir()):
        if not group_dir.is_dir():
            continue
        if group_dir.name in {"node_modules", ".git"}:
            continue
        for lambda_dir in sorted(group_dir.iterdir()):
            if lambda_dir.is_dir():
                index[lambda_dir.name].append(str(lambda_dir.resolve()))
    return index


def collect_entries(refs_dir: Path, lambdas_root: Path):
    project_to_lambdas = load_frontend_refs(refs_dir)
    lambda_index = build_lambda_index(lambdas_root)

    entries = []
    unresolved = []
    ambiguous = []

    for project, lambdas in sorted(project_to_lambdas.items()):
        for lambda_name in lambdas:
            matches = lambda_index.get(lambda_name, [])
            if len(matches) == 1:
                entries.append(
                    {
                        "frontend_project": project,
                        "entry_lambda": lambda_name,
                        "status": "resolved",
                        "resolved_lambda_path": matches[0],
                    }
                )
            elif len(matches) == 0:
                unresolved.append({"frontend_project": project, "entry_lambda": lambda_name})
                entries.append(
                    {
                        "frontend_project": project,
                        "entry_lambda": lambda_name,
                        "status": "unresolved",
                        "resolved_lambda_path": None,
                    }
                )
            else:
                ambiguous.append(
                    {
                        "frontend_project": project,
                        "entry_lambda": lambda_name,
                        "candidates": matches,
                    }
                )
                entries.append(
                    {
                        "frontend_project": project,
                        "entry_lambda": lambda_name,
                        "status": "ambiguous",
                        "resolved_lambda_path": None,
                        "candidates": matches,
                    }
                )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "refs_dir": str(refs_dir.resolve()),
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
    parser = argparse.ArgumentParser(description="Collect frontend-reachable lambdas from CodeDeliver refs.")
    parser.add_argument("--refs-dir", default="/home/dm-soft-1/.codex/refs")
    parser.add_argument("--lambdas-root", default="/home/dm-soft-1/Downloads/lambdas")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    refs_dir = Path(args.refs_dir)
    lambdas_root = Path(args.lambdas_root)

    if not refs_dir.exists():
        raise SystemExit(f"refs directory not found: {refs_dir}")
    if not lambdas_root.exists():
        raise SystemExit(f"lambdas root not found: {lambdas_root}")

    result = collect_entries(refs_dir=refs_dir, lambdas_root=lambdas_root)
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
