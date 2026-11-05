# 75: Caveman with techsanity off grants no starting techs

**Reported:** 2026-11-04, found while triaging [#64](64-researched-at-start-ignores-caveman.md)

**Status:** needs-triage

## Report

With caveman on and techsanity off, every scenario starts with no tech below its opening age
researched: no Blacksmith techs, no Loom, no unit upgrades. Joan 1 opens in Castle and starts
with nothing from the Dark or Feudal Age. Caveman should hold back upgrade techs only (#64).
Every other below-age tech should still be granted.

Found from code. Not yet seen in game.

## Why

1. **Caveman alone moves the scenario back to the Dark Age.** `InstallHandler.scenario_needs_age_up`
   returns True when `AP_US_CAVEMAN` is set, whatever techsanity is set to. `steps_for` then adds
   `ScenarioParser.rebase_to_dark`. `test_caveman_rebases_on_its_own` pins this (techsanity 0,
   caveman 1). The engine then auto-researches nothing.
2. **Nothing grants the techs back.**
   - `_write_tech_data` writes an empty `TechData()` when techsanity is none.
   - `InitTechsanity` returns at once on `TECHSANITY_NONE`, so `reconstructStartingState` never
     runs.
   - `ClimbToVanillaAge` completes only the age techs (Feudal, Castle, Imperial), not the techs
     below them.

Thus the only code that grants below-age techs after the move back to Dark never runs when
techsanity is off.

## Logic side

The logic still assumes P1 has every non-upgrade tech below the opening age.
`ScenarioTechLogic.researched_at_start` does not depend on techsanity, so after #64 it is True for
those techs and False only for the withheld ones. That matches the intended game behavior, so the
fix is expected to be game-side only. Confirm this when triaging.

## Open questions

- Fix direction: write a grant-only tech table and run the reconstruction when techsanity is off
  but caveman is on, or stop caveman from moving the scenario back to Dark when techsanity is off.
  If the scenario is not moved back, the engine auto-researches the upgrades too, which breaks
  #64's "caveman withholds upgrades".

## Comments
