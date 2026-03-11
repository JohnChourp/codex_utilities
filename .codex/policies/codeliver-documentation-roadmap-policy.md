# CodeDeliver Documentation + Roadmap Policy (On-Demand)

## 3) Mandatory documentation behavior (README + FAQ)

Any time you:

- explain a business flow, OR
- change a business flow, OR
- modify any lambda/project behavior,
  you MUST add or update a `README.md` in the relevant folder and ensure it ends with a section:

## “Συχνές ερωτήσεις (FAQ)”

### 3.0 README scope rule (KEEP IT SHORT)

- README files must describe the history.
- Do **NOT** include:
  - **“How to verify” sections**
- Keep updates minimal: only what an engineer/ops person needs to use, operate, and troubleshoot the component.

### 3.1 Which README must be updated/created?

- If the change is within a lambda folder: update/create `README.md` in that lambda’s root folder.
- If the change is within a project (frontend/backend/tool): update/create `README.md` in that project root folder.
- If the change spans multiple lambdas/projects:
  - Update each impacted component README (minimum), and
  - Optionally add a short “Integration Notes” section in the most central README.

### 3.2 README content requirements (minimum structure)

The README MUST include (in this order, unless a repo convention dictates otherwise):

1. **Overview**
   - What the lambda/project does and why it exists.
2. **Business flow**
   - Describe the flow in plain terms (create/update/delete delivery guy, device assignment, login, etc.)
   - Mention key invariants (e.g., unique identifiers, required states).
3. **Inputs & outputs**
   - For lambdas: include sample event JSON and sample response JSON.
   - For APIs: include sample request/response payloads.
4. **Configuration**
   - Required env vars (name, meaning, example).
   - Required AWS resources (tables, buckets, topics, queues) as discovered from code.
   - IAM requirements (high-level permissions, validated from code/templates).
5. **Examples**
   - Include at least:
     - One realistic “happy-path” example
     - One failure example with the expected error shape/message
     - (If relevant) one edge-case example
6. **Συχνές ερωτήσεις (FAQ)** (MANDATORY, at the very end)

### 3.3 FAQ requirements (ops-focused, no change tracking)

The FAQ section MUST explicitly cover:

- **Συνηθισμένες αποτυχίες / failure cases**
  - Typical errors, causes, and how to fix/diagnose
- **Επιπτώσεις σε σχετικές διαδικασίες**
  Must mention impact on:
  - login/auth
  - notifications (push/SNS/etc.)
  - dispatch/routes
  - cleanup (deletions, deprovisioning, orphan records)
- **Πώς επηρεάζονται άλλα components**
  - Which other lambdas/projects are likely affected and why (validated from code searches)
- **Παραδείγματα**
  - At least one Q/A with real payload/event snippets

The FAQ should be written in Greek (since it is user-facing/ops-facing), unless the repository convention requires English.

### 3.4 FAQ template (copy/paste)

Append something like this at the end of the README:

## Συχνές ερωτήσεις (FAQ)

### Γιατί αποτυγχάνει το login/auth;

- Πιθανές αιτίες:
  - (π.χ. missing env var, invalid token audience/issuer, authorizer mismatch, scope/role mismatch)
- Έλεγχοι:
  - (π.χ. logs, decoded JWT claims, env vars, API gateway authorizer config)

### Δεν έρχονται notifications. Τι να ελέγξω;

- (π.χ. SNS topic/event publish, device token mapping, permissions, dead-letter queues)

### Το dispatch/routes δεν ενημερώνεται σωστά. Τι να ελέγξω;

- (π.χ. EventBridge rules, SQS consumers, route recalculation triggers, ordering/idempotency)

### Έγινε delete/cleanup και έμειναν “ορφανά” δεδομένα. Τι κάνουμε;

- (π.χ. ποια tables/queues επηρεάζονται, πώς γίνεται re-run cleanup, remediation steps)

### Πώς επηρεάζονται άλλα components;

- (π.χ. ποια lambdas/projects καταναλώνουν/παράγουν αυτά τα events ή χρησιμοποιούν τα ίδια tables)

### Παραδείγματα

**Happy path**

```json
{
  "example": "..."
}
```

**Failure example**

```
{
  "error": "..."
}
```

Roadmap maintenance (MANDATORY)

A roadmap is a forward-looking artifact. For CodeDeliver, ROADMAP.md must be scannable and must answer three questions:

1. What is already delivered?
2. What is currently underway (or clearly unfinished)?
3. What should we do next?

Exception (ONE-TIME bootstrap per component):
When a ROADMAP.md is being created for the first time for a given lambda/project, it MUST be bootstrapped from the functional git commit history for that component scope (see 4.4). This establishes an accurate baseline of what shipped, while still keeping the roadmap readable (no per-commit history dump).

4.1 Placement rules (STRICT)

Lambdas:

- ROADMAP.md lives inside each lambda’s root folder (one per lambda).

Projects:

- ROADMAP.md is SINGLE per project and lives at the project root (next to that project’s package.json / angular.json / project.json).

Rules:

- Do NOT create ROADMAP.md files inside project subfolders (components/pages/features/services/modules).
- If multiple areas/components inside the same project are affected, capture everything in the single project-root ROADMAP.md.

  4.2 When to update ROADMAP.md

Whenever you propose changes that would reasonably be committed (feature, bug fix, refactor, contract change, config change), you MUST also update the relevant ROADMAP.md file(s) as part of the output.

4.3 ROADMAP.md structure (STRICT)

ROADMAP.md MUST contain exactly three top-level sections, in this exact order:

1. Completed
2. In Progress
3. Next

Rules:

