#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def npm_view(package: str, field: str) -> object:
    command = ["npm", "view", package, field, "--json"]
    try:
        raw = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Failed to resolve {package} {field} via npm view.\nCommand: {' '.join(command)}\nOutput:\n{exc.output}"
        ) from exc

    raw = raw.strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def pick_tag(dist_tags: object, tag_name: str) -> str | None:
    if isinstance(dist_tags, dict):
        value = dist_tags.get(tag_name)
        if isinstance(value, str) and value.strip():
            return value
    return None


def resolve(channel: str) -> dict[str, object]:
    angular_cli_tags = npm_view("@angular/cli", "dist-tags")
    angular_core_tags = npm_view("@angular/core", "dist-tags")
    ionic_tags = npm_view("@ionic/angular", "dist-tags")
    capacitor_tags = npm_view("@capacitor/core", "dist-tags")
    ionicons_tags = npm_view("ionicons", "dist-tags")
    angular_engines = npm_view("@angular/cli@latest", "engines")

    capacitor_stable = pick_tag(capacitor_tags, "latest")
    capacitor_next = pick_tag(capacitor_tags, "next")
    selected_capacitor = capacitor_stable if channel == "stable" else (capacitor_next or capacitor_stable)

    return {
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "channel": channel,
        "angular": {
            "cli": pick_tag(angular_cli_tags, "latest"),
            "core": pick_tag(angular_core_tags, "latest"),
            "engines": angular_engines,
        },
        "ionic": {
            "angular": pick_tag(ionic_tags, "latest"),
            "ionicons": pick_tag(ionicons_tags, "latest"),
        },
        "capacitor": {
            "stable": capacitor_stable,
            "next": capacitor_next,
            "selected": selected_capacitor,
        },
    }


def print_human(data: dict[str, object]) -> None:
    print("Resolved package versions")
    print(f"- Timestamp: {data['resolved_at']}")
    print(f"- Channel: {data['channel']}")
    print(f"- Angular CLI: {data['angular']['cli']}")
    print(f"- Angular Core: {data['angular']['core']}")
    print(f"- Ionic Angular: {data['ionic']['angular']}")
    print(f"- Ionicons: {data['ionic']['ionicons']}")
    print(f"- Capacitor stable: {data['capacitor']['stable']}")
    print(f"- Capacitor next: {data['capacitor']['next']}")
    print(f"- Capacitor selected: {data['capacitor']['selected']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve stable Ionic Angular mobile stack versions from npm.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--capacitor-channel",
        choices=("stable", "next"),
        default="stable",
        help="Use stable Capacitor by default. Use next only when explicitly requested.",
    )
    args = parser.parse_args(argv)

    try:
        data = resolve(args.capacitor_channel)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_human(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
