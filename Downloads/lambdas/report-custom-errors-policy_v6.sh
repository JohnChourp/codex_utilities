#!/usr/bin/env bash
set -euo pipefail

# report-custom-errors-policy.sh
#
# Usage:
#   ./report-custom-errors-policy.sh
#   ./report-custom-errors-policy.sh -o custom-errors-policy-report.json
#   ./report-custom-errors-policy.sh -r /path/to/root -o report.json
#
# Requirements:
#   - Node.js installed (Node 18+; works with Node 22)

ROOT_DIR="."
OUTPUT_FILE="custom-errors-policy-report.json"

while getopts ":r:o:h" opt; do
  case "$opt" in
    r) ROOT_DIR="$OPTARG" ;;
    o) OUTPUT_FILE="$OPTARG" ;;
    h)
      cat <<EOF
Usage:
  $(basename "$0") [-r rootDir] [-o outputFile]

Options:
  -r  Root directory to scan (default: .)
  -o  Output JSON report file (default: custom-errors-policy-report.json)
  -h  Show help
EOF
      exit 0
      ;;
    \?)
      echo "Unknown option: -$OPTARG" >&2
      exit 2
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 2
      ;;
  esac
done

if ! command -v node >/dev/null 2>&1; then
  echo "Error: node is required but was not found in PATH." >&2
  exit 1
fi

ROOT_DIR_ABS="$(cd "$ROOT_DIR" && pwd)"
OUTPUT_FILE_ABS="$(python3 - <<PY 2>/dev/null || true
import os
print(os.path.abspath("$OUTPUT_FILE"))
PY
)"
if [[ -z "${OUTPUT_FILE_ABS:-}" ]]; then
  if [[ "$OUTPUT_FILE" = /* ]]; then
    OUTPUT_FILE_ABS="$OUTPUT_FILE"
  else
    OUTPUT_FILE_ABS="$PWD/$OUTPUT_FILE"
  fi
fi

export ROOT_DIR_ABS
export OUTPUT_FILE_ABS

node <<'NODE'
const fs = require("node:fs/promises");
const path = require("node:path");

const rootDir = process.env.ROOT_DIR_ABS;
const outputFile = process.env.OUTPUT_FILE_ABS;

if (!rootDir || !outputFile) {
  console.error("Missing ROOT_DIR_ABS or OUTPUT_FILE_ABS env var.");
  process.exit(1);
}

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".serverless"]);

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function normalizeToPosixPath(value) {
  return value.split(path.sep).join("/");
}

function safeJsonParse(jsonText, contextPath) {
  try {
    return JSON.parse(jsonText);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to parse JSON at ${contextPath}: ${message}`);
  }
}

async function findFilesByName(rootDir, targetFileName) {
  const matched = [];
  const stack = [rootDir];

  while (stack.length) {
    const currentDir = stack.pop();
    if (!currentDir) continue;

    let entries;
    try {
      entries = await fs.readdir(currentDir, { withFileTypes: true });
    } catch {
      continue;
    }

    for (const entry of entries) {
      const entryPath = path.join(currentDir, entry.name);

      if (entry.isDirectory()) {
        if (SKIP_DIRS.has(entry.name)) continue;
        stack.push(entryPath);
        continue;
      }

      if (entry.isFile() && entry.name === targetFileName) {
        matched.push(entryPath);
      }
    }
  }

  matched.sort((a, b) => a.localeCompare(b));
  return matched;
}

async function findNearestPackageJson(startDir, stopDir) {
  let currentDir = startDir;

  while (true) {
    const candidate = path.join(currentDir, "package.json");
    if (await fileExists(candidate)) return candidate;

    const parent = path.dirname(currentDir);
    if (parent === currentDir) return null;

    if (stopDir && path.resolve(currentDir) === path.resolve(stopDir)) return null;

    currentDir = parent;
  }
}

function extractRepoNameFromRepositoryUrl(repositoryUrl) {
  if (!repositoryUrl || typeof repositoryUrl !== "string") return null;

  let cleaned = repositoryUrl.trim();
  cleaned = cleaned.replace(/^git\+/, "");

  if (cleaned.startsWith("git@") && cleaned.includes(":")) {
    const afterColon = cleaned.split(":").slice(1).join(":");
    cleaned = `https://github.com/${afterColon}`;
  }

  cleaned = cleaned.replace(/#.*/, "");
  cleaned = cleaned.replace(/\.git$/i, "");

  try {
    const url = new URL(cleaned);
    cleaned = url.pathname;
  } catch {
    // path-like
  }

  cleaned = cleaned.replace(/\\/g, "/").replace(/\/+$/, "");
  const last = cleaned.split("/").filter(Boolean).pop();
  return last || null;
}

