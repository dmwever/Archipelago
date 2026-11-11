# Scenario difficulty

Label: wayfinder:map

## Destination

A locked spec, `worlds/age2de/docs/spec-scenario-difficulty.md`, covering the `scenario_difficulty`
option, how each tier maps onto AI behaviour and difficulty triggers, the AI builder's source format,
and the install-time injection, ready to slice into implementation tickets.

## Notes

- Domain: age2de apworld (Archipelago) + Ageipelago mod repo. Consult the `ageipelago` and
  `aoe2-modding` skills; read scenarios through `aoe2-modding`, ids from the vendored
  `worlds/age2de/AoE2ScenarioParser/datasets/`.
- Glossary: **Scenario difficulty** and **Lobby difficulty** in `worlds/age2de/CONTEXT.md`.
- Branches: `scenario-difficulty` in both repos (Archipelago off `v0.4.0`, Ageipelago off `0.4.0`).
- Standing decisions from charting (2026-11-11):
  - New yaml Choice `scenario_difficulty`, separate from `trap_difficulty`, same five names
    (easiest/standard/medium/hard/legendary), default `standard`.
  - Tier is baked in at install; the lobby difficulty stops governing AP AIs.
  - Tier → AI branch: easiest = easy branch with build caps lowered; standard = easy; medium =
    moderate; hard = hard; legendary = hard branch with build caps raised.
  - Difficulty-conditional scenario triggers are in scope: the tier drives them too.
  - Only scripts that branch on `difficulty` are built; non-combat / placeholder AIs
    (PromiDE, Promisory, Joan-noncombat, RandomGame, _ajl, Fe Immobile AI, Greg's Peaceful) pass
    through unchanged.
- Known facts: 18 AP scenarios embed 127 per-player AI scripts, readable via the parser's
  `player_manager.players[i].ai_script`; the parser can write them with
  `Player.set_custom_ai(name, ai_script)`. Install edits scenarios through `ScenarioParser.apply`
  steps chosen in `InstallHandler.steps_for`.

## Decisions so far

- [Inventory difficulty branches in embedded AIs](issues/01-inventory-ai-difficulty-branches.md):
  75 of 127 scripts are live; 44 branch at runtime (407 rules, incl. difficulty-scaled
  `cc-add-resource` cheats), 4 (Mongols-scn1) at compile time via `#load-if-defined DIFFICULTY-*`,
  27 not at all; `== normal`/`== standard` validity open.
- [Audit difficulty-conditional triggers](issues/02-audit-difficulty-triggers.md): 30 Difficulty
  Level triggers plus 8 fired by AI difficulty signals; Genghis 1 hard removes the Wolf Relic
  location's relic, easy gives P1 free techs (Loom, Murder Holes) and Attila 6 buildings;
  condition direction (level N or easier) inferred, not verified.

## Not yet specified

- **Playtesting a tier.** How a tier gets verified in game (which scenarios, what counts as
  "harder"), and whether any automated check covers the built scripts.

## Out of scope
