#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from generate_openai_yaml import write_openai_yaml

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "assets"}

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

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

If the skill is executable, the canonical flow must live in scripts plus `skill.runtime.json`.
Do not leave the runnable behavior only in prose. Generate or update `scripts/run.py`,
`scripts/main.py`, and `skill.runtime.json` so the skill can be executed via `run-skill`.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
"""

RUNNER_TEMPLATE = """#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _runtime_support_dir() -> Path:
    script_path = Path(__file__).resolve()
    candidates = [
        script_path.parents[2] / '.system' / 'skill-runtime-lib' / 'scripts',
        script_path.parents[2] / 'skill-runtime-lib' / 'scripts',
        script_path.parents[3] / '.system' / 'skill-runtime-lib' / 'scripts',
    ]
    for candidate in candidates:
        if (candidate / 'runtime_support.py').is_file():
            return candidate
    raise SystemExit('Unable to locate shared skill runtime support.')


RUNTIME_SUPPORT_DIR = _runtime_support_dir()
if str(RUNTIME_SUPPORT_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SUPPORT_DIR))

from runtime_support import launch_current_skill


if __name__ == '__main__':
    raise SystemExit(launch_current_skill(Path(__file__).resolve(), sys.argv[1:]))
"""

EXAMPLE_MAIN_SCRIPT = '''#!/usr/bin/env python3
"""
Canonical main command for {skill_name}

Replace this placeholder with the real skill logic.
"""

from __future__ import annotations


def main():
    print("TODO: implement {skill_name}")

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

Example real reference docs from other skills:
- product-management/references/communication.md - Comprehensive guide for status updates
- product-management/references/context_building.md - Deep-dive on gathering context
- bigquery/references/ - API references and query examples

## When Reference Docs Are Useful

Reference docs are ideal for:
- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for main SKILL.md
- Content that's only needed for specific use cases

## Structure Suggestions

### API Reference Example
- Overview
- Authentication
- Endpoints with examples
- Error codes
- Rate limits

### Workflow Guide Example
- Prerequisites
- Step-by-step instructions
- Common patterns
- Troubleshooting
- Best practices
"""

EXAMPLE_ASSET = """# Example Asset File

This placeholder represents where asset files would be stored.
Replace with actual asset files (templates, images, fonts, etc.) or delete if not needed.

Asset files are NOT intended to be loaded into context, but rather used within
the output Codex produces.

Example asset files from other skills:
- Brand guidelines: logo.png, slides_template.pptx
- Frontend builder: hello-world/ directory with HTML/React boilerplate
- Typography: custom-font.ttf, font-family.woff2
- Data: sample_data.csv, test_dataset.json

## Common Asset Types

- Templates: .pptx, .docx, boilerplate directories
- Images: .png, .jpg, .svg, .gif
- Fonts: .ttf, .otf, .woff, .woff2
- Boilerplate code: Project directories, starter files
- Icons: .ico, .svg
- Data files: .csv, .json, .xml, .yaml

Note: This is a text placeholder. Actual assets can be any file type.
"""


def normalize_skill_name(skill_name):
    """Normalize a skill name to lowercase hyphen-case."""
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_resources(raw_resources):
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        sys.exit(1)
    deduped = []
    seen = set()
    for resource in resources:
        if resource not in seen:
            deduped.append(resource)
            seen.add(resource)
    return deduped


def parse_supported_os(raw_supported_os):
    values = [item.strip() for item in raw_supported_os.split(",") if item.strip()]
    if not values:
        values = ["macos", "linux", "windows"]
    normalized = []
    aliases = {
        "mac": "macos",
        "macos": "macos",
        "darwin": "macos",
        "linux": "linux",
        "ubuntu": "linux",
        "windows": "windows",
        "win": "windows",
        "win32": "windows",
    }
    for value in values:
        key = aliases.get(value.lower())
        if key is None:
            print(f"[ERROR] Unsupported OS value: {value}")
            sys.exit(1)
        if key not in normalized:
            normalized.append(key)
    return normalized


def create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples):
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(exist_ok=True)
        if resource == "scripts":
            print("[OK] Created scripts/")
        elif resource == "references":
            if include_examples:
                example_reference = resource_dir / "api_reference.md"
                example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
                print("[OK] Created references/api_reference.md")
            else:
                print("[OK] Created references/")
        elif resource == "assets":
            if include_examples:
                example_asset = resource_dir / "example_asset.txt"
                example_asset.write_text(EXAMPLE_ASSET)
                print("[OK] Created assets/example_asset.txt")
            else:
                print("[OK] Created assets/")


