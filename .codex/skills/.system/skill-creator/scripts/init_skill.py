#!/usr/bin/env python3
"""Initialize a new skill with runtime metadata and optional launcher."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from generate_openai_yaml import write_openai_yaml

RUNTIME_SUPPORT_DIR = (
    Path(__file__).resolve().parents[2] / "skill-runtime-lib" / "scripts"
)
if str(RUNTIME_SUPPORT_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SUPPORT_DIR))

from runtime_support import validate_skill

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "assets"}
RUNTIME_MODES = {"auto", "guidance", "python_launcher"}

SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" -> "Reading" -> "Creating" -> "Editing"
- Structure: ## Overview -> ## Workflow Decision Tree -> ## Step 1 -> ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" -> "Merge PDFs" -> "Split PDFs" -> "Extract Text"
- Structure: ## Overview -> ## Quick Start -> ## Task Category 1 -> ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" -> "Colors" -> "Typography" -> "Features"
- Structure: ## Overview -> ## Guidelines -> ## Specifications -> ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" -> numbered capability list
- Structure: ## Overview -> ## Core Capabilities -> ### 1. Feature -> ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed]

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this section if no resources are required.
"""

RUN_TEMPLATE = """#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _runtime_support_dir() -> Path:
    script_path = Path(__file__).resolve()
    candidates = [
        script_path.parents[2] / ".system" / "skill-runtime-lib" / "scripts",
        script_path.parents[2] / "skill-runtime-lib" / "scripts",
        script_path.parents[3] / ".system" / "skill-runtime-lib" / "scripts",
    ]
    for candidate in candidates:
        if (candidate / "runtime_support.py").is_file():
            return candidate
    raise SystemExit("Unable to locate shared skill runtime support.")


RUNTIME_SUPPORT_DIR = _runtime_support_dir()
if str(RUNTIME_SUPPORT_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SUPPORT_DIR))

from runtime_support import launch_current_skill


if __name__ == "__main__":
    raise SystemExit(launch_current_skill(Path(__file__).resolve(), sys.argv[1:]))
"""

MAIN_TEMPLATE = """#!/usr/bin/env python3
from __future__ import annotations


def main() -> int:
    print("Replace scripts/main.py with the real implementation for {skill_name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""

REFERENCE_TEMPLATE = """# Reference Documentation for {skill_title}

