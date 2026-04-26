#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any


PERSONAL_SECTION_HEADING = "## Personal shared instruction sources"
CONFLICT_SECTION_HEADING = "## Conflict resolution"
CONFLICT_REF = Path(".codex/refs/personal-shared-conflict-resolution.md")
AGENTS = Path(".codex/AGENTS.md")


@dataclass(frozen=True)
class BrainConfig:
    key: str
    domain: str
    repo: Path
    source_role: str
    source_truth_bullet: str
    clickup_row: str
    skill_only_row: str | None
    validation_row: str
    conflict_extra_bullets: tuple[str, ...]
    working_replacements: tuple[tuple[str, str], ...] = ()


def home_repo(*parts: str) -> Path:
    return Path.home().joinpath(*parts)


BRAINS: dict[str, BrainConfig] = {
    "crp": BrainConfig(
        key="crp",
        domain="CRP",
        repo=home_repo("Downloads", "projects", "cloud-repos-panel-brain"),
        source_role=(
            "Canonical CRP domain guidance, local skills, policies, playbooks, refs, "
            "and repo routing rules."
        ),
        source_truth_bullet=(
            "Keep CRP local ClickUp, repo routing, and domain policies from this brain "
            "repo as the source of truth; use `codexDevAgent` only as generic fallback guidance."
        ),
        clickup_row=(
            "Keep CRP ClickUp and repo-routing behavior governed by local CRP policies "
            "in this brain repo. Do not copy OPTC opt-in ClickUp behavior into CRP."
        ),
        skill_only_row=(
            "When `.codex/policies/codeliver-skill-execution-policy.md` classifies a "
            "request as skill-only, that local policy overrides the general ClickUp "
            "lifecycle for that run."
        ),
        validation_row=(
            "For CRP project or lambda code changes, use the canonical sibling repos "
            "`$HOME/Downloads/projects/cloud-repos-panel` and "
            "`$HOME/Downloads/lambdas/crp_all/*` as the source of truth and run the "
            "targeted validation required by local CRP guidance. Shared generic "
            "validation rules can add checks but cannot weaken local CRP requirements."
        ),
        conflict_extra_bullets=(
            "Keep CRP ClickUp and repo-routing behavior governed by local CRP policies; do not replace it with OPTC opt-in ClickUp behavior.",
            "Local skill-only execution policy overrides the general ClickUp workflow for requests that qualify as skill-only runs.",
        ),
    ),
    "optc": BrainConfig(
        key="optc",
        domain="OPTC",
        repo=home_repo("Downloads", "projects", "optc-team-builder-brain"),
        source_role="Canonical OPTC domain guidance, local skills, refs, and app compatibility rules.",
        source_truth_bullet=(
            "Keep OPTC local workflow, skill routing, and app-compatibility rules from "
            "this brain repo as the source of truth; use `codexDevAgent` only as generic fallback guidance."
        ),
        clickup_row=(
            "ClickUp is opt-in for OPTC. Use ClickUp rules only when the user provides "
            "a task/link or explicitly asks for ClickUp handling."
        ),
        skill_only_row=None,
        validation_row=(
            "For app/code changes, use the sibling app repo "
            "`$HOME/Downloads/projects/optc-team-builder` as the source of truth and "
            "run the targeted validation required by local OPTC guidance. Shared "
            "generic validation rules can add checks but cannot weaken the local OPTC "
            "requirements."
        ),
        conflict_extra_bullets=(
            "ClickUp is opt-in for OPTC work. Apply ClickUp rules only when the user provides a task/link or explicitly asks for ClickUp handling.",
        ),
    ),
    "codeliver": BrainConfig(
        key="codeliver",
        domain="CodeDeliver",
        repo=home_repo("Downloads", "lambdas", "codeliver_all", "dm-codeliver-brain"),
        source_role=(
            "Canonical CodeDeliver domain guidance, local skills, policies, playbooks, "
            "refs, ClickUp routing, and system maps."
        ),
        source_truth_bullet=(
            "CodeDeliver ClickUp routing and auto-task rules in this file override "
            "`codexDevAgent`'s generic rule to confirm the target List first when the "
            "request matches a deterministic CodeDeliver route."
        ),
        clickup_row=(
            "Keep the mandatory CodeDeliver ClickUp workflow and deterministic "
            "auto-routing from this brain repo. When a deterministic CodeDeliver route "
            "matches, do not ask for the target List just because `codexDevAgent` would."
        ),
        skill_only_row=(
            "When `.codex/policies/codeliver-skill-execution-policy.md` classifies a "
            "request as skill-only, that local policy overrides the general ClickUp "
            "lifecycle for that run."
        ),
        validation_row=(
            "For CodeDeliver project or lambda code changes, use the canonical sibling "
            "repos `$HOME/Downloads/projects/codeliver-*` and "
            "`$HOME/Downloads/lambdas/codeliver_all/*` as the source of truth and run "
            "the targeted validation required by local CodeDeliver guidance. Shared "
            "generic validation rules can add checks but cannot weaken local "
            "CodeDeliver requirements."
        ),
        conflict_extra_bullets=(
            "Local skill-only execution policy overrides the general ClickUp workflow for requests that qualify as skill-only runs.",
        ),
        working_replacements=(
            (
                "- Unless the user explicitly says otherwise, create a new ClickUp task for the conversation using that workflow.",
                "- For skill-only execution requests, apply `.codex/policies/codeliver-skill-execution-policy.md` as the local carve-out from the default ClickUp workflow.\n"
                "- For non-skill-only requests, unless the user explicitly says otherwise, create a new ClickUp task for the conversation using the default ClickUp workflow.",
            ),
        ),
    ),
}


