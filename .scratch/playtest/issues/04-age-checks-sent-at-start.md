# 04: Reach Feudal / Reach Castle sent at the start of Joan 1

**Reported:** 2026-10-19, playtesting

**Status:** needs-triage

## Report

Reach Feudal Age and Reach Castle Age were sent during Joan of Arc 1 (An Unlikely Messiah). Age
locations should only send when the player completes the research.

## Audit (from code, not verified in game)

XS side, `Ages.xs`:

1. `InitAges` → `ClimbToVanillaAge` forces each age tech up to the scenario's vanilla age to
   `STATE_DONE` (skipped only under `start_in_dark_age`). Joan 1 sets `SetVanillaAge(CASTLE_AGE)`
   (`AP_Joan_1.xs`), so Feudal and Castle are marked done at startup.
2. With `shuffle_ages` on, `InitAges` registers age locations 1–3 and enables `ShuffleAgesUpdate`.
3. `ShuffleAgesUpdate` checks every age whose tech state is `cTechStateDone` — it cannot tell
   "researched by the player" from "granted by the climb", so it fires both on its first tick.

Affects every scenario whose vanilla age is above Dark, not only Joan 1: all Joan scenarios
(Castle start), and Genghis 3–6 / Attila ones starting Feudal or later — whenever
`existing_techs` isn't `start_in_dark_age`.

The apworld already agrees with the report: `ScenarioAgeLogic.can_research`
(`logic/scenarios/ScenarioAgeLogic.py`) only lets an age at or below a scenario's starting age
count when `DARK_START` holds, and `fixed_force` scenarios (Joan 1) can't reach an age at all. So
these are out-of-logic early checks — logic is fine, the game sends too much.

Likely shape of a fix: exclude ages at or below `apVanillaAge` from the shuffle-ages check (or
snapshot which age techs were already done after `ClimbToVanillaAge` and skip those), and decide
whether a `fixed_force` scenario should register age locations at all.