function getRepositoryFieldValue(packageJson) {
  if (!packageJson) return null;
  if (typeof packageJson.repository === "string") return packageJson.repository;
  if (packageJson.repository && typeof packageJson.repository === "object") {
    return packageJson.repository.url ?? null;
  }
  return null;
}

function objectHasAnyTrue(value) {
  if (value === true) return true;
  if (Array.isArray(value)) return value.some(objectHasAnyTrue);
  if (value && typeof value === "object") return Object.values(value).some(objectHasAnyTrue);
  return false;
}

/**
 * Output format for trueBooleanPaths:
 * - For errors.<ERROR_CODE>.<flag>: output only "<ERROR_CODE>"
 * - For defaults.<key>: output "defaults.<key>"
 *
 * Result is unique + sorted.
 */
function collectTrueFlagsAsShortList(policyJson) {
  const out = new Set();

  const defaults = policyJson?.defaults;
  if (defaults && typeof defaults === "object" && !Array.isArray(defaults)) {
    for (const [key, val] of Object.entries(defaults)) {
      if (val === true) out.add(`defaults.${key}`);
    }
  }

  const errors = policyJson?.errors;
  if (errors && typeof errors === "object" && !Array.isArray(errors)) {
    for (const [errorCode, errorPolicy] of Object.entries(errors)) {
      if (objectHasAnyTrue(errorPolicy)) out.add(errorCode);
    }
  }

  return Array.from(out).sort((a, b) => a.localeCompare(b));
}

/**
 * Lambda entry rules:
 * - Always include lambdaName
 * - Include repoName only if it exists AND differs from lambdaName
 * - Include repoNameResolved only when false
 * - Include policyParseError only when non-null/non-empty
 * - Exclude lambdas where trueBooleanPaths is empty *unless* there is a policyParseError
 * - trueBooleanPaths contains SHORT values (error codes / defaults keys), not full dotted paths
 */
function buildLambdaEntryOrNull({ lambdaName, repoName, repoNameResolved, trueBooleanPaths, policyParseError }) {
  const hasParseError = Boolean(policyParseError);
  const hasTrueFlags = Array.isArray(trueBooleanPaths) && trueBooleanPaths.length > 0;

  if (!hasTrueFlags && !hasParseError) return null;

  const entry = { lambdaName, trueBooleanPaths };

  if (repoName && repoName !== lambdaName) {
    entry.repoName = repoName;
  }
  if (!repoNameResolved) {
    entry.repoNameResolved = false;
  }
  if (policyParseError) {
    entry.policyParseError = policyParseError;
  }

  return entry;
}

