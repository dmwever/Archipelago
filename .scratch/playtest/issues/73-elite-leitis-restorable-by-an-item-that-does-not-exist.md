# 73: Own Elite Leitis is in logic behind a tech item the seed never creates

**Reported:** 2026-11-02, playtesting

**Status:** needs-triage

## Report

Own Elite Leitis is in logic for Genghis 5 with the Leitis Line item, but the units get
cavemanified.

## Reproduced

Built a world with caveman on, unitsanity `all`, techsanity `all`, all three campaigns:

```
ELITE_LEITIS.upgrade_tech    : 3800
pool.techs.includes(3800)    : False
pool.units includes LEITIS   : False
pool.units includes E. LEITIS: True
can_restore(ELITE_LEITIS)    : Has('Leitis Line')
survives_caveman(E. LEITIS)  : Has('Leitis Line')
G5 is_granted(E. LEITIS)     : HasAll('Genghis Khan, The Promise: Hermit Monks', 'Leitis Line')
```

Logic therefore says: hold the Hermit Monks mercenary and the Leitis Line item, and Own Elite
Leitis is reachable in Genghis 5. The Elite Leitis arrive as ten soldiers of
`AP_GENGHIS_5_HERMITS` (4018).

## The game requires an item that was never made

The installed table has exactly **one** row on line 868:

```
addUnit(441, 1236, 868, 28, 1, 3800, 0);
addUnitItem(1236, 368);
```

Elite Leitis, tier 1, `upgradeItemId` **3800**. The base Leitis (1234) is absent, because no
scenario civilisation trains it - `pool.units.includes(LEITIS)` is False - so the line has no
lower tier at all.

`cavemanTarget` walks the line for the highest tier at or below the original that passes
`technologyUnlocked`:

```xs
bool technologyUnlocked(vector unit) {
    if (structGetBool(unit, "locked")) return (false);
    if (AP_TS_MODE == TECHSANITY_NONE) return (true);
    int itemId = structGetInt(unit, "upgradeItemId");
    if (itemId < 0) return (true);
    return (TechItemReceived(itemId));
}
```

This install runs `AP_TS_MODE = 3`, so it falls through to `TechItemReceived(3800)`. **Item 3800
is not in the pool**, so it can never be received, `technologyUnlocked` is false forever, the
only row on the line is rejected, `bestTypeId` stays -1, and `cavemanTarget` falls through to
`CAVEMAN_MILITIA`.

So every Elite Leitis becomes a Militia, always, and Own Elite Leitis cannot be checked.

## The asymmetry

The two sides disagree on exactly one case: an upgrade tech that is **not in the pool**.

| | behaviour when the tech is absent from the pool |
| --- | --- |
| `UnitLogic.can_restore` | drops the tech requirement - `if tech is None or not pool.techs.includes(tech): return has_unit_items(unit)` |
| `technologyUnlocked` | has no equivalent escape - the row still carries `upgradeItemId 3800` and demands an item that does not exist |

The row builder is where they part company. `client/handlers/install/UnitData.py`:

```python
def upgrade_item_for(self, unit):
    tech = unit.upgrade_tech
    if tech is None or tech.item is None:
        return self.NO_UPGRADE_ITEM
    return tech.item.id
```

It guards `tech is None` and `tech.item is None` but **not** "the tech is not in the pool", which
is the guard `can_restore` has.

## The fix

Make `upgrade_item_for` return `NO_UPGRADE_ITEM` when the tech is not in the pool. The installed
row then carries `-1`, `technologyUnlocked` returns true on the `itemId < 0` branch, caveman
keeps the Elite Leitis on the Leitis Line item alone, and the game matches what logic already
promises. It needs the pool reachable from that method, which is worth checking before costing
it.

The alternative - making `can_restore` return `False_()` when the tech is not pooled - matches
the game but strands the unit: with no lower tier on the line and no obtainable tech item, Own
Elite Leitis would become unreachable everywhere rather than just here.

## Scope

This is not Leitis-specific. Any unit whose row is created by a **grant** while its upgrade tech
is outside the pool hits the same wall. A sweep comparing each installed row's `upgradeItemId`
against `pool.techs.includes` would list the rest; the Hermit Monks roster is simply where it
surfaced.

Severity: reachable in logic, impossible in game, so it can strand a seed.

## Comments
