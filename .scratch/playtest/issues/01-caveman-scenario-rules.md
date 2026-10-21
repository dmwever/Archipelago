# 01: Caveman is not applied to scenario rules

**Reported:** 2026-10-15, playtesting

**Status:** needs-triage

## Report

In caveman mode, Genghis 1 relic collection should require the Monk Line.

## Audit

No per-scenario rule accounts for caveman. Only the global unit locations do
(`logic/unit_logic.py:43`, `granted & (NOT_CAVEMAN | can_restore(unit))`). Wherever a scenario rule
relies on units an item hands over, the logic counts them even when the game has knocked them down
to Militia.

| Scenario | Rule leans on | Missing in caveman |
|---|---|---|
| Genghis 1 (reported) | Kereyid Tribe item gates the three relics, Recruit Ungirrads, Any Relic, Victory (`rules/genghis_rules/genghis_1.py`) | Monk Line *(mercenary)* |
| Every scenario | `ScenarioResourceLogic._collect_relics`: `has_unit_items(MONK) \| obtains_unit(MONK)` — the second branch skips the items. Affects Attila 3 / Joan 4 starting monks, Genghis 5 Hermit monk | Monk Line on the `obtains_unit` branch |
| Joan 1 | Transport Ships item gates Recruits, both river locations, Victory | Transport Ship line |
| Joan 3 | Transport Ships item gates crossing the sea and the base requirement | Transport Ship line |
| Genghis 3 | Transport Ship item gates Find Engineers, Find Bombards, villagers | Transport Ship line |
| Joan 2 | Trade Carts item gates Bring Carts, Conquer Bridge, can cross; Dock item gives transport | Trade Cart line; Crossbow + Knight lines for the escort; Transport Ship line for the Dock route |
| Joan 6 | French Army item counts toward besieging the town | Archer, Militia, Scout, Knight, Trebuchet lines |
| Attila 2 | Scythian Troops beat Blue alone | Mangudai, Ram, Mangonel lines *(mercenary)* |
| Genghis 3 | Bombards item counts as siege | Bombard Cannon line *(mercenary)* |
| Joan 6 | French Artillery counts toward siege | Hand Cannoneer, Bombard lines *(mercenary)* |

Not affected: villagers (caveman-exempt, `UnitData.is_caveman_exempt`), heroes and escort units, and
every `counters` / `has_military` check (those are training-based and already ask for unit items).

## Open question

Mercenary spawns are caveman-immune in the game: `MercenarySpawn.xs:77` calls
`MarkUnitCavemanImmune`. If that is intended, the *(mercenary)* rows — including the reported
Genghis 1 case — are not real game-side problems, and logic is only being conservative. If the
Kereyid monks did turn into Militia in the playtest, the immunity itself is broken.

Units handed over by scenario triggers (Joan 1/2/3/6, Genghis 3 transport) are not immune, so those
rows are real.