Replace this file with the reference material that the skill should load on demand.
"""

ASSET_TEMPLATE = """This placeholder represents an output asset for the skill.
Replace it with a real template, image, font, or other artifact when needed.
"""


def normalize_skill_name(skill_name: str) -> str:
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case_skill_name(skill_name: str) -> str:
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_resources(raw_resources: str) -> list[str]:
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        sys.exit(1)
    deduped: list[str] = []
    seen: set[str] = set()
    for resource in resources:
        if resource not in seen:
            deduped.append(resource)
            seen.add(resource)
    return deduped


def resolve_runtime_mode(requested: str, resources: list[str]) -> str:
    if requested == "auto":
        return "python_launcher" if "scripts" in resources else "guidance"
    return requested


def build_runtime_config(skill_name: str, execution_mode: str) -> dict[str, object]:
    runtime: dict[str, object] = {
        "schema_version": 1,
        "skill_name": skill_name,
        "execution_mode": execution_mode,
        "supported_os": ["macos", "linux", "windows"],
        "unsupported_behavior": "fail_fast",
        "preflight": {
            "cache_ttl_seconds": 600,
            "checks": [],
        },
        "entrypoint": None,
        "tooling": {
            "python": {
                "macos": ["python3"],
                "linux": ["python3"],
                "windows": ["py", "-3"],
            },
            "bash": {
                "macos": ["bash"],
                "linux": ["bash"],
                "windows": ["bash"],
            },
        },
    }
    if execution_mode == "python_launcher":
        runtime["preflight"] = {
            "cache_ttl_seconds": 600,
            "checks": [
                {
                    "type": "tool",
                    "name": "python",
                    "install_hint": {
                        "macos": "Install Python 3 and ensure python3 is in PATH.",
                        "linux": "Install python3 and ensure it is in PATH.",
                        "windows": "Install Python 3 or the py launcher and ensure it is in PATH.",
                    },
                }
            ],
        }
        runtime["entrypoint"] = {"kind": "python", "path": "scripts/run.py"}
        runtime["default_command"] = "main"
        runtime["commands"] = [
            {
                "name": "main",
                "description": "Primary skill command",
                "kind": "python",
                "path": "scripts/main.py",
                "args": [],
            }
        ]
    return runtime


def write_text_file(path: Path, content: str, executable: bool = False) -> None:
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def create_resource_dirs(
    skill_dir: Path,
    skill_name: str,
    skill_title: str,
    resources: list[str],
    execution_mode: str,
) -> None:
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(exist_ok=True)
        if resource == "references":
            write_text_file(resource_dir / "reference.md", REFERENCE_TEMPLATE.format(skill_title=skill_title))
            print("[OK] Created references/reference.md")
        elif resource == "assets":
            write_text_file(resource_dir / "asset.txt", ASSET_TEMPLATE)
            print("[OK] Created assets/asset.txt")
        elif resource == "scripts":
            print("[OK] Created scripts/")

    if execution_mode == "python_launcher":
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        write_text_file(scripts_dir / "run.py", RUN_TEMPLATE, executable=True)
        write_text_file(
            scripts_dir / "main.py",
            MAIN_TEMPLATE.format(skill_name=skill_name),
            executable=True,
        )
        print("[OK] Created scripts/run.py")
        print("[OK] Created scripts/main.py")


def init_skill(
    skill_name: str,
    path: str,
    resources: list[str],
    interface_overrides: list[str],
    runtime_mode: str,
) -> Path | None:
    skill_dir = Path(path).resolve() / skill_name
    if skill_dir.exists():
        print(f"[ERROR] Skill directory already exists: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] Created skill directory: {skill_dir}")
    except Exception as exc:
        print(f"[ERROR] Error creating directory: {exc}")
        return None

    skill_title = title_case_skill_name(skill_name)
    try:
        write_text_file(
            skill_dir / "SKILL.md",
            SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title),
        )
        print("[OK] Created SKILL.md")
    except Exception as exc:
        print(f"[ERROR] Error creating SKILL.md: {exc}")
        return None

    try:
        result = write_openai_yaml(skill_dir, skill_name, interface_overrides)
        if not result:
            return None
    except Exception as exc:
        print(f"[ERROR] Error creating agents/openai.yaml: {exc}")
        return None

    try:
        create_resource_dirs(skill_dir, skill_name, skill_title, resources, runtime_mode)
        runtime_path = skill_dir / "skill.runtime.json"
        runtime_payload = build_runtime_config(skill_name, runtime_mode)
        runtime_path.write_text(json.dumps(runtime_payload, indent=2) + "\n", encoding="utf-8")
        print("[OK] Created skill.runtime.json")
    except Exception as exc:
        print(f"[ERROR] Error creating runtime resources: {exc}")
        return None

    issues = validate_skill(skill_dir)
    errors = [issue for issue in issues if issue.level == "ERROR"]
    if errors:
        for issue in errors:
            print(issue.format(), file=sys.stderr)
        print("[ERROR] New skill failed validation")
        return None

    print(f"\n[OK] Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to replace the TODO placeholders.")
    print("2. Update skill.runtime.json to declare the final preflight and supported OS matrix.")
    if runtime_mode == "python_launcher":
        print("3. Replace scripts/main.py with the real implementation and keep scripts/run.py as the canonical launcher.")
    else:
        print("3. Add scripts/ only if the skill later becomes executable, then switch runtime_mode to python_launcher.")
    print("4. Run the validator again before installing or syncing the skill.")
    return skill_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new skill directory with runtime metadata.")
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument("--resources", default="", help="Comma-separated list: scripts,references,assets")
    parser.add_argument(
        "--runtime-mode",
        default="auto",
        choices=sorted(RUNTIME_MODES),
        help="Runtime mode for the new skill. Defaults to auto.",
    )
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="Interface override in key=value format (repeatable)",
    )
    args = parser.parse_args()

    raw_skill_name = args.skill_name
    skill_name = normalize_skill_name(raw_skill_name)
    if not skill_name:
        print("[ERROR] Skill name must include at least one letter or digit.")
        sys.exit(1)
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"[ERROR] Skill name '{skill_name}' is too long ({len(skill_name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH} characters."
        )
        sys.exit(1)
    if skill_name != raw_skill_name:
        print(f"Note: Normalized skill name from '{raw_skill_name}' to '{skill_name}'.")

    resources = parse_resources(args.resources)
    runtime_mode = resolve_runtime_mode(args.runtime_mode, resources)
    if runtime_mode == "python_launcher" and "scripts" not in resources:
        resources = ["scripts", *resources]

    print(f"Initializing skill: {skill_name}")
    print(f"   Location: {args.path}")
    print(f"   Runtime mode: {runtime_mode}")
    if resources:
        print(f"   Resources: {', '.join(resources)}")
    else:
        print("   Resources: none")
    print()

    result = init_skill(skill_name, args.path, resources, args.interface, runtime_mode)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
