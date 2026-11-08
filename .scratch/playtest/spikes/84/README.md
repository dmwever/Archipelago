# 84: can any XS query see a Wonder foundation?

[#84](../../issues/84-wonder-foundation-is-never-tracked.md) deduced, from a real `PT82_G3W` run,
that `xsGetPlayerUnitIds(owner, WONDER, ...)` does not return a Wonder that is still a foundation.
A deduction from two behaviours is not a reading. Its first ruling is **probe first**, before any
detection route is committed to, and this is that probe.

It is a layer-2 question in the [#78](../78/README.md) sense: `XsTesting` can answer it with no
real scenario and no eye. The harness is the same one, extended - `Test.xs` in the live xs folder,
sidecar format `AP78` **version 2**, one new case `CASE_FOUNDATION` (13).

## What it stages

Four stages, about twenty seconds, with the completed Wonder as its own control so both readings
come out of one run:

| stage | state |
| --- | --- |
| 1 | a Wonder **foundation** for P2 (`xsCreateUnit(WONDER, 2, pos, true, …)`), threat armed |
| 2 | and a **completed** Wonder for P2 forty tiles away |
| 3 | and `RevealAround` called on the foundation's own position |
| 4 | and a second foundation out in the fog carrying the real `RevealFootprint` grid, with a lone line-of-sight 1 revealer twenty tiles from it |
| 5 | and the first foundation's build points driven to `cTrainTime` |

Stage 4 is the only part a person has to look at, and it is there because **line of sight is a
radius, not a square**. The grid in `VictoryThreats.xs` places one revealer per footprint tile
precisely so that it covers the footprint whichever shape the engine rasterises a radius-1 reveal
to - but how far it bleeds past the construction site is a measurement, and fog cannot be read
from script. The lone revealer beside it makes that shape countable on its own.

At every stage it records, for the foundation and for the completed Wonder side by side:

| probe | what it tells us |
| --- | --- |
| `xsGetPlayerUnitIds(2, WONDER)` | whether an object-id query sees a foundation - the query `ScanOwnerWonders` uses today |
| the same by `cBuildingClass`, `cMiscBuildingClass`, `cFlagClassBuilding` | whether a class query sees what the object-id query misses |
| `xsGetObjectCount(2, WONDER)` vs `xsGetObjectCountTotal(2, WONDER)` | the docs say `…Total` counts "alive/standing + queued/foundation"; if that holds it is a *detector*, but it hands back no id |
| `xsGetUnitBuildPoints` and `IsWonderComplete` on each id | separates "found but incomplete" from "not found" |
| `FindWonderSlot` on each id | whether `WonderThreatWatch` tracked it - the mod's own answer, not just the engine's |
| `RevealAround` at the foundation's tile | whether the reveal half works there at all, independently of whether the foundation was found |
| `xsGetUnitPosition` on the foundation | whether a reveal can be placed on it |

Each query has its own scan array and its own cached size, so a refused query reads **-1** and can
never be reported as another probe's number.

## Where it stages things

The map is 120x120, so the harness works off its centre at (60, 60). **P1's Town Center in
`XsTesting` is at (67, 53)**, which is what the staging tiles have to keep clear of - the first
run put a foundation at (68, 68), fifteen tiles from it, and a Wonder under the wide completed-Wonder
reveal swallowed the player's own base.

| what | tile | from P1's TC | from A |
| --- | --- | --- | --- |
| foundation A, the one driven through 0% -> 10% -> complete | (78, 78) | 27 | - |
| completed Wonder B, the control | (96, 78) | 38 | 18 |
| foundation C, left untouched | (40, 70) | 32 | 38 |
| the lone line-of-sight 1 revealer | (40, 50) | 27 | 46 |

B has to stand well clear of A, not just out of the way of the player. A carries a footprint
reveal reaching about three tiles from its centre; B carries the completed-Wonder circle, radius
`THREAT_REVEAL_RADIUS`. At twelve tiles
apart the circle lapped over the construction site and the two reveals read as one patch, so the
separation is now 18, which leaves five tiles of dark between them.

**The compass is not settled.** Each map axis is a diagonal on screen and nothing in the
`aoe2-modding` KB records which. Two sightings here read `+x` as north-east and `-x` as
south-west; the maintainer later described the same axes as north-west and south-west. The note
that had been added to `docs/agent/references/xs-mod.md` is removed again - a wrong compass in the
canonical reference is worse than none.

## Running it

1. No seed is needed. The case reads no `UnitData.xs` or `TechData.xs` row, so any install does.
2. Start `XsTesting` at any speed and leave it alone, about twenty-five seconds. At the stage 4
   chat line, look west: one construction site under the grid, one lone revealer south of it.
3. When the chat turns green - *"AP78 done, file closed"* - quit the scenario so the file flushes.
4. `py -3 read.py`. With no argument it reads `profile/default1.xsdat`.

`read.py` prints the probe table and then a **verdict** block: which queries, if any, returned the
foundation, whether `xsGetObjectCountTotal` counted it, and whether the mod tracked it. It also
asserts the handful of things that have an expectation - the control Wonder enumerates, the
foundation reads incomplete, the footprint matches the dat - so a run that proves nothing says so
instead of printing a table nobody can trust.

`selftest.py` proves the reader without the game: a synthetic good run, one sidecar per possible
detection outcome (nothing sees it / the class query sees it / the object-id query sees it / the
mod tracked it / `…Total` misses it), and six seeded faults plus two malformed sidecars.

```
py -3 selftest.py
```

## Result, 2026-11-07: run 1, 68 records, 8 of 8 assertions pass

**No *typed* query sees a foundation.** `WONDER` by object id, `cBuildingClass` and
`cMiscBuildingClass` all miss it; `cFlagClassBuilding` is refused outright.

**But the untyped one does.** `xsGetPlayerUnitIds(owner, -1)`, filtered on
`xsGetUnitObjectId(id) == WONDER`, returns every Wonder the owner has, foundations included, with
their ids - its count matches `xsGetObjectCountTotal` at every stage (run 3). That is the route
the fix uses, and an id is what makes the footprint reveal possible at all.

**`xsGetObjectCountTotal` does see it.** A foundation appearing moves it +1 and
`xsGetObjectCount` +0; that foundation finishing moves `xsGetObjectCount` +1 and the total +0.
A detector for any owner, scripted or not - but it returns a number, never an id, so there is no
position to reveal. Read it as a step, never as an absolute: `XsTesting` itself ships P2 a Wonder
foundation (unit 546, `status` 0), which sits under every total in the run and confirms the same
result from an object no script created.

**The reveal half works.** `RevealAround` at the foundation's own tile returned a revealer, and
`xsGetUnitPosition` on a foundation reads correctly. `FindWonderSlot` on it is -1 until the tick
its build points reach `cTrainTime`, then 1.

**A line-of-sight 1 revealer lights exactly 3x3** (measured in game, 2026-11-07), but the grid
that matches the construction site was settled by eye, not by arithmetic from that: a
square block of revealers, one per tile, anchored half a tile below the centre
`xsGetUnitPosition` reports. For the 6x6 Wonder that is 4x4, which is now stated outright as
`THREAT_FOUNDATION_ROWS` rather than derived from `cUnitSizeX`. **Corrected 2026-11-08: the
Wonder is 5x5 and the grid is now 5x5, centred.** Both halves of the by-eye result were
compensating for a spike that placed the Wonder half a tile off the grid; see the correction
below. The completed Wonder's circle was
separately rebuilt on the same principle: four `THREAT_REVEAL_RADIUS` revealers in a block at the
Wonder's centre, through the shared `RevealGrid`. Several attempts to derive either geometry -
resizing, recentring, snapping to tile centres, shifting the grid by a tile - all came out wrong;
the reveal is one of the things only a person looking at it can settle.

**The grid is the right shape.** Stage 4's `RevealFootprint` read as "a map revealer the perfect
size for a wonder" on screen - no circle. The maintainer's wide reveal at the first
foundation was *not* seen, because the line-of-sight 1 `RevealAround` calls a stage later
collapsed it: the type-wide `cSetAttribute` inside `RevealAround` re-pins every revealer the
player owns, and the probe's own loose one was in none of the arrays `RepinRevealers` restores.
That is fixed here now too, and it is the review's finding 1 caught in play.

**The counter route was ruled in** on the strength of that, so `read.py` now *asserts* the two
counter deltas rather than printing them: they are what `WatchOwnerFoundations` in
`VictoryThreats.xs` relies on, and a future engine change that broke them would show up here as a
failing row rather than as a warning that silently stopped firing.

Run 3 turned the spike from a question into a regression test: stage 3 now leaves the grid to
the mod, and `read.py` asserts that a foundation reaches a slot. Full write-up in the ticket.

## What was settled without the game

**`empires2_x2_p1.dat` is on this machine**, under the Steam install at `resources/_common/dat/` -
#84 and [spike 82](../82/README.md) both recorded that it was not.

```
kit dat unit <dat> 0 276   ->  WNDR collision_size_x = 2.5
```

**Corrected 2026-11-08: `2 x collision_size_x` IS the tile footprint, and a Wonder is 5x5.**

This file previously said the rule gives 5 but a Wonder occupies 6x6, measured in game on
2026-11-07. The measurement was wrong, not the rule. `runFoundationCase` created the Wonder at
`xsVectorSet(1.0 * (spotX + 18), 1.0 * (spotZ + 18), 0.0)` - whole integers, a tile *corner*. A
building whose half-extent is 2.5 has to sit on a tile *centre* to align to the grid, so the
spike's Wonder was half a tile off on both axes and covered part of six columns and six rows.
What was measured was the misplacement, not the building.

The rule matches every building whose size is independently known - House 1.0 (2x2), Barracks
and Monastery 1.5 (3x3), Town Center and Castle 2.0 (4x4) - and it matches the Wonder as well.
A half-integer half-extent means an odd footprint, which means the building belongs on a tile
centre; an integer one means an even footprint and a tile corner. That is the thing to carry
forward.

Take the footprint from the dat. Check placement before trusting anything measured off a spike.

## What it still cannot answer

- **Whether a Wonder the AI or a villager starts behaves like `xsCreateUnit(…, foundation: true)`.**
  The probe stages a foundation the only way XS can. If the two differ, only a real scenario shows
  it - and `PT82_G3W` already stages one.
- **The reveal itself.** Fog is a visual, and map revealers are not enumerable, so `read.py`
  records the revealer ids and leaves the lit ground to an eye. Stage 4 is built to make that
  look take seconds rather than a playthrough.
