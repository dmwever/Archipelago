# 84: a Wonder foundation is never tracked, so nothing reveals it

**Reported:** 2026-11-07, playing `PT82_G3W` for [#82](82-layer-3-in-game-checks.md)

**Status:** done

**Related:** [#60](60-genghis3-jin-wonder-no-threat.md) (the victory threats this belongs to),
[#82](82-layer-3-in-game-checks.md) (the run that found it),
[#81](81-wonder-threat-owner-array-is-one-slot-short.md) (the other `VictoryThreats.xs` bug)

## Report

`VictoryThreats.xs` is supposed to reveal an enemy Wonder the moment it goes up, so the player can
go and destroy it before the countdown runs out. Played on a real scenario, **a Wonder foundation
gets no map revealer at all**. The completed Wonder does.

Two things are wrong, and they are separable.

## 1. The foundation is never tracked

`TrackWonder` creates the revealer unconditionally:

```
xsArraySetInt(wonderSlotRevealers, slot,
              RevealAround(xsGetUnitPosition(unitId), THREAT_REVEAL_RADIUS));
```

so if the foundation reached `TrackWonder`, a revealer would exist. `RevealAround` demonstrably
works - the completed Wonder at (167,165) got one in the same run, same owner, same call site.
The only variable between the two is whether `ScanOwnerWonders` found the object:

```
wonderScan = xsGetPlayerUnitIds(owner, WONDER, wonderScan);
```

**So `xsGetPlayerUnitIds(owner, WONDER, ...)` almost certainly does not return a foundation.**
That is a deduction from the two behaviours, not something anyone has read off a probe, and it
should be confirmed before anything is built on it.

It is worth more than the reveal. Until the foundation is tracked, the mod does not know a Wonder
is being built at all: no slot is claimed, no revealer, no warning. The countdown still works,
because it starts on completion, when the object does enumerate.

### Confirming it cheaply

This is a layer-2 question, not a layer-3 one - `XsTesting` can answer it without a real
scenario. Create a Wonder foundation for P2, then record, for the same object:

| probe | what it tells us |
| --- | --- |
| `xsGetPlayerUnitIds(2, WONDER)` size | whether an object-id query sees a foundation |
| the same by building class | whether a class query sees what the object-id query misses |
| `xsGetObjectCount(2, WONDER)` | a third reading, and whether it is -1 like map revealers |
| `xsGetUnitBuildPoints` on any id found | separates "found but incomplete" from "not found" |

`spikes/78/` already has the harness and the reader for exactly this shape of question.

**Built, 2026-11-07.** [`spikes/84/`](../spikes/84/README.md). The probe is case 13 in the live
`Test.xs`, sidecar format `AP78` version 2, with `read.py` and a `selftest.py` that proves the
reader against every possible detection outcome. It still needs one `XsTesting` boot.

### Two candidate fixes

1. **Find a query that sees foundations**, from the probe above, and use it in
   `ScanOwnerWonders`. General: works wherever a Wonder is started, scripted or not.
2. **Let the scenario say so.** Attila 6 already carries a `place_foundation` effect per city -
   `Red Constructs Wonder` at (216,24), and the rest at (33,55), (136,178), (123,72), (129,78).
   Those triggers are the exact moment and place. A `script_call` beside each one would tell the
   mod directly, with no discovery needed. Deterministic, but only covers Wonders the scenario
   scripts; Genghis 3 has no such trigger at all, which is why AP added the threat there.

## 2. The reveal is the wrong shape anyway

Vanilla reveals **only the foundation itself** - nothing around it. The maintainer's screenshot
of the vanilla behaviour shows it exactly: a soft-edged diamond of lit ground stopping at the
construction site's fence, the timber and stone piles and the two villagers inside it visible,
and solid black a tile beyond. That is the target.

`RevealAround` asks for `THREAT_REVEAL_RADIUS = 10`, which is far more generous than the game's
own behaviour - a 10-tile circle would light up most of a town.

The maintainer's proposal: a grid of line-of-sight 1 revealers over the foundation's footprint,
cleared when the Wonder is built. That matches vanilla and keeps the reveal proportionate to what
the player is being warned about.

Open in that proposal:

- **What happens on completion.** "Cleared when the Wonder is built" could mean the completed
  Wonder carries no reveal at all, or that the grid is replaced by the present radius-10 revealer.
  The second keeps today's behaviour for the thing the countdown is actually about; the first is
  closer to vanilla throughout.
- ~~**The footprint size.**~~ **Settled, 2026-11-07: the Wonder is 5x5.** There *is* an
  `empires2_x2_p1.dat` on this machine - the Steam install has it at
  `resources/_common/dat/empires2_x2_p1.dat`, which this ticket and `spikes/82/README.md` both
  got wrong. `kit dat unit <dat> 0 276` reads `collision_size_x = 2.5`.

  **Superseded 2026-11-07: `2 x collision_size_x` is not the tile footprint.** It gives 5; a
  Wonder occupies **6x6**, measured in game. The doubling rule matches every building whose size
  is independently known - House 1.0 (2x2), Barracks and Monastery 1.5 (3x3), Town Center and
  Castle 2.0 (4x4) - and was wrong for the one building this ticket is about, which cost several
  rounds of a reveal grid that was a tile short. `spikes/82/forks.py` is corrected to 6.
- **The relic half is fine.** Settled by the maintainer: relics work as intended. The monastery
  revealer in `RelicThreatWatch` does its job when the threat is armed, and the only thing that
  arms it is `Test.xs:1107` - no shipped scenario calls `EnableRelicThreat()`, which is what
  [#78](78-in-game-checks-round-2.md) recorded as groundwork. So the contrast in the report is
  between a relic path that works when exercised and a Wonder-foundation path that does not work
  at all.

## Rulings

- **2026-11-07** - Probe first. Settle whether any XS query sees a foundation, in `XsTesting`,
  before committing to a detection route.
- **2026-11-07** - On completion the grid clears and **the wide completed-Wonder reveal
  takes over** (`THREAT_REVEAL_RADIUS`, since reduced from 10 to 9).
  The countdown is about the finished Wonder, so the player keeps the generous view of what they
  have to destroy. Nothing about completed-Wonder behaviour changes.
- **2026-11-07** - The relic half works as intended; this ticket is only about the Wonder
  foundation.
- **2026-11-07** - Detection is **counter-driven**: `xsGetObjectCountTotal` against
  `xsGetObjectCount`, per owner, and only while that owner's threat is armed. The
  scenario-declared `script_call` route is **rejected**.
- **2026-11-07** - A reveal waits until construction has actually **begun**
  (`xsGetUnitBuildPoints > 0`). An untouched foundation is invisible in game, so revealing it
  shows the player nothing. The "has begun a Wonder" announcement moves to the same moment.
- **2026-11-07** - A foundation *is* reachable by id, through
  `xsGetPlayerUnitIds(owner, -1)` filtered on `xsGetUnitObjectId == WONDER`. The counter stays as
  the **gate** that decides when to pay for that scan; the scan supplies the id, and so the
  position the footprint reveal needs.

## Acceptance criteria

- [x] The probe above is run and recorded, so "foundations are not enumerated" is engine-verified
      rather than deduced. *(Run 2026-11-07. No id-returning query sees a foundation.)*
- [x] A ruling on which detection route to take, recorded under *Rulings*. *(Ruled 2026-11-07:
      counter-driven, armed with the threat; scenario-declared rejected.)*
- [x] A ruling on what the reveal becomes once the Wonder completes. *(Ruled 2026-11-07: the
      grid clears and the wide completed-Wonder reveal takes over.)*
- [x] A Wonder foundation reveals its own footprint and no more. *(Seen 2026-11-07: lit ground
      stopping at the construction fence, timber and stone piles visible, black a tile beyond -
      the vanilla screenshot this ticket was written against. Repeated on a shipped
      scenario 2026-11-08, in the `PT82_G3W` run that closed the criterion below.)*
- [x] The completed Wonder still arms its countdown and still gets the wide `THREAT_REVEAL_RADIUS` reveal;
      `PT82_G3W` re-run confirms both, since it already stages a foundation and a completed
      Wonder forty tiles apart. *(Played 2026-11-08; accepted by the maintainer.)*

## Comments

**2026-11-07, agent.** Part 2 is built; part 1 is held behind its own ruling.

*Part 1 - detection.* Not touched. The ruling says probe first, and the probe needs one
`XsTesting` boot. [`spikes/84/`](../spikes/84/README.md) is that probe: it stages a foundation
and a completed Wonder side by side and records, per stage, the object-id query, three class
queries, `xsGetObjectCount` against `xsGetObjectCountTotal`, build points, `IsWonderComplete`,
`FindWonderSlot`, `xsGetUnitPosition`, and what `RevealAround` returns at the foundation's tile.
`read.py` prints a verdict naming whichever query returned the foundation, or confirming that
none did. `selftest.py` passes 14/14 with no game.

Two readings in it are worth naming in advance:

- `xsGetObjectCountTotal` is documented as counting "alive/standing + queued/foundation". If it
  reads one above `xsGetObjectCount` while the foundation stands, it is a usable *detector* - but
  it returns no id, so it would only tell `ScanOwnerWonders` to go looking, not where.
- `RevealAround` is called on the foundation's own tile at stage 3. If it returns a unit id there,
  then the reveal half was never the problem and the report's deduction is confirmed from both
  ends rather than one.

*Part 2 - the reveal shape.* Implemented in `VictoryThreats.xs`, in the working tree:

- `TrackWonder` now branches. A Wonder that is already complete keeps today's radius-10 revealer,
  unchanged. One that is not gets `RevealFootprint`: **one line-of-sight 1 revealer per footprint
  tile**, 25 of them for the 5x5 Wonder.
- `StartWonderCountdown` calls `CompleteWonderReveal` first, which clears the grid and creates the
  radius-10 revealer if the slot has none yet - the 2026-11-07 ruling, and nothing about a Wonder
  tracked already complete changes.
- `ReleaseWonderSlot` clears the grid too, so a foundation that is destroyed or captured takes its
  reveal with it.
- The grid lives in `wonderSlotFootprint`, `THREAT_FOUNDATION_CAPACITY` (16) ids per slot, so a
  footprint up to 8 tiles fits and the array is sized once in `InitVictoryThreats`.
- The footprint is read from the engine at run time, `2 x cUnitSizeX` by `2 x cUnitSizeY`, rather
  than hardcoded, with 5 as the fallback when either read lands outside 1-5. The dat says 5 and
  the probe records the live reading, so the two can be checked against each other. Say if you
  would rather it were the constant.
- `RevealAround`'s first call is `cSetAttribute` on `MAP_REVEALER`, which is a **type-wide**
  write: it re-applies to every revealer this player already owns and undoes the per-unit line of
  sight each was pinned to. That was harmless while every wonder reveal used radius 10; with a
  radius-1 grid in the mix, one owner starting a Wonder would have collapsed another owner's
  radius-10 reveal to a single tile, and completing it would have ballooned every footprint
  revealer into the 10-tile circle this ticket is trying to get rid of. `RepinRevealers` now
  restores all three sets after any batch that creates revealers. The relic path gets the same
  protection, which it needed already.

None of that runs for a foundation until part 1 lands, because nothing calls `TrackWonder` for
one. It is correct for a completed Wonder today and it is what a tracked foundation will get.

*A caveat worth stating plainly.* The grid's geometry rests on how the engine rasterises a
radius-1 reveal, and nothing on this machine measures that. One revealer per footprint tile is the
shape that covers the footprint under either reading - circular or square - at the cost of up to a
tile of bleed. Stage 4 of the probe stages the real `RevealFootprint` over a foundation out in the
fog with a lone radius-1 revealer beside it, so the same boot that answers part 1 also says what
the reveal actually looks like. If the bleed is wider than the screenshot allows, the fix is
`THREAT_FOUNDATION_LOS` and the spacing, not the structure.

*What is left.* The probe boot, the detection ruling that follows it, and then the `PT82_G3W`
re-run the acceptance criteria name. `spikes/82/forks.py` is corrected to a 5-tile Wonder
footprint, so that rebuild picks a plot the Wonder actually fits on.

**2026-11-07, agent - the probe was run, and it answers part 1.**

`spikes/84/read.py` against `default1.xsdat`, 68 records, all five stages, 8/8 assertions pass.

### No id-returning query sees a foundation

Both foundations the run staged, and the one `XsTesting` already ships, are invisible to every
query that hands back a unit id. The `holds` columns are measured against ids `xsCreateUnit`
returned, so there is no ambiguity about what was being looked for.

| query | sees a foundation? |
| --- | --- |
| `xsGetPlayerUnitIds(2, WONDER)` | **no** - size 0 with a foundation standing, 1 once the control Wonder is up |
| `xsGetPlayerUnitIds(2, cBuildingClass)` | **no** - it holds P2's Monastery and the completed Wonder, never a foundation |
| `xsGetPlayerUnitIds(2, cMiscBuildingClass)` | **no** - returns 0 throughout; the Wonder is not in that class even when complete |
| `xsGetPlayerUnitIds(2, cFlagClassBuilding)` | **refused**, -1 at every stage - flag classes are not accepted |

So the report's deduction is confirmed, and `ScanOwnerWonders` cannot be repointed at another
query. Route 1 in the report is dead.

### But the engine does know

Read as steps rather than absolutes, the two counters separate cleanly:

| event | `xsGetObjectCount` | `xsGetObjectCountTotal` |
| --- | --- | --- |
| a foundation appears | +0 | **+1** |
| that foundation finishes | +1 | +0 |

`xsGetObjectCountTotal(owner, WONDER)` counts foundations and `xsGetObjectCount` does not, exactly
as the function reference claims. That is a **detector**: `WonderThreatWatch` can know a Wonder is
being built the tick it is started, for any owner, scripted or not. What it cannot do is say
*where* - it returns a number, never an id, so there is no position to reveal and no object to
hold in a slot.

Absolute readings carry a per-scenario offset and must not be used: `XsTesting` itself ships P2 a
Monastery, two Wonders and **a Wonder foundation** (`kit scen units` - unit 546 at (61.5, 38.5),
`status` 0, which is `ObjectState.FOUNDATION`). That foundation is the +1 under every total, and
it is a second, independent confirmation of the same result from an object no script created.

**Run 2, 14:42, with the baseline stage added, reads that offset directly and corrects run 1.**
At baseline, before the probe creates anything: `xsGetObjectCount` 2, `xsGetObjectCountTotal` 3,
`cBuildingClass` 3. So the scenario's two `status` 2 Wonders *are* standing - run 1 happened to
have none, which is why its `byClass` read 1 and why the completed control took slot 0 there and
slot 2 here. The gap is 1 at baseline, exactly the one pre-placed foundation. Every conclusion
below is unchanged and now rests on a non-zero baseline, which is the stronger reading: the id
lists grow only when a Wonder *completes*, never when a foundation is laid.

### The other half of the deduction, confirmed from the other end

`RevealAround` at the foundation's own tile returned unit id 574, and `xsGetUnitPosition` on a
foundation reads correctly (68, 68). So the reveal path works there; the foundation was simply
never found. Both ends of the report's deduction now rest on readings.

`FindWonderSlot` on the first foundation reads -1 at stages 1-4 and **1** at stage 5, the moment
its build points reach `cTrainTime`. The mod picks a Wonder up on completion and not before,
which is the bug stated precisely.

`countRevealers()` reads 0 at every stage, confirming again that map revealers are not
enumerable - the reveal is only ever an eye.

### What the maintainer saw

> I never saw the foundation revealed, but I did see a map revealer the perfect size for a wonder
> to the southwest

Both halves are informative.

**"Perfect size for a wonder"** is stage 4: the real `RevealFootprint` over a foundation out in
the fog. The grid is right - one line-of-sight 1 revealer per footprint tile lights a 5x5 and
reads as Wonder-sized on screen, with no circle around it. That is acceptance criterion 4
answered in layer 2, which is better than this ticket hoped for.

**"Never saw the foundation revealed"** has two causes, and the second is a real finding.

1. The first foundation is never tracked, so the mod reveals nothing. That is the bug.
2. The radius-10 reveal the probe put there itself at stage 3 **was collapsed to one tile four
   seconds later**, by the type-wide `cSetAttribute` inside the 25 `RevealAround` calls of stage
   4. `RepinRevealers` restored every revealer the mod tracks; the probe's own loose revealer was
   not in any of those arrays, so it stayed at line of sight 1. This is the stomping the code
   review predicted, observed in play - the fix in `VictoryThreats.xs` is doing its job for the
   tracked ones, and the harness has now been given the same treatment for its own.

### What this leaves for a ruling

Route 1 is gone, so the choice is between, or a combination of:

- **Scenario-declared (report route 2).** A `script_call` beside each `place_foundation` effect.
  Exact, gives a position, so the footprint reveal works in full. Covers Attila 6's five cities;
  covers nothing in Genghis 3, where no such trigger exists.
- **Counter-driven warning.** `xsGetObjectCountTotal` against `xsGetObjectCount` per armed owner,
  every tick. Works everywhere including an AI-built Wonder, costs two calls per owner, and gives
  the player the warning the report says is worth more than the reveal - *"Red has begun a
  Wonder"* - with no reveal and no slot, because there is no id.

They compose: the counter arms the warning everywhere, the `script_call` adds the reveal where a
scenario can say where. Nothing in either changes completed-Wonder behaviour.

**2026-11-07, agent - the counter route is built.**

`WatchOwnerFoundations` in `VictoryThreats.xs`, called from `WonderThreatWatch` inside the
armed-owner loop, so it costs two engine calls per armed owner per second and nothing at all for
an owner whose threat was never armed.

```
int CountOwnerFoundations(int owner) {
    return (xsGetObjectCountTotal(owner, WONDER) - xsGetObjectCount(owner, WONDER));
}
```

The gap is the owner's foundation count, exactly - the probe run checks that arithmetic against
the engine in both directions, and `read.py` now asserts it rather than merely printing it:

| event | `xsGetObjectCount` | `xsGetObjectCountTotal` | the gap |
| --- | --- | --- | --- |
| a foundation appears | +0 | +1 | **+1** |
| that foundation finishes | +1 | +0 | back to 0 |

A rise in the gap announces *"&lt;colour&gt;&lt;name&gt; has begun a Wonder!"* on the top panel,
in the same shape as the completion announcement. It fires on the rise only, so a foundation that
stands for twenty minutes says it once; a second Wonder started later says it again. The per-owner
count is held in `wonderOwnerFoundations`, indexed `owner - 1` like the rest, and
`RetireWonderOwner` zeroes it so a defeated city cannot leave a stale reading behind.

It needs no baseline and no scenario cooperation: the gap is absolute, and it counts a foundation
whoever laid it - a trigger, the AI, or a player's villagers.

### What it does not give, and what I think you were pointing at

The counter hands back a number, never an id, so there is still no position - and a reveal needs
one. `ScanOwnerWonders` is unchanged and still only ever finds completed Wonders, so `TrackWonder`
is only ever reached with a complete Wonder and **`RevealFootprint` currently has no live
caller**. The grid you saw working on screen is correct and in place, but nothing reaches it. I
have left it wired rather than deleting it, because it is one `IsWonderComplete` call to keep and
the moment anything can name a foundation it is already right.

So acceptance criterion 4 is not met by this route alone, and I have not ticked it.

**2026-11-07, maintainer:** *"You can get foundations by getting all units
`xsGetPlayerUnitIds(playerId, -1)` and then filtering."*

That is now in the probe, as a fifth query beside the other four, with the returned ids filtered
by `xsGetUnitObjectId(id) == WONDER` and the filtered count recorded beside
`xsGetObjectCountTotal`. If the two agree at every stage, the all-units scan sees foundations, and
`ScanOwnerWonders` can be repointed at it: that hands back an **id**, so a position, so
`RevealFootprint` becomes reachable and acceptance criterion 4 is back in play. `read.py` asserts
the agreement and the verdict block names the query if it works.

One caveat the maintainer raised with it: *"It may be that a foundation isn't counted until the
player starts to build it."* Worth holding, but the run already argues against it for the state
that matters. The probe's foundation reads `xsGetUnitBuildPoints` **0** - no construction has
happened on it at all - and `xsGetObjectCountTotal` counts it anyway, while every id query misses
it. So a zero-progress foundation is already counted, at least one made by `xsCreateUnit`. What
that does not settle is whether a foundation a *player* placed behaves identically before a
villager reaches it; `xsCreateUnit` is the only way XS can stage one, and XS has no build command
to task a villager with. That difference, if it exists, is layer 3.

### Still to check in game

- **The all-units query**, which is the one that decides whether the reveal is reachable.

- The warning fires once when a Wonder is started, and reads correctly, on a real scenario.
- `PT82_G3W` still arms its countdown and still gets the radius-10 reveal on completion
  (acceptance criterion 5), with the fork rebuilt against the corrected 5-tile Wonder footprint.

**2026-11-07, run 3 - the maintainer's lead lands it.**

> You can get foundations by getting all units `xsGetPlayerUnitIds(playerId, -1)` and then
> filtering

Measured, and it is exactly right. The all-units list, filtered on
`xsGetUnitObjectId(id) == WONDER`, matches `xsGetObjectCountTotal` at **every stage**:

```
filtered count / xsGetObjectCountTotal:  0:1/1  1:2/2  2:3/3  3:3/3  4:4/4  5:4/4
```

So the scan returns every Wonder the owner has, foundations included, **with their ids**. That is
the thing the typed queries would not give, and it changes the outcome of this ticket: an id means
`xsGetUnitPosition`, which means `RevealFootprint` is reachable and criterion 4 is back on.

### What is built now

`ScanOwnerFoundations` does the all-units pass and `TrackWonder`s any Wonder not already in a
slot. It is **gated by the counter**, which is what the ruling is for and what makes it
affordable:

```
if (found > TrackedFoundations(owner)) {
    ScanOwnerFoundations(owner);
}
```

`CountOwnerFoundations` is the cheap two-call reading of how many foundations the owner has;
`TrackedFoundations` counts how many of those are already in slots. They agree on every tick
except the one where a new foundation appears, so the expensive scan runs **once per foundation
laid**, not once per second - and never at all for an owner with nothing under construction, or
one whose threat was never armed.

From there the part-2 work that had no caller becomes live by itself: `TrackWonder` sees an
incomplete Wonder, lays the footprint grid, `TickWonderSlot` watches its build points, and
`StartWonderCountdown` clears the grid for today's radius-10 reveal on completion. Nothing about
completed-Wonder behaviour changes.

The announcement stays where the ruling put it, firing on a rise in the gap, after the scan so the
reveal is up before the player is told.

### The probe now tests the fix rather than the question

Stage 3 no longer lays a grid itself - it creates a second foundation and leaves it to the mod, so
what the sidecar records is the shipped path end to end. `read.py` has a new assertion,
**"the mod tracks a Wonder while it is still a foundation"**, which reads `FindWonderSlot` on the
foundation across stages 1-4.

Against run 3, taken before the fix, it reports what it should:

```
[FAIL] the mod tracks a Wonder while it is still a foundation
       FindWonderSlot on the foundation by stage: {1: -1, 2: -1, 3: -1, 4: -1}
       [-1 throughout: ScanOwnerFoundations did not reach it, which is the #84 bug unfixed]
```

14 of 15. A run with the fix should read 15 of 15, and the foundation should carry a Wonder-sized
reveal on screen from the moment it appears.

### On "it may not be counted until the player starts to build it"

Still not fully settled, but narrowed. The probe's foundation reads `xsGetUnitBuildPoints` **0**,
so no construction has happened on it, and it is both counted by `xsGetObjectCountTotal` and
returned by the all-units scan. A zero-progress foundation is therefore found - at least one made
by `xsCreateUnit`. Whether a foundation a *player* placed behaves identically before a villager
reaches it is the one thing left, and it needs a real scenario: `xsCreateUnit` is the only way XS
can stage a foundation, and there is no build command to task a villager with. If it turns out a
player's untouched foundation is invisible, the symptom will be a reveal that appears when the
first villager arrives rather than at placement - a delay, not a failure.

**2026-11-07, run 4 - the fix works, and the play test found three things.**

The sidecar reads **15 of 15**, and the row that matters:

```
[PASS] the mod tracks a Wonder while it is still a foundation
       FindWonderSlot on the foundation by stage: {1: 1, 2: 1, 3: 1, 4: 1}
```

Tracked from the first tick after it appears, where every run before this read -1. Part 1 is done.

The three oddities, in order.

### 1. The foundation was invisible - fixed, and it is a better rule

Right, and the cause is that the foundation had **0 build points**: nothing had been built on it,
so the game renders no construction site and the reveal lit empty ground. Revealing at placement
is wrong anyway - a foundation can be cancelled, and the player is being pointed at nothing.

A slot is still **claimed** the moment the foundation appears, because that is what closes the
counter gate and keeps the all-units scan from running every tick. What waits is the reveal:

- `RevealWonderSlot` lays nothing while `xsGetUnitBuildPoints` is 0.
- It lays the footprint grid, and announces, the first tick the points rise above 0.
- `TickWonderSlot` retries it each tick, so a foundation that sits untouched for ten minutes gets
  its reveal the moment a villager finally starts work.

The announcement moved with it. It used to fire on a rise in the counter gap, which is placement
time; it now fires with the reveal. Announcing *"Red has begun a Wonder!"* while nothing is
visible and nothing is being built would have been the same bug in words. Say if you want the
placement-time warning back as well - they are two lines apart.

### 2. The radius was the full 10 - that was the harness, not the mod

That circle was the probe's own `RevealAround(foundation, THREAT_REVEAL_RADIUS)` at stage 2,
which was there to answer "does `RevealAround` work at a foundation's tile at all". It does - run
1 and run 3 both recorded a revealer id - so the question is closed and the call is **removed**.
The only reveals on screen now come from the mod.

It was also unreadable from the sidecar, which is why it took an eye to catch. That is fixed:
`WonderSlotRevealKind(slot)` reports 0 for none, 1 for the footprint grid, 2 for the radius-10
circle, the harness records it per stage, and `read.py` now asserts all three of

- an untouched foundation carries **no** reveal,
- a part-built one carries the **grid**,
- a completed one carries the **circle**.

The probe stages that sequence deliberately: the first foundation is driven to 10% of `cTrainTime`
at stage 2, so "construction has begun" is a state the harness actually produces rather than one
we reason about.

### 3. The Wonder completed with 1 HP - a harness artefact, now also fixed

`xsSetUnitBuildPoints` finishes a building without touching its hit points. A foundation starts at
1 HP and gains the rest as it is built, so forcing the build points straight to `cTrainTime`
leaves a finished Wonder on 1 HP. Nothing a villager builds behaves that way, and nothing in
`VictoryThreats.xs` reads hit points - `IsWonderStanding` only asks whether the object exists and
who owns it - so the mod is unaffected.

The harness now sets hit points alongside the build points, so the staged Wonder is not a
one-shot oddity that someone later mistakes for a mod bug.

**Worth keeping for the knowledge base:** `xsSetUnitBuildPoints` completes a building and does
**not** restore its hit points.

### What is left

- A play test of the new timing: the reveal should appear when a villager starts work, be
  Wonder-sized, and become the radius-10 circle on completion.
- The one thing layer 2 still cannot stage: a foundation a **player** placed, untouched. The probe
  can only make one with `xsCreateUnit`. If a player's untouched foundation is invisible to the
  all-units scan too, the new rule hides that completely - we would not reveal it at that point
  anyway - so the worst case is now a non-issue rather than a gap.
- `PT82_G3W` re-run for criterion 5.

**2026-11-07, run 5 - the reveal is right.**

18 of 18, and the screenshot settles criterion 4: a fenced construction site lit to its edge, the
timber and stone piles inside it visible, solid black a tile beyond. That is the vanilla
behaviour this ticket was written against, reproduced by the footprint grid.

Two things came out of the same look.

**The control Wonder's circle lapped over it.** B stood twelve tiles from A; A's footprint reveal
reaches about three tiles from its centre and B's radius-10 circle reaches ten, so the two lit
patches touched and read as one. That is a harness layout fault, not a mod one - in play the two
are a scenario apart. B moves to 22 tiles out, leaving nine tiles of dark between them.

**The compass is now pinned.** Each map axis is a diagonal on screen, and nothing in the
`aoe2-modding` KB records which. Two sightings settle it: a Wonder at `+x` reported north-east,
and the earlier one at `-x` reported south-west.

| move | on screen |
| --- | --- |
| `+x` | north-east |
| `-x` | south-west |
| `+y` | south-east |
| `-y` | north-west |

So "ten tiles south-east" was `y + 10`. I moved `(+10, +10)`, which is due east - away from the
Town Center, which was the point, but not what was asked. Written into
`docs/agent/references/xs-mod.md` so the next person does not have to measure it again.

**2026-11-07, run 6 - a false alarm, and what it cost.**

*Resolved by the maintainer: the civilisation picked for that run was defeated at the start.* That
accounts for the whole of run 6. `WonderThreatWatch` calls `RetireWonderOwner` the moment
`xsGetPlayerInGame(owner)` goes false, which disarms the owner and releases every slot - hence
`FindWonderSlot` reading -1 for the foundation *and* for the completed control Wonder - and a
defeated player's buildings are razed, which is the control Wonder vanishing between stages 2 and
3. Nothing in the code was at fault.

The cost was mine: I had shipped five changes at once on top of a working run, so when it came
back broken there was no way to tell which one did it, and I reverted all five - including
`TileCentre`, which was never implicated and is the fix for the offset that is still open. The
probe now records `xsGetPlayerInGame` and the owner's object count per stage, so a defeated owner
reports itself by name instead of looking like a logic bug.

**What follows was written before that was known, and its conclusion is wrong.**

**2026-11-07, run 6 - I broke it, and reverted.**

Run 5 was 18 of 18 with a correct reveal on screen. The ask after it was one thing: move the two
staged Wonders apart. I shipped five changes instead - the separation, every staged position moved
on to tile centres, a `TileCentre` snap inside `RevealFootprint`, the position record rescaled, and
later a watcher heartbeat - on the theory that the reported "one LOS to the east" came from a 5x5
building straddling the tile grid.

Run 6 came back with **nothing tracked at all**: `FindWonderSlot` -1 for the foundation *and* for
the completed control Wonder, which does not touch any of the new code. `xsGetObjectCount` also
shows the control Wonder being destroyed between stages 2 and 3, which had never happened before.
I could not account for either from reading the code, and the cause is still unknown.

**Everything after run 5 is reverted.** `VictoryThreats.xs` and `Test.xs` are back to the run-5
state, with exactly one change applied on top: the control Wonder moves from `spotX + 30` to
`spotX + 36`, so it stands 18 tiles from the foundation instead of 12. A footprint reveal reaches
about three tiles and the radius-10 circle reaches ten, so 18 leaves five tiles of dark between
them, which is what the overlap complaint was about.

**Still open, and not to be guessed at again:** the reveal sitting one LOS east of the construction
site. The half-tile theory is plausible - `XsTesting`'s own Wonders sit at (61.5, 38.5) and its
Monastery at (55.5, 56.5), so odd footprints do land on `N.5` while the harness stages on whole
numbers - but it is a theory, it is not what run 6 tested in isolation, and it is not worth another
boot until it can be changed on its own and measured.

The lesson for this ticket, which has been run on measurement throughout: one change per run.

**Withdrawn - the run-6 write-up below is kept only because it names the half-tile theory.**

A 5x5 building's legal centre is a **tile centre**, `N.5` - `XsTesting`'s own shipped Wonders sit
at (61.5, 38.5) and its Monastery at (55.5, 56.5), while the 4x4 Town Center sits at (67, 53).
Odd footprints land on `N.5`, even ones on `N.0`.

The harness was creating its Wonders at `spotX + 18`, a whole number, so the staged building
straddled the tile grid by half a tile and `RevealFootprint` inherited the offset: the revealer
column that should have lit the western edge fell on the boundary, and the lit patch came out one
tile east of the construction site.

Two changes, because the harness fault and the robustness gap are different things:

- **The harness stages at tile centres now** - `1.0 * spotX + 18.5` rather than
  `1.0 * (spotX + 18)`, and the same for the control Wonder, the second foundation and the lone
  revealer. A Wonder a player or the AI builds is always on a legal centre, so this was never
  going to show up in play; it was the probe lying about the geometry.
- **`RevealFootprint` snaps every revealer to the centre of the tile it lands in**, through a
  `TileCentre` helper (XS has `xsCeilToInt` but no floor, so it is `-ceil(-v) + 0.5`). With a
  legally placed Wonder the grid was already right; with anything else it now lights whole tiles
  instead of straddling them.

`xsGetUnitPosition` is also recorded to a tenth of a tile now rather than through `xsCeilToInt`,
which was rounding 78.5 to 79 and hiding exactly this. `read.py` says outright when a staged
Wonder is not on a tile centre.

**2026-11-07, run 7 - `TileCentre` restored, on its own.**

With the defeat explained, run 5's behaviour is the baseline again and the remaining report is
precise: *"the map revealers are covering one tile too much to the northeast and southeast"* -
`+x` and `+y`, the two axes the compass pins as those directions.

That is the signature of revealers sitting on tile **corners** rather than tile centres. A
position of `76.0` is the boundary between tiles 75 and 76, so a revealer placed there lights
ambiguously and the patch grows by a tile on the `+x` and `+y` sides. Tile centres are `N.5` -
which is also where the game itself puts odd-footprint buildings, `XsTesting`'s own Wonders at
(61.5, 38.5) and its Monastery at (55.5, 56.5).

So `RevealFootprint` snaps every revealer to the centre of the tile it lands in, through a
`TileCentre` helper - XS has `xsCeilToInt` but no floor, so it is `-ceil(-v) + 0.5`.

**That is the only change in this run.** The staged positions, the harness, the reader and
everything else stay exactly as they were in run 5.

**2026-11-07, run 8 - the grid was twice as dense as it needed to be.**

The measurement that settles the reveal shape, from the maintainer: **a single line-of-sight 1 map
revealer lights exactly a 3x3 area.** Not a disc, not a diamond - a 3x3 square.

That makes the grid built after the code review plainly wrong. It placed one revealer per
footprint tile, so five per axis across a 5-tile Wonder, each lighting three tiles: the union is
**7 tiles across a 5-tile building**, a tile of bleed on every side. The review's finding 2 had
argued the opposite - that line of sight is a radius and a wider spacing would leave the corners
dark - and that was wrong. The original spacing was right and I changed it on a plausible-sounding
argument rather than a reading.

Two revealers per axis, two tiles apart, tile it exactly:

```
footprint tiles   76 77 78 79 80        (centre reported 78)
revealer at 77 ->  76 77 78
revealer at 79 ->        78 79 80
union          ->  76 77 78 79 80       exactly the footprint, no bleed
```

So `RevealFootprint` places `tiles / 2` revealers per axis at a spacing of 2, centred on the
building. For the 5x5 Wonder that is four revealers rather than twenty-five, and the lit area is
the construction site and nothing else. `TileCentre` stays, because it is what keeps each revealer
on a tile rather than a boundary.

**That is the only change in this run.**

Two things the maintainer offered that turned out not to be needed, recorded so they are not
re-tried: a line of sight below 1, and deleting the easternmost revealers on a foundation. Both
were workarounds for a grid that was simply too dense.

**2026-11-07, run 9 - the patch was offset, not the wrong size.**

Two readings, taken together, say one thing:

| grid | what was seen |
| --- | --- |
| 5 revealers per axis, 7 tiles lit | one tile too much on north-east and south-east, nothing wrong on south-west or north-west |
| 2 revealers per axis, 5 tiles lit | still over on north-east and south-east, and now the **north-west and south-west corners are dark** |

A patch that is too big would have bled on all four sides. A patch that is the right size but one
tile too far in `+x` and `+y` over-reaches on north-east and south-east and falls short on
north-west and south-west - which is exactly both rows. The maintainer said as much twice before I
listened; the asymmetry *was* the evidence.

So `xsGetUnitPosition` on a Wonder does not report the centre tile of its footprint - it reports
one tile east and south of it. `RevealFootprint` subtracts that tile:

```
firstX = xsVectorGetX(centre) - 1.0 * stepsX      (was stepsX - 1)
```

For the 5x5 Wonder with a reported centre of 78: revealers at tiles 76 and 78, windows 75-77 and
77-79, union **75-79** - the footprint, with nothing over and no corner left dark.

**That is the only change in this run.**

**2026-11-07, run 10 - the original, minus one row on each positive axis.**

Settled by the maintainer, after I had spent three runs guessing at it:

> The original. Do one TINY thing. When going in the positive x direction, do one single tile
> fewer rows. When going in the positive y direction, do one single fewer tile rows.
> You did -2 rows with your last four or so attempts, making the footprint too small.

`RevealFootprint` is the original again - one revealer per footprint tile, spacing 1, `firstX`
unchanged, no `TileCentre` - with the loop bounds `tilesX - 1` and `tilesY - 1`. For the 5x5
Wonder that is a 4x4 block of revealers rather than 5x5, which drops the single extra tile on each
of the two positive axes and leaves the rest exactly as it was.

What I got wrong, repeatedly: I read "one tile too much" as a sizing or centring error and rebuilt
the grid around a model of where the light lands, twice reducing it by two rows and leaving the
far corners dark. The fix was one row, on two axes, with everything else untouched.

**The compass note I added to `docs/agent/references/xs-mod.md` has been removed.** I wrote it as
`+x` north-east and `+y` south-east, from one sighting; the maintainer later described the same
axes as north-west and south-west. It is unresolved, and a wrong compass in the canonical
reference is worse than none.

**2026-11-07, run 11 - the completed Wonder's circle shifted one tile down on both axes.**

The foundation grid was already right after run 10 and is untouched: a `(tiles - 1)` square block
of line-of-sight 1 revealers, one per tile, which for the 5x5 Wonder is 4x4 and lights the
construction site.

What was off by a tile was the **completed** Wonder's radius-10 circle. Both places that create it
- `RevealWonderSlot` when a Wonder is tracked already finished, and `CompleteWonderReveal` when one
finishes under us - now go through

```
vector WonderRevealPoint(int unitId) {
    vector centre = xsGetUnitPosition(unitId);
    return (xsVectorSet(xsVectorGetX(centre) - 1.0, xsVectorGetY(centre) - 1.0, 0.0));
}
```

so the circle sits one tile down on both axes. Nothing else about completed-Wonder behaviour
changes - same radius, same swap from the grid, same countdown.

*(I first applied this shift to the foundation grid, having misread which revealer was meant. The
maintainer had already reverted that by hand; the grid in the tree is the run-10 version.)*

**2026-11-07, the row count is explicit and `PT82_G3W` is rebuilt for criterion 5.**

No boot in this round - three desk changes, each one the resolution the Outstanding list named.

**`WonderFootprintAxis` is gone, and the grid is unmoved.** The derivation it fed was
`2 x cUnitSizeX`, the rule this ticket disproved, and it returned 5 for a 6-tile Wonder.
`RevealFootprint` now reads `THREAT_FOUNDATION_ROWS = 4` outright:

| | rows | first revealer |
| --- | --- | --- |
| before | `tilesX - 1` with `tilesX` 5 | `centre - 0.5 * (5 - 1)` = `centre - 2.0` |
| after | `THREAT_FOUNDATION_ROWS` = 4 | `centre - 0.5 * 4` = `centre - 2.0` |

Same four revealers per axis from the same tile, so the reveal the maintainer approved on screen
in run 10 is the reveal that is still laid. `THREAT_FOUNDATION_MAX_TILES` and
`THREAT_FOUNDATION_TILES` had no reader left and are deleted; `THREAT_FOUNDATION_CAPACITY` drops
from 36 to 16, which is `4 x 4` and what the grid has always placed. The `owner` argument to
`RevealFootprint` was only there to query the dat and is gone too. `xs-check` is clean on `AP.xs`
and `Test.xs`.

**`PT82_G3W` now reads the behaviour the mod actually has.** Its `look` lines still described the
pre-fix mod - *"About ten tiles of fog lift around (118,174) when the foundation appears"* - which
is the opposite of the ruling that a reveal waits for build points. Played as written it would
have reported the fix as a failure. The fork now stages the whole sequence and latches each
reading at the tick it belongs to, so a Wonder destroyed during the look cannot rewrite it:

| tick | what happens | latched |
| --- | --- | --- |
| 5 | a Jin Wonder foundation on the cleared Blacksmith plot | |
| 10 | - | `foundation_slot_idle` (must not be -1), `foundation_reveal_idle` (must be 0) |
| 20 | `xsSetUnitBuildPoints` to 10% of `cTrainTime` | `foundation_begun` (must be 1) |
| 30 | - | `foundation_reveal_built` (must be 1, the grid) |
| 35 | a finished Jin Wonder forty tiles away | |
| 45 | - | `wonder_slot_armed` (must not be -1), `wonder_reveal_armed` (must be 2, the circle), `wonder_years_armed` |

`foundation_slot_idle` is the #84 regression test on a shipped scenario rather than in
`XsTesting`: -1 there is the original bug. `wonder_reveal_armed` is criterion 5's own reading -
2 is `WonderSlotRevealKind`'s circle, so the swap from grid to circle on completion is asserted
rather than left to the eye. Six asserted probes, up from one.

Two new generated helpers carry it: `PT82RevealKind`, which answers -1 for a unit in no slot
instead of indexing an array at -1, and `PT82BuildTo`, which is the `xsSetUnitBuildPoints` call
from `spikes/84`'s stage 2.

**The idle window is five seconds, deliberately.** The Jin are an AI player and the foundation is
theirs, so their villagers may finish it. The reading that must see an untouched foundation is
latched at tick 10, five seconds after it appears; the fifteen seconds of nothing-lit that the eye
needs run from there. If villagers do reach it first the patch lights early and
`foundation_reveal_idle` reads 1 - that is the mod working, and it is written into the caveats so
it is not reported as a bug.

`selftest.py` is 22 of 22 and `build.py G3W` is clean, including `xs-check` over the generated
fork.

**Stale docs corrected.** `spikes/84/README.md` still cited `WonderRevealPoint`, which was
reverted and is not in the tree, the radius-10 circle, which is 9, the 5x5 footprint, which is
6x6, and the compass note as living in `xs-mod.md`, which was removed as unresolved.
`spikes/84/read.py` called reveal kind 2 "radius 10" in its table and its assertion.

**2026-11-07, the completed Wonder gets the same treatment.** Maintainer's call, after the
footprint refactor landed: the finished Wonder should carry **four revealers in a block at its
centre**, on the same principle as the grid, rather than one revealer at the tile
`xsGetUnitPosition` reports. There were exactly two places that made it - `RevealWonderSlot`, when
a Wonder is tracked already finished, and `CompleteWonderReveal`, when one finishes under us - and
both now call `RevealWonder`.

The two grids are the same function with different numbers:

| | rows | spacing | radius | revealers |
| --- | --- | --- | --- | --- |
| foundation | `THREAT_FOUNDATION_ROWS` 4 | 1 tile | `THREAT_FOUNDATION_LOS` 1 | 16 |
| completed Wonder | `THREAT_WONDER_REVEAL_ROWS` 2 | 1 tile | `THREAT_REVEAL_RADIUS` | 4 |

`RevealGrid` and `ClearGrid` take the array, base, rows and radius, so `RevealFootprint`,
`ClearFootprint`, `RevealWonder` and `ClearWonderReveal` are each one call. `wonderSlotRevealers`
widened from one cell per slot to four, and `RepinRevealers`, `WonderSlotRevealKind` and
`ReleaseWonderSlot` moved with it; `HasWonderReveal(slot)` is the one place that now knows the
block is keyed on its first cell. **`THREAT_REVEAL_RADIUS` is 8**, set by the maintainer in the
same round.

Shipped in `e13708a`, with `731205b` before it. Prose in the harness names
`THREAT_REVEAL_RADIUS` rather than its value now - the number moved three times in a day and the
write-ups kept trailing it.

**What the review caught, and what was done.** Two axes, both against the state before this
round.

- **Criterion 5's countdown half was not asserted.** `wonder_reveal_armed == 2` does not prove the
  countdown armed: `RevealWonderSlot` lays the block on the complete branch *before*
  `StartWonderCountdown` is reached, so the reveal latches either way. `wonderSlotCounting` is set
  by `StartWonderCountdown` and by nothing else, so `IsWonderCounting(slot)` is now in
  `VictoryThreats.xs` and `wonder_counting` asserts it. That is the half of criterion 5 that would
  otherwise have gone back to the eye, which is what the rebuild was for. *(XS globals do not
  cross an include, so the harness needed the accessor rather than the array.)*
- **The AI caveat covered one probe, not both.** The Jin can start the foundation before tick 10
  *and* finish it before tick 30. Both now say so.
- **The Rulings entry was withdrawn.** `docs/agents/issue-tracker.md` says one dated line,
  the decision only, and a ruling records the maintainer's decision - not an agent's
  implementation choice. The row-count decision is recorded in this comment instead.
- **Stale `radius-10` in this file's own Rulings and criterion 5** now name
  `THREAT_REVEAL_RADIUS` instead of a number.
- **Not done, deliberately:** a `Latch(name, tick, expr, expect)` type to replace the
  `globals`/`stage`/`probes` triple each latched reading spells out three times. It is a real
  smell and `A6W` has it too, so it is a harness-wide change, not a G3W one. Likewise
  `THREAT_FOUNDATION_CAPACITY` and `THREAT_WONDER_REVEAL_CAPACITY` must each stay the square of
  their rows, which nothing enforces; they sit on the next line from the rows they belong to.

`selftest.py` is 22 of 22 in `spikes/82` and clean in `spikes/84`; `build.py G3W` passes
`xs-check` over the generated fork; `xs-check` is clean on `AP.xs` and `Test.xs`.

**2026-11-08 - closed.** `PT82_G3W` played and accepted by the maintainer, which is
criterion 5 and the shipped-scenario half of criterion 4. All five criteria are ticked.

## Left open, neither of them blocking

- **The `spikes/84` probe has not been re-run since the geometry settled.** The last clean
  read was 18 of 18, before the footprint row count became explicit and the completed
  Wonder became a four-revealer block. It is a regression test that has gone stale, not a
  question anyone is waiting on; one `XsTesting` boot refreshes it.
- **A foundation a *player* placed, untouched**, is still unstageable at either layer. The
  reveal waits on build points either way, so the worst case is a reveal that arrives late.
