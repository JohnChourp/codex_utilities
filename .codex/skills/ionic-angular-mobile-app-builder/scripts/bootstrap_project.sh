#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  bootstrap_project.sh --project-type <text> [options]

Options:
  --project-type <text>       Short app description such as "travel planner app" (required)
  --project-name <slug>       Target folder/package name
  --app-name <text>           Human-friendly app name
  --app-id <id>               Capacitor app id
  --destination <path>        Parent directory for the new project (default: current directory)
  --capacitor-channel <mode>  stable or next (default: stable)
  --skip-platforms            Skip cap add android/ios
  --skip-build                Skip initial npm run build
  --skip-install              Skip npm install after Angular scaffold
  --force                     Allow creating inside an existing empty target directory
  -h, --help                  Show help
USAGE
}

log() {
    printf '[ionic-angular-mobile-app-builder] %s\n' "$*"
}

warn() {
    printf '[ionic-angular-mobile-app-builder][warn] %s\n' "$*" >&2
}

fail() {
    printf '[ionic-angular-mobile-app-builder][error] %s\n' "$*" >&2
    exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd -P)"

PROJECT_TYPE=""
PROJECT_NAME=""
APP_NAME=""
APP_ID=""
DESTINATION="$PWD"
CAPACITOR_CHANNEL="stable"
SKIP_PLATFORMS=0
SKIP_BUILD=0
SKIP_INSTALL=0
FORCE=0

while (($# > 0)); do
    case "$1" in
        --project-type)
            PROJECT_TYPE="${2:-}"
            shift 2
            ;;
        --project-name)
            PROJECT_NAME="${2:-}"
            shift 2
            ;;
        --app-name)
            APP_NAME="${2:-}"
            shift 2
            ;;
        --app-id)
            APP_ID="${2:-}"
            shift 2
            ;;
        --destination)
            DESTINATION="${2:-}"
            shift 2
            ;;
        --capacitor-channel)
            CAPACITOR_CHANNEL="${2:-}"
            shift 2
            ;;
        --skip-platforms)
            SKIP_PLATFORMS=1
            shift
            ;;
        --skip-build)
            SKIP_BUILD=1
            shift
            ;;
        --skip-install)
            SKIP_INSTALL=1
            shift
            ;;
        --force)
            FORCE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            fail "Unknown option: $1"
            ;;
    esac
done

[[ -n "$PROJECT_TYPE" ]] || fail "--project-type is required"
[[ "$CAPACITOR_CHANNEL" == "stable" || "$CAPACITOR_CHANNEL" == "next" ]] || fail "--capacitor-channel must be stable or next"

slugify() {
    PROJECT_SOURCE="$1" python3 - <<'PY'
import os
import re

value = os.environ["PROJECT_SOURCE"].strip().lower()
value = re.sub(r"[^a-z0-9]+", "-", value)
value = re.sub(r"-{2,}", "-", value).strip("-")
print(value or "ionic-mobile-app")
PY
}

titleize() {
    PROJECT_SOURCE="$1" python3 - <<'PY'
import os
import re

words = re.sub(r"[^a-zA-Z0-9]+", " ", os.environ["PROJECT_SOURCE"]).split()
words = words[:6] or ["Ionic", "Mobile", "App"]
print(" ".join(word.capitalize() for word in words))
PY
}

PROJECT_NAME="${PROJECT_NAME:-$(slugify "$PROJECT_TYPE")}"
APP_NAME="${APP_NAME:-$(titleize "$PROJECT_TYPE")}"
APP_ID="${APP_ID:-com.example.${PROJECT_NAME//-/}}"
mkdir -p "$DESTINATION"
DESTINATION="$(cd "$DESTINATION" && pwd -P)"
PROJECT_DIR="$DESTINATION/$PROJECT_NAME"

bash "$SCRIPT_DIR/post_setup_checks.sh"

if [[ -e "$PROJECT_DIR" ]]; then
    if [[ $FORCE -eq 1 && -d "$PROJECT_DIR" ]]; then
        if find "$PROJECT_DIR" -mindepth 1 -maxdepth 1 ! -name '.DS_Store' | read -r _; then
            fail "Target directory already exists and is not empty: $PROJECT_DIR"
        fi
    else
        fail "Target directory already exists: $PROJECT_DIR"
    fi
fi

VERSION_FILE="$(mktemp)"
python3 "$SCRIPT_DIR/resolve_versions.py" --json --capacitor-channel "$CAPACITOR_CHANNEL" >"$VERSION_FILE"

ANGULAR_CLI_VERSION="$(python3 - <<'PY' "$VERSION_FILE"
import json
import sys
with open(sys.argv[1]) as fh:
    data = json.load(fh)
