# Does the scenario difficulty touch logic or locations?

Type: grilling
Status: resolved
Blocked by: 02

## Question

Where a difficulty trigger changes map content (Genghis 1 Hard removes a relic and adds enemy
units), does the seed's tier change what locations exist or what reaching them costs? If so, does
logic read the tier, or do we neutralise those triggers so logic stays tier-independent?

Inputs from the audit ([Audit difficulty-conditional triggers](02-audit-difficulty-triggers.md)):
- Genghis 1 hard removes the relic behind *Pick Up the Relic Surrounded by Wolves* (fired by an
  AI signal, not a trigger condition).
- Easy/easiest gives P1 free Loom (Attila 1) and Murder Holes (Attila 1–5), a free Castle and two
  Mining Camps (Attila 6); Genghis 6 gives Siege Onagers plus Onager/Siege Onager research. These
  bypass techsanity and building-shuffle items.
- Joan 5 easy turns P3 Neutral to P1; Joan 6 removes capturable GAIA siege on harder tiers.

## Answer

**Yes: logic reads the scenario difficulty, narrowly.** Difficulty triggers stay as the scenario
authors wrote them (no stripping), and logic follows what they do to P1. Terms added to
`worlds/age2de/CONTEXT.md`: **Difficulty grant**, **Difficulty-dependent location** ("tier" is now
an avoided word).

- **Scope (standing, revisit if playtests demand):** the difficulty enters logic only through
  (a) the scenario's starting state (`obtains_tech`, `obtains_unit`, `starts_with_building`) and
  (b) which locations exist. Defeat and combat-strength rules do not scale with difficulty.
- **Genghis 1 Wolf Relic:** *Pick Up the Relic Surrounded by Wolves* is a difficulty-dependent
  location, absent on hard and legendary. Same mechanism as branching: `ScenarioPool.includes_location`
  drops it, install disables its AP trigger as `InstallHandler.branching_triggers` does. The hard
  trigger's relic removal stays.
- **Free techs kept:** Loom (Attila 1), Murder Holes (Attila 1–5) become `obtains_tech[...] = True_()`
  at the granting difficulties. Under techsanity the item is still required (Chemistry precedent,
  `logic/genghis/genghis_1.py`, `ScenarioTechLogic._has_researched`).
- **Attila 6 buildings kept:** `starts_with_building[CASTLE]` and `[MINING_CAMP]` at the granting
  difficulties.
- **Genghis 6 Siege Onagers:** `obtains_unit[SIEGE_ONAGER]` + `obtains_tech[ONAGER, SIEGE_ONAGER]`,
  only at the difficulties *Verify Difficulty Level condition direction in game* shows it firing;
  nothing if it never fires at a level we use.
- **Everything else** (Joan 5 diplomacy, Joan 6 GAIA artillery — 3 Bombards + 1 Trebuchet survive
  on hard, so `keeps_its_siege` holds — Joan 3 oaks, enemy-only effects) stays out of logic for now.
- **Data home:** new `worlds/age2de/locations/connections/ScenarioDifficulty.py`, beside
  `ScenarioExclusions.py` / `ScenarioTriggerUnits.py`, holding two per-scenario maps:
  `DIFFICULTY_DEPENDENT_GRANTS` (grant -> scenario difficulties that give it) and
  `DIFFICULTY_DEPENDENT_LOCATIONS` (location -> difficulties where it is absent). Scenario logic
  reads the grants; `includes_location` (and so install) reads the locations. Difficulty sets are
  filled once *Trigger handling per scenario difficulty* and the condition-direction ticket resolve.
- **Guard:** no automated file-vs-table test; a one-off audit re-run by hand when a scenario is
  re-saved, as ADR 0005 does for trigger units. The trigger audit asset is that audit's first run.
- **Fog:** which yaml options interact with the difficulty (techsanity, building shuffle,
  branching, ...) is unknown; parked on the map.
