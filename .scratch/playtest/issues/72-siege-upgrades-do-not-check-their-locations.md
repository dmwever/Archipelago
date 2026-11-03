# 72: Siege Ram and Siege Onager upgrades do not check their Own locations

**Reported:** 2026-11-02, playtesting

**Status:** needs-info

## Report

Researching the Siege Ram and Siege Onager upgrades did not instantly check Own Siege Ram and
Own Siege Onager.

## The data is right

Both rows exist with valid location ids, so this is not a missing row:

```
addUnit(343, 422, 869, 28, 1, 3651, 0);   Capped Ram    tier 1
addUnit(363, 548, 869, 28, 2, 3684, 0);   Siege Ram     tier 2   -> location 363
addUnit(364, 550, 825, 28, 1, 3685, 0);   Onager        tier 1
addUnit(376, 588, 825, 28, 2, 3694, 0);   Siege Onager  tier 2   -> location 376
```

`MarkRowOwned` carries no item or visibility guard - it returns early only if the row is already
owned or its `locationId` is below zero - so nothing is filtering these out on the way to
`AP_Check_Location`.

## Why an upgrade is a hard case

An upgraded unit **keeps its unit id** and only changes object type. `collectNewUnits` compares
unit ids against the previous scan, so an upgrade is invisible to the incremental path:

```xs
int passUnits = units;
if (unitsDirty == false) {
    passUnits = collectNewUnits(units);
}
```

The only things that force the full pass that would notice the new type are `unitsDirty`, set in
three places: the research-count watcher (`Unitsanity.xs:453`), `UnlockTech`
(`Techsanity.xs:159`), and a row's `hasAllItems` turning true (`Unitsanity.xs:309`).

## Two candidates

### 1. `checkOwnedUnits` stops at the copy id

```xs
if (MarkOwnedByType(xsGetUnitCopyId(unitId)) == false) {
    MarkOwnedByType(xsGetUnitObjectId(unitId));
}
```

`MarkOwnedByType` returns true if `findUnit` matches **any** row. `xsGetUnitCopyId` returns the
unit's copy id in data, which is a different dat field from the object id. If a Siege Ram's copy
id resolves to a row already in the table - the Capped Ram, say, or the line's base - the first
call succeeds, `found` is true, and the fallback that would have marked **548** never runs.

Neither 422, 548, 550 nor 588 has an `addUnitVariant` line, so `canonicalTypeOf` is the identity
for all four and `MarkOwnedByType`'s `canonical != typeId` branch does nothing to save it.

Against this reading: it would break **every** tier upgrade, not only these two, and only these
two were reported.

### 2. Caveman eats the pass before the check

```xs
unitsTransformed = false;
ApplyCaveman(passUnits);
...
if (unitsTransformed) {
    return;          // before checkOwnedUnits
}
checkOwnedUnits(passUnits);
```

If caveman transforms anything on the same tick, the rule returns before any ownership is
marked. `unitsDirty` stays true so the next tick retries, but a tick that keeps transforming
keeps skipping the check. Siege Ram and Siege Onager are both **tier 2** with an upgrade item
(3684, 3694), which is exactly what `cavemanTarget` looks at.

## To settle it

The question is what `xsGetUnitCopyId` returns for a unit that has just been upgraded. A
throwaway probe answers it: own a Capped Ram, research Siege Ram, and write
`xsGetUnitObjectId`, `xsGetUnitCopyId` and `findUnit` on both for each of P1's units to an
`.xsdat`. If the copy id comes back as the pre-upgrade type, candidate 1 is the cause and the
fix is to mark by object id first, or to mark both rather than stopping at the first hit.

Also worth capturing in the same run: whether `unitsTransformed` was true on the tick the
research completed, which settles candidate 2 at the same time.

## Unverified

Whether the locations checked **late** rather than never. The report says "did not instantly
check"; a delayed check and a missing one have different causes, and the distinction decides
which of the two candidates above is even in play.

## Comments
