#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PAGE_TS_SUFFIX = ".page.ts"
PAGE_HTML_SUFFIX = ".page.html"
COMPONENT_TS_SUFFIX = ".component.ts"
COMPONENT_HTML_SUFFIX = ".component.html"

SELECTOR_RE = re.compile(r"selector:\s*['\"](?P<selector>app-[a-z0-9-]+)['\"]")
CLASS_RE = re.compile(r"export class\s+(?P<class_name>[A-Za-z0-9_]+)")
APP_TAG_RE = re.compile(r"<(?P<selector>app-[a-z0-9-]+)\b")
CONTROL_FLOW_OPEN_RE = re.compile(r"@(?P<kind>for|if|switch|case|default|else|defer|placeholder|loading|error)\b[^{}]*\{")
SINGLE_CLOSE_BRACE_RE = re.compile(r"(?<!\{)\}(?!\})")

PAGE_TRACE_RE = re.compile(
    r"ionViewDidEnter\s*\([^)]*\)\s*(?::\s*[^{]+)?\{[\s\S]{0,600}?console\.log\([^)]*\bcomponent\b",
    re.MULTILINE,
)
MODAL_TRACE_RE = re.compile(
    r"ngOnChanges\s*\([^)]*\)\s*(?::\s*[^{]+)?\{[\s\S]{0,2400}?"
    r"if\s*\(\s*changes\[(?:'|\")isOpen(?:'|\")\][^)]*&&[^)]*this\.isOpen\s*\)\s*\{"
    r"[\s\S]{0,600}?console\.log\([^)]*\bcomponent\b",
    re.MULTILINE,
)
SHARED_TRACE_RE = re.compile(
    r"ngOnInit\s*\([^)]*\)\s*(?::\s*[^{]+)?\{[\s\S]{0,600}?console\.log\([^)]*\bcomponent\b",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Artifact:
    path: Path
    relative_path: str
    class_name: str
    selector: str | None
    kind: str


@dataclass(frozen=True)
class SelectorUsage:
    selector: str
    html_path: Path
    relative_html_path: str
    line: int
    in_loop: bool


@dataclass(frozen=True)
class Issue:
    kind: str
    relative_path: str
    line: int
    summary: str
    details: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "path": self.relative_path,
            "line": self.line,
            "summary": self.summary,
            "details": self.details,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit Angular/Ionic debug-trace coverage for pages, modal components, and shared components.",
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project directory or any nested path inside the Angular/Ionic project. Defaults to the current directory.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan the full project instead of limiting the audit to git-changed Angular files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report as JSON.",
    )
    return parser


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        package_json = candidate / "package.json"
        src_app = candidate / "src" / "app"
        if not package_json.exists() or not src_app.exists():
            continue

        try:
            package_payload = json.loads(read_text(package_json))
        except (OSError, json.JSONDecodeError):
            continue

        dependencies = package_payload.get("dependencies") or {}
        dev_dependencies = package_payload.get("devDependencies") or {}
        if "@angular/core" in dependencies or "@angular/core" in dev_dependencies:
            return candidate

    raise SystemExit("Could not resolve an Angular project root from the provided path.")


