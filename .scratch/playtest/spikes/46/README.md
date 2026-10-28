# 46: the caveman catalog harness

Harness for [#46](../../issues/46-caveman-catalog-spike.md): what `ApplyCaveman` does to
**every row** of the installed seed's unit table, not just the two rows [#16](../../issues/16-caveman-scenario-ships-and-carts.md)
names.

Built on the `XsTesting` setup from #33, #35 and #10, with one addition: the map needs water.

## The map

`XsTesting.aoe2scenario` is 120x120 and has **one terrain type** — all land. 17 of the 107
catalog rows are ships and cannot be created on it at all, so the run would record them as
untestable.

`XsTestingWater.aoe2scenario` is XsTesting with tiles 90-119 on both axes set to terrain 23
(Water, Medium). It is built from XsTesting by the kit, so it is reproducible:

```bash
K=/c/Users/dmwev/Documents/GitHub/aoe2kit/bin/kit.exe
S="/c/Users/dmwev/Documents/GitHub/Ageipelago/age 2 files/resources/_common/scenario"
$K scen plan  "$S/XsTesting.aoe2scenario" --recipe map-recipe.json
$K scen patch "$S/XsTesting.aoe2scenario" "$S/XsTestingWater.aoe2scenario" --recipe map-recipe.json
$K scen write-check "$S/XsTesting.aoe2scenario" "$S/XsTestingWater.aoe2scenario"
```

The patch reports `map_tiles_changed: 900`, `rebuild_ok: true`, `invariant_ok: true`, and the
output keeps XsTesting's XS wiring (`script_name: Test`, `script_file_path: Test.xs`) and its
two triggers and one unit. Verification label is `structure_verified_not_engine_verified`: the
engine oracle is the run itself, and the run says so — if the water square is wrong, the
Transport Ship probe fails to create and the land/water STAGE lines report `found=0`.

This replaces the untracked `TS_Spike.aoe2scenario` that #35 used. That file is on the
maintainer's disk only and is not in either repo.

## The script

**`Test.xs` in the Ageipelago xs folder is the harness.** There is no copy step and no second
copy in this directory: `XsTesting.aoe2scenario` and `XsTestingWater.aoe2scenario` both run
`Test.xs` by name, so the live file is the only one that matters and staging a copy beside it
only invites running the wrong one. `Test.xs` is gitignored; the run it replaced was spike 10's
run E, which is kept at `../10/TestE.xs`.

Like the #10 harness it does **not** go through `InitAP`, so no client and no seeded scenario
are needed: it calls `initializeStructsScript()`, `InitLocations()`, `InitUnitsanity()`,
`InitCaveman()`, `InitProfessions()`, sets `startupGranted = 1` itself, and then drives the real
`UnitsanityChecks` rule. The installed seed supplies the unit table; nothing is granted at boot,
so every row starts `locked`.

Lint before running, from the xs folder — it must report **0 errors**:

```bash
./xs-check.exe -I . -- Test.xs
```

Two `NumDownCast` warnings on the `xsVectorGetX`/`xsVectorGetZ` reads are expected; that is the
codebase's own float-to-int idiom (`structs.xs:320`). The four `DiscardedFn` and one
`FirstOprArith` warnings come from the library files, not this script.

## What it does

Map positions are `xsVectorSet(x, y, 0.0)` — **x and y are the map axes and the third slot is
unused**, the convention `APavilion.xs:38` and `TrapItems.xs:414` both use. Run 1 used
`(x, 0.0, z)` and put all 107 rows on row 0 of the map; see *Run 1* below.

At boot it finds two spots:

- the **land spot** is the map centre;
- the **water spot** is the first tile on a 16x16 coarse grid whose
  `xsGetMapTileAttribute(x, y, cTileTerrainId)` is 23, the Water, Medium the map paints at
  90-119.

The spot finder reads **terrain**, not unit creation. Run 1 probed by creating a Transport Ship
and asking whether the engine accepted it, and the engine accepted one on grass at (2, 0):
`xsCreateUnit` with `checkCollision = false` ignores terrain entirely. Both `STAGE` lines carry
the terrain id actually found, so the run says whether it had real water.

Then, for all `unitTableCount` rows, **two passes each** — one on land, one on water:

1. on the land pass, write `META` (typeId, lineId, tier, cavemanExempt, locked) and `PREDICT`
   (what `cavemanTarget(typeId)` says it will become);
2. create the unit for P1 at that pass's spot — no fallback, since a fallback only fires when
   the create fails and it never does;
3. wait `SETTLE_TICKS` (4) ticks so the real `UnitsanityChecks` rule gets its pass;
4. write `RESULT`, then remove both the probe and anything that replaced it.

Probing every row on both spots, rather than classifying rows and sending ships to the water,
means the harness never has to know which rows are ships — and it answers "what happens to this
row when it is standing on water" for the land rows too.

## How to read the outcome

`RESULT` carries one of four outcomes:

| outcome | what the run saw | meaning |
| --- | --- | --- |
| `left alone` | the probe still exists, no ledger entry | caveman did not touch this row |
| `swapped` | a unit exists whose ledger original is this row's type | normal cavemanify; `PLACE` says what it became and where |
| `destroyed` | the probe's ledger entry is `CAVEMAN_REMOVED` and nothing replaced it | **`transformUnit` removed the unit and its `xsCreateUnit` failed** |
| `untested` | `xsCreateUnit` refused both spots | the row could not be probed on this map |

`destroyed` is the finding the ticket is chasing. `transformUnit` (`Caveman.xs:186`) removes the
unit and writes `CAVEMAN_REMOVED` to the ledger **before** it creates the replacement, and
returns early if that create fails. A row that lands here is gone for good: the ledger row is
closed, so receiving its unit item later restores nothing.

The replacement is found by scanning P1's units for one whose `originalTypeOf` is this row's
type. Only one row is live at a time, so there is no ambiguity.

## Run 1 (2026-10-28): void for water, good for everything else

`run1-void.xsdat` with `run1-void-ledger.json`. The ledger passed 19206 of 19206 and the footer
was intact, so the file and the harness mechanics are sound. What it settles:

- **107 of 107 rows measured.** 66 swapped, 41 left alone.
- **Every non-exempt row targets Militia at a fully locked table**, exactly as `cavemanTarget`
  predicts. The 41 left alone are the 40 `cavemanExempt` rows plus Militia itself, which targets
  `self`. By class: foot 36/38, siege 13/3, water 17/0.
- **No ship is exempt** — all 17 water rows swapped. That was the .dat prediction and it holds.
- Nothing was `destroyed` and nothing was `untested`.

What it does **not** settle, because of the `(x, 0.0, z)` bug above: every unit, ships included,
was created on grass at row 0. The 17 water rows record a ship on land becoming a Militia on
land. #16's actual question — what happens when the replacement is a land unit asked for at a
water tile — is untouched. That is what run 2 is for.

Note for reading the output: Militia's internal name in the .dat is `SPRMN`, so "predicted
SPRMN" means Militia (74). `PKEMN` is the Spearman (93).

## Run 2 (2026-10-28): the answer

`run2.xsdat` with `run2-ledger.json`: 19206 of 19206 ledger checks, footer intact, 1065 records,
107 of 107 rows probed twice. Land spot (60, 60) terrain 0; **water spot (96, 96) terrain 23**,
so the water pass really was on water.

**Every ship becomes a Militia created on the water tile.** All 17 water rows swapped on both
spots, with the replacement at the probe's own tile — (60, 60) on land, (96, 96) on water.
`transformUnit`'s `xsCreateUnit` never failed for any of the 107 rows on either spot, so the
`destroyed` outcome did not occur at all.

Land and water columns are identical throughout, which follows from `xsCreateUnit` with
`checkCollision = false` ignoring terrain.

Not covered: whether that Militia can move off the water. The harness removes each probe four
ticks after creating it and never issues an order.

## Run and decode

Start `XsTestingWater` at any speed and leave it alone. The chat shows the boot line, then one
line at the end. When it says *AP46 done, file closed*, quit the scenario so the file flushes,
then copy `profile/default1.xsdat` to `spikes/46/run2.xsdat`. The profile file is always
`default1.xsdat`, never named after the script, and it is only flushed when the scenario
unloads.

```bash
py -3 decode.py run2.xsdat
```

`decode.py` looks for `<stem>-ledger.json` beside the file (regenerate with
`py -3 make_ledger.py`, then rename to match the run), joins each row against `catalog.json` for
names and placement class, and prints one line per row with **both** passes side by side, then
the counts by spot and by placement class, and the `destroyed` list.

## catalog.json

The 107 rows of `UnitData.xs` for the currently installed seed, joined against
`empires2_x2_p1.dat` through `kit dat sql`. Per row: `typeId`, `lineId`, `tier`, `age`,
`locationId`, `upgradeItemId`, `cavemanExempt` from the seed, and `name`, `terr`
(`terrain_table_id`) and `place` from the dat.

`place` collapses the nine `terrain_table_id` values in the catalog into the three groups whose
passability rows are identical to each other:

| place | terrain tables | rows | what |
| --- | --- | --- | --- |
| `foot` | 7, 28 | 74 | infantry, archers, monks, cavalry, villagers, foot and mounted heroes |
| `siege` | 20, 29, 31 | 16 | siege, the Trade Cart, the Bombard Cannon, the packed Trebuchet |
| `water` | 3, 13, 15, 30 | 17 | every ship |

The seed's table is **not** fixed: it is whatever `/install` wrote for the yaml. Spike 10 ran
against a 107-row table too, but a different yaml gives a different set. `Test.xs` enumerates
`unitTableCount` at run time and never reads `catalog.json`, so the run is always complete;
`catalog.json` only supplies names for the report, and a row the run reports that is missing
from it decodes as `?`. Regenerate it when the seed changes.