- Do NOT add additional top-level sections.
- Do NOT include verification steps, command snippets, or changelog/history narration.
- Do NOT include commit-level metadata (messages/authors/dates/SHAs) anywhere in ROADMAP.md.

  4.4 FIRST-TIME creation of ROADMAP.md (ONE-TIME per lambda/project)

Goal:
Create a truthful baseline where:

- “Completed” is a milestone-style summary synthesized from all FUNCTIONAL commits affecting the scope path,
- without listing commits, authors, dates, SHAs, diffs, or file paths.

Hard rules:

- When a commit is classified as NON_FUNCTIONAL_ONLY, DO NOT include it in ROADMAP.md at all.
- For every included commit (FUNCTIONAL), you MUST read `git show <SHA> -- <SCOPE_PATH>` to understand the behavior change.
- ROADMAP.md MUST NOT include:
  - commit messages, SHAs, dates, or authors
  - per-commit breakdowns or “what changed in commit X” narratives
  - file names/paths or file-by-file change lists
- “Completed” MUST reflect the net/current behavior of the component (do not include features that were later removed/reverted).

  4.4.1 Define “NON_FUNCTIONAL_ONLY” commits (for filtering)

A commit is considered NON_FUNCTIONAL_ONLY for this roadmap scope if, within the scope path being documented, it ONLY changes files from the following allowlist:

- ROADMAP.md
- README.md
- outfile.json
- payload.json
- package.json
- package-lock.json

Notes:

- Apply this filter ONLY to files changed within the scoped path of the roadmap (lambda root folder or project root folder).
- If a commit changes any other file(s) in the scope path, it is FUNCTIONAL and MUST be treated as input to the “Completed” milestone synthesis.

  4.4.2 REQUIRED git-based workflow to build the baseline

Identify the git root:

- `git rev-parse --show-toplevel`

Choose the scope path for this roadmap:

- For a lambda roadmap: the lambda folder path (where ROADMAP.md will live)
- For a project roadmap: the project root path (where ROADMAP.md will live)

List commits affecting the scope path (oldest → newest):

- `git log --reverse --date=short --format="%H|%ad|%an|%ae|%s" -- <SCOPE_PATH>`

For each commit SHA in that list:

1. List files changed within the scope path:
   - `git show --name-only --pretty=format: <SHA> -- <SCOPE_PATH>`
2. Classify:
   - If and only if the changed files within scope are exclusively in the NON_FUNCTIONAL_ONLY allowlist → skip completely.
   - Otherwise → FUNCTIONAL.
3. For every FUNCTIONAL commit, read the diff within scope:
   - `git show <SHA> -- <SCOPE_PATH>`
4. Extract the behavior/outcome changes and synthesize them into milestone-style “Completed” bullets (see 4.4.3).

If git history is not available in the environment:

- Explicitly state that limitation and provide the exact commands the user should run locally.
- Ask the user to paste:
  - the `git log ... -- <SCOPE_PATH>` output, and
  - the `git show <SHA> -- <SCOPE_PATH>` diffs for the top N FUNCTIONAL commits at a time.

    4.4.3 How to write the three sections (content rules)

## Completed

- Write as milestone-style outcomes/capabilities that exist now (net/current behavior).
- NO commit metadata, NO per-commit narration, NO file/path mentions.
- Prefer business/feature language (“Supports X”, “Validates Y”, “Publishes event Z”) rather than implementation language.
- Keep it reasonably compact:
  - Aim for ~5–20 bullets depending on scope size.
  - Merge related commits into a single milestone where appropriate.

## In Progress

- Items that appear partially implemented, clearly unfinished, or started but not completed.
- Must be grounded in the current codebase state (not only commit history):
  - TODO/FIXME markers
  - stubs / “not implemented” branches
  - commented-out WIP blocks
  - obvious missing error handling/edge cases implied by current logic
  - failing or incomplete tests (if present)
  - missing config wiring implied by code
- Prefer checkboxes:
  - `- [ ] ...`
- If nothing is clearly in progress, include a single explicit line:
  - `- [ ] No in-progress items identified in the current codebase.`

## Next

- Concrete, component-specific follow-ups and improvement ideas (brainstorm), based on gaps/opportunities you observed while reading diffs and current code.
- Prefer higher-leverage items (reliability, ops, correctness, observability, contract clarity, idempotency).
- Prefer checkboxes:
  - `- [ ] ...`

# Roadmap

## Completed

- (Add milestone-style bullets that summarize the net/current delivered capabilities for this component.)

## In Progress

- [ ] (Add unfinished or partially implemented work items detected in the current codebase.)

## Next

- [ ] (Add concrete, component-specific follow-ups and improvement ideas.)

  4.5 Ongoing ROADMAP.md updates (after the first-time bootstrap)

After ROADMAP.md exists for a given lambda/project:

- Do NOT regenerate from git history unless explicitly requested.
- Keep the file forward-looking and current:
  - Move items from Next → In Progress when work starts.
  - Move items from In Progress → Completed when the work is actually shipped and present in the codebase.
- Keep “Completed” as a concise, net/current capability summary (avoid turning it into a per-release or per-commit history).

  4.6 Roadmap formatting rules (keep scannable)

- Use exactly the three required top-level headings in the required order.
- Completed:
  - Prefer plain bullets (no checkboxes) unless there’s a strong reason to use checkboxes.
- In Progress / Next:
  - Prefer checkbox lists (`- [ ]`).
- Avoid long narrative paragraphs.
- Do NOT add “How to verify” steps in ROADMAP.md (verification belongs in the assistant reply).

  4.7 Sticky policy: Thread-Scoped ClickUp Tracking (MANDATORY)

