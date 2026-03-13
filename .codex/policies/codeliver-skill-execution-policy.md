# CodeDeliver Skill-Only Execution Policy (On-Demand)

Load this policy when the user asks to run an existing local utility/debug skill or equivalent local automation without requesting repository code changes, PM workflow, or documentation work.

## Skill-only execution carve-out

- This carve-out applies only to execution-only requests:
- run an existing skill by name
- run a local debug/serve/install/inspect/launch automation
- execute an already available helper script or workflow without changing repo code
- This carve-out stops applying as soon as the request turns into implementation, refactor, bugfix, documentation, task management, or release work.

## Required behavior

- Execute directly when the request is clear and local prerequisites are discoverable.
- Do not create or update ClickUp tasks for skill-only execution requests.
- Do not run ClickUp search, repo-linking, time-tracking, status updates, or closeout workflow.
- Do not ask delivery mode, target branch, `push only`, or `deploy` for skill-only execution requests.
- Keep chat output minimal:
- one short kickoff update
- blocker/failure updates only when needed
- one short closeout without a step-by-step recap unless the user asks for details
- Do not mention token saving, log saving, verbosity optimization, or similar meta rationale in user-facing replies.
- Do not narrate each retry path in chat. Avoid user-facing lines like “τώρα ξανατρέχω με Χ” unless the user explicitly asked for a detailed debug walkthrough.

## Self-correcting execution

- Before rerunning a failing skill path, inspect the most relevant existing logs/output first and prefer the narrowest safe fallback over repeating the same failing command with more noise.
- Use internal recovery loops for reproducible blockers:
- inspect blocker
- try the smallest safe workaround
- verify the intended result
- continue the skill flow if the workaround succeeds
- If a workaround succeeds and is reproducible, fold it back into the canonical local skill or policy text so the next execution starts from the corrected path.
- Persist learned recovery knowledge only after confirmed success. Do not write back speculative, partial, or failed attempts.
- Treat transient environment blockers as non-knowledge events. Examples: disconnected device, expired auth, missing system binary, unavailable external service.
- Treat reproducible, locally fixable execution patterns as skill knowledge. Examples: safer fallback order, Android-only continuation after non-Android prepare failure, resource regeneration before install retry, known plugin re-patch before rebuild.

## Validation and escalation

- Prefer the skill's existing defaults and only pass extra flags when the user asked for them or local context makes them necessary.
- If execution fails after reasonable recovery attempts, report the concrete blocker and the shortest useful next action.
- If the user then asks to modify the skill, repo code, or global workflow, switch back to the normal implementation workflow and re-enable the usual gates.