def personal_section(config: BrainConfig) -> str:
    return f"""## Personal shared instruction sources

- At the start of each task, look for these personal shared repos when they exist locally:
  - `$HOME/Downloads/projects/codex_utilities`
  - `$HOME/Downloads/projects/codexDevAgent`
- For every {config.domain} task, read `$HOME/Downloads/projects/codex_utilities/.codex/AGENTS.md` when present.
- For every {config.domain} task, read `$HOME/Downloads/projects/codexDevAgent/AGENTS.md` when present.
- If either personal repo is missing, continue without it and do not recreate it.
- Never edit `codex_utilities` or `codexDevAgent` to resolve conflicts for this domain.
- When either personal source changes and creates a conflict, resolve the adaptation in this brain repo's `.codex/AGENTS.md` or local `.codex/refs/` files only.
- Use `.codex/refs/personal-shared-conflict-resolution.md` as the local conflict matrix for these shared sources.
"""


def conflict_section(config: BrainConfig) -> str:
    extras = "\n".join(f"- {line}" for line in config.conflict_extra_bullets)
    if extras:
        extras += "\n"
    article = "an" if config.domain == "OPTC" else "a"
    return f"""## Conflict resolution

- Local {config.domain} domain rules in this brain repo win over shared or generic workflow rules.
- `codex_utilities` is the canonical shared executable asset and core source, not {article} {config.domain} domain authority.
- `codexDevAgent` supplies general workflow and skill-routing guidance only where it does not conflict with this brain repo; it is not a mandatory {config.domain} workflow.
- Always reply in Greek; this overrides `codexDevAgent`'s English default.
- {config.source_truth_bullet}
- Prefer same-named local {config.domain} skills, policies, playbooks, and refs first; then use `codex_utilities`; then `codexDevAgent`; then global `~/.codex` only when explicitly needed.
{extras}- Generic `codexDevAgent` branch, PR, push, release, and deploy gates apply only when the user requests commit, PR-ready changes, push, release, or deploy work.
- When `codex_utilities`, `codexDevAgent`, and this brain repo disagree, record the durable adaptation in this repo only.
"""


