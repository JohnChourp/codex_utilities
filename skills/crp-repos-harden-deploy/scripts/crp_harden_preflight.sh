#!/usr/bin/env bash
set -euo pipefail

say() { printf '%s\n' "$*"; }

say "== binaries =="
if command -v crp >/dev/null 2>&1; then
  say "crp: $(command -v crp)"
  crp --version 2>/dev/null || crp --help | head -n 1 || true
else
  say "crp: MISSING"
fi

if command -v la >/dev/null 2>&1; then
  say "la:  $(command -v la)"
  la --version 2>/dev/null || true
else
  say "la:  MISSING"
fi

say ""
say "== npm auth (mandatory) =="
if command -v whc >/dev/null 2>&1; then
  say "whc: $(command -v whc)"
  whc npm-automation verify || true
else
  say "whc: not found; falling back to npm whoami"
  npm whoami || true
fi

say ""
say "== gh auth (recommended) =="
if command -v gh >/dev/null 2>&1; then
  gh auth status || true
else
  say "gh: not found"
fi

say ""
say "== la update-check (mandatory before running any la ...) =="
if command -v whc >/dev/null 2>&1; then
  say "Run:"
  say "  whc updates --non-interactive"
  say "  # if updates exist: whc u"
  say "  la --version"
else
  say "whc not found; cannot run the standardized update-check sequence."
fi

say ""
say "== aws creds (optional but recommended for deploy) =="
if command -v aws >/dev/null 2>&1; then
  if [[ -n "${AWS_PROFILE:-}" ]]; then
    say "AWS_PROFILE=$AWS_PROFILE"
    aws sts get-caller-identity --profile "$AWS_PROFILE" --output json 2>/dev/null || true
  else
    say "Set AWS_PROFILE to test sts get-caller-identity."
  fi
else
  say "aws: not found"
fi

say ""
say "== repo deploy target (infer aws alias/profile from package.json) =="
if [[ -f "package.json" ]] && command -v node >/dev/null 2>&1; then
  node - <<'NODE' || true
const fs = require("fs");

function pickAliasFromScripts(scripts) {
  const keys = ["deploy:prod:upgrade", "deploy:prod", "deploy:prod:check"];
  for (const k of keys) {
    const s = scripts && scripts[k];
    if (typeof s !== "string") continue;
    const m = s.match(/lambda-upload\s+deploy-prod\s+([A-Za-z0-9_-]+)/);
    if (m && m[1]) return { from: `scripts.${k}`, alias: m[1] };
  }
  return null;
}

try {
  const pkg = JSON.parse(fs.readFileSync("package.json", "utf8"));
  const scripts = pkg.scripts || {};

  const fromScripts = pickAliasFromScripts(scripts);
  if (fromScripts) {
    console.log(`deploy alias: ${fromScripts.alias} (from ${fromScripts.from})`);
    console.log(`suggested AWS_PROFILE: ${fromScripts.alias}`);
  } else {
    console.log("deploy alias: not detected from package.json scripts");
  }

  const deployed = pkg.lambda_upload && Array.isArray(pkg.lambda_upload.deployed_accounts)
    ? pkg.lambda_upload.deployed_accounts
    : [];
  if (deployed.length) {
    const last = deployed[deployed.length - 1];
    if (last && typeof last === "object") {
      const parts = [];
      if (last.alias) parts.push(`alias=${last.alias}`);
      if (last.region) parts.push(`region=${last.region}`);
      if (last.account_id) parts.push(`account_id=${last.account_id}`);
      if (last.last_deployed_at) parts.push(`last_deployed_at=${last.last_deployed_at}`);
      console.log(`lambda_upload.deployed_accounts last: ${parts.join(" ")}`);
    }
  }
} catch (e) {
  console.log(`failed to parse package.json for deploy alias: ${e && e.message ? e.message : String(e)}`);
}
NODE
elif [[ ! -f "package.json" ]]; then
  say "package.json: not found"
elif ! command -v node >/dev/null 2>&1; then
  say "node: not found (cannot parse package.json)"
fi

say ""
say "== repo deploy target (fallback: infer via CRP lambda inventory) =="
if [[ -f "package.json" ]] && command -v node >/dev/null 2>&1 && command -v crp >/dev/null 2>&1; then
  # Only run the (slower) CRP inventory probe when we couldn't detect an alias in scripts.
  NEED_INVENTORY="$(
    node - <<'NODE' || true
