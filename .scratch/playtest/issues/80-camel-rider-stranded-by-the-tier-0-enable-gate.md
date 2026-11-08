# 80: the tier == 0 enable gate strands Mongols' Camel Rider

**Reported:** 2026-11-06, from spike Q1 of [#74](74-skirmishers-train-elite-without-the-research.md)

**Status:** wontfix (premise disproved in game)

**Related:** [#74](74-skirmishers-train-elite-without-the-research.md) (the gate this is about),
[#78](78-in-game-checks-round-2.md) (the check list), [`spikes/74/README.md`](../spikes/74/README.md)

## Report

Spike Q1 asks whether Mongols' Camel Rider still appears under #74's candidate fix. It does not,
and the installed data says so without booting the game.

`setUnitDisable` now fires `cEnableObject` only for a row with `tier == 0`
(`Unitsanity.xs:204`, commit `7584f72`). Camel Rider is tier 1 and its line has no tier-0 row in
this seed, so nothing ever enables it.

## The chain

From the current install (seed 58234/33548, unitsanity `all`, techsanity `all`, caveman on):

```
addUnit(337, 329, 884, 27, 1, -1, 0);    Camel Rider        tier 1, no upgrade item
addUnitUntrainable(329, 17);             not for Huns
addUnitUntrainable(329, 2);              not for Franks
addUnit(338, 330, 884, 28, 2, 3677, 0);  Heavy Camel Rider  tier 2
```

Line 884 holds those two rows and nothing else. Every route to an enable is closed:

| route | why it is closed |
| --- | --- |
| its own row | `tier == 1`, so the gate skips `cEnableObject` |
| a tier-0 head on the line | line 884 has no tier-0 row — Camel Scout is not in `pool.units` |
| being a variant of an enabled type | `addUnitVariant` never names 329 |
| its upgrade tech promoting it | `upgradeItemId` is -1; there is no upgrade tech for this row |

The seed's civs are 2 Franks, 12 Mongols and 17 Huns. 329 is untrainable for 2 and 17, so
`trainable` is **true for Mongols**, and `ageReached(27)` holds from Castle Age. The row is meant
to be trainable and cannot be. Heavy Camel Rider (330) has an upgrade tech, but it upgrades
Camel Riders that can never exist, so the whole camel line is dead for Mongols.

This is exactly the failure Q1 was written to detect, and Q1's own text says what it means:

> If any run shows no Camel Rider, rule A is not enough.

## Elite Leitis is the near miss, and it is fine

Line 868 has the same shape — one tier-1 row, no head, `upgradeItemId -1` — but
`addUnitUntrainable(1236, ...)` names all three seed civs, so `trainable` is false and
`setUnitDisable` would not enable it with or without the gate. It is granted by the Hermit Monks
mercenary, never trained. Only Camel Rider is actually stranded.

## The fix

The gate's intent is right: an upgraded tier must not be trainable just because its age arrived.
What it gets wrong is treating `tier == 0` as "is the line head". In a seed the pool can leave a
line headless, and then the lowest tier present *is* the head.

Recommended: enable when the row has **no lower-tier row on its own line in the installed
table**, rather than when `tier == 0`. That keeps Elite Skirmisher gated (Skirmisher is present
at tier 0, so it carries the enable), frees Camel Rider, and needs no installer change — the
unit table already holds every line and tier.

The spike's own option B — have the installer mark "has an upgrade tech" and enable those rows —
also works, but it is a second place for the two sides to disagree, which is how
[#73](73-elite-leitis-restorable-by-an-item-that-does-not-exist.md) happened.

Option 1 from #74's brief (enable on the upgrade tech having been applied) does not fix this on
its own: Camel Rider has no upgrade tech, so there is nothing to wait for.

## How it was found

`.scratch/playtest/spikes/78/install_checks.py`, which reads the installed `UnitData.xs` and
`TechData.xs` and asserts the invariants #73 and #74 turn on:

```
[FAIL] #74  no row is trainable, unenableable and has no upgrade tech to promote it
            type 329 (loc 337) trainable for civ [12]
```

Static, so it is a strong prediction rather than an engine-verified result. Q1 in game is still
worth one look at a Mongol Stable, and it is now a sharp question with an expected answer.

## Acceptance criteria

- [ ] A row that is the lowest tier present on its line is enabled when its age is reached and it
      is trainable.
- [ ] A row with a lower tier present on its line is still not enabled by age alone — #74's fix
      holds for the skirmisher, galley, demolition and ram lines.
- [ ] `install_checks.py`'s two #74 rows are re-expressed against the new rule and pass. They
      assert the *data*, which an XS change does not alter, so they must be rewritten rather than
      merely re-run.
- [ ] In game: a Mongol scenario with the Camel line item offers Camel Rider at the Stable in
      Castle Age, and Heavy Camel Rider after its upgrade.
- [ ] In game: Joan 4's Archery Range still offers Skirmisher, not Elite Skirmisher.

## Comments

### Engine-verified, and the predicate is confirmed (2026-11-06)

The maintainer proposed a different fix: install the unit table in `(line, tier)` order so the
base tier always registers first, then revert `7584f72` entirely. Spiked in
[`spikes/80/`](../spikes/80/README.md) by reordering the installed `UnitData.xs`, removing the
gate, and looking at two train menus as Mongols at Imperial Age.

**Result: Stable showed Camel Rider, Archery Range showed Elite Skirmisher.**

That disproves the ordering hypothesis — base-first registration does not win the button — but it
confirms this ticket twice over:

- Camel Rider appears the moment the gate is gone, so the gate is what strands it. This was
  inferred from the installed table before; it is now engine-verified.
- Elite Skirmisher appears the moment the gate is gone, so a row with a lower tier present on its
  line must stay gated or #74 returns.

Those are exactly the two cases the proposed predicate separates, so the fix stands as written:
enable a `tier > 0` row only when it is the lowest tier present on its line **and** has no
upgrade tech that could free it. Dropping either half fails one of the two observations.

The spike also corrects #74's *Established* claim that the engine binds the button to the first
unit enabled. It does not. Nor does it simply take the highest tier — the Stable showed Camel
Rider rather than Heavy Camel Rider, with both enabled. The real rule is still unknown, and the
fix does not depend on knowing it.

### Disproved (2026-11-06)

**The premise is false. Camel Rider is offered with the gate in place.**

Run 2 of [`spikes/80/`](../spikes/80/README.md) placed a Stable and an Archery Range for a Mongol
P1 at Imperial Age, with the shipped `tier == 0` gate and the installed row order. The Archery
Range offered **Skirmisher** and the Stable offered **Camel Rider**. Both are correct, and the
second is the case this ticket said was impossible.

**Where the analysis went wrong.** It assumed `cEnableObject` is the only route to availability.
It is not. `setObjectDisable` clears the AP disabled flag for **every** row, whatever its tier:

```xs
xsEffectAmount(cSetAttribute, objectId, cDisabledFlag, disableFlag, 1);
if (enable) { xsEffectAmount(cEnableObject, objectId, cAttributeEnable, 1.0, 1); }
```

Only the second line is gated. Once the flag is clear, the **vanilla tech tree decides**, and
that is the behaviour the gate was designed to defer to:

- Mongols have Camel Rider natively from Castle Age, gated by age rather than by an upgrade tech.
  Clearing the flag is therefore enough, and `cEnableObject` was never needed.
- Elite Skirmisher is gated in vanilla by its own research, which is unresearched here. Clearing
  the flag does not make it trainable, so it stays off the button.

That is exactly the split `7584f72` intended: stop forcing upgraded tiers available, and let
vanilla gate them. The row's `upgradeItemId` and the headless line turn out not to matter.

**Consequences.** No change is needed in `Unitsanity.xs`. The `lowestTierOnLine` predicate
proposed above is unnecessary and would re-introduce a forced enable for no reason. The two #74
rows in `spikes/78/install_checks.py` assert an invariant that does not exist and are withdrawn.

Closing without a change. The open question that remains is not this ticket's: whether a
researched upgrade still reaches the train button when `cEnableObject` never fires for the
upgraded tier. That is #74's own criteria, and spike 80 run 3 tests it.
