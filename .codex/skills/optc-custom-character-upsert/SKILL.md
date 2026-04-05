---
name: optc-custom-character-upsert
description: Add or update a custom OPTC character in the optc-team-builder repo from a fixed JSON template plus image path or URL, then reapply the local dataset without fetching upstream data.
---

# OPTC Custom Character Upsert

Use this skill when the user wants to add or update a custom character for `optc-team-builder`.

## Guardrails

- Only use this skill inside the `optc-team-builder` workspace.
- Do not edit `public/assets/data/*` by hand.
- Do not run `scripts/import-optc-data.mjs` for this workflow.
- Prefer the fixed template at `$PWD/scripts/data/manual-character-template.json` after confirming the cwd is the repo root.

## Required workflow

1. Verify the cwd is the `optc-team-builder` repo.
2. Read the template file and mirror its shape exactly.
3. Resolve the image source:
   - Accept a local path or HTTP/HTTPS URL directly.
   - If the user only attached an image and no usable file path or URL is available to tools, ask for a local path or URL before proceeding.
4. Write the user payload to a temporary JSON file.
5. Run:

```bash
node scripts/upsert-manual-character.mjs --payload-file /tmp/payload.json
```

6. If the image must override the template field, pass:

```bash
node scripts/upsert-manual-character.mjs --payload-file /tmp/payload.json --image "/absolute/path/or/url"
```

7. Report the final custom id from the CLI output.

## Notes

- The repo stores source records in `scripts/data/manual-characters.json`.
- Source images live in `scripts/data/character-images/`.
- The CLI automatically reapplies the local dataset and refreshes:
  - `public/assets/data/optc-seed.sql`
  - `public/assets/data/optc-manifest.json`
  - `public/assets/data/optc-auto-builder-abilities.json`
  - `public/assets/data/optc-preview.json`
  - `public/assets/data/optc-unresolved-images.json`

## Output expectation

- Confirm whether the run created or updated a character.
- Return the final custom id.
- Mention the overlay file and generated dataset files that changed.