def conflict_ref_text(config: BrainConfig) -> str:
    clickup_label = "ClickUp"
    if config.key == "crp":
        clickup_label = "ClickUp and repo routing"
    elif config.key == "codeliver":
        clickup_label = "ClickUp and deterministic routing"
    skill_precedence = f"Prefer local {config.domain} skills/policies/playbooks/refs first"
    if config.key == "optc":
        skill_precedence = "Prefer local OPTC skills/refs first"
    rows = [
        (
            "Startup instruction loading",
            f"For every {config.domain} task, read `codex_utilities/.codex/AGENTS.md` "
            "and `codexDevAgent/AGENTS.md` when they exist. Missing personal repos "
            "are not recreated.",
        ),
        (
            "Language",
            "Reply to the user in Greek / Ελληνικά. This overrides the `codexDevAgent` "
            "English default. Repo markdown may stay in English when that matches "
            "existing local style.",
        ),
        (clickup_label, config.clickup_row),
    ]
    if config.skill_only_row:
        rows.append(("Skill-only execution", config.skill_only_row))
    rows.extend(
        [
            (
                "`CODEX_HOME` and shared core",
                f"Treat this brain repo's `.codex` as the local {config.domain} "
                "guidance home. Use `codex_utilities` as the declared shared core "
                "through `.codex/refs/shared-core-resolution.generated.md`. Do not "
                "make global `~/.codex` the primary source unless explicitly needed.",
            ),
            (
                "Skill precedence",
                f"{skill_precedence}, then `codex_utilities`, then `codexDevAgent`, "
                "then global `~/.codex` only when necessary.",
            ),
            ("Validation", config.validation_row),
            (
                "Branch, PR, push, release, deploy",
                "Generic `codexDevAgent` gates apply only when the user requests "
                "commit, PR-ready changes, push, release, or deploy work. Do not push "
                "or deploy without explicit confirmation.",
            ),
            (
                "Conflict fixes",
                f"Never edit `codex_utilities` or `codexDevAgent` to adapt "
                f"{config.domain} behavior. Make durable adaptations only in this "
                "brain repo's `.codex/AGENTS.md` or local `.codex/refs/` files.",
            ),
        ]
    )
    matrix = "\n".join(f"| {name} | {value} |" for name, value in rows)
    return f"""# Personal Shared Conflict Resolution

This reference resolves recurring conflicts between the {config.domain} brain, `codex_utilities`, and `codexDevAgent`.

## Source Roles

| Source | Role in {config.domain} work | Conflict behavior |
| --- | --- | --- |
| `{config.repo.name}/.codex` | {config.source_role} | Wins for all {config.domain} domain behavior. |
| `codex_utilities/.codex` | Shared executable/core asset source, including shared skills, scripts, rules, and resolved configs. | Use for shared assets and core lookup, not for overriding {config.domain} domain rules. |
| `codexDevAgent/AGENTS.md` | Generic workflow and skill-routing guidance. | Use only as fallback where {config.domain} guidance is silent. |

## Conflict Matrix

| Area | {config.domain} decision |
| --- | --- |
{matrix}

## Operating Rule

When a shared personal source changes and creates a new contradiction, resolve the {config.domain}-specific interpretation here or in `.codex/AGENTS.md`, then keep the shared repos read-only for this domain.
"""


def replace_section(text: str, heading: str, replacement: str) -> tuple[str, str | None]:
    pattern = re.compile(rf"^{re.escape(heading)}\n.*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    matches = list(pattern.finditer(text))
    if not matches:
        return text, f"missing required section `{heading}`"
    if len(matches) > 1:
        return text, f"multiple `{heading}` sections found"
    new_text = text[: matches[0].start()] + replacement.rstrip() + "\n\n" + text[matches[0].end():].lstrip()
    return re.sub(r"\n{3,}", "\n\n", new_text).rstrip() + "\n", None


def apply_working_replacements(text: str, config: BrainConfig) -> tuple[str, list[str]]:
    decisions: list[str] = []
    for old, new in config.working_replacements:
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            decisions.append(f"could not find working-rule anchor for {config.domain}")
    return text, decisions


def desired_agents_text(original: str, config: BrainConfig) -> tuple[str, list[str]]:
    decisions: list[str] = []
    if "<<<<<<<" in original or ">>>>>>>" in original or "=======" in original:
        decisions.append("merge conflict markers found in AGENTS.md")
        return original, decisions

    text, decision = replace_section(original, PERSONAL_SECTION_HEADING, personal_section(config))
    if decision:
        decisions.append(decision)
    text, decision = replace_section(text, CONFLICT_SECTION_HEADING, conflict_section(config))
    if decision:
        decisions.append(decision)
    text, working_decisions = apply_working_replacements(text, config)
    decisions.extend(working_decisions)
    return text, decisions


def unified_diff(path: Path, old: str | None, new: str) -> str:
    old_lines = [] if old is None else old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{path} (current)",
            tofile=f"{path} (desired)",
        )
    )