print(data["angular"]["cli"])
PY
)"
ANGULAR_CORE_VERSION="$(python3 - <<'PY' "$VERSION_FILE"
import json
import sys
with open(sys.argv[1]) as fh:
    data = json.load(fh)
print(data["angular"]["core"])
PY
)"
IONIC_VERSION="$(python3 - <<'PY' "$VERSION_FILE"
import json
import sys
with open(sys.argv[1]) as fh:
    data = json.load(fh)
print(data["ionic"]["angular"])
PY
)"
IONICONS_VERSION="$(python3 - <<'PY' "$VERSION_FILE"
import json
import sys
with open(sys.argv[1]) as fh:
    data = json.load(fh)
print(data["ionic"]["ionicons"])
PY
)"
CAPACITOR_VERSION="$(python3 - <<'PY' "$VERSION_FILE"
import json
import sys
with open(sys.argv[1]) as fh:
    data = json.load(fh)
print(data["capacitor"]["selected"])
PY
)"
rm -f "$VERSION_FILE"

log "Creating Angular app with @angular/cli@$ANGULAR_CLI_VERSION"
(
    cd "$DESTINATION"
    npx -y @angular/cli@"$ANGULAR_CLI_VERSION" new "$PROJECT_NAME" \
        --routing \
        --style=scss \
        --standalone \
        --skip-git \
        --directory "$PROJECT_NAME" \
        --package-manager npm \
        --defaults
)

cd "$PROJECT_DIR"

if [[ $SKIP_INSTALL -eq 0 ]]; then
    log "Installing Ionic and Capacitor dependencies"
    npm install @angular/animations@"$ANGULAR_CORE_VERSION"
    npm install @ionic/angular@"$IONIC_VERSION" ionicons@"$IONICONS_VERSION"
    npm install @capacitor/core@"$CAPACITOR_VERSION" @capacitor/cli@"$CAPACITOR_VERSION" @capacitor/android@"$CAPACITOR_VERSION" @capacitor/ios@"$CAPACITOR_VERSION"
else
    warn "Skipping dependency installation (--skip-install)"
fi

log "Writing Ionic and Capacitor project files"
cat > ionic.config.json <<EOF
{
  "name": "$PROJECT_NAME",
  "type": "angular",
  "integrations": {
    "capacitor": {}
  }
}
EOF

cat > capacitor.config.ts <<EOF
import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "$APP_ID",
  appName: "$APP_NAME",
  webDir: "dist/$PROJECT_NAME/browser"
};

export default config;
EOF

log "Updating package.json scripts"
node <<'NODE'
const fs = require('fs');
const path = require('path');

const packagePath = path.join(process.cwd(), 'package.json');
const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
pkg.scripts = pkg.scripts || {};
pkg.scripts['build:mobile'] = 'npm run build && npx cap sync';
pkg.scripts['cap:sync'] = 'npx cap sync';
pkg.scripts['cap:copy'] = 'npx cap copy';
pkg.scripts['android:open'] = 'npx cap open android';
pkg.scripts['ios:open'] = 'npx cap open ios';
pkg.scripts['android:sync'] = 'npx cap sync android';
pkg.scripts['ios:sync'] = 'npx cap sync ios';
fs.writeFileSync(packagePath, JSON.stringify(pkg, null, 2) + '\n');
NODE

log "Applying mobile shell starter template"
PROJECT_TYPE="$PROJECT_TYPE" \
PROJECT_NAME="$PROJECT_NAME" \
APP_NAME="$APP_NAME" \
APP_ID="$APP_ID" \
SKILL_DIR="$SKILL_DIR" \
python3 - <<'PY'
from __future__ import annotations

import hashlib
import os
from pathlib import Path

skill_dir = Path(os.environ["SKILL_DIR"])
project_root = Path.cwd()
template_root = skill_dir / "assets" / "mobile-shell"
project_type = os.environ["PROJECT_TYPE"]
project_name = os.environ["PROJECT_NAME"]
app_name = os.environ["APP_NAME"]
app_id = os.environ["APP_ID"]

palettes = [
    {
        "PRIMARY": "#0f766e",
        "SECONDARY": "#14b8a6",
        "ACCENT": "#f59e0b",
        "SURFACE": "#f4fbfa",
        "SURFACE_STRONG": "#dff6f1",
        "INK": "#0f172a",
        "MUTED": "#48606c",
    },
    {
        "PRIMARY": "#1d4ed8",
        "SECONDARY": "#60a5fa",
        "ACCENT": "#f97316",
        "SURFACE": "#f5f9ff",
        "SURFACE_STRONG": "#dbeafe",
        "INK": "#0b1220",
        "MUTED": "#4a5d7a",
    },
    {
        "PRIMARY": "#be123c",
        "SECONDARY": "#fb7185",
        "ACCENT": "#22c55e",
        "SURFACE": "#fff6f8",
        "SURFACE_STRONG": "#ffe4ea",
        "INK": "#1f2937",
        "MUTED": "#6b7280",
    },
    {
        "PRIMARY": "#7c3aed",
        "SECONDARY": "#a78bfa",
        "ACCENT": "#06b6d4",
        "SURFACE": "#faf7ff",
        "SURFACE_STRONG": "#ede9fe",
        "INK": "#1e1b4b",
        "MUTED": "#5b5b8a",
    },
]

