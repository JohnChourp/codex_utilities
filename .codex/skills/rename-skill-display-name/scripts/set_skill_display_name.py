#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


SKILLS_ROOT = Path("/Users/john/.codex/skills")


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def read_frontmatter_name(skill_md: Path) -> str | None:
    try:
        lines = skill_md.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:40]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def resolve_skill_dir(raw: str) -> Path:
    candidate = Path(raw).expanduser()
    if candidate.is_file() and candidate.name == "SKILL.md":
        return candidate.parent
    if candidate.is_dir():
        return candidate

    direct = SKILLS_ROOT / raw
    if direct.is_dir():
        return direct

    lowered = raw.casefold()
    matches: list[Path] = []
    for skill_md in SKILLS_ROOT.glob("*/SKILL.md"):
        skill_dir = skill_md.parent
        if skill_dir.name.casefold() == lowered:
            matches.append(skill_dir)
            continue
        frontmatter_name = read_frontmatter_name(skill_md)
        if frontmatter_name and frontmatter_name.casefold() == lowered:
            matches.append(skill_dir)

    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]

    checked = [str(candidate), str(direct)]
    if unique_matches:
        raise SystemExit(
            "Multiple skills matched. Be more specific.\n"
            + "\n".join(str(path) for path in unique_matches)
        )
    raise SystemExit(
        "Skill not found. Checked:\n" + "\n".join(checked)
    )


def update_openai_yaml(path: Path, display_name: str) -> None:
    display_line = f"  display_name: {yaml_quote(display_name)}"
    interface_line = "interface:"

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(interface_line + "\n" + display_line + "\n", encoding="utf-8")
        return

    lines = path.read_text(encoding="utf-8").splitlines()
    interface_idx = next((i for i, line in enumerate(lines) if line.strip() == interface_line), None)

    if interface_idx is None:
        new_lines = [interface_line, display_line, ""] + lines
        path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
        return

    next_section_idx = len(lines)
    for idx in range(interface_idx + 1, len(lines)):
        line = lines[idx]
        if line and not line.startswith(" "):
            next_section_idx = idx
            break

    display_idx = None
    for idx in range(interface_idx + 1, next_section_idx):
        if lines[idx].lstrip().startswith("display_name:"):
            display_idx = idx
            break

    if display_idx is not None:
        lines[display_idx] = display_line
    else:
        lines.insert(interface_idx + 1, display_line)

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rename only a skill display name in agents/openai.yaml")
    parser.add_argument("--skill", required=True, help="Skill folder, SKILL.md path, or skill name")
    parser.add_argument("--display-name", required=True, help="New UI display name")
    args = parser.parse_args()

    skill_dir = resolve_skill_dir(args.skill)
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    update_openai_yaml(openai_yaml, args.display_name)

    print(f"skill_dir={skill_dir}")
    print(f"openai_yaml={openai_yaml}")
    print(f"display_name={args.display_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
