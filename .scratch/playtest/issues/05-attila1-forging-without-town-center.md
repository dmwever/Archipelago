# 05: Attila 1 Forging is in logic without being able to afford a Town Center

**Reported:** 2026-10-19, playtesting

**Status:** needs-triage

## Report

In Attila 1, Research Forging is in logic though the player cannot afford a Town Center.
`/explain` (abridged):

```
Research Forging in The Scourge of God (Attila the Hun 1)
    Researches it at the Blacksmith in the Feudal Age -> True
        Can research Forging -> True
            Has Feudal Age -> True
            Has a Town Center to work from -> True
            Any 2 of -> True
                Has a Mining Camp ... Can build a Mining Camp -> False
                Has a Dock ... Can build a Dock -> True
                Has a Mill, standing or buildable -> True
                Has a Lumber Camp, standing or buildable -> False
                Has a Barracks, standing or buildable -> False
            Has a Blacksmith, standing or buildable -> True
        Can easily gather food -> True   (10000 food expected)

The Scourge of God: Has a Town Center to work from -> True
    Any of -> True
        Has Bleda's Camp -> False
        All of -> True
            Has Builder -> True
            Has villagers -> True
```

## Audit (from code)

`ScenarioBuildingLogic.has_tc` (`logic/scenarios/ScenarioBuildingLogic.py:49-56`) is
`standing | can_build_tc()`, and `can_build_tc` is structural only: build permission plus
`has_builders()`. Nothing pays the Town Center's 275 wood / 100 stone.

`ScenarioLogic.has_base` (`logic/ScenarioLogic.py`) does pay for it — where no TC stands, it asks
for the `TOWN_CENTER_WOOD` and `TOWN_CENTER_STONE` items. `has_tc` doesn't share that, and it is
what the age climb uses (`ScenarioAgeLogic._climb_rule`, `& self.scenario.buildings.has_tc()`), so
every age, and every tech behind an age, inherits the unpaid TC.

In this seed Attila 1 has no Bleda's Camp, so villagers come from Attila's Camp / Roman Villagers,
and both Lumber Camp and Mining Camp are unbuildable — no wood or stone income at all.

The same trace shows a wider pattern: the "Any 2 of" age-up buildings (Dock, Mill) and the
Blacksmith are "standing or buildable" without paying their wood either, and only Forging's own
food cost is checked. With no wood income, none of them could actually go up.

## Likely shape of a fix

Make the built path of `has_tc` pay the way `has_base` does (TC wood + stone items, or
`can_pay(TOWN_CENTER.cost)`), and check whether `has_building`'s buildable path should ask for the
building's cost wherever it feeds a research or age-up.