hash_index = int(hashlib.sha256(project_type.encode("utf-8")).hexdigest(), 16) % len(palettes)
palette = palettes[hash_index]

keywords = [word for word in project_type.replace("-", " ").split() if word]
headline_word = keywords[0].capitalize() if keywords else "Mobile"
tagline = f"Plan, track, and grow your {project_type.lower()} flow from one calm mobile hub."
insight_title = f"{headline_word} rhythm"
insight_body = f"See the next best actions for your {project_type.lower()} in one fast overview."
discovery_title = f"Discover better {project_type.lower()} moments"
profile_title = f"Personalize your {project_type.lower()} experience"

replacements = {
    "__APP_TITLE__": app_name,
    "__PROJECT_TYPE__": project_type,
    "__PROJECT_SLUG__": project_name,
    "__APP_ID__": app_id,
    "__TAGLINE__": tagline,
    "__INSIGHT_TITLE__": insight_title,
    "__INSIGHT_BODY__": insight_body,
    "__DISCOVERY_TITLE__": discovery_title,
    "__PROFILE_TITLE__": profile_title,
}
replacements.update({f"__{key}__": value for key, value in palette.items()})

target_src = project_root / "src"
for item in (template_root / "src").rglob("*"):
    relative = item.relative_to(template_root / "src")
    destination = target_src / relative
    if item.is_dir():
        destination.mkdir(parents=True, exist_ok=True)
        continue
    text = item.read_text()
    for needle, value in replacements.items():
        text = text.replace(needle, value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text)

for stale_file in [
    project_root / "src" / "app" / "app.config.ts",
    project_root / "src" / "app" / "app.html",
    project_root / "src" / "app" / "app.scss",
    project_root / "src" / "app" / "app.spec.ts",
    project_root / "src" / "app" / "app.ts",
]:
    if stale_file.exists():
        stale_file.unlink()
PY

if [[ $SKIP_BUILD -eq 0 ]]; then
    log "Running initial web build"
    npm run build

    if [[ -d "dist/$PROJECT_NAME" && ! -d "dist/$PROJECT_NAME/browser" ]]; then
        log "Adjusting Capacitor webDir to dist/$PROJECT_NAME"
        python3 - <<'PY'
from pathlib import Path

config_path = Path("capacitor.config.ts")
text = config_path.read_text()
config_path.write_text(text.replace('webDir: "dist/' + Path.cwd().name + '/browser"', 'webDir: "dist/' + Path.cwd().name + '"'))
PY
    fi
else
    warn "Skipping initial build (--skip-build)"
fi

if [[ $SKIP_PLATFORMS -eq 0 ]]; then
    log "Adding Android platform"
    if ! npx cap add android; then
        warn "Android platform creation failed. Check Java/Android SDK setup, then re-run: npx cap add android"
    fi

    if [[ "$(uname -s)" == "Darwin" ]]; then
        if command -v xcrun >/dev/null 2>&1 && xcrun simctl help >/dev/null 2>&1; then
            log "Adding iOS platform"
            if ! npx cap add ios; then
                warn "iOS platform creation failed. Check Xcode setup, then re-run: npx cap add ios"
            fi
        else
            warn "Skipping iOS platform because Xcode simulator tools are unavailable"
        fi
    else
        warn "Skipping iOS platform because iOS tooling is only supported on macOS"
    fi

    log "Syncing Capacitor"
    npx cap sync
else
    warn "Skipping native platform creation (--skip-platforms)"
fi

log "Project created at $PROJECT_DIR"
log "Angular core: $ANGULAR_CORE_VERSION"
log "Ionic Angular: $IONIC_VERSION"
log "Capacitor: $CAPACITOR_VERSION ($CAPACITOR_CHANNEL)"
log "Next steps:"
printf '  cd %s\n' "$PROJECT_DIR"
printf '  npm run build\n'
printf '  $CODEX_HOME/skills/ionic-android-codex-deploy/scripts/ionic_android_codex_deploy.sh --project %s\n' "$PROJECT_DIR"
printf '  $CODEX_HOME/skills/ionic-ios-codex-deploy/scripts/ionic_ios_codex_deploy.sh --project %s\n' "$PROJECT_DIR"