const fs = require("fs");
function pickAliasFromScripts(scripts) {
  const keys = ["deploy:prod:upgrade", "deploy:prod", "deploy:prod:check"];
  for (const k of keys) {
    const s = scripts && scripts[k];
    if (typeof s !== "string") continue;
    const m = s.match(/lambda-upload\s+deploy-prod\s+([A-Za-z0-9_-]+)/);
    if (m && m[1]) return m[1];
  }
  return "";
}
try {
  const pkg = JSON.parse(fs.readFileSync("package.json", "utf8"));
  const alias = pickAliasFromScripts(pkg.scripts || {});
  process.stdout.write(alias ? "0" : "1");
} catch {
  process.stdout.write("1");
}
NODE
  )"

  if [[ "$NEED_INVENTORY" = "1" ]]; then
    FUNCTION_NAME="$(
      node - <<'NODE' || true
const fs = require("fs");
const path = require("path");
try {
  const pkg = JSON.parse(fs.readFileSync("package.json", "utf8"));
  if (pkg && typeof pkg.name === "string" && pkg.name.trim()) {
    process.stdout.write(pkg.name.trim());
  } else {
    process.stdout.write(path.basename(process.cwd()));
  }
} catch {
  process.stdout.write(path.basename(process.cwd()));
}
NODE
    )"

    REGION="$(
      node - <<'NODE' || true
const fs = require("fs");
try {
  const pkg = JSON.parse(fs.readFileSync("package.json", "utf8"));
  const deployed = pkg.lambda_upload && Array.isArray(pkg.lambda_upload.deployed_accounts)
    ? pkg.lambda_upload.deployed_accounts
    : [];
  const last = deployed.length ? deployed[deployed.length - 1] : null;
  if (last && typeof last === "object" && typeof last.region === "string" && last.region.trim()) {
    process.stdout.write(last.region.trim());
  } else {
    process.stdout.write("eu-west-1");
  }
} catch {
  process.stdout.write("eu-west-1");
}
NODE
    )"

    PROFILES_CSV="$(
      node - <<'NODE' || true
const fs = require("fs");
const home = process.env.HOME;
const p = home ? home + "/.uplambda.json" : "";
try {
  if (!p || !fs.existsSync(p)) process.exit(0);
  const j = JSON.parse(fs.readFileSync(p, "utf8"));
  const keys = Object.keys(j || {}).filter((k) => typeof k === "string" && k.trim());
  // Keep it deterministic and short: use all aliases from uplambda, in stable order.
  keys.sort();
  process.stdout.write(keys.join(","));
} catch {
  // ignore
}
NODE
    )"

    if [[ -z "$PROFILES_CSV" ]]; then
      say "uplambda profiles: not found (no ~/.uplambda.json); skipping inventory probe"
    else
      say "probing function=$FUNCTION_NAME region=$REGION profiles=$PROFILES_CSV"
      INV_OUT="$(mktemp -t crp-lambda-inventory.XXXXXX.json)"
      crp repos lambda-inventory --profiles "$PROFILES_CSV" --region "$REGION" --out "$INV_OUT" --limit 0 >/dev/null 2>&1 || true

      node - <<'NODE' "$INV_OUT" "$FUNCTION_NAME" || true
const fs = require("fs");
const invPath = process.argv[2];
const fn = process.argv[3];
try {
  const j = JSON.parse(fs.readFileSync(invPath, "utf8"));
  const funcs = Array.isArray(j.functions) ? j.functions : [];
  const row = funcs.find((x) => x && x.functionName === fn);
  if (!row || !Array.isArray(row.accounts) || !row.accounts.length) {
    console.log("inventory: function not found under the probed profiles");
    process.exit(0);
  }
  const acct = row.accounts[0];
  if (acct && acct.profile) console.log(`suggested AWS_PROFILE (inventory): ${acct.profile}`);
  if (acct && acct.accountId) console.log(`accountId (inventory): ${acct.accountId}`);
  if (acct && acct.alias) console.log(`account alias (inventory): ${acct.alias}`);
} catch (e) {
  console.log(`inventory: failed to parse: ${e && e.message ? e.message : String(e)}`);
}
NODE
    fi
  else
    say "skipping inventory probe (deploy alias already detected from scripts)"
  fi
else
  say "skipping inventory probe (requires crp + node + package.json)"
fi