def git_changed_paths(project_root: Path) -> list[Path]:
    command = ["git", "-C", str(project_root), "status", "--porcelain"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return []

    changed: list[Path] = []
    for raw_line in result.stdout.splitlines():
        if not raw_line.strip():
            continue
        path_fragment = raw_line[3:]
        if " -> " in path_fragment:
            path_fragment = path_fragment.split(" -> ", maxsplit=1)[1]
        changed.append(project_root / path_fragment)
    return changed


def discover_artifacts(project_root: Path) -> tuple[list[Artifact], list[Artifact], dict[str, Artifact]]:
    pages: list[Artifact] = []
    components: list[Artifact] = []
    selector_map: dict[str, Artifact] = {}

    src_app = project_root / "src" / "app"
    for path in sorted(src_app.rglob("*.ts")):
        if path.name.endswith(".spec.ts"):
            continue
        relative_path = path.relative_to(project_root).as_posix()
        text = read_text(path)
        class_match = CLASS_RE.search(text)
        class_name = class_match.group("class_name") if class_match else path.stem
        selector_match = SELECTOR_RE.search(text)
        selector = selector_match.group("selector") if selector_match else None

        if path.name.endswith(PAGE_TS_SUFFIX):
            artifact = Artifact(path=path, relative_path=relative_path, class_name=class_name, selector=selector, kind="page")
            pages.append(artifact)
            continue

        if path.name.endswith(COMPONENT_TS_SUFFIX):
            text_lower = text.lower()
            is_modal_component = "ionmodal" in text_lower and re.search(r"public\s+isOpen\s*=", text) is not None
            kind = "modal_component" if is_modal_component else "shared_component"
            artifact = Artifact(path=path, relative_path=relative_path, class_name=class_name, selector=selector, kind=kind)
            components.append(artifact)
            if selector:
                selector_map[selector] = artifact

    return pages, components, selector_map


def sanitize_template_line(line: str) -> str:
    return re.sub(r"\{\{.*?\}\}", "", line)


def compute_loop_lines(lines: list[str]) -> set[int]:
    loop_lines: set[int] = set()
    stack: list[str] = []

    for index, raw_line in enumerate(lines):
        line = sanitize_template_line(raw_line)
        if "*ngFor" in line:
            loop_lines.add(index)

        close_count = len(SINGLE_CLOSE_BRACE_RE.findall(line))
        for _ in range(close_count):
            if stack:
                stack.pop()

        for match in CONTROL_FLOW_OPEN_RE.finditer(line):
            stack.append(match.group("kind"))

        if "for" in stack:
            loop_lines.add(index)

    return loop_lines


def collect_selector_usages(project_root: Path, selector_map: dict[str, Artifact]) -> dict[str, list[SelectorUsage]]:
    usages: dict[str, list[SelectorUsage]] = {selector: [] for selector in selector_map}

    for html_path in sorted((project_root / "src" / "app").rglob("*.html")):
        text = read_text(html_path)
        lines = text.splitlines()
        loop_lines = compute_loop_lines(lines)
        relative_html_path = html_path.relative_to(project_root).as_posix()

        for index, line in enumerate(lines):
            for match in APP_TAG_RE.finditer(line):
                selector = match.group("selector")
                if selector not in selector_map:
                    continue
                usages[selector].append(
                    SelectorUsage(
                        selector=selector,
                        html_path=html_path,
                        relative_html_path=relative_html_path,
                        line=index + 1,
                        in_loop=index in loop_lines or "*ngFor" in line,
                    ),
                )

    return usages


def resolve_html_peer(ts_path: Path) -> Path | None:
    if ts_path.name.endswith(PAGE_TS_SUFFIX):
        candidate = ts_path.with_name(ts_path.name.replace(PAGE_TS_SUFFIX, PAGE_HTML_SUFFIX))
        return candidate if candidate.exists() else None
    if ts_path.name.endswith(COMPONENT_TS_SUFFIX):
        candidate = ts_path.with_name(ts_path.name.replace(COMPONENT_TS_SUFFIX, COMPONENT_HTML_SUFFIX))
        return candidate if candidate.exists() else None
    return None


def select_targets(
    project_root: Path,
    pages: list[Artifact],
    components: list[Artifact],
    selector_map: dict[str, Artifact],
    selector_usages: dict[str, list[SelectorUsage]],
    scan_all: bool,
) -> tuple[str, list[Artifact]]:
    all_candidates = pages + components
    if scan_all:
        return "all", all_candidates

    changed_paths = git_changed_paths(project_root)
    candidate_paths: set[Path] = set()

    for changed_path in changed_paths:
        if not changed_path.exists():
            continue
        if changed_path.name.endswith((PAGE_TS_SUFFIX, COMPONENT_TS_SUFFIX)):
            candidate_paths.add(changed_path)
            continue
        if changed_path.name.endswith((PAGE_HTML_SUFFIX, COMPONENT_HTML_SUFFIX)):
            candidate_ts = changed_path.with_suffix(".ts")
            if candidate_ts.exists():
                candidate_paths.add(candidate_ts)

            try:
                relative_changed = changed_path.relative_to(project_root)
            except ValueError:
                continue

            if relative_changed.parts[:3] != ("src", "app"):
                continue

            for selector, usages in selector_usages.items():
                if any(usage.html_path == changed_path and not usage.in_loop for usage in usages):
                    candidate_paths.add(selector_map[selector].path)

    if not candidate_paths:
        return "all-fallback", all_candidates

    filtered = [artifact for artifact in all_candidates if artifact.path in candidate_paths]
    return "changed", filtered


def find_anchor_line(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    return line_number(text, match.start())


def audit_page(artifact: Artifact) -> Issue | None:
    text = read_text(artifact.path)
    if PAGE_TRACE_RE.search(text):
        return None

    ion_view_line = find_anchor_line(text, r"^\s*public\s+ionViewDidEnter\s*\(")
    class_line = find_anchor_line(text, r"^\s*export class ")
    details: list[str] = []

    if ion_view_line is None:
        details.append("Missing `ionViewDidEnter` with `console.log(\"<PageName> component\")`.")
        line = class_line or 1
    else:
        details.append("`ionViewDidEnter` exists but no `console.log(\"... component\")` was found inside it.")
        line = ion_view_line

    return Issue(
        kind="page-trace-missing",
        relative_path=artifact.relative_path,
        line=line,
        summary=f"Page trace missing in {artifact.class_name}.",
        details=details,
    )


def audit_modal_component(artifact: Artifact, usages: Iterable[SelectorUsage]) -> Issue | None:
    text = read_text(artifact.path)
    if MODAL_TRACE_RE.search(text):
        return None

    ng_on_changes_line = find_anchor_line(text, r"^\s*public\s+ngOnChanges\s*\(")
    class_line = find_anchor_line(text, r"^\s*export class ")
    line = ng_on_changes_line or class_line or 1

    details = [
        "Missing modal-open trace inside the `isOpen` branch of `ngOnChanges`.",
        "Expected shape: `if (changes[\"isOpen\"] && this.isOpen) { console.log(\"<ComponentName> component\"); ... }`.",
    ]

    non_loop_usages = [usage for usage in usages if not usage.in_loop]
    if non_loop_usages:
        details.extend(
            f"Selector use: {usage.relative_html_path}:{usage.line}"
            for usage in non_loop_usages[:8]
        )

    return Issue(
        kind="modal-trace-missing",
        relative_path=artifact.relative_path,
        line=line,
        summary=f"Modal component trace missing in {artifact.class_name}.",
        details=details,
    )


def audit_shared_component(artifact: Artifact, usages: Iterable[SelectorUsage]) -> Issue | None:
    non_loop_usages = [usage for usage in usages if not usage.in_loop]
    if not non_loop_usages:
        return None

    text = read_text(artifact.path)
    if SHARED_TRACE_RE.search(text):
        return None

    ng_on_init_line = find_anchor_line(text, r"^\s*public\s+ngOnInit\s*\(")
    class_line = find_anchor_line(text, r"^\s*export class ")
    details = []

    if ng_on_init_line is None:
        details.append("Missing `ngOnInit` with `console.log(\"<ComponentName> component\")` for non-loop selector usage.")
        line = class_line or 1
    else:
        details.append("`ngOnInit` exists but no `console.log(\"... component\")` was found inside it.")
        line = ng_on_init_line

    details.extend(
        f"Selector use: {usage.relative_html_path}:{usage.line}"
        for usage in non_loop_usages[:8]
    )

    return Issue(
        kind="shared-component-trace-missing",
        relative_path=artifact.relative_path,
        line=line,
        summary=f"Shared component trace missing in {artifact.class_name}.",
        details=details,
    )


def audit_project(project_root: Path, scan_all: bool) -> tuple[str, list[Issue]]:
    pages, components, selector_map = discover_artifacts(project_root)
    selector_usages = collect_selector_usages(project_root, selector_map)
    mode, targets = select_targets(project_root, pages, components, selector_map, selector_usages, scan_all)
    issues: list[Issue] = []

    for artifact in targets:
        if artifact.kind == "page":
            issue = audit_page(artifact)
        elif artifact.kind == "modal_component":
            issue = audit_modal_component(artifact, selector_usages.get(artifact.selector or "", []))
        else:
            issue = audit_shared_component(artifact, selector_usages.get(artifact.selector or "", []))
        if issue is not None:
            issues.append(issue)

    issues.sort(key=lambda item: (item.relative_path, item.line, item.kind))
    return mode, issues


def print_text_report(project_root: Path, mode: str, issues: list[Issue]) -> None:
    print(f"project={project_root}")
    print(f"mode={mode}")
    print(f"issues={len(issues)}")

    if not issues:
        print("No Angular/Ionic debug-trace gaps found.")
        return

    for issue in issues:
        print(f"- [{issue.kind}] {issue.relative_path}:{issue.line} {issue.summary}")
        for detail in issue.details:
            print(f"  {detail}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = find_project_root(Path(args.project))
    mode, issues = audit_project(project_root, scan_all=args.all)

    if args.json:
        payload = {
            "project": str(project_root),
            "mode": mode,
            "issues": [issue.to_dict() for issue in issues],
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print_text_report(project_root, mode, issues)

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
