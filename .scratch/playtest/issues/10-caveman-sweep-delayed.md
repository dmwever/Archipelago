# 10: Caveman knockdowns and unit checks are starved while the unit count keeps moving

**Reported:** 2026-10-20, playtesting

**Status:** needs-triage (after #35)

**Blocked by:** #35 (the unit id lookup spike). #33 is done. #34 (caveman-off checks) folds into this
ticket.

## Report

On caveman mode, a Knight stayed a Knight for a long time, then turned into a Militia.

The reporter has since confirmed the Knight was **converted**. Conversion is not the cause (see the
audit): a converted Knight is an ordinary player-1 unit, and the delay is in when the sweep runs,
not in how the unit arrived. What conversion does supply is the *context* — it happens in combat,
which is exactly when the sweep starves.

## Audit (from code, not verified in game)

The caveman sweep runs in the `UnitsanityChecks` rule (`Unitsanity.xs:323-366`), once a second.
Two things mark the unit list dirty, and each of them **returns early** instead of sweeping:

```
if (owned != unitsOwned) { unitsOwned = owned; unitsDirty = true; return; }   // :336-340
if (researched > unitsResearchCount) { ...; unitsDirty = true; return; }      // :343-347
```

`ApplyCaveman` (`:358`) only runs on a tick where neither the unit count nor the research count
changed since the previous tick. `ApplyCaveman` itself (`Caveman.xs:207`) has no timer — it is
driven entirely by the `units` array the rule hands it, so the rule's scheduling is the whole story.

Two ways that delays it:

1. **Busy games starve the sweep.** While the unit count changes every second (training queues,
   deaths in a fight, units created by triggers), every tick takes the early return and the sweep
   never runs. A converted Knight stays a Knight until there's a quiet second. That fits "a long
   time, then it changed", and combat is where conversions happen.
2. **A one-for-one swap is never seen.** Dirtiness only compares the *total* count
   (`xsArrayGetSize(units)` against `unitsOwned`). If a Knight joins in the same second another unit
   is lost, the count doesn't change and nothing marks the list dirty at all. The Knight is only
   swept when some *later*, unrelated change happens.

### The mod starves its own sweep, on a schedule

`RunSeat` (`MercenarySpawn.xs:84-98`) places one soldier per game second, and `MercenarySpawnLoop`
runs all four seats (`AP_Constants.xs:97`) in parallel. Any multi-soldier pavilion muster therefore
moves the unit count every second for the length of the muster — Kereyid Tribe's 8 + 2 is a
ten-second window — and `UnitsanityChecks` takes the early return on every one of those ticks.
`ClearSpawnArea()` at muster start removes buildings, adding more. The mustered soldiers are immune
(`MercenarySpawn.xs:77`), so the victim is any non-immune unit already on the map. This is a
deterministic repro that needs no fighting.

### The blast radius is wider than caveman

The same two early returns also gate `EvictProfessions` (`:359`) and **`checkOwnedUnits`** (`:365`),
which is what sends the unitsanity location checks. `CheckProfessionLocations` has its own
`PROFESSION_SWEEP_SECONDS` backstop (`:350-352`) and survives; `checkOwnedUnits` does not. So during
busy play Ageipelago is *withholding unit location checks*, not merely delaying a cosmetic
knockdown. `unitsTransformed` (`:360`) pushes `checkOwnedUnits` back a further tick on top of that.

### Why the gate is there

`ApplyCaveman` is O(units × cavemanCount): `originalTypeOf` linear-scans the ledger (up to
`CAVEMAN_LEDGER_CAPACITY`, 400) for every unit, and `removeDeadCavemen` walks it once per sweep. At
200 pop that is tens of thousands of operations on the sim thread each tick. `findUnit` and
`canonicalTypeOf` are O(1) array lookups, so `checkOwnedUnits` is cheap by comparison. Any fix has
to keep a cost bound on the caveman sweep specifically — which is the argument for a seconds-based
backstop over sweeping unconditionally every tick.

### Ruled out

- **Conversion itself.** A converted Knight is an ordinary player-1 unit of type Knight, picked up
  by `xsGetPlayerUnitIds(1, -1, ...)`, not immune, and its row isn't caveman-exempt. Confirmed with
  the reporter.
- **Mercenary immunity.** A mercenary item has two routes: the pavilion route
  (`MercenarySpawn.xs:77`, immune) and the scenario route (`MercenaryItems.xs` sets a flag the
  scenario's own triggers read, not immune). A pavilion Knight could not have turned at all, so the
  reported Knight came through a non-immune route. Closed by the maintainer; nothing to chase, and
  the two routes also explain the [issue 01](01-caveman-scenario-rules.md) Kereyid monks with no
  contradiction.
- **Knight → Militia specifically.** The Knight line has no lower tier, so `cavemanTarget` falls
  through to `CAVEMAN_MILITIA` (`Caveman.xs:178`). Expected.

### Open, but not blocking

The KB has no measured answer on whether `xsGetPlayerUnitIds` sees garrisoned units
(`AoE2_AI_Modder/docs/agent/references/XS_MEASURED_BEHAVIOR.md` covers the function, not garrison).
If it doesn't, a unit sitting in a castle or transport is invisible until it exits and is knocked
down on exit. That is inherent and is not fixed by anything below.

## Comments

> *This was generated by AI during triage.*

### Triage Notes (2026-10-22)

**Rulings from the maintainer:**

- The Knight was **converted**. Conversion was already ruled out as the cause and stays ruled out.
- The mercenary-immunity question is **closed**. Pavilion route is immune, scenario route is not, so
  there is no contradiction to split out and no new ticket.

**What this settles:** all three original needs-info questions. How the unit was obtained is
answered and doesn't fork the work — trained, converted and scenario-granted units all sit on the
identical code path. What was happening at the time is answered by the mechanisms: both predict
"turns on the next quiet second", and the pavilion muster gives a repro that doesn't depend on the
reporter's memory of the fight.

> *This was generated by AI during triage.*

### Triage Notes (2026-10-26)

**Status:** back to needs-triage. The brief was marked ready-for-agent, but its design rested on a
cost nobody had measured. The maintainer asked for proof before accepting any part as
ready-for-agent, and the proof isn't there yet.

**The audit still holds.** Re-checked against the current XS: the two early returns are unchanged
at `Unitsanity.xs:336-347`.

**The brief gets `checkOwnedUnits`'s cost wrong.** It calls the function O(1), which is true of
`findUnit` and `canonicalTypeOf` only.
- For each unit with a unit row, `MarkRowOwned` reads `structGetInt(unit, "owned")`
  (`Unitsanity.xs:174`).
- That is a linear string comparison over the Unit struct's 13 attribute names
  (`structs.xs:586,123`), up to twice per unit.
- It is probably still cheap, but it isn't measured. See #33.

**Maintainer ruling: location checks stay after the knockdown.** A unit P1 owns for a moment before
its caveman knockdown does not check its location. The current order already does this, because
checks only run after a sweep that transformed nothing.

Running checks every tick, ahead of the sweep, would break this. A converted Knight with no Knight
items would check the Knight location before becoming a Militia. `transformUnit` also replaces the
unit with a new id (`Caveman.xs:184-197`), so a check on the tick of a transform would read a
stale snapshot.

So with caveman on, the checks stay tied to the sweep, and this ticket keeps them.

**Split:**
- **#33 (spike):** measure the per-tick cost of `ApplyCaveman` and `checkOwnedUnits` at about
  200 pop. Its answer table decides this ticket's fix shape: sweep every tick, add a backstop like
  `PROFESSION_SWEEP_SECONDS`, or first make `originalTypeOf` O(1).
- **#34:** location checks with caveman off. Nothing transforms there, so the checks can leave the
  gate once #33 shows they are cheap.
- **This ticket:** the caveman sweep, and the location checks that follow it, with caveman on.

**Brief lines superseded:**
- "`checkOwnedUnits(units)`: cheap (O(1) lookups … It can afford to run far more often than the
  caveman sweep." It is not O(1), and with caveman on it must not run ahead of the sweep.
- "An owned-unit location check fires within the same bound under the same conditions." This still
  stands, but only for checks that come *after* a settled sweep.

> *This was generated by AI during triage.*

### Triage Notes (2026-10-27)

**Status:** needs-triage, blocked by spike [#35](35-unit-id-lookup-spike.md). #33 is done, and the
design below came out of a grilling session with the maintainer. Only the choice of id lookup is
left, and #35 decides it.

**What #33 showed** (see its *Answer*):
- A full cavemanify pass costs about 20 game-ms at 200 units with an empty ledger, about 50 with a
  200-entry ledger, and about 130 with a full one. The location checks cost about 15.
- Once a second, either one is about 2% of game time. On every `highFrequency` tick, a full pass
  keeps only 56% of the tick rate, even with an empty ledger. The per-unit work (struct reads, the
  immune list) is too heavy to repeat 30 times a game second.
- #33's table placed this ticket in row 4, because of the ledger scan. The maintainer agreed that
  the 400-entry ledger is out of reach in play. A realistic worst case is about 200 entries.

**Maintainer rulings:**
- **Row 3 is rejected.** A seconds-based backstop like `PROFESSION_SWEEP_SECONDS` is too slow.
- **Delay bound:** high frequency is the aim. If that fails, once a second is tolerable. A unit is
  cavemanified within 1 s, and its location is checked within 2 s at worst, under any load.
- **Both early returns go** (`Unitsanity.xs:336-347`). The count skip has no other job that anyone
  knows of. History: `1a2c2b6` ("Fix unitsanity mode") added the count skip and the
  stop-after-cavemanify guard (`:360-362`) together. Before that, `600c4b9` swept, fetched the
  roster again and checked in one tick, so a removed Knight could still send its check. The guard is
  what fixed that, and it stays. The maintainer wants this confirmed in game: #35 question 4 and
  the muster test below cover it. The research skip goes as well, because the full-pass triggers
  below handle a research.
- **High frequency, new units only.** The rule runs on every tick and lists P1's unit ids, which the
  KB measures as too cheap to see. Only the units that are new to P1 since last tick are
  cavemanified and checked. A conversion or a one-for-one swap is caught, because the unit's id is
  new to P1.
- **Full pass only when an item arrives** (`refreshUnitLocks`, `Techsanity.xs:158`, which already
  set `unitsDirty`) **or a research finishes** (the research count). No timed pass. No scenario
  trigger is known to change a P1 unit's type in place. Packing and unpacking is already covered by
  `canonicalTypeOf`.
- **Location checks:** a cavemanified unit is checked on the next tick, because the
  stop-after-cavemanify guard stays. A new unit that was not cavemanified is checked on the same
  tick. The 2026-10-26 ruling holds: checks come after the cavemanify, never before.
- **Caveman off:** the same rule, without the cavemanify step. **#34 folds into this ticket.**
- **Professions:** `CheckProfessionLocations` keeps its 2 s timer. `EvictProfessions` runs on any
  tick where P1's unit list changed, so no less often than today and no more.
- **Dropped:** the claim that a failed `xsCreateUnit` in `transformUnit` (`Caveman.xs:188-191`) sends
  the wrong check. It depends on what `xsGetUnitCopyId` returns for a removed unit, which isn't
  recorded. The maintainer isn't worried about it.

**Vocabulary:** *cavemanify* and *original unit* are now in `worlds/age2de/CONTEXT.md`. Avoid
"knockdown" and "ceiling". New text uses the glossary terms. Older notes in this file are left as
written.

**Why #35:** the KB doesn't record whether `xsGetPlayerUnitIds` returns ids in order, how high ids
get, what a large XS array or `xsArrayResizeInt` costs, or whether a removed unit still shows in the
same tick. Those facts choose between a sorted walk, an id-indexed array and a hash table. The
maintainer confirmed that unit ids only go up.

**Next:** once #35 has its numbers, write a new Agent Brief from these rulings and #35's answer
table, then set this ticket's status.

## Agent Brief

> *This was generated by AI during triage.*

> **Superseded in full (2026-10-27).** Don't hand this brief to an agent. Its fix shape (a
> backstop sweep, with `checkOwnedUnits` called cheap) was replaced by the design in *Triage Notes
> (2026-10-27)*. A new brief is written after #35. It is kept here for its history only.

**Category:** bug

**Summary:** The unitsanity tick refuses to sweep on any tick where the unit count or research count
moved, so caveman knockdowns and unit location checks are withheld for as long as the roster keeps
changing — and a net-zero roster change is never noticed at all.

**Current behavior:**

The once-a-second `UnitsanityChecks` rule compares the player's unit count and research count
against the previous tick. If either moved, it records the new value, sets `unitsDirty`, and returns
without doing any work. `ApplyCaveman`, `EvictProfessions` and `checkOwnedUnits` therefore only run
on a tick where nothing changed since the tick before. Two failures follow:

- While the roster changes every second — a fight, a training queue, trigger spawns, or a pavilion
  mercenary muster placing one soldier per second — no sweep ever runs. A unit that should be
  knocked down keeps its real type indefinitely, and owned-unit location checks are not sent.
- A change that nets to zero (a unit gained in the same second another is lost, the common case for
  a conversion in combat) doesn't move the count, so the list is never even marked dirty. The new
  unit is only swept when some later, unrelated change happens.

**Desired behavior:**

A change to the roster is acted on within a bounded, short time regardless of how busy the game is,
and a net-zero change is still caught.

- Noticing a change and acting on it happen on the same tick. Recording new state must not consume
  the tick.
- There is an upper bound on how long a unit can hold a type caveman should have taken away, and on
  how long an owned-unit location check can be withheld. Neither depends on the game going quiet.
  `PROFESSION_SWEEP_SECONDS` is the existing pattern for this in the same rule.
- The bound holds for a unit that arrives during a net-zero second.

**Key interfaces:**

- `UnitsanityChecks` rule: the two early-return branches that set `unitsDirty` are the defect. The
  rule should still fetch the roster once per tick and share that array with everything it calls.
- `unitsDirty`: keep it as the "something changed, do the expensive pass" hint. It is also set from
  outside the rule when a tech or unit item arrives (`Techsanity.xs`, `Unitsanity.xs`), which is how
  a unit climbs back up after an item; that path must keep working.
- `ApplyCaveman(units)`: unchanged in behavior. It is the expensive call — O(units × cavemanCount)
  through `originalTypeOf`'s linear ledger scan — so it is the one that needs a cost bound, not
  `checkOwnedUnits`.
- `checkOwnedUnits(units)`: cheap (O(1) lookups through `findUnit` / `canonicalTypeOf`). It can
  afford to run far more often than the caveman sweep, and it is the one that sends locations.
- `unitsTransformed`: the rule currently returns after a transform without clearing `unitsDirty`, so
  checks are deferred another tick. Preserve the intent (re-sweep after transforms settle) without
  letting it extend the bound indefinitely.

**Acceptance criteria:**

- [ ] A unit that caveman should knock down is knocked down within a small bounded number of seconds
      while the unit count is changing every second — verified with a pavilion muster of a
      multi-soldier mercenary (e.g. Kereyid Tribe) with a non-immune unit of a locked line on the
      map.
- [ ] A unit gained in the same second another unit is lost is knocked down within the same bound.
- [ ] An owned-unit location check fires within the same bound under the same conditions.
- [ ] Receiving a unit or tech item still lets an already-knocked-down unit climb back to its new
      tier, with no regression to the `cavemanTargetsStale` / `unitsDirty` path.
- [ ] Mercenaries spawned at the pavilion are still never knocked down.
- [ ] No measurable sim-thread stall at high population: the caveman sweep does not run every tick
      at 200 pop.
- [ ] `./xs-check.exe -I . -- AP_<Scenario>.xs` is clean for the scenario entry points (run from the
      xs folder; needs v0.2.30 or later).

**Out of scope:**

- Making mercenaries, monks, ships or carts caveman-exempt. Routing and exemption rulings are
  settled elsewhere; see issues [01](01-caveman-scenario-rules.md) and
  [16](16-caveman-scenario-ships-and-carts.md).
- Changing what `cavemanTarget` picks, including the Militia fallback for a line with no lower tier.
- The garrison question above. If `xsGetPlayerUnitIds` hides garrisoned units, a unit knocked down
  on leaving a building is expected and is not this ticket.
- Any change to the apworld logic. This is game-side only.
