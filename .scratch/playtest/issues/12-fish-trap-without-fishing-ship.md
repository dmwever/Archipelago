# 12: Build Fish Trap doesn't require a Fishing Ship

**Reported:** 2026-10-20, playtesting

**Status:** needs-triage

## Report

Build Fish Trap appears to be in logic without the Fishing Ship.

## Audit (from code)

In AoE2, Fish Traps are built by Fishing Ships, not villagers.

`ScenarioCanBuild.answer` (`logic/custom_logic/ScenarioQuestions.py:153-163`) treats every building
the same way: the building item, `scenario.has_builders()` (villagers + the Builder profession),
the building's age, its prerequisite (Dock, `locations/Buildings.py:87`) and, for water buildings,
`has_water_access()`. A Fish Trap is in `_WATER_BUILDINGS`, but nothing swaps the builder.

So the rule:

- **misses** the Fishing Ship: neither its unit items (Fishing Ship Line / Boat upgrade token /
  Dock unit item, depending on `unitsanity_items`) nor the wood to build one.
- **asks for** villagers and the Builder profession, which a Fish Trap doesn't need.

The global location (`Logic.can_build_location_anywhere`) and every rule that asks
`has_building(FISH_TRAP)` inherit this. That includes `ScenarioResourceLogic._work_fish_traps`,
but that one is saved by its own `can_crew_fishing_ships()`. The Build location and anything else
that only asks "is there a Fish Trap" are not.

The right check already exists: `ScenarioResourceLogic.can_crew_fishing_ships()` (`:157-166`),
which is Fishing Ship items, the ship's age, and wood for one. It doesn't check the scenario's
`excluded_units` or whether the civ trains Fishing Ships. That's harmless today, since the only
scenario excluding Fishing Ships (Genghis 6) also excludes the Fish Trap and the Dock, but it's worth
covering if the builder check moves over to it.

## Likely shape of a fix

In `ScenarioCanBuild`, use the Fishing Ship (`can_crew_fishing_ships()` or a structural version of
it) as the builder for `FISH_TRAP` instead of `has_builders()`.