def plan_brain(config: BrainConfig) -> dict[str, Any]:
    repo = config.repo
    agents_path = repo / AGENTS
    ref_path = repo / CONFLICT_REF
    decisions: list[str] = []
    files: list[dict[str, Any]] = []

    if not repo.is_dir():
        return {"brain": config.key, "repo": str(repo), "decision_required": ["brain repo missing"], "files": []}
    if not (repo / ".codex").is_dir():
        return {"brain": config.key, "repo": str(repo), "decision_required": ["brain .codex missing"], "files": []}
    if not agents_path.is_file():
        return {"brain": config.key, "repo": str(repo), "decision_required": ["AGENTS.md missing"], "files": []}

    agents_old = agents_path.read_text(encoding="utf-8")
    agents_new, agent_decisions = desired_agents_text(agents_old, config)
    decisions.extend(agent_decisions)
    files.append(
        {
            "path": str(agents_path),
            "old": agents_old,
            "new": agents_new,
            "changed": agents_old != agents_new,
        }
    )

    ref_old = ref_path.read_text(encoding="utf-8") if ref_path.exists() else None
    ref_new = conflict_ref_text(config)
    if ref_old and ("<<<<<<<" in ref_old or ">>>>>>>" in ref_old or "=======" in ref_old):
        decisions.append("merge conflict markers found in conflict-resolution ref")
    files.append(
        {
            "path": str(ref_path),
            "old": ref_old,
            "new": ref_new,
            "changed": ref_old != ref_new,
        }
    )

    return {"brain": config.key, "repo": str(repo), "decision_required": decisions, "files": files}


def write_plan(plan: dict[str, Any], dry_run: bool) -> None:
    if plan["decision_required"]:
        return
    for file_plan in plan["files"]:
        if not file_plan["changed"] or dry_run:
            continue
        path = Path(file_plan["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file_plan["new"], encoding="utf-8")


def parse_brains(raw: str) -> list[BrainConfig]:
    if raw == "all":
        return [BRAINS["crp"], BRAINS["optc"], BRAINS["codeliver"]]
    selected: list[BrainConfig] = []
    for key in [part.strip() for part in raw.split(",") if part.strip()]:
        if key not in BRAINS:
            valid = ", ".join(["all", *BRAINS])
            raise SystemExit(f"Unknown brain `{key}`. Valid values: {valid}")
        selected.append(BRAINS[key])
    if not selected:
        raise SystemExit("No brains selected.")
    return selected


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync shared-agent conflict policy across known brain repos."
    )
    parser.add_argument("--brains", default="all", help="all or comma-list: crp,optc,codeliver")
    parser.add_argument("--dry-run", action="store_true", help="Plan changes without writing files.")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if changes or decisions are needed.")
    parser.add_argument("--show-diff", action="store_true", help="Print unified diffs for changed files.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result JSON.")
    return parser.parse_args(argv)


def summarize(plans: list[dict[str, Any]], dry_run: bool, show_diff: bool) -> None:
    print(f"dry_run={'yes' if dry_run else 'no'}")
    for plan in plans:
        decisions = plan["decision_required"]
        status = "decision_required" if decisions else "ok"
        print(f"brain={plan['brain']} repo={plan['repo']} status={status}")
        for decision in decisions:
            print(f"  decision_required={decision}")
        for file_plan in plan["files"]:
            print(f"  file={file_plan['path']} changed={'yes' if file_plan['changed'] else 'no'}")
            if show_diff and file_plan["changed"]:
                print(unified_diff(Path(file_plan["path"]), file_plan["old"], file_plan["new"]).rstrip())


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    configs = parse_brains(args.brains)
    plans = [plan_brain(config) for config in configs]

    for plan in plans:
        write_plan(plan, dry_run=args.dry_run or args.check)

    summarize(plans, dry_run=args.dry_run or args.check, show_diff=args.show_diff)

    if args.json:
        payload = []
        for plan in plans:
            payload.append(
                {
                    "brain": plan["brain"],
                    "repo": plan["repo"],
                    "decision_required": plan["decision_required"],
                    "files": [
                        {"path": file_plan["path"], "changed": file_plan["changed"]}
                        for file_plan in plan["files"]
                    ],
                }
            )
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    any_decisions = any(plan["decision_required"] for plan in plans)
    any_changes = any(file_plan["changed"] for plan in plans for file_plan in plan["files"])
    if any_decisions:
        return 3
    if args.check and any_changes:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
