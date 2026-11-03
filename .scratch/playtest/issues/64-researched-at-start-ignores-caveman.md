# 64: researched_at_start grants upgrade techs that caveman withholds

**Reported:** 2026-10-31, playtesting

**Status:** needs-triage

## Report

"Man-at-Arms trains it at the Barracks" expects the player to start with the upgrade, even
though under caveman the player does not have Man-at-Arms unlocked. The "starts with it"
reasoning does not handle caveman.

## The two sides disagree by exactly one guard

**The game** withholds upgrade techs under caveman. `Techsanity.xs`,
`reconstructStartingState`:

```xs
if (civCanResearch(tech) && structGetInt(tech, "age") < vanillaAge) {
    bool grant = true;
    if (AP_US_CAVEMAN == 1 && structGetBool(tech, "isUpgrade")) {
        grant = false;
    }
    ...
```

**Logic** does not. `logic/scenarios/ScenarioTechLogic.py`:

```python
def researched_at_start(self, tech: Age2TechData) -> bool:
    """The scenario researched it for itself: it belongs below the age the scenario opens in,
    and it is not withheld."""
    return (tech.age < self.scenario.scenario.vanilla_age
            and not self.world.pool.techs.locked_at_start(tech))
```

Both key on the same test - the tech's age is below the scenario's opening age. The game then
excludes upgrades when caveman is on; logic has no equivalent. And the "withheld" half does not
cover it either: `TechPool.locked_at_start` only inspects the **Existing Techs** option
(`find_items`, `start_in_dark_age`, `only_find_units`) and never looks at caveman.

`tech.is_upgrade` exists on the Python side too - `items/Items.py:57` - and
`client/handlers/install/TechData.py:86` is what writes it into the table the XS then reads. So
the field the game branches on is already available to logic.

## Where it leaks

`has_upgrade_tech` (`ScenarioUnitLogic.py:78`) short-circuits on it:

```python
if self.scenario.techs.researched_at_start(tech):
    return True_()   # the scenario researched it for itself, so the tier is upgraded
```

`has_upgrade_tech` feeds `ScenarioCanTrain`:

```python
return (scenario.logic.units.has_unit_items(self.unit)
        & scenario.units.has_upgrade_tech(self.unit)
        & somewhere & scenario.ages.has_reached(self.unit.age))
```

So for any scenario opening in Feudal or later, logic believes the Man-at-Arms upgrade is
already researched and lets `can_train(MAN_AT_ARMS)` through, while the game under caveman never
granted it.

Four call sites share the fault, so the fix belongs in `researched_at_start` or
`locked_at_start` rather than at any one of them:

| site | what it decides |
| --- | --- |
| `ScenarioUnitLogic.py:83` `has_upgrade_tech` | whether the tier is trainable |
| `ScenarioUnitLogic.py:74` `upgraded_away` | whether a lower tier is gone, which **removes** training options |
| `ScenarioTechLogic.py:56` `_has_researched` | whether the tech counts as held |
| `explain/Explainer.py:703` | what /explain shows |

`upgraded_away` is worth a second look: it returns **True** when the tech is researched at
start, which prunes the lower tier. Under caveman the lower tier is exactly what the player
still has, so the error there points the opposite way from the training one.

## Severity

The training leak is too-generous: logic offers a Man-at-Arms the game will not train, so a
location gated behind fielding one can be unreachable. That direction can strand a seed.

## Note on the first branch

`has_upgrade_tech` also returns `True_()` when `not self.world.pool.techs.includes(tech)`, which
is every tech when techsanity is off. Whether that branch needs the same caveman guard depends
on what the game does with upgrade techs when techsanity is off, which is not established here.

## Comments
