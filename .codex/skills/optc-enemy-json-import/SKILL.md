---
name: optc-enemy-json-import
description: Turn an OPTC enemy description into canonical enemy JSON for the saved-enemies Import Enemy flow.
---

# OPTC Enemy JSON Import

Use this skill when the user describes an OPTC enemy in prose, screenshots, quest guide text, or mixed battle notes and wants import-ready JSON for the `Import Enemy` button in the saved enemies modal. This skill returns JSON only. If the prompt also asks for a team, roster advice, or broader strategy, still prioritize the import-ready enemy JSON unless the user explicitly asks to override that default.

## Output rules

1. Return only one fenced `json` block.
2. Do not add prose before or after the JSON unless the user explicitly asks for explanation.
3. Never invent `imageDataUrl`.
4. If a detail cannot be represented structurally, place it in `enemy.notes`.
5. If the prompt mixes team-building or roster requests into the skill invocation, still return only the enemy JSON unless the user explicitly asks for a second output.

## Canonical schema

```json
{
  "schemaVersion": 1,
  "source": "optc-enemy-skill",
  "exportType": "enemy",
  "enemy": {
    "name": "Enemy name",
    "notes": "Optional notes",
    "selectedTypes": ["DEX", "INT", "PSY", "QCK", "STR"],
    "selectedClasses": [
      "Booster",
      "Cerebral",
      "Driven",
      "Evolver",
      "Fighter",
      "Free Spirit",
      "Powerhouse",
      "Shooter",
      "Slasher",
      "Striker"
    ],
    "requiredAbilities": [],
    "enemyMechanics": [],
    "requireAllSelectedTypesInTeam": false,
    "requireAllSelectedClassesPerCharacter": false,
    "requireAllSpecialsSupportTeam": false
  }
}
```

## Defaults

1. If the prompt does not specify types, set `selectedTypes` to all standard OPTC types.
2. If the prompt does not specify classes, set `selectedClasses` to all standard OPTC classes.
3. If the prompt does not specify strict matching, keep all three toggle booleans `false`.
4. Omit `imageDataUrl` unless the user explicitly provides it.
5. If the prompt includes multiple screenshots, multiple battles, or quest-wide mechanics, treat the payload as a whole-quest import by default instead of boss-only.
6. If the prompt mixes team-building language with skill invocation, prioritize import-ready enemy JSON and do not ask about roster or team-building preferences unless the user explicitly asks for that second output.
7. If an ambiguity does not change the schema or supported keys, choose the safest JSON-compatible interpretation and capture the nuance in `enemy.notes` instead of asking a follow-up question.

## Mapping guidance

1. Add `enemyMechanics` only for structured enemy behavior already supported by the app catalog, such as:
   - `enemy_increased_defense`
   - `enemy_barrier`
   - `enemy_threshold_damage_reduction`
   - `crew_bind`
   - `interrupt_special`
2. Add `requiredAbilities` only for direct counters the builder should target, and only when those counters already exist in the app ability catalog.
3. Use `deal_fixed_damage` when the prompt says the enemy is only reliably beaten by fixed damage.
4. Use `inflict_poison` when poison, toxic, venom, or poison-only kill logic is required.
5. If the prompt says normal attacks do not work because of very high defense, model that as:
   - `enemyMechanics`: `enemy_increased_defense`
   - `requiredAbilities`: `deal_fixed_damage` and/or `inflict_poison` when the prompt explicitly says those work
6. If a mechanic is real but unsupported by the current schema or catalogs, place it in `enemy.notes` instead of inventing structure. Common examples include `special reverse`, `limited taps`, exact positional quirks, enemy type change, and interrupt side effects that cannot be represented cleanly.
7. If the prompt already provides quest-wide evidence from multiple waves or battles, do not ask whether to model only the boss or the whole quest; default to whole quest.
8. Keep situational advice like "defense reduction + high damage can work" inside `notes` unless the user explicitly wants it enforced as a hard requirement.

## Barrel / Bundle rule

For red cloth bundle / barrel-style enemies:

1. Set `enemyMechanics` to include `enemy_increased_defense` with a long or permanent duration when implied.
2. Add `deal_fixed_damage`.
3. Add `inflict_poison` if poison is described as a valid kill method.
4. Mention any weaker fallback strategy in `notes`.

## Asset

For a ready-made example, use [`assets/red-cloth-bundle.enemy.json`](./assets/red-cloth-bundle.enemy.json).
