# 80: does installing the unit table in tier order fix #74 on its own?

[#74](../../issues/74-skirmishers-train-elite-without-the-research.md)'s root cause is
registration order: the engine binds a shared train button to the **first** unit enabled into it,
and `refreshUnitLocks` walks the unit table in installed order. Where an upgraded tier registers
before its base, the button binds to the upgraded unit.

The committed fix (`7584f72`) attacked the symptom: never `cEnableObject` a row with `tier > 0`.
That strands any row whose line has no tier-0 member in the seed, which is
[#80](../../issues/80-camel-rider-stranded-by-the-tier-0-enable-gate.md) — Mongols' Camel Rider.

**This spike tests the other direction**: install the rows in `(line, tier)` order so the base
always registers first, drop the gate entirely, and see whether the button binds correctly on its
own. If it does, `7584f72` can be reverted and #80 never exists.

## Why the order is wrong today

`InstallHandler.UnitData.rows()` returns `list(out.values())`, which is `places()` order. Six of
this seed's 36 lines come out with an upgraded tier ahead of its base:

```
line 802  Elite Skirmisher(t1) before Skirmisher(t0)
line 832  Hussar(t2), Scout Cavalry(t0), Light Cavalry(t1)
line 833  War Galley(t1), Galleon(t2), Galley(t0)
line 857  Fire Ship(t1), Fast Fire Ship(t2), Fire Galley(t0)
line 858  Demolition Ship(t1), Heavy Demo(t2), Demolition Raft(t0)
line 869  Capped Ram(t1), Siege Ram(t2), Battering Ram(t0)
```

Line 884 (Camel Rider, Heavy Camel Rider) is **not** in that list — it is already "sorted"
because it has no tier-0 row at all. That is the same fact #80 turns on.

The real fix, if the spike holds, is one line in `client/handlers/install/UnitData.py`:

```python
return sorted(out.values(), key=lambda row: (row.line_id, row.tier))
```

Python's sort is stable, so rows within a line keep their relative order.

## What this spike changes

Three edits, all reversible. **None of them is a fix — do not commit them.**

| what | how to undo |
| --- | --- |
| `UnitData.xs` rows reordered by `(line, tier)` | `py -3 reorder_unitdata.py --restore` |
| `Unitsanity.xs` gate reverted to pre-`7584f72` | `git checkout -- "age 2 files/resources/_common/xs/Unitsanity.xs"` in Ageipelago |
| `Test.xs` opens a train-menu spike after the layer-2 harness | it is gitignored; the layer-2 harness still runs first and still writes its sidecar |

`reorder_unitdata.py` keeps its own backup at `UnitData.xs.preorder`. Re-running `/install`
would overwrite the reorder, so do not re-install between now and reading the result.

## Running it

**Set `XsTesting`'s P1 civ to Mongols first.** The Stable question needs it:
`addUnitUntrainable(329, …)` names Huns and Franks, so only Mongols can train the Camel Rider.
The Archery Range question works on any civ — neither Skirmisher nor Elite Skirmisher is
restricted in this seed.

Boot `XsTesting`. The layer-2 harness runs as before and closes its sidecar. Then the spike
delivers the skirmisher and camel line items, places an Archery Range and a Stable at the map
centre, and prints the two questions in chat. Click each building and read the train menu.

## The two questions

| building | expected if ordering is enough | expected if it is not |
| --- | --- | --- |
| **Archery Range** | **Skirmisher** — base bound first, Elite Skirmisher enabled but unbound and its research still unresearched | Elite Skirmisher, meaning first-enabled-wins is wrong and a gate is needed |
| **Stable** | **Camel Rider** — enabled normally with no gate, and bound ahead of Heavy Camel Rider | nothing offered, meaning the enable did not reach it; or Heavy Camel Rider, meaning order does not decide binding |

## How to read the result

- **Skirmisher and Camel Rider.** Ordering is the whole fix. Revert `7584f72`, sort in the
  installer, close #80, and #74's criteria are met without a gate.
- **Skirmisher but no Camel Rider.** Ordering fixes #74 but something else blocks a headless
  line. The gate is not the cause, so #80 needs a different answer.
- **Elite Skirmisher.** "First enabled wins" is wrong, the reorder cannot work, and the gate —
  or the `lowestTierOnLine` predicate in #80 — stays.

## Result, 2026-11-06: the hypothesis is disproved

| building | seen | expected if ordering were enough |
| --- | --- | --- |
| Archery Range | **Elite Skirmisher** | Skirmisher |
| Stable | **Camel Rider** | Camel Rider |

Base-first ordering does **not** fix the train button. Skirmisher (tier 0) was registered and
enabled before Elite Skirmisher (tier 1), and the Archery Range still bound to Elite Skirmisher.
Tier order is not the lever, and the installer does not need to sort.

### This corrects #74's model

[#74](../../issues/74-skirmishers-train-elite-without-the-research.md) records under *Established*:

> The engine binds a shared train button to the first unit enabled into it, and
> `refreshUnitLocks` walks the unit table in registration order.

The first half is wrong. The base was enabled first here and did not win the button. The eight
lines #74 identified were a real correlation with registration order, but order is not the cause.

What the engine actually does is still unknown, and one observation argues against the obvious
replacement theory. If the rule were "the most upgraded enabled tier wins", the Stable should
have shown **Heavy Camel Rider** (tier 2, age 28, enabled at Imperial, trainable by Mongols).
It showed Camel Rider. So it is neither first-enabled nor highest-tier. That is worth knowing but
does not block the fix.

**Caveat on this run.** The harness climbs to Imperial Age, so every upgraded tier is age-reached
and enabled. The spike therefore tests the most permissive case. It cannot tell us how the
binding behaves when an upgraded tier's age has not been reached.

### It validates #80's predicate in both directions

With the gate removed, the run shows exactly the two behaviours the proposed predicate is built
to separate:

- **Camel Rider appears.** Its line has no tier-0 row, so with no gate it is enabled and bound.
  This confirms the gate is what strands it — #80's diagnosis, now engine-verified rather than
  inferred from the table.
- **Elite Skirmisher appears.** Its line has a tier-0 row, so it must stay gated or #74 returns.

So the fix is to gate on *"is this the lowest tier present on its line, with no upgrade tech to
free it"* rather than on `tier == 0`. The spike shows both halves are needed: drop the gate and
#74 returns, keep `tier == 0` and Camel Rider stays stranded.

`7584f72` stays. The reorder and the gate revert were undone after the run.

## Run 2: does the gate actually fix the Archery Range?

Run 1 only ever looked at the train menu with the gate **removed**. Nobody has looked at it with
the gate **in**. So the premise this whole ticket rests on — that `tier == 0` makes the Archery
Range offer Skirmisher — is still unverified. If it does not, option 3 is dead and #80's
predicate is pointless, because the predicate keeps the gate for exactly these rows.

Run 2 is the same two buildings in the shipped configuration.

| what | state |
| --- | --- |
| `Unitsanity.xs` | the committed `tier == 0` gate, restored |
| `UnitData.xs` | the installed order, restored |
| `Test.xs` | `SPIKE_TRAIN_MENU = 1`, so the spike runs at boot |

`Test.xs` now has a mode switch at the top. `SPIKE_TRAIN_MENU = 1` places the two buildings
immediately and skips the eight layer-2 cases. Set it back to `0` to run the layer-2 harness and
write the sidecar.

### What each answer means

| Archery Range | Stable | reading |
| --- | --- | --- |
| **Skirmisher** | **neither** | the gate works and strands Camel Rider — #80's predicate is right, and it is the whole fix |
| **Skirmisher** | Camel Rider | the gate works and does *not* strand Camel Rider, so #80 is wrong and nothing needs changing |
| **Elite Skirmisher** | either | **the gate does not work at all.** Option 3 is dead. #74 needs option 1 (gate on the upgrade tech having been applied) and #80 becomes moot |

The third row is the one worth the boot. Everything downstream assumes it cannot happen, and
nothing has tested it.

### Result, run 2: the gate works, and #80 is wrong

**Archery Range offered Skirmisher. Stable offered Camel Rider.** Both correct, with the shipped
gate in place — and the second is the case #80 said was impossible.

The mechanism #80 missed is that `cEnableObject` is not the only route to availability.
`setObjectDisable` clears the AP disabled flag for **every** row, whatever its tier, and only the
enable is gated:

```xs
xsEffectAmount(cSetAttribute, objectId, cDisabledFlag, disableFlag, 1);
if (enable) { xsEffectAmount(cEnableObject, objectId, cAttributeEnable, 1.0, 1); }
```

Once the flag is clear the **vanilla tech tree decides**, which is what the gate was built to
defer to. Mongols have Camel Rider natively from Castle Age, gated by age, so it appears without
an enable. Elite Skirmisher is gated in vanilla by its own research, which is unresearched, so it
does not. The headless line and the missing `upgradeItemId` turn out to be irrelevant.

`7584f72` stands as written. #80 is closed as wontfix, and the `lowestTierOnLine` predicate is
withdrawn.

## Run 3: do upgrades still reach the button?

The gate means `cEnableObject` never fires for a `tier > 0` row. Run 2 shows that is right while
the upgrade is unresearched. It says nothing about what happens **after** the upgrade is
researched — and if the upgraded unit never reaches the button, the gate trades #74's bug for a
worse one.

Three lines, chosen to cover the shapes that differ:

| line | shape | steps |
| --- | --- | --- |
| 802 skirmisher | installed upgrade-first, the line #74 was filed on | Skirmisher -> Elite Skirmisher (tech 98) |
| 884 camel | headless, so the upgrade is tier 1 -> tier 2 | Camel Rider -> Heavy Camel Rider (tech 236) |
| 800 archer | ordinary, and the only one with two upgrade steps | Archer -> Crossbowman (tech 100) -> Arbalester (tech 237) |

Spearman was the obvious fourth but Halberdier is Mongol-disabled, and Mongols are needed for the
camel line, so the archer line carries the "normal unit" question instead.

`Test.xs` runs three phases, 30 seconds apart, so one boot answers all of it:

1. Line items only. Expect Skirmisher, Archer, Camel Rider.
2. Elite Skirmisher, Heavy Camel Rider and Crossbowman researched, each with its tech item
   delivered first. Expect all three buttons to move up one tier.
3. Arbalester researched. Expect a second step on the same line.

Each upgrade is applied the real way — `UnlockTech` then the research — so techsanity's shadow
applies the effect, exactly as `#72` verified in layer 2.

**If any button fails to move, the gate is not safe** and #74 needs option 1 from its brief:
enable on the upgrade tech having actually been applied, rather than never enabling.

### Result, run 3: upgrades always reach the button

Every line moved up a tier when its upgrade was researched — the skirmisher line, the headless
camel line, and the archer line across two steps. The gate costs nothing. `7584f72` is correct
and #74's mechanism is settled.

## Run 4: the whole table, as a rule rather than three samples

Three lines is a sample. This run checks all 34, to show the behaviour is a rule.

The rule under test, in one sentence: **a line's train button shows the highest tier the civ can
reach with what is researched, and nothing the civ cannot reach** — because `setObjectDisable`
clears the disabled flag for every row and leaves the rest to vanilla.

`expected_menus.py` prints the prediction from `UnitData.xs` and `TechData.xs` alone — no dat, no
train-location lookup. A line shares one train button, so one line is one thing to look at. The
current seed's prediction is saved beside it in `expected_mongols.txt`:

- **17 lines should change unit** between the phases.
- **9 should stay put** (single-tier lines).
- **8 should stay empty** (no tier the civ can train).

The strongest rows are the ones that stop short of the top, because they can only be right if
vanilla's civ gating is doing the work rather than ours:

| line | ladder | phase 2 should show |
| --- | --- | --- |
| 817 | Spearman -> Pikeman -> Halberdier(not Mongol) | **Pikeman**, not Halberdier |
| 809 | 38 -> 283 -> 569(not Mongol) | **283** |
| 934 | 2626 -> 2627 -> 2628(not Mongol) | **2627** |
| 884 | Camel Rider -> Heavy Camel Rider | **Heavy Camel Rider**, from a line with no tier 0 |
| 868 | Elite Leitis(not Mongol) | **nothing** |

### Running it

Set `SPIKE_TRAIN_MENU = 2` in `Test.xs` (already set). Boot `XsTesting` as Mongols.

1. Phase 1 delivers **every** unit item by walking the installed table in XS, and places a
   Barracks, Archery Range, Stable, Siege Workshop, Castle, Monastery and Dock.
2. After 30 seconds, phase 2 researches **every** upgrade tech by walking `TechData` in XS.

Neither list is hardcoded — the spike reads the same tables `expected_menus.py` reads, so the
prediction and the run cannot drift apart.

`xsCreateUnit` places a Dock on land, so the ship lines are covered in the same run - confirmed
by the maintainer. `XsTestingWater` is not needed.


### Run 4, first attempt: the harness broke its own prediction

Every line came out at its top tier, boats included. That was the spike, not the game.

`setTechDone` writes `Ready` and then `Done`. The `Ready` write was added for the layer-2 #72
cases, where Siege Ram read `Disabled` for the civ and a direct `Done` was a no-op. But **Ready
bypasses the civ restriction as well as the prerequisites**, so researching every upgrade that
way hands the civ techs it can never research - Halberdier to Mongols, and so on. Every ladder
then runs to the top, which is exactly what was seen.

Two facts make this a harness fault rather than a finding:

- `civCanResearch` tests the **tech's own** civ field, and Halberdier is a common tech with
  `civ == -1`, so it passes. `deferEffect` only withholds *unique* techs, and only when
  `AP_TS_UNIQUES` is `SHUFFLED` (this seed is 1). So techsanity will apply a common tech's effect
  cross-civ once it is held and researched.
- What stops a Mongol in real play is the **engine**: a civ-disabled tech never reaches `Done`,
  so `onTechResearched` never fires. The `Ready` write is the only reason it did here.

`researchEveryUpgrade` now writes `Done` only, so a civ-disabled tech refuses exactly as it would
in play, and it runs five passes so prerequisite chains resolve in any order. It reports how many
upgrades reached `Done` against how many exist; the shortfall should be the civ-disabled ones.

`setTechDone` keeps its `Ready` write for the layer-2 #72 cases, where forcing past the civ is
deliberate and recorded as a caveat.

### The Heavy Warships umbrella, and what it does to the Carrack

One tech in the seed stands for three upgrades:

```
addTech(3622, 35, -1, -1, 1, 0, 28, 1, 34)      effectId -1, the only such row
```

`applyViaShadow` sees `isHeavyWarships` and fires `GALLEON_EFFECT`, `CARRACK_EFFECT` and
`FAST_FIRE_SHIP_EFFECT` together. The component techs 911, 904 and 246 are not in `TechData` at
all, so the umbrella is the only way any of the three lands.

The data already says which rows it drives — they are the rows whose `upgradeItemId` is 3622:

| row | line | unit | Mongols can train it |
| --- | --- | --- | --- |
| 346 | 833 | Galleon (442) | yes |
| 356 | 857 | Fast Fire Ship (532) | yes |
| 598 | 934 | **Carrack (2628)** | **no** |

So researching Heavy Warships as Mongols applies the Carrack effect as well, and line 934 runs
Hulk -> War Hulk -> **Carrack** even though `addUnitUntrainable(2628, 12)` says Mongols cannot
train one. `expected_menus.py` now reads the `effectId == -1` sentinel and marks such rows
`(forced)`, so the prediction matches what the mod actually does rather than what the civ table
alone would suggest.

**Whether the mod should do that is a separate question.** The three effects are hardcoded
constants with no link back to a unit row, so `applyViaShadow` cannot currently tell which of the
three the civ is entitled to. The unit table does know — the rows above carry both the shared
upgrade item and the per-civ trainable flag — so a civ-aware version is possible without new
data. Raised here rather than filed; it is a one-unit cosmetic divergence, not a logic break,
because Own Carrack is not reachable in logic for a Mongol scenario either way.

### Result, run 4: the rule holds across the whole table

Every line matched `expected_mongols.txt` in both phases, boats included. 17 lines moved up a
tier when their upgrades landed, 9 stayed put, 8 stayed empty, and the lines that should stop
short of their top tier did — Pikeman rather than Halberdier on 817, War Hulk rather than Carrack
on 934.

So the behaviour is a rule, not a coincidence of the three lines sampled in run 3:

> A line's train button shows the highest tier the civ can reach with what is researched, and
> nothing the civ cannot reach.

`setObjectDisable` clears the disabled flag for every row and `cEnableObject` fires only for
tier 0; everything above that is vanilla's decision. `7584f72` is correct, #80 is closed, and
#74's mechanism is settled for a techsanity-`all` seed.

**Not covered by this sweep:** techsanity off, where no tech item exists and the upgrade is
researched normally. That arm of #74's criteria is still untested.

## The relic threat, rebuilt on attribute 55

`EnableRelicThreat()` has no caller, so none of this runs in play yet. It is groundwork.

### What the probes measured (spike 78, case 8)

A Gaia relic, a Monk and a Monastery owned by P2, in `XsTesting`. P2's monk captures the relic.

| question | answer |
| --- | --- |
| does `ALL_RELICS_CAPTURED` (55) flip? | **yes** - 0 at t=1, 1 from t=4, for **P2 only**; P1 stayed 0 |
| does it need relic victory switched on? | **no** - re-run with `conquest_required=0`, `mode=4`, same result |
| can a relic be enumerated per owner? | **no** - `cRelicClass` and unit id 285 both read 0 for every player, garrisoned or not |
| `xsGetObjectCount(p, RELIC)`? | **no** - returns -1 |
| `xsGetPlayerUnitIds(0, cRelicClass, ...)`? | **yes** - reads 1 while garrisoned, and after the monastery went |

The last row is the useful one: relics are reachable through the player-0 scan even inside a
monastery, so the threat can reveal **the relics themselves** rather than guessing at buildings.

### Why the old implementation could never have worked

`FindRelicHolder` scanned each player for `cRelicClass` units and resolved each relic's
monastery. A garrisoned relic is in none of those lists, so `relics` stayed 0 and the function
returned -1 at every sample of the whole run. `RevealRelicMonasteries` had the same defect and
would have revealed nothing.

### What changed

The original algorithm was right. Its only defect was **enumeration**: it scanned each player for
`cRelicClass` units, and a relic is in no player's list - loose or garrisoned. So `relics` stayed
0 and `FindRelicHolder` returned -1 at every sample of every run.

`FindRelicHolder` now enumerates with `xsGetPlayerUnitIds(0, cRelicClass, ...)` and keeps the
rest: `FindRelicMonastery` resolves the container, `IsRelicThreatHolder` and
`IsAlliedWithHolders` judge it. `RevealRelicMonasteries` became `RevealRelics`, revealing each
relic from the same scan rather than guessing at buildings - it also no longer assigns the
`-1`-means-unchanged return straight into its array, which the original did.

### Engine-verified, one relic across a full capture and release

```
t=4..34   relic 534 -> unit 499 (MONASTERY/P2)   FindRelicHolder = 2
t=37..58  relic 534 -> loose                     FindRelicHolder = -1
```

`xsGetGarrisonedInUnitId` resolves for a relic found through the player-0 scan, names the
container a Monastery owned by P2, and releases as soon as the building starts dying. The threat
arms and cancels on live possession, which is what it needs to do.

### Attribute 55 is a trap for this purpose

It flips correctly - 0 to 1 for the capturing player only, with relic victory switched off - but
it **never clears**. It stayed 1 for every sample after the monastery was destroyed by damage,
with the relic lying loose on the ground. Used as the hold condition it would pin a countdown
open forever and `CancelRelicCountdown` would never fire. It is a sound trigger and an unsound
predicate, so the mod does not use it; the constant lives only in the spike's `Test.xs`.

Chasing it was still worth it: the player-0 enumeration that fixes the real bug was found while
probing for it.

### Still open

- **Team semantics.** Whether two allied enemies splitting the relics between them should arm the
  threat, and whether `IsAlliedWithHolders` handles it. Needs three or more players.
- **None of this runs yet.** `EnableRelicThreat()` still has no caller.

## The map revealer resists every normal handle

Engine-verified in `XsTesting`, three revealers side by side, one removal method each:

| method | result |
| --- | --- |
| `xsRemoveUnit` | **no effect** - the patch stayed lit |
| hit points to 0 (`cSetUnitAttribute` / `cHitpoints`) | **cleared it** |
| line of sight to 0 | not observable - it sat inside the Town Centre's own sight |

So `RemoveRevealer` now drives hit points to 0. Three separate facts about this object, each
measured rather than assumed, and each one bit at some point:

- `xsGetPlayerUnitIds` cannot enumerate a map revealer, for any player including 0. That is why
  the #60 "Wonder is revealed" check had to become a visual one.
- `xsDoesUnitExist` never reports one as existing. `RemoveRevealer` guarded on it, so the removal
  was skipped and the reveal stayed up for good.
- `xsRemoveUnit` does not clear one either, so dropping the guard was not enough.

### Radius

`MAP_REVEALER` 837 ships with `line_of_sight` 4, and a unit explores its radius the moment it
exists, so setting `cLineOfSight` after `xsCreateUnit` left a permanently explored 4-tile ring
around a 3-tile visible core. `RevealAround` now writes the radius onto the object type before
creating the unit, so it is born at the right size. The relic reveal is `THREAT_RELIC_REVEAL_RADIUS`
3, centred on the holding monastery; the wonder reveal stays at 10.

The dat has six revealer types - `837`/`1774`/`1775` at sight 4/10/20, and `1872`-`1874`, the
same sizes marked TEMP with 0 hit points. **4 is the smallest**, so a 3-tile reveal is only
reachable by writing the attribute; there is no smaller stock object to pick instead.

**Latent trap.** `cSetAttribute` writes the *object type*, so it very likely retunes revealers
that already exist. A relic reveal at 3 firing while a wonder reveal at 10 is standing would
shrink the wonder's. Nothing arms both today - nothing arms the relic threat at all - but if that
changes, giving each threat its own revealer id (`1774` has a natural sight of 10 and needs no
write) closes it.

### The sweep cannot judge civ-restricted top tiers

Run 4 of the sweep showed lines 809 and 817 running past the civ's real top tier - Paladin for
Mongols, Halberdier for Mongols - while 934 stopped at War Hulk. That was the harness, not the
mod, and the earlier layer-2 data already said why:

Halberdier (tech 429) recorded a pre-state of **0, NotReady** - not -1, Disabled. The engine does
not report a tech the civ lacks as Disabled, so the sweep's `Done` write goes through and
`applyViaShadow` applies the real effect. This is the same class of over-forcing as the `Ready`
write that was removed earlier, one level subtler: `Ready` bypassed the civ and the
prerequisites, and a plain `Done` still bypasses anything reporting NotReady.

934 stopped for an unrelated reason - the explicit civ gate added to `applyViaShadow` for the
Heavy Warships umbrella - so it was never evidence that the sweep respects civ restrictions.

`expected_menus.py` now reports the **sweep's** outcome rather than a player's, and lists the
lines where they differ as untestable. In this seed that is exactly two lines, 809 and 817, which
are exactly the two that were observed not to stop. Every other line is a real test of the tier
gate, which is what #74 is about; civ gating is vanilla's job and is not what the sweep measures.
