# 13: Easy resources don't require a base, and a base doesn't require the Villager Line

**Reported:** 2026-10-20, playtesting

**Status:** needs-triage

## Report

A base is not required for easy resources; in particular, the Villager Line is missing.

## Audit (from code)

### The Villager Line is never asked by scenario logic

`UnitLogic.has_villager_item` (`logic/unit_logic.py:124-127`), which is `Has(Unit Line: Villager)`
when the villager is shuffled, is used only by `has_unit_items` for the global villager locations.
No scenario rule asks for it:

- `ScenarioLogic.has_vils()` is just `starting_state.has_vils`.
- `ScenarioLogic._has_base()` asks for `STARTING_VILLAGER_FOOD` (150 food, i.e. the food to *train*
  the starting villagers) and the Town Center wood and stone, but not the Villager Line needed to
  train them.

So with `shuffle_villager` on, a base, and everything gathered through it, is in logic before the
player can train a villager.

### Easy food skips the base entirely

`ScenarioHasEasyResource` (`logic/custom_logic/ScenarioQuestions.py:240-305`):

| Resource | Path | Asks `has_base()`? |
|---|---|---|
| Gold | raw mining / oysters / whales | yes (`& scenario.has_base()`) |
| Stone | raw quarrying | yes |
| Wood | `can_gather_wood` (`ScenarioResourceLogic._chop_wood`) | yes |
| Food | raw hunt / herd / forage / shore fish / boat fish (`_food_easily`) | **no** |
| Food | `endless_food` | indirectly, through `_can_get_wood_easily` |

The raw food gatherers (`_hunt`, `_herd`, `_forage`, `_fish_from_shore`,
`ScenarioResourceLogic.py:112-150`) ask a dropsite, `has_vils()` and the job, but not a base. That
contradicts `has_base`'s own docstring ("the easy sources ask for a base themselves"). This matches
the issue 05 trace, where "Can easily gather food -> True" held in Attila 1 without an affordable
Town Center.

Side paths worth a look for the same gap: the ally-trade paths (`ally_trade_gold` /
`ally_trade_wood`, `ScenarioResourceLogic.py:287-324`) accept `can_gather_gold()` or seed items for
gold, and a Dock that is only "standing or buildable". `can_gather_gold` includes relics, oysters and
whales with no base. Scenario `easy_resource_sources` overrides (e.g. Attila 3's gold lump) are
authored per scenario and presumably intentional.

## Likely shape of a fix

- Add `logic.units.has_villager_item()` to `_has_base` where the base's villagers have to be
  trained, i.e. where no villagers stand at start. Decide whether `has_vils` should also ask for it
  when the villagers only arrive by training.
- Add `& scenario.has_base()` to the raw-food half of `_food_easily`, matching gold and stone.
