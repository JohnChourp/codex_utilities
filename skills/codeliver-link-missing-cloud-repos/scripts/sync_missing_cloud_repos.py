#!/usr/bin/env python3
"""Sync missing codeliver cloud repos into a CRP project."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

API_BASE = "https://mpq5pzhhv2.execute-api.eu-west-1.amazonaws.com/prod"
ENDPOINTS = {
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
DEFAULT_BUCKET = "cloud-repos-panel-data"
DEFAULT_PREFIX = "codeliver-"
DEFAULT_PROJECT_NAME = "codeliver"
DEFAULT_FALLBACK_FEATURE = "uncategorized-repos"
DEFAULT_AUTO_SUBPROJECT = "cloud-repos-auto-linking"
DEFAULT_AUTO_FEATURE = "auto-linked-codeliver-repos"

GENERIC_TOKENS = {
    "codeliver",
    "repo",
    "repos",
    "lambda",
    "function",
    "handler",
    "api",
    "crp",
    "dm",
    "all",
}


@dataclass
class FeatureRef:
    feature_id: str
    feature_name: str
    tokens: set[str]


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")


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
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {url}: {payload}") from e


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def _tokenize(value: str) -> set[str]:
    tokens = {
        part
        for part in re.split(r"[^a-z0-9]+", value.lower())
        if part and len(part) > 1 and part not in GENERIC_TOKENS
    }
    return tokens


def _find_feature(features: list[FeatureRef], feature_id_or_name: str) -> FeatureRef | None:
    needle = feature_id_or_name.strip().lower()
    for f in features:
        if f.feature_id.lower() == needle or f.feature_name.lower() == needle:
            return f
    return None


def _score_feature(repo_id: str, feature: FeatureRef) -> int:
    repo_tokens = _tokenize(repo_id)
    common = repo_tokens.intersection(feature.tokens)
    if not common:
        return 0
    score = len(common)
    if "dispatch" in common or "route" in common:
        score += 1
    if "simulation" in common:
        score += 1
    return score


def _extract_s3_repos(payload: Any, prefix: str) -> list[str]:
    if isinstance(payload, dict):
        raw_items = payload.get("repos", [])
    elif isinstance(payload, list):
        raw_items = payload
    else:
        raw_items = []

    repos: list[str] = []
    for item in raw_items:
        if isinstance(item, dict):
            rid = item.get("repo_id") or item.get("name") or item.get("repo")
        else:
            rid = item
        if isinstance(rid, str) and rid.startswith(prefix):
            repos.append(rid)

    return sorted(set(repos))


def _download_s3_repos_json(bucket: str, key: str) -> tuple[Path, Any]:
    if shutil.which("aws") is None:
        raise RuntimeError("AWS CLI not found in PATH.")
    fd, tmp_name = tempfile.mkstemp(prefix="crp-repos-", suffix=".json")
    os.close(fd)
    tmp_path = Path(tmp_name)
    cmd = [
        "aws",
        "s3",
        "cp",
        f"s3://{bucket}/{key}",
        str(tmp_path),
        "--only-show-errors",
    ]
    run = _run(cmd)
    if run.returncode != 0:
        stderr = (run.stderr or run.stdout or "").strip()
        raise RuntimeError(f"Failed to download s3://{bucket}/{key}: {stderr}")
    return tmp_path, _read_json(tmp_path)


def _select_project(cfg: dict[str, Any], token: str, project_name: str, project_id: str | None) -> tuple[str, str]:
    if project_id:
        current_name = str(cfg.get("currentProject", {}).get("name") or "")
        return project_id, current_name or project_name

    current = cfg.get("currentProject") or {}
    curr_id = str(current.get("id") or "").strip()
    curr_name = str(current.get("name") or "").strip()
    if curr_id and curr_name.lower() == project_name.lower():
        return curr_id, curr_name

    res = _http_post(
        ENDPOINTS["fetch_projects"],
        {"type": "fetch-projects", "page": 0, "searchTerm": "", "project_id": "", "nextContinuationToken": ""},
        token,
    )
    projects = res.get("data", res)
    if not isinstance(projects, list):
        raise RuntimeError("Unexpected response from crp-fetch-projects.")
    for p in projects:
        pid = str(p.get("project_id") or p.get("id") or "").strip()
        pname = str(p.get("project_name") or p.get("name") or "").strip()
        if pname.lower() == project_name.lower() and pid:
            return pid, pname
    raise RuntimeError(f"Project '{project_name}' was not found.")


def _fetch_features(project_id: str, token: str) -> list[FeatureRef]:
    res = _http_post(
        ENDPOINTS["fetch_features"],
        {"type": "fetch-features-by-project-id", "project_id": project_id},
        token,
    )
    rows = res.get("data", res)
    if not isinstance(rows, list):
        return []
    out: list[FeatureRef] = []
    for item in rows:
        fid = str(item.get("feature_id") or item.get("id") or "").strip()
        name = str(item.get("feature_name") or item.get("name") or "").strip()
        if not fid or not name:
            continue
        out.append(FeatureRef(feature_id=fid, feature_name=name, tokens=_tokenize(name)))
    return out


def _fetch_subprojects(project_id: str, token: str) -> list[dict[str, Any]]:
    res = _http_post(
        ENDPOINTS["fetch_subprojects"],
        {"type": "fetch-subprojects-by-project-id", "project_id": project_id},
        token,
    )
    rows = res.get("data", res)
    return rows if isinstance(rows, list) else []


def _fetch_project_cloud_repos(project_id: str, token: str) -> list[dict[str, Any]]:
    res = _http_post(
        ENDPOINTS["fetch_cloud_repos"],
        {"type": "fetch-cloud-repos-by-project-id", "project_id": project_id},
        token,
    )
    rows = res.get("data", res)
    return rows if isinstance(rows, list) else []


def _create_subproject(project_id: str, token: str, subproject_name: str) -> dict[str, Any]:
    body = {
        "type": "create",
        "subProject": {
            "name": subproject_name,
            "subproject_name": subproject_name,
            "project_id": project_id,
            "res_aws": {},
            "description": "Auto-created for cloud repo auto-linking.",
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
            "description": "Auto-created fallback feature for missing codeliver cloud repos.",
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


def _resolve_fallback_feature(
    features: list[FeatureRef],
    project_id: str,
    token: str,
    fallback_feature: str,
    auto_subproject_name: str,
    auto_feature_name: str,
    allow_create: bool,
    dry_run: bool,
) -> tuple[FeatureRef, dict[str, Any] | None]:
    existing = _find_feature(features, fallback_feature)
    if existing:
        return existing, None
    if not allow_create:
        raise RuntimeError(
            f"Fallback feature '{fallback_feature}' not found and auto-create is disabled."
        )

    fallback_name = fallback_feature
    looks_like_id = bool(re.fullmatch(r"[a-f0-9-]{12,}", fallback_feature.lower()))
    if looks_like_id:
        fallback_name = auto_feature_name

    if dry_run:
        fake = FeatureRef(
            feature_id="DRY-RUN-FEATURE-ID",
            feature_name=fallback_name,
            tokens=_tokenize(fallback_name),
        )
        created_info = {
            "dry_run": True,
            "subproject_name": auto_subproject_name,
            "feature_name": fallback_name,
        }
        return fake, created_info

    subprojects = _fetch_subprojects(project_id, token)
    selected_subproject_id = ""
    for sp in subprojects:
        sid = str(sp.get("subproject_id") or sp.get("id") or "").strip()
        sname = str(sp.get("subproject_name") or sp.get("name") or "").strip()
        if sid and sname.lower() == auto_subproject_name.lower():
            selected_subproject_id = sid
            break

    created_info: dict[str, Any] = {}
    if not selected_subproject_id:
        sp_res = _create_subproject(project_id, token, auto_subproject_name)
        sp_data = sp_res.get("data", sp_res)
        selected_subproject_id = str(sp_data.get("subproject_id") or sp_data.get("id") or "").strip()
        if not selected_subproject_id:
            raise RuntimeError("Failed to create fallback subproject.")
        created_info["created_subproject"] = {
            "subproject_id": selected_subproject_id,
            "subproject_name": str(sp_data.get("subproject_name") or sp_data.get("name") or auto_subproject_name),
        }

    f_res = _create_feature(project_id, selected_subproject_id, token, fallback_name)
    f_data = f_res.get("data", f_res)
    fid = str(f_data.get("feature_id") or f_data.get("id") or "").strip()
    fname = str(f_data.get("feature_name") or f_data.get("name") or fallback_name).strip()
    if not fid:
        raise RuntimeError("Failed to create fallback feature.")
    created_info["created_feature"] = {"feature_id": fid, "feature_name": fname}

    created_ref = FeatureRef(feature_id=fid, feature_name=fname, tokens=_tokenize(fname))
    features.append(created_ref)
    return created_ref, created_info


def _best_feature_for_repo(
    repo_id: str,
    features: list[FeatureRef],
    fallback: FeatureRef,
    min_score: int,
) -> tuple[FeatureRef, int]:
    best: FeatureRef | None = None
    best_score = -1
    for feature in features:
        score = _score_feature(repo_id, feature)
        if score > best_score:
            best = feature
            best_score = score
    if best is not None and best_score >= min_score:
        return best, best_score
    return fallback, best_score


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find codeliver-* repos missing from CRP project links and auto-link them."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--crp-org", default="")
    parser.add_argument("--repos-key", default="")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    parser.add_argument("--project-id", default="")
    parser.add_argument("--fallback-feature", default=DEFAULT_FALLBACK_FEATURE)
    parser.add_argument("--auto-subproject-name", default=DEFAULT_AUTO_SUBPROJECT)
    parser.add_argument("--auto-feature-name", default=DEFAULT_AUTO_FEATURE)
    parser.add_argument("--min-match-score", type=int, default=2)
    parser.add_argument("--out", default="missing-cloud-repos-sync-report.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-create-fallback", action="store_true")
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

    crp_org = args.crp_org.strip() or str(((cfg.get("api") or {}).get("auth") or {}).get("user", {}).get("org") or "").strip()
    if not crp_org:
        print("ERROR: CRP org missing. Use --crp-org or set it in ~/.crp/config.json.", file=sys.stderr)
        return 2

    key = args.repos_key.strip() or f"{crp_org}-repos.json"
    project_id, project_name = _select_project(cfg, token, args.project_name, args.project_id or None)

    report: dict[str, Any] = {
        "timestamp_ms": int(time.time() * 1000),
        "bucket": args.bucket,
        "repos_key": key,
        "project_id": project_id,
        "project_name": project_name,
        "prefix": args.prefix,
        "dry_run": args.dry_run,
        "fallback_feature": args.fallback_feature,
        "min_match_score": args.min_match_score,
    }

    tmp_s3_path, s3_payload = _download_s3_repos_json(args.bucket, key)
    s3_repos = _extract_s3_repos(s3_payload, args.prefix)
    report["s3_repo_count"] = len(s3_repos)
    report["s3_download_path"] = str(tmp_s3_path)

    cloud_rows = _fetch_project_cloud_repos(project_id, token)
    linked_repos = sorted(
        {
            str(row.get("repo_id") or "").strip()
            for row in cloud_rows
            if str(row.get("repo_id") or "").strip()
        }
    )
    report["project_linked_repo_count"] = len(linked_repos)

    missing = sorted(set(s3_repos) - set(linked_repos))
    report["missing_repo_count"] = len(missing)
    report["missing_repos"] = missing

    features = _fetch_features(project_id, token)
    if not features:
        print("ERROR: No features found in target project.", file=sys.stderr)
        return 3

    fallback, created_info = _resolve_fallback_feature(
        features=features,
        project_id=project_id,
        token=token,
        fallback_feature=args.fallback_feature,
        auto_subproject_name=args.auto_subproject_name,
        auto_feature_name=args.auto_feature_name,
        allow_create=not args.no_create_fallback,
        dry_run=args.dry_run,
    )
    if created_info:
        report["fallback_creation"] = created_info

    decisions: list[dict[str, Any]] = []
    linked_ok = 0
    linked_fail = 0
    for repo_id in missing:
        target, score = _best_feature_for_repo(
            repo_id=repo_id,
            features=features,
            fallback=fallback,
            min_score=args.min_match_score,
        )
        decision = {
            "repo_id": repo_id,
            "target_feature_id": target.feature_id,
            "target_feature_name": target.feature_name,
            "score": score,
            "used_fallback": target.feature_id == fallback.feature_id,
        }
        if args.dry_run:
            decision["status"] = "planned"
        else:
            try:
                res = _link_repo(project_id, target.feature_id, repo_id, token)
                success = bool(res.get("success"))
                decision["status"] = "linked" if success else "failed"
                if success:
                    linked_ok += 1
                else:
                    linked_fail += 1
                    decision["error"] = res.get("comment_id") or res.get("message") or "unknown_error"
            except Exception as exc:  # pragma: no cover
                linked_fail += 1
                decision["status"] = "failed"
                decision["error"] = str(exc)
        decisions.append(decision)

    report["decisions"] = decisions
    report["linked_ok"] = linked_ok
    report["linked_fail"] = linked_fail

    out_path = Path(args.out).expanduser().resolve()
    _write_json(out_path, report)

    print(f"S3 repos ({args.prefix}*): {len(s3_repos)}")
    print(f"Already linked in project: {len(linked_repos)}")
    print(f"Missing repos: {len(missing)}")
    if args.dry_run:
        print("Mode: DRY RUN (no link actions executed)")
    else:
        print(f"Linked OK: {linked_ok}")
        print(f"Linked Failed: {linked_fail}")
    print(f"Report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
