# 11: Khan shows up as trainable at the Castle

**Reported:** 2026-10-20, playtesting

**Status:** needs-triage

## Report

A Khan appears in the Castle's train menu.

## Audit (from code, not verified in game)

Khan is `Age2HeroData.KHAN` (location 604, unit 1275, `locations/Heroes.py:39`: "scenario-only unit,
not a hero"). The installed `UnitData.xs` gives it the same kind of row as every hero and escort
unit (locations 584–605, `UnitData.xs:266-283`):

```
addUnit(604, 1275, -1, 25, 0, -1, 1);   // no line, Dark Age, caveman-exempt, no items
```

What happens to such a row in `Unitsanity.xs`:

1. `addUnit` sets `"trainable"` to true by default (`:68`). Only `addUnitUntrainable` clears it, and
   the client writes no untrainable entries for a granted-only row
   (`client/handlers/install/UnitData.py`, `unit_row` → `is_granted_only` passes `()` for
   untrainable civs).
2. `InitUnitsanity` hides it (`setUnitHidden(unit, true)`).
3. The first `refreshUnitLocks` finds it locked with no items, so it counts as having all of them,
   and unhides it: `setUnitHidden(unit, false)` → `setUnitDisable(unit, 0.0)`.
4. `setUnitDisable` (`:141-155`): Dark Age reached and `trainable` true → `enable = true` →
   `cEnableObject` on 1275.

`cEnableObject` makes the unit available to player 1. Khan has a Castle train slot in the game data,
so it shows up there.

Every hero/escort row goes through the same path; the Khan is just the one whose data has a train
location. Any granted-only row whose unit has a train button would do the same, for any civ.

## Likely shape of a fix

Granted-only rows must never be enabled, only un-disabled. Either have the client mark them
untrainable for every civ, or have the XS skip `cEnableObject` for rows with no line
(`lineId < 0`). Note that the `cDisabledFlag` reset to 0 also matters, if a scenario relied on the
unit staying disabled.
