#!/usr/bin/env python3
"""Sync CRP project cloud repos for GitHub repositories that contain a target token."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

API_BASE = "https://mpq5pzhhv2.execute-api.eu-west-1.amazonaws.com/prod"
ENDPOINTS = {
    "renew": f"{API_BASE}/crp-renew-token",
    "fetch_projects": f"{API_BASE}/crp-fetch-projects",
    "fetch_features": f"{API_BASE}/crp-fetch-features",
    "fetch_subprojects": f"{API_BASE}/crp-fetch-subprojects",
    "fetch_cloud_repos": f"{API_BASE}/crp-fetch-cloud-repos",
    "handle_subproject": f"{API_BASE}/crp-handle-subproject",
    "handle_feature": f"{API_BASE}/crp-handle-feature",
    "handle_cloud_repo": f"{API_BASE}/crp-handle-cloud-repo",
}

TOKEN_HEADER = "authorization"
DEFAULT_CONFIG_PATH = Path.home() / ".crp" / "config.json"
DEFAULT_PROJECT_NAME = "crp"
DEFAULT_NAME_CONTAINS = "crp-"
DEFAULT_SPECIAL_REPOS = ["cloud-repos-panel", "crp-cli"]
DEFAULT_AUTO_SUBPROJECT = "cloud-repos-auto-linking"
DEFAULT_AUTO_FEATURE = "auto-linked-crp-repos"
DEFAULT_DOWNLOADS_ROOT = Path.home() / "Downloads"
DEFAULT_CLONE_ROOT = DEFAULT_DOWNLOADS_ROOT / "lambdas" / "crp_all"
DEFAULT_PROJECTS_ROOT = DEFAULT_DOWNLOADS_ROOT / "projects"
DEFAULT_REPOS_LIST_OUT = DEFAULT_CLONE_ROOT / "current-crp-target-repos.txt"
DEFAULT_REPORT_OUT = DEFAULT_CLONE_ROOT / "crp-cloud-repos-sync-report.json"
DEFAULT_FEATURES_CLOUD_REPOS_OUT = DEFAULT_CLONE_ROOT / "current-crp-cloud-repos-from-all-features.txt"

URL_FIELD_HINTS = ("url", "clone", "ssh", "https", "git", "repo")


@dataclass
class FeatureRef:
    feature_id: str
    subproject_id: str
    feature_name: str


@dataclass
class LocalSyncResult:
    repo_id: str
    local_path: str
    cloud_status: str
    local_status: str
    details: str
    fallback_used: bool = False


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=True)
        fh.write("\n")


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        capture_output=True,
        cwd=str(cwd) if cwd else None,
    )


def _compact_err(run: subprocess.CompletedProcess[str], fallback: str) -> str:
    raw = (run.stderr or run.stdout or "").strip()
    if not raw:
        return fallback
    one_line = re.sub(r"\s+", " ", raw)
    return one_line[:600]


def _http_post(url: str, body: dict[str, Any], token: str, timeout: int = 25) -> Any:
    raw = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        method="POST",
        data=raw,
        headers={
            "content-type": "application/json",
            TOKEN_HEADER: token,
            "origin": "http://localhost",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {url}: {payload}") from exc


def _select_project(cfg: dict[str, Any], token: str, project_name: str, project_id: str) -> tuple[str, str]:
    explicit_project_id = project_id.strip()
    if explicit_project_id:
        current_name = str((cfg.get("currentProject") or {}).get("name") or "").strip()
        return explicit_project_id, current_name or project_name

    current = cfg.get("currentProject") or {}
    curr_id = str(current.get("id") or "").strip()
    curr_name = str(current.get("name") or "").strip()
    if curr_id and curr_name.lower() == project_name.lower():
        return curr_id, curr_name

    payload = {
        "type": "fetch-projects",
        "page": 0,
        "searchTerm": "",
        "project_id": "",
        "nextContinuationToken": "",
    }
    res = _http_post(ENDPOINTS["fetch_projects"], payload, token)
    rows = res.get("data", res)
    if not isinstance(rows, list):
        raise RuntimeError("Unexpected response from crp-fetch-projects")

    for row in rows:
        pid = str(row.get("project_id") or row.get("id") or "").strip()
        name = str(row.get("project_name") or row.get("name") or "").strip()
        if pid and name.lower() == project_name.lower():
            return pid, name

    raise RuntimeError(f"Project '{project_name}' was not found")


def _fetch_subprojects(project_id: str, token: str) -> list[dict[str, Any]]:
    res = _http_post(
        ENDPOINTS["fetch_subprojects"],
        {"type": "fetch-subprojects-by-project-id", "project_id": project_id},
        token,
    )
    rows = res.get("data", res)
    return rows if isinstance(rows, list) else []


def _fetch_features(project_id: str, token: str) -> list[FeatureRef]:
    res = _http_post(
        ENDPOINTS["fetch_features"],
        {"type": "fetch-features-by-project-id", "project_id": project_id},
        token,
    )
    rows = res.get("data", res)
    out: list[FeatureRef] = []
    if not isinstance(rows, list):
        return out

    for row in rows:
        feature_id = str(row.get("feature_id") or row.get("id") or "").strip()
        subproject_id = str(row.get("subproject_id") or "").strip()
        feature_name = str(row.get("feature_name") or row.get("name") or "").strip()
        if feature_id and feature_name:
            out.append(
                FeatureRef(
                    feature_id=feature_id,
                    subproject_id=subproject_id,
                    feature_name=feature_name,
                )
            )
    return out


def _fetch_project_cloud_repos(project_id: str, token: str) -> list[dict[str, Any]]:
    res = _http_post(
        ENDPOINTS["fetch_cloud_repos"],
        {"type": "fetch-cloud-repos-by-project-id", "project_id": project_id},
        token,
    )
    rows = res.get("data", res)
    return rows if isinstance(rows, list) else []


def _fetch_feature_cloud_repos(feature_id: str, token: str) -> list[dict[str, Any]]:
    res = _http_post(
        ENDPOINTS["fetch_cloud_repos"],
        {"type": "fetch-cloud-repos-by-feature-id", "feature_id": feature_id},
        token,
    )
    rows = res.get("data", res)
    return rows if isinstance(rows, list) else []


def _collect_cloud_repos_from_all_features(project_id: str, token: str) -> tuple[list[str], int, dict[str, str]]:
    features = _fetch_features(project_id, token)
    repos: set[str] = set()
    feature_errors: dict[str, str] = {}

    for feature in features:
        try:
            rows = _fetch_feature_cloud_repos(feature.feature_id, token)
        except Exception as exc:
            feature_errors[feature.feature_id] = str(exc)
            continue

        for row in rows:
            if not isinstance(row, dict):
                continue
            repo_id = str(row.get("repo_id") or row.get("repo") or row.get("name") or "").strip()
            if repo_id:
                repos.add(repo_id)

    return sorted(repos), len(features), feature_errors


def _create_subproject(project_id: str, token: str, subproject_name: str) -> dict[str, Any]:
    body = {
        "type": "create",
        "subProject": {
            "name": subproject_name,
            "subproject_name": subproject_name,
            "project_id": project_id,
            "res_aws": {},
            "description": "Auto-created for CRP cloud repo auto-linking.",
        },
    }
    return _http_post(ENDPOINTS["handle_subproject"], body, token)


def _create_feature(project_id: str, subproject_id: str, token: str, feature_name: str) -> dict[str, Any]:
    body = {
        "type": "create",
        "feature": {
            "project_id": project_id,
            "subproject_id": subproject_id,
            "feature_name": feature_name,
            "res_aws": {},
            "description": "Auto-created feature for CRP cloud repo auto-linking.",
        },
    }
    return _http_post(ENDPOINTS["handle_feature"], body, token)


def _link_repo(project_id: str, feature_id: str, repo_id: str, token: str) -> dict[str, Any]:
    body = {
        "type": "create-and-in-feature",
        "cloudRepo": {
            "project_id": project_id,
            "feature_id": feature_id,
            "repo_id": repo_id,
        },
    }
    return _http_post(ENDPOINTS["handle_cloud_repo"], body, token)


def _resolve_github_org(cfg: dict[str, Any], token: str, explicit_org: str) -> str:
    if explicit_org.strip():
        return explicit_org.strip()

    from_cfg = str((cfg.get("github") or {}).get("org") or "").strip()
    if from_cfg:
        return from_cfg

    try:
        renew_res = _http_post(ENDPOINTS["renew"], {}, token, timeout=10)
        org = str((renew_res.get("org_settings") or {}).get("github_org") or "").strip()
        if org:
            return org
    except Exception:
        pass

    return str(((cfg.get("api") or {}).get("auth") or {}).get("user", {}).get("org") or "").strip()


def _fetch_github_repos(org: str, name_contains: str, exclude_archived: bool) -> tuple[int, list[str]]:
    if not org:
        raise RuntimeError("GitHub org is empty")
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI (gh) not found in PATH")

    run = _run(["gh", "repo", "list", org, "--limit", "1000", "--json", "name,isArchived"])
    if run.returncode != 0:
        raise RuntimeError(_compact_err(run, "gh repo list failed"))

    rows = json.loads(run.stdout or "[]")
    if not isinstance(rows, list):
        rows = []

    needle = name_contains.lower()
    matched: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        if needle not in name.lower():
            continue
        if exclude_archived and bool(row.get("isArchived")):
            continue
        matched.add(name)

    return len(rows), sorted(matched)


def _is_special_repo(repo_id: str, special_repos: set[str]) -> bool:
    return repo_id in special_repos


def _normalize_clone_url(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""

    if raw.startswith("git+"):
        raw = raw[4:]

    if raw.startswith("git@") or raw.startswith("ssh://"):
        return raw if raw.endswith(".git") else f"{raw}.git"

    if raw.startswith("https://") or raw.startswith("http://"):
        if "/tree/" in raw or "/blob/" in raw:
            return ""
        return raw if raw.endswith(".git") else f"{raw}.git"

    return ""


def _url_kind(key: str, url: str) -> str:
    lowered_key = key.lower()
    lowered_url = url.lower()
    if "ssh" in lowered_key or lowered_url.startswith("git@") or lowered_url.startswith("ssh://"):
        return "ssh"
    if "https" in lowered_key or lowered_url.startswith("http://") or lowered_url.startswith("https://"):
        return "https"
    return "any"


def _extract_repo_urls(rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        repo_id = str(row.get("repo_id") or row.get("repo") or row.get("name") or "").strip()
        if not repo_id:
            continue

        bucket = out.setdefault(repo_id, {})
        for key, value in row.items():
            if not isinstance(value, str):
                continue
            lowered = key.lower()
            if not any(hint in lowered for hint in URL_FIELD_HINTS):
                continue
            url = _normalize_clone_url(value)
            if not url:
                continue
            kind = _url_kind(key, url)
            bucket.setdefault(kind, url)
    return out


def _pick_clone_url(repo_id: str, repo_urls: dict[str, dict[str, str]], github_org: str, prefer: str) -> tuple[str, str]:
    urls = repo_urls.get(repo_id, {})
    if prefer in urls:
        return urls[prefer], prefer

    secondary = "https" if prefer == "ssh" else "ssh"
    if secondary in urls:
        return urls[secondary], secondary

    if "any" in urls:
        return urls["any"], "any"

    if not github_org:
        return "", "unresolved"

    if prefer == "https":
        return f"https://github.com/{github_org}/{repo_id}.git", "generated_https"
    return f"git@github.com:{github_org}/{repo_id}.git", "generated_ssh"


def _sync_existing_repo(repo_dir: Path) -> tuple[str, str]:
    if not repo_dir.exists():
        return "missing", "Local path does not exist"

    if repo_dir.is_file():
        return "path_conflict", "Target path exists as file"

    if not (repo_dir / ".git").exists():
        return "skipped_not_git_toplevel", "Directory is not a git repository"

    fetch = _run(["git", "-C", str(repo_dir), "fetch", "--all", "--prune", "--quiet"])
    if fetch.returncode != 0:
        return "fetch_failed", _compact_err(fetch, "git fetch failed")

    dirty = _run(["git", "-C", str(repo_dir), "status", "--porcelain"])
    if dirty.returncode == 0 and (dirty.stdout or "").strip():
        return "skipped_dirty", "Skipped pull due to local changes"

    branch = _run(["git", "-C", str(repo_dir), "symbolic-ref", "--short", "-q", "HEAD"])
    current_branch = (branch.stdout or "").strip()
    if branch.returncode != 0 or not current_branch:
        return "skipped_no_upstream", "Skipped pull because branch is detached or unknown"

    upstream = _run(["git", "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream.returncode != 0 or not (upstream.stdout or "").strip():
        return "skipped_no_upstream", "Skipped pull because upstream is missing"

    pull = _run(["git", "-C", str(repo_dir), "pull", "--ff-only", "--quiet"])
    if pull.returncode != 0:
        return "pull_failed", _compact_err(pull, "git pull failed")

    return "synced", "Fetch and pull completed"


def _clone_repo(repo_id: str, repo_dir: Path, url: str) -> tuple[str, str]:
    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    run = _run(["git", "clone", url, str(repo_dir)])
    if run.returncode == 0:
        return "cloned", "Clone completed"
    return "clone_failed", _compact_err(run, "git clone failed")


def _is_publickey_error(message: str) -> bool:
    lowered = message.lower()
    return "permission denied (publickey)" in lowered or "could not read from remote repository" in lowered


def _ensure_special_repo_location(repo_id: str, clone_root: Path, projects_root: Path) -> tuple[Path, str]:
    target = projects_root / repo_id
    legacy = clone_root / repo_id

    if legacy.is_dir() and not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(legacy), str(target))
        return target, "moved_to_projects"

    return target, "unchanged"


def _ensure_auto_feature(
    project_id: str,
    token: str,
    subproject_name: str,
    feature_name: str,
    dry_run: bool,
) -> tuple[FeatureRef, dict[str, Any]]:
    created: dict[str, Any] = {}

    subprojects = _fetch_subprojects(project_id, token)
    features = _fetch_features(project_id, token)

    subproject_id = ""
    for sp in subprojects:
        sid = str(sp.get("subproject_id") or sp.get("id") or "").strip()
        sname = str(sp.get("subproject_name") or sp.get("name") or "").strip()
        if sid and sname.lower() == subproject_name.lower():
            subproject_id = sid
            break

    if not subproject_id:
        if dry_run:
            subproject_id = "DRY-RUN-SUBPROJECT"
            created["created_subproject"] = {"subproject_id": subproject_id, "subproject_name": subproject_name, "dry_run": True}
        else:
            created_sub = _create_subproject(project_id, token, subproject_name)
            payload = created_sub.get("data", created_sub)
            subproject_id = str(payload.get("subproject_id") or payload.get("id") or "").strip()
            if not subproject_id:
                raise RuntimeError("Failed to create auto subproject")
            created["created_subproject"] = {
                "subproject_id": subproject_id,
                "subproject_name": str(payload.get("subproject_name") or payload.get("name") or subproject_name),
            }

    for feature in features:
        if feature.feature_name.lower() == feature_name.lower() and feature.subproject_id == subproject_id:
            return feature, created

    if dry_run:
        feature = FeatureRef(
            feature_id="DRY-RUN-FEATURE",
            subproject_id=subproject_id,
            feature_name=feature_name,
        )
        created["created_feature"] = {
            "feature_id": feature.feature_id,
            "feature_name": feature.feature_name,
            "subproject_id": subproject_id,
            "dry_run": True,
        }
        return feature, created

    created_feature = _create_feature(project_id, subproject_id, token, feature_name)
    payload = created_feature.get("data", created_feature)
    feature_id = str(payload.get("feature_id") or payload.get("id") or "").strip()
    name = str(payload.get("feature_name") or payload.get("name") or feature_name).strip()
    if not feature_id:
        raise RuntimeError("Failed to create auto feature")

    created["created_feature"] = {
        "feature_id": feature_id,
        "feature_name": name,
        "subproject_id": subproject_id,
    }
    return FeatureRef(feature_id=feature_id, subproject_id=subproject_id, feature_name=name), created


def _parse_special_repos(raw: str) -> list[str]:
    parts = [item.strip() for item in raw.split(",")]
    return sorted({item for item in parts if item})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync CRP cloud repos and local repositories")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    parser.add_argument("--project-id", default="")
    parser.add_argument("--name-contains", default=DEFAULT_NAME_CONTAINS)
    parser.add_argument("--include-special-repos", default=",".join(DEFAULT_SPECIAL_REPOS))
    parser.add_argument("--exclude-archived", dest="exclude_archived", action="store_true", default=True)
    parser.add_argument("--include-archived", dest="exclude_archived", action="store_false")
    parser.add_argument("--auto-subproject-name", default=DEFAULT_AUTO_SUBPROJECT)
    parser.add_argument("--auto-feature-name", default=DEFAULT_AUTO_FEATURE)
    parser.add_argument("--clone-root", default=str(DEFAULT_CLONE_ROOT))
    parser.add_argument("--projects-root", default=str(DEFAULT_PROJECTS_ROOT))
    parser.add_argument("--clone-prefer", choices=["ssh", "https"], default="ssh")
    parser.add_argument("--github-org", default="")
    parser.add_argument("--repos-list-out", default=str(DEFAULT_REPOS_LIST_OUT))
    parser.add_argument("--features-cloud-repos-out", default=str(DEFAULT_FEATURES_CLOUD_REPOS_OUT))
    parser.add_argument("--out", default=str(DEFAULT_REPORT_OUT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-local-sync", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    cfg_path = Path(args.config).expanduser().resolve()
    if not cfg_path.exists():
        print(f"ERROR: config not found: {cfg_path}", file=sys.stderr)
        return 2

    cfg = _read_json(cfg_path)
    token = str(((cfg.get("api") or {}).get("auth") or {}).get("token") or "").strip()
    if not token:
        print("ERROR: CRP token missing. Run `crp login`.", file=sys.stderr)
        return 2

    project_id, project_name = _select_project(cfg, token, args.project_name, args.project_id)
    github_org = _resolve_github_org(cfg, token, args.github_org)
    if not github_org:
        print("ERROR: Unable to resolve GitHub org.", file=sys.stderr)
        return 2

    special_repos = set(_parse_special_repos(args.include_special_repos))
    github_repo_count, github_filtered = _fetch_github_repos(github_org, args.name_contains, args.exclude_archived)

    target_repos = sorted(set(github_filtered).union(special_repos))

    cloud_rows = _fetch_project_cloud_repos(project_id, token)
    cloud_linked = sorted(
        {
            str(row.get("repo_id") or "").strip()
            for row in cloud_rows
            if str(row.get("repo_id") or "").strip()
        }
    )

    missing_cloud = sorted(set(target_repos) - set(cloud_linked))

    auto_feature, auto_creation = _ensure_auto_feature(
        project_id=project_id,
        token=token,
        subproject_name=args.auto_subproject_name,
        feature_name=args.auto_feature_name,
        dry_run=args.dry_run,
    )

    cloud_results: dict[str, str] = {}
    created_cloud_repo_count = 0
    cloud_link_errors: dict[str, str] = {}

    for repo_id in target_repos:
        if repo_id in cloud_linked:
            cloud_results[repo_id] = "already_linked"
            continue

        if args.dry_run:
            cloud_results[repo_id] = "cloud_link_planned"
            continue

        try:
            res = _link_repo(project_id, auto_feature.feature_id, repo_id, token)
            success = bool(res.get("success"))
            if success:
                cloud_results[repo_id] = "cloud_linked"
                created_cloud_repo_count += 1
            else:
                cloud_results[repo_id] = "cloud_link_failed"
                cloud_link_errors[repo_id] = str(res.get("comment_id") or res.get("message") or "unknown_error")
        except Exception as exc:
            cloud_results[repo_id] = "cloud_link_failed"
            cloud_link_errors[repo_id] = str(exc)

    repo_urls = _extract_repo_urls(cloud_rows)

    clone_root = Path(args.clone_root).expanduser().resolve()
    projects_root = Path(args.projects_root).expanduser().resolve()

    local_results: list[LocalSyncResult] = []
    local_sync_summary = {
        "total": len(target_repos),
        "synced": 0,
        "cloned": 0,
        "exists": 0,
        "skipped_dirty": 0,
        "skipped_no_upstream": 0,
        "skipped_not_git_toplevel": 0,
        "clone_failed": 0,
        "fetch_failed": 0,
        "pull_failed": 0,
        "path_conflict": 0,
        "missing": 0,
        "moved_to_projects": 0,
    }

    if not args.no_local_sync:
        if not args.dry_run:
            clone_root.mkdir(parents=True, exist_ok=True)
            projects_root.mkdir(parents=True, exist_ok=True)

        for repo_id in target_repos:
            cloud_status = cloud_results.get(repo_id, "already_linked")
            if cloud_status == "cloud_link_failed":
                local_results.append(
                    LocalSyncResult(
                        repo_id=repo_id,
                        local_path="",
                        cloud_status=cloud_status,
                        local_status="clone_failed",
                        details=f"Cloud link failed: {cloud_link_errors.get(repo_id, 'unknown_error')}",
                    )
                )
                local_sync_summary["clone_failed"] += 1
                continue

            fallback_used = False
            details = ""
            move_state = "unchanged"
            if _is_special_repo(repo_id, special_repos):
                if args.dry_run:
                    repo_path = projects_root / repo_id
                else:
                    repo_path, move_state = _ensure_special_repo_location(repo_id, clone_root, projects_root)
            else:
                repo_path = clone_root / repo_id

            if move_state == "moved_to_projects":
                local_sync_summary["moved_to_projects"] += 1

            if args.dry_run:
                status = "exists" if repo_path.exists() else "cloned"
                details = "dry-run"
                local_results.append(
                    LocalSyncResult(
                        repo_id=repo_id,
                        local_path=str(repo_path),
                        cloud_status=cloud_status,
                        local_status=status,
                        details=details,
                    )
                )
                local_sync_summary[status] += 1
                continue

            sync_status, sync_details = _sync_existing_repo(repo_path)
            if sync_status == "missing":
                clone_url, _source = _pick_clone_url(repo_id, repo_urls, github_org, args.clone_prefer)
                if not clone_url:
                    local_results.append(
                        LocalSyncResult(
                            repo_id=repo_id,
                            local_path=str(repo_path),
                            cloud_status=cloud_status,
                            local_status="clone_failed",
                            details="Unable to resolve clone URL",
                        )
                    )
                    local_sync_summary["clone_failed"] += 1
                    continue

                status, details = _clone_repo(repo_id, repo_path, clone_url)
                if status == "clone_failed" and args.clone_prefer == "ssh" and _is_publickey_error(details):
                    https_url = f"https://github.com/{github_org}/{repo_id}.git"
                    status, details = _clone_repo(repo_id, repo_path, https_url)
                    fallback_used = status == "cloned"

                if status == "cloned":
                    # Ensure cloned repositories immediately receive latest upstream head state.
                    sync_after_clone, sync_after_clone_details = _sync_existing_repo(repo_path)
                    if sync_after_clone in {"synced", "skipped_dirty", "skipped_no_upstream", "skipped_not_git_toplevel"}:
                        if sync_after_clone == "synced":
                            details = "Clone completed + synced"
                        else:
                            details = f"Clone completed + {sync_after_clone_details}"
                    else:
                        details = f"Clone completed + sync issue: {sync_after_clone_details}"

                local_results.append(
                    LocalSyncResult(
                        repo_id=repo_id,
                        local_path=str(repo_path),
                        cloud_status=cloud_status,
                        local_status=status,
                        details=details,
                        fallback_used=fallback_used,
                    )
                )
                local_sync_summary[status] += 1
                continue

            if sync_status == "synced":
                local_status = "synced"
            elif sync_status == "skipped_dirty":
                local_status = "skipped_dirty"
            elif sync_status == "skipped_no_upstream":
                local_status = "skipped_no_upstream"
            elif sync_status == "skipped_not_git_toplevel":
                local_status = "skipped_not_git_toplevel"
            elif sync_status == "fetch_failed":
                local_status = "fetch_failed"
            elif sync_status == "pull_failed":
                local_status = "pull_failed"
            elif sync_status == "path_conflict":
                local_status = "path_conflict"
            else:
                local_status = sync_status

            local_results.append(
                LocalSyncResult(
                    repo_id=repo_id,
                    local_path=str(repo_path),
                    cloud_status=cloud_status,
                    local_status=local_status,
                    details=sync_details,
                )
            )

            if local_status in local_sync_summary:
                local_sync_summary[local_status] += 1
            else:
                local_sync_summary["missing"] += 1

    else:
        local_sync_summary = {"disabled": True}

    repos_list_out = Path(args.repos_list_out).expanduser().resolve()
    repos_list_out.parent.mkdir(parents=True, exist_ok=True)
    with repos_list_out.open("w", encoding="utf-8") as fh:
        for repo_id in target_repos:
            fh.write(f"{repo_id}\n")

    feature_cloud_repos, scanned_feature_count, feature_cloud_repo_errors = _collect_cloud_repos_from_all_features(project_id, token)
    feature_cloud_repos_out = Path(args.features_cloud_repos_out).expanduser().resolve()
    feature_cloud_repos_out.parent.mkdir(parents=True, exist_ok=True)
    with feature_cloud_repos_out.open("w", encoding="utf-8") as fh:
        for repo_id in feature_cloud_repos:
            fh.write(f"{repo_id}\n")

    report = {
        "timestamp_ms": int(time.time() * 1000),
        "project_id": project_id,
        "project_name": project_name,
        "github_org": github_org,
        "name_contains": args.name_contains,
        "exclude_archived": bool(args.exclude_archived),
        "special_repos": sorted(special_repos),
        "github_repo_count": github_repo_count,
        "github_filtered_repo_count": len(github_filtered),
        "project_cloud_repo_count": len(cloud_linked),
        "target_repo_count": len(target_repos),
        "missing_cloud_repo_count": len(missing_cloud),
        "created_cloud_repo_count": created_cloud_repo_count,
        "auto_subproject_name": args.auto_subproject_name,
        "auto_feature_name": args.auto_feature_name,
        "auto_feature": {
            "feature_id": auto_feature.feature_id,
            "feature_name": auto_feature.feature_name,
            "subproject_id": auto_feature.subproject_id,
        },
        "auto_creation": auto_creation,
        "repos_list_out": str(repos_list_out),
        "features_cloud_repos_out": str(feature_cloud_repos_out),
        "features_scanned_count": scanned_feature_count,
        "features_cloud_repo_count": len(feature_cloud_repos),
        "features_cloud_repo_fetch_errors": feature_cloud_repo_errors,
        "missing_cloud_repos": missing_cloud,
        "cloud_link_errors": cloud_link_errors,
        "local_sync_summary": local_sync_summary,
        "repos": [
            {
                "repo_id": item.repo_id,
                "local_path": item.local_path,
                "cloud_status": item.cloud_status,
                "local_status": item.local_status,
                "details": item.details,
                "fallback_https_used": item.fallback_used,
            }
            for item in local_results
        ],
        "dry_run": bool(args.dry_run),
        "no_local_sync": bool(args.no_local_sync),
    }

    out_path = Path(args.out).expanduser().resolve()
    _write_json(out_path, report)

    print(f"Project: {project_name} ({project_id})")
    print(f"GitHub repos scanned: {github_repo_count}")
    print(f"GitHub repos matched '{args.name_contains}': {len(github_filtered)}")
    print(f"Target repos (matched + special): {len(target_repos)}")
    print(f"Missing cloud repos: {len(missing_cloud)}")
    if not args.dry_run:
        print(f"Created cloud repos: {created_cloud_repo_count}")
    if not args.no_local_sync:
        summary = local_sync_summary
        print(
            "Local sync summary:"
            f" synced={summary.get('synced', 0)}"
            f", cloned={summary.get('cloned', 0)}"
            f", exists={summary.get('exists', 0)}"
            f", skipped_dirty={summary.get('skipped_dirty', 0)}"
            f", clone_failed={summary.get('clone_failed', 0)}"
            f", fetch_failed={summary.get('fetch_failed', 0)}"
            f", pull_failed={summary.get('pull_failed', 0)}"
        )
    print(f"Target list: {repos_list_out}")
    print(f"Cloud repos from all features: {feature_cloud_repos_out} ({len(feature_cloud_repos)})")
    print(f"Report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