(async () => {
  const policyFiles = await findFilesByName(rootDir, "custom_errors.policy.json");

  const lambdas = [];
  let lambdasExcludedBecauseNoTrueFlags = 0;

  const packageJsonByPath = new Map(); // packageJsonPath -> {repoName, repoNameResolved, repositoryFieldValue, reason}
  const reposMissingName = [];
  const policiesMissingRepoName = [];

  for (const policyFilePath of policyFiles) {
    const policyDir = path.dirname(policyFilePath);
    const nearestPackageJsonPath = await findNearestPackageJson(policyDir, rootDir);

    let repositoryFieldValue = null;
    let repoName = null;
    let repoNameResolved = false;

    if (nearestPackageJsonPath) {
      if (!packageJsonByPath.has(nearestPackageJsonPath)) {
        try {
          const packageJsonText = await fs.readFile(nearestPackageJsonPath, "utf8");
          const packageJson = safeJsonParse(packageJsonText, nearestPackageJsonPath);

          repositoryFieldValue = getRepositoryFieldValue(packageJson);
          repoName = extractRepoNameFromRepositoryUrl(repositoryFieldValue);
          repoNameResolved = Boolean(repoName);

          const reason = repoNameResolved
            ? null
            : (!repositoryFieldValue
                ? "package.json has no repository or repository.url"
                : "repository value present but repo name could not be parsed");

          packageJsonByPath.set(nearestPackageJsonPath, {
            repoName,
            repoNameResolved,
            repositoryFieldValue,
            reason,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : String(error);
          packageJsonByPath.set(nearestPackageJsonPath, {
            repoName: null,
            repoNameResolved: false,
            repositoryFieldValue: null,
            reason: `failed to read/parse package.json: ${message}`,
          });
        }
      }

      const cached = packageJsonByPath.get(nearestPackageJsonPath);
      repoName = cached.repoName;
      repoNameResolved = cached.repoNameResolved;
      repositoryFieldValue = cached.repositoryFieldValue ?? null;
    }

    const lambdaName = repoNameResolved ? repoName : path.basename(policyDir);

    let policyJson = null;
    let policyParseError = null;

    try {
      const policyJsonText = await fs.readFile(policyFilePath, "utf8");
      policyJson = safeJsonParse(policyJsonText, policyFilePath);
    } catch (error) {
      policyParseError = error instanceof Error ? error.message : String(error);
    }

    const trueBooleanPaths = policyJson ? collectTrueFlagsAsShortList(policyJson) : [];

    if (!repoNameResolved) {
      policiesMissingRepoName.push({
        policyDir: normalizeToPosixPath(path.relative(rootDir, policyDir)),
        fallbackLambdaName: lambdaName,
        reason: !nearestPackageJsonPath
          ? "no package.json found above this policy file"
          : (packageJsonByPath.get(nearestPackageJsonPath)?.reason ?? "repo name could not be resolved"),
        repositoryFieldValue,
      });
    }

    const lambdaEntry = buildLambdaEntryOrNull({
      lambdaName,
      repoName,
      repoNameResolved,
      trueBooleanPaths,
      policyParseError,
    });

    if (lambdaEntry) {
      lambdas.push(lambdaEntry);
    } else {
      lambdasExcludedBecauseNoTrueFlags += 1;
    }
  }

  for (const [pkgPath, info] of packageJsonByPath.entries()) {
    if (!info.repoNameResolved) {
      reposMissingName.push({
        repoDir: normalizeToPosixPath(path.relative(rootDir, path.dirname(pkgPath))),
        reason: info.reason ?? "repo name could not be resolved",
        repositoryFieldValue: info.repositoryFieldValue ?? null,
      });
    }
  }

  reposMissingName.sort((a, b) => a.repoDir.localeCompare(b.repoDir));
  policiesMissingRepoName.sort((a, b) => a.policyDir.localeCompare(b.policyDir));
  lambdas.sort((a, b) => a.lambdaName.localeCompare(b.lambdaName));

  const report = {
    generatedAtUtc: new Date().toISOString(),
    rootDir: normalizeToPosixPath(rootDir),
    policyFilesFound: policyFiles.length,
    lambdasCount: lambdas.length,
    lambdasExcludedBecauseNoTrueFlags,
    lambdas,
    reposMissingName,
    policiesMissingRepoName,
  };

  await fs.mkdir(path.dirname(outputFile), { recursive: true });
  await fs.writeFile(outputFile, JSON.stringify(report, null, 2) + "\n", "utf8");

  console.log(`Wrote report: ${outputFile}`);
  console.log(`Policies scanned: ${policyFiles.length}`);
  console.log(`Lambdas included: ${lambdas.length}`);
  console.log(`Lambdas excluded (no true flags): ${lambdasExcludedBecauseNoTrueFlags}`);
  console.log(`Repos missing name: ${reposMissingName.length}`);
  console.log(`Policies missing repo name: ${policiesMissingRepoName.length}`);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
NODE

