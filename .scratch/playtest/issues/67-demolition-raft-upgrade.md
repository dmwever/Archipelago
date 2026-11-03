# 67: Demolition Raft does not upgrade to Demolition Ship

**Reported:** 2026-11-02, playtesting

**Status:** needs-info

## Report

The Demolition Raft does not upgrade to a Demolition Ship even with the item.

## How the upgrade is meant to work

It is a **real research**, not a free age upgrade. From `empires2_x2_p1.dat`, tech **905
"Demolition Ship"**:

| | |
| --- | --- |
| cost | 25 wood + 75 gold |
| research location | 45 (Dock), 20 seconds, button 13 |
| required techs | **102** (Feudal Age) and **605** ("Demo Galley (make avail)") |
| effect | 912 |

The installed line in `UnitData.xs` is consistent with that:

```
addUnit(421, 1104, 858, 26, 0,   -1, 0);   Demolition Raft,       tier 0, no upgrade item
addUnit(351,  527, 858, 27, 1, 3842, 0);   Demolition Ship,       tier 1, upgrade item 3842
addUnit(352,  528, 858, 28, 2, 3680, 0);   Heavy Demolition Ship, tier 2, upgrade item 3680
addUnitItem(1104, 358);                    the line unlock sits on the raft only
```

Note `upgradeItemId` is read in exactly one place - `Caveman.xs:144`, to decide which tier
caveman drops a unit to. Unitsanity stores it and never consults it. So nothing in the unitsanity
layer gates the raft becoming a ship; the **tech** is the whole mechanism.

## Which item was held?

Two different items could be meant, and they do different things:

| item | id | what it does |
| --- | --- | --- |
| `UNIT_LINE_DEMOLITION_RAFT` | 358 | unlocks the line so the raft can be trained |
| `TECH_DEMOLITION_SHIP` | 3842 | the upgrade research itself |

Only 3842 upgrades anything. This needs answering before the rest can be narrowed.

## Two verified findings, either way

### A stripped tech is a noop, not a lock

```xs
void stripTech(vector tech) {
    xsEffectAmount(cModifyTech, structGetInt(tech, "id"), cAttrSetEffect, 1.0 * NOOP_EFFECT, 1);
}
```

Techsanity does not disable a stripped tech - it swaps the effect for a noop. So the research
button stays on the Dock, still costs 25 wood and 75 gold and still takes 20 seconds, and does
**nothing** when it completes. A player without the item can spend the resources and the time
and see no upgrade, with no feedback saying why.

Whether the item restores the effect afterwards hinges on `tryApplyEffect`:

```xs
bool mustResearch = (AP_TS_BEHAVIOR == BEHAVIOR_MUST_RESEARCH)
                 || structGetBool(tech, "isUpgrade");
...
if (mustResearch && structGetBool(tech, "researched") == false) {
    return;
}
```

An upgrade tech **always** requires `researched`, whatever the behaviour option says. There is a
watcher that records `researched` when it sees a tech reach `cTechStateDone`
(`Techsanity.xs:299`), so a tech researched before the item should in principle be picked up
when the item lands. That path is not verified here, and it is exactly the path a player who
researched early would be on.

### The prerequisite is not recorded

`TechData.xs`:

```
addTech(3680, 244, 233, -1, 1, 0, 28, 1, 905);   Heavy Demolition Ship, prerequisite 905
addTech(3842, 905, 912, -1, 1, 0, 27, 1,  -1);   Demolition Ship,       prerequisite -1
```

The last field is the prerequisite tech id. Heavy Demolition Ship correctly names 905. Demolition
Ship names **none**, while the dat requires **605**. It matches `locations/Techs.py`, where
`DEMOLITION_SHIP` carries `""` as its prerequisite and `HEAVY_DEMOLITION_SHIP` carries
`"DEMOLITION_SHIP"`.

Tech 605 is "Demo Galley (make avail)" - no cost, no research location, so an enabling tech
rather than something a player researches. Whether anything in this project strips or withholds
it is not established. If 605 is ever not done, tech 905 cannot be researched at all, and no
amount of items would change that.

## To narrow it

1. Which item was held - 358 or 3842?
2. Was the Dock research clicked, and did it complete?
3. Was it researched before or after the item arrived?

A sidecar probe reading `xsGetTechState(905, 1)`, `xsGetTechState(605, 1)` and the struct's
`hasItem` / `researched` / `effectDone` would answer all three in one run.

## Comments