def create_runtime_files(skill_dir, skill_name, supported_os):
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    run_py = scripts_dir / "run.py"
    run_py.write_text(RUNNER_TEMPLATE)
    run_py.chmod(0o755)
    print("[OK] Created scripts/run.py")

    main_py = scripts_dir / "main.py"
    if not main_py.exists():
        main_py.write_text(EXAMPLE_MAIN_SCRIPT.format(skill_name=skill_name))
        main_py.chmod(0o755)
        print("[OK] Created scripts/main.py")

    runtime_payload = {
        "schema_version": 2,
        "skill_name": skill_name,
        "execution_mode": "python_launcher",
        "supported_os": supported_os,
        "unsupported_behavior": "fail_fast",
        "preflight": {
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
        },
        "entrypoint": {
            "kind": "python",
            "path": "scripts/run.py",
        },
        "tooling": {
            "python": {
                "macos": ["python3"],
                "linux": ["python3"],
                "windows": ["py", "-3"],
            }
        },
        "default_command": skill_name,
        "commands": [
            {
                "name": skill_name,
                "description": "Primary skill command",
                "kind": "python",
                "path": "scripts/main.py",
                "args": [],
            }
        ],
        "recording": {
            "enabled_by_default": False,
            "output_dir_template": "~/.codex/tmp/skill-runs/{skill}/{timestamp}",
            "artifacts": ["run.json", "command.txt", "stdout.log", "stderr.log"],
        },
    }
    runtime_path = skill_dir / "skill.runtime.json"
    runtime_path.write_text(json.dumps(runtime_payload, indent=2) + "\n")
    print("[OK] Created skill.runtime.json")


def init_skill(skill_name, path, resources, include_examples, interface_overrides, supported_os):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created
        resources: Resource directories to create
        include_examples: Whether to create example files in resource directories

    Returns:
        Path to created skill directory, or None if error
    """
    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(f"[ERROR] Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"[ERROR] Error creating directory: {e}")
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    skill_md_path = skill_dir / "SKILL.md"
    try:
        skill_md_path.write_text(skill_content)
        print("[OK] Created SKILL.md")
    except Exception as e:
        print(f"[ERROR] Error creating SKILL.md: {e}")
        return None

    # Create agents/openai.yaml
    try:
        result = write_openai_yaml(skill_dir, skill_name, interface_overrides)
        if not result:
            return None
    except Exception as e:
        print(f"[ERROR] Error creating agents/openai.yaml: {e}")
        return None

    # Create resource directories if requested
    if resources:
        try:
            create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples)
        except Exception as e:
            print(f"[ERROR] Error creating resource directories: {e}")
            return None

    if "scripts" in resources:
        try:
            create_runtime_files(skill_dir, skill_name, supported_os)
        except Exception as e:
            print(f"[ERROR] Error creating runtime files: {e}")
            return None

    # Print next steps
    print(f"\n[OK] Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")
    if resources:
        if include_examples:
            print("2. Customize or delete the example files in scripts/, references/, and assets/")
        else:
            print("2. Add resources to scripts/, references/, and assets/ as needed")
    else:
        print("2. Create resource directories only if needed (scripts/, references/, assets/)")
    print("3. Update agents/openai.yaml if the UI metadata should differ")
    print("4. Run the validator when ready to check the skill structure")
    print(
        "5. Forward-test complex skills with realistic user requests to ensure they work as intended"
    )

    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description="Create a new skill directory with a SKILL.md template.",
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated list: scripts,references,assets",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Create example files inside the selected resource directories",
    )
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="Interface override in key=value format (repeatable)",
    )
    parser.add_argument(
        "--supported-os",
        default="macos,linux,windows",
        help="Comma-separated supported OS list for executable skills",
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
    supported_os = parse_supported_os(args.supported_os)
    if args.examples and not resources:
        print("[ERROR] --examples requires --resources to be set.")
        sys.exit(1)

    path = args.path

    print(f"Initializing skill: {skill_name}")
    print(f"   Location: {path}")
    if resources:
        print(f"   Resources: {', '.join(resources)}")
        if args.examples:
            print("   Examples: enabled")
        if "scripts" in resources:
            print(f"   Supported OS: {', '.join(supported_os)}")
    else:
        print("   Resources: none (create as needed)")
    print()

    result = init_skill(skill_name, path, resources, args.examples, args.interface, supported_os)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
