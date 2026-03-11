#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized or "ionic-mobile-app"


def titleize_project_type(value: str) -> str:
    words = re.sub(r"[^a-zA-Z0-9]+", " ", value).split()
    if not words:
        return "Ionic Mobile App"
    return " ".join(word.capitalize() for word in words[:6])


def default_app_id(project_name: str) -> str:
    compact = project_name.replace("-", "")
    return f"com.example.{compact or 'ionicmobileapp'}"


def run_command(command: list[str]) -> int:
    process = subprocess.run(command)
    return process.returncode


def build_scaffold_command(args: argparse.Namespace) -> list[str]:
    project_name = args.project_name or slugify(args.project_type)
    app_name = args.app_name or titleize_project_type(args.project_type)
    app_id = args.app_id or default_app_id(project_name)

    command = [
        "bash",
        str(SCRIPT_DIR / "bootstrap_project.sh"),
        "--project-type",
        args.project_type,
        "--project-name",
        project_name,
        "--app-name",
        app_name,
        "--app-id",
        app_id,
        "--destination",
        str(Path(args.destination).expanduser().resolve()),
        "--capacitor-channel",
        args.capacitor_channel,
    ]

    if args.skip_platforms:
        command.append("--skip-platforms")
    if args.skip_build:
        command.append("--skip-build")
    if args.skip_install:
        command.append("--skip-install")
    if args.force:
        command.append("--force")

    return command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launcher for the ionic-angular-mobile-app-builder skill."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("versions", help="Resolve current Angular/Ionic/Capacitor versions.")

    check_parser = subparsers.add_parser("check", help="Run local environment checks.")
    check_parser.add_argument("--project", default=".", help="Optional project directory to inspect.")
    check_parser.add_argument("--require-android", action="store_true")
    check_parser.add_argument("--require-ios", action="store_true")

    scaffold_parser = subparsers.add_parser("scaffold", help="Create a new Ionic Angular app.")
    scaffold_parser.add_argument("--project-type", required=True, help="Short project description such as 'travel planner app'.")
    scaffold_parser.add_argument("--project-name", help="Directory/package slug. Defaults to a slugified project type.")
    scaffold_parser.add_argument("--app-name", help="Display name shown in native shells.")
    scaffold_parser.add_argument("--app-id", help="Capacitor app id. Defaults to com.example.<slug>.")
    scaffold_parser.add_argument("--destination", default=".", help="Directory where the new project folder will be created.")
    scaffold_parser.add_argument(
        "--capacitor-channel",
        choices=("stable", "next"),
        default="stable",
        help="Use stable Capacitor by default. Use next only for preview mode.",
    )
    scaffold_parser.add_argument("--skip-platforms", action="store_true", help="Do not run cap add android/ios.")
    scaffold_parser.add_argument("--skip-build", action="store_true", help="Skip the initial npm run build.")
    scaffold_parser.add_argument("--skip-install", action="store_true", help="Skip npm install steps after Angular scaffold.")
    scaffold_parser.add_argument("--force", action="store_true", help="Allow creation inside an existing empty destination folder.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "versions":
        return run_command(["python3", str(SCRIPT_DIR / "resolve_versions.py")])

    if args.command == "check":
        command = [
            "bash",
            str(SCRIPT_DIR / "post_setup_checks.sh"),
            "--project",
            str(Path(args.project).expanduser().resolve()),
        ]
        if args.require_android:
            command.append("--require-android")
        if args.require_ios:
            command.append("--require-ios")
        return run_command(command)

    if args.command == "scaffold":
        return run_command(build_scaffold_command(args))

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
