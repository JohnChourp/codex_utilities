---
name: clickup-repo-linking
description: Link implementation tasks to repository registry tasks in ClickUp with safe ownership checks and validated relationships. Use when work spans one or more repos and task-to-repo linkage must be established before implementation.
---

# Clickup Repo Linking

Use this skill before implementation starts.

## 1) Resolve repositories involved

1. Identify all repos that will be changed.
2. For each repo, search repo-registry list `901502503337` for an existing repo task.
3. If missing, create a repo task named exactly as the GitHub repository name.
4. Set/select `repo_type` from existing list options. Ask user when uncertain.

## 2) Validate source task write eligibility

1. Read source task using `clickup_get_task`.
2. Confirm source task is assigned to the requesting user.
3. Skip write operations when source task is assigned to someone else.

## 3) Link tasks natively when possible

1. Preferred API: `POST https://api.clickup.com/api/v2/task/{task_id}/link/{links_to}`.
2. Auth only via env var `CLICKUP_API_TOKEN`.
3. If shell is non-interactive and token is in shell profile, run `source ~/.bashrc`.
4. Validate each link call returns `HTTP 200`.
5. Re-read source task and confirm linked task presence/count.

## 4) Fallback when native linking fails

1. Keep a short `Repos` section in source task description.
2. Paste repo-task links there.
3. Do not modify tasks not assigned to the requesting user.

## 5) Tooling checklist

1. Find tasks: `clickup_search` with `asset_types=["task"]`.
2. Scope to list when known: `filters.location.subcategories=["<list_id>"]`.
3. Read and verify: `clickup_get_task`.
4. Update source task fallback text: `clickup_update_task`.
