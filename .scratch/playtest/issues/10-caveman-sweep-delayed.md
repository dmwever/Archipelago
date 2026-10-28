# 10: Caveman knockdowns and unit checks are starved while the unit count keeps moving

**Reported:** 2026-10-20, playtesting

**Status:** ready-for-human (awaiting playtest)

**Blocked by:** none. #33 and #35 are done. #34 (caveman-off checks) folds into this ticket.

**Related:** [#41](41-cavemanify-garrisoned-units.md) (the garrison fix, split out of #35's follow-up)

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

> *This was generated by AI during triage.*

### Triage Notes (2026-10-27, after #35)

**Status:** ready-for-agent. The new brief is below, under *Agent Brief*.

**#35 decided the design: row 1, the sorted walk.**
- `xsGetPlayerUnitIds(1, -1)` returns ids in strictly rising order, and a converted unit lands at
  its sorted place. So this tick's list and last tick's can be walked side by side, with no array
  sized to the ids.
- Only new units search the caveman ledger, so the ledger stays a list.

**Removed units still read as their old selves.** #35 measured that a unit taken off by
`xsRemoveUnit` is still listed, still exists and still has its old type on the next tick. It is
gone by 2 s. How many `highFrequency` ticks that covers is not measured.
- The walk never treats such an id as new.
- A full pass would see it, though: an item arriving the tick after a cavemanify would check the
  removed Knight as a Knight.
- So any id the mod removed is never cavemanified or checked while it is still listed.

**Villager jobs (maintainer, 2026-10-27).**
- `evictProfession`, `EvictProfessions` and `RefreshProfessions` stay as they are. A grilling round
  on moving eviction into the walk was dropped.
- Fact-checked: today P1 can't send a villager job location without its profession.
  - A locked job's type is disabled and out of the villager swap group, so P1's villagers can't
    switch into it.
  - An arrival in a locked job raises the unit count. `CheckProfessionLocations` only runs on a
    clean tick, after a pass where eviction ran and transformed nothing.
  - An evicted villager, still listed beside its replacement, keeps the count up, so the 2 s timer
    stays held until the stale id drops out.
- The one narrow hole today is the net-zero second (mechanism 2), which this ticket closes.
- **Ruling:** the redesign drops the count skip that does that holding, so the brief adds one line.
  A villager that `EvictProfessions` replaced never sends its job location.

**When `EvictProfessions` runs (maintainer, 2026-10-27).**
- The earlier ruling ran it on any tick where P1's list changed. On the every-tick rule, in a
  fight, that is nearly every tick.
- One call is likely the most expensive thing the rule does: a scan of the unit table, plus a
  `baseVillager` scan of the table and an `xsGetPlayerUnitIds` call for each locked job. That is
  several thousand struct reads. This is estimated from code; #33 didn't measure it.
- **Ruling:** the rule calls it only on a tick where the walk finds a new unit whose type is a
  villager job with its row still locked.
  - A villager can only be in a locked job by arriving in it, because a locked job is out of the
    swap group. So that is enough.
  - An item arriving already evicts through `RefreshProfessions`, so the full pass adds no call.
  - The function itself stays as it is.

**Split:** #35's follow-up asked `transformUnit` to put a garrisoned unit's replacement back in its
container. That bug exists whatever the rule's timing, so it is
[#41](41-cavemanify-garrisoned-units.md), not this ticket.

### Implementation (2026-10-27)

> *This was generated by AI.* In the working tree on Ageipelago `0.3.0`, uncommitted. The
> `xs-check` box is ticked: all 18 entry points report only the 6 warnings that were there before.
> The other boxes are the maintainer's in-game playtest.

Three files: `Unitsanity.xs`, `Caveman.xs`, `Professions.xs`. No apworld change.

- **`UnitsanityChecks`** is `highFrequency` and has no early returns. `unitsOwned` and `testArray`
  are gone.
  - It lists P1's units once a tick. `collectNewUnits` walks this tick's list beside last tick's
    (`unitScan` / `lastUnitScan`, swapped by `swapUnitScans`) and returns the new ids, or `-1`.
  - A full pass (`unitsDirty`, now also set by a research rise) uses every listed unit instead.
  - Order: `ApplyCaveman`, then `EvictProfessions` only if `anyUnitWithLockedProfession`, then stop
    if `unitsTransformed`, else `checkOwnedUnits`. `CheckProfessionLocations` keeps its 2 s timer
    and runs only on a tick that removed nothing.
  - On a tick that stops, last tick's list is not replaced. The next tick sees the same units as
    new again, so an untransformed new unit still gets its location check.
- **Untracked units:** `UntrackUnit` / `IsUnitUntracked`, a list of `UNTRACKED_UNIT_CAPACITY`
  (256) ids. `transformUnit` and `evictProfession` untrack every unit they remove.
  `pruneUntrackedUnits` drops an id once P1's list no longer has it (binary search on the sorted
  list). `ApplyCaveman`, `checkOwnedUnits`, `CheckProfessionLocations`,
  `anyUnitWithLockedProfession` and `evictProfession` skip untracked ids.
- **`removeDeadCavemen`** runs at most every `CAVEMAN_REAP_SECONDS` (2) inside `ApplyCaveman`.

For the maintainer to rule on:

- **`evictProfession` skips untracked ids.** The brief says how villagers are evicted must not
  change. Without the skip, a second call while an evicted villager is still listed would create
  a duplicate villager.
- **The 256 cap.** Past it, `UntrackUnit` posts a red chat line and the extra ids go unprotected,
  so a transformed unit's location could be sent on the retry tick.
- **The 2 s check bound** is not strict if a unit that needs cavemanify arrives on every tick.
  Each stopped tick re-walks a growing set until one tick removes nothing.
- **Constants.** `UNTRACKED_UNIT_CAPACITY` and `CAVEMAN_REAP_SECONDS` are file-local `const`, like
  `Caveman.xs`'s existing ones, not `extern const` in `AP_Constants.xs` as `xs.md` asks.

## Agent Brief

> *This was generated by AI during triage.* It replaces the brief below, and the rulings in the
> Comments above are its background.

**Category:** bug

**Summary:** The unitsanity rule waits for a quiet second before it cavemanifies or checks
anything. Make it act on every tick, for the units that are new to P1, and keep the full pass for
when an item arrives or a research finishes.

**Current behavior:**

The `UnitsanityChecks` rule runs once a second. Two things make it return without doing work:
- **The unit count changed** since last tick. It records the count, sets `unitsDirty`, and returns.
- **The research count rose.** It does the same.

`ApplyCaveman`, `EvictProfessions` and `checkOwnedUnits` therefore only run on a tick where nothing
changed since the tick before. Two failures follow:
- While the unit count changes every second, nothing is cavemanified and no unit location is
  checked. That happens in a fight, during a training queue, or during a pavilion muster, which
  places one soldier a second.
- A unit gained in the same second another is lost doesn't move the count, so it is never noticed
  until some later change.

This holds with caveman on and off. With caveman off, it is location checks alone that wait.

**Desired behavior:**

- **The rule runs on every tick** (`highFrequency`) and lists P1's unit ids once per tick, sharing
  that list with everything it calls. Both early returns go.
- **New units:** a unit is new to P1 when its id is in this tick's list and not in last tick's. The
  list comes back in rising id order, so the two lists are compared by walking them side by side.
  Don't add an array indexed by unit id, or a hash table.
  - A conversion, or a one-for-one swap, is a new id, so it is caught.
  - A garrisoned unit stays in the list, so leaving a garrison is not new.
- **On each tick, in this order:**
  1. With caveman on, cavemanify the new units only.
  2. If a new unit's type is a villager job whose row is still locked, run `EvictProfessions`.
     Never call it otherwise, on a normal tick or a full pass. An item arriving already evicts
     through `RefreshProfessions`.
  3. If either step removed a unit, stop. Nothing is checked on that tick.
  4. Otherwise, check the locations of the new units.
  - With caveman off, step 1 is skipped. The rest is the same.
- **A full pass** runs all of the above over every listed unit, instead of the new ones. It runs on
  the tick after one of these, and at no other time:
  - An item arrives. `unitsDirty` already marks this, from the unit and tech item handlers.
  - P1's research count rises.
  - There is no timed full pass.
- **Ids the mod removed:**
  - A unit removed by cavemanify or by `EvictProfessions` stays listed, existing and typed as its
    old self for at least one more tick.
  - Such an id is never cavemanified again, never sends a unit location and never sends a villager
    job location while it is still listed. A full pass included.
  - Cavemanify already marks its removals in the ledger as `CAVEMAN_REMOVED`.
  - For `EvictProfessions`, the rule may find out which ids it removed. Two ways are fine: compare
    the listed ids of locked job types before and after the call, or have the call report them.
  - Which villagers get evicted, and how, must not change.
- **Profession checks:**
  - `CheckProfessionLocations` keeps its 2 s timer.
  - It doesn't run on a tick that removed a unit, and it skips removed ids that are still listed.
- **Bounds, under any load:**
  - A unit is cavemanified within 1 game second of joining P1, and on the next tick where possible.
  - Its location is checked within 2 game seconds at worst.
- **Checks stay after the cavemanify, never before it.** A converted Knight with no Knight items
  never sends the Knight location. It is checked as what it was cavemanified into, on the next tick.

**Key interfaces:**

- `UnitsanityChecks` rule: its schedule, its two early returns, and the dirty and transformed
  handling. Most of the change is here.
- `unitsDirty`: keep it as the "full pass needed" flag, set from outside the rule when an item
  arrives. The unit-count use of it goes. A rise in the research count also asks for a full pass.
- `unitsOwned` and `unitsResearchCount`: they change meaning, or are replaced by the previous
  tick's id list.
- `ApplyCaveman(units)`: called with the new units on a normal tick, and with every unit on a full
  pass. A normal tick must not walk the whole ledger for each listed unit. The ledger may still be
  cleared of dead units, but not on every tick at full cost.
- `checkOwnedUnits(units)`: called with the same set as `ApplyCaveman`. It must skip ids the mod
  removed.
- `unitsTransformed`: still the signal that a step removed a unit, so the tick stops.
- `EvictProfessions` / `evictProfession` / `RefreshProfessions`: behavior unchanged. Only when
  the rule calls `EvictProfessions` changes: only on a new unit in a locked villager job. The
  per-unit test must be an O(1) lookup, such as `isProfessionType` plus the row's `locked` flag,
  not a table scan. See the removed-id rule above.
- `CheckProfessionLocations(units)`: keeps the 2 s timer, gated as above.

**Acceptance criteria:**

The in-game criteria are run by the maintainer, in the `XsTesting` setup from #33 and #35 or in a
live scenario. The agent's job is the code and the XS check.

- [ ] With caveman on, during a pavilion muster of a multi-soldier mercenary (Kereyid Tribe), a
      separate, non-immune unit of a locked line placed on the map is cavemanified within 1 game
      second.
- [x] A unit converted in the same second as P1 loses another unit is cavemanified within 1 game
      second.
- [x] A converted Knight with no Knight items never sends the Knight location. The location of
      what it became is checked within 2 game seconds.
- [x] With an item arriving on the tick after a cavemanify, the removed unit's location is not
      sent. This also answers #35's question 4 in play.
- [x] Receiving a unit or tech item still raises cavemanified units of that line, up to their
      original unit.
- [x] Finishing a research triggers one full pass.
- [x] With caveman off, during a pavilion muster of a multi-soldier mercenary (Kereyid Tribe), a
      separate unit P1 trains has its location checked within 1 game second.
- [x] With the Shepherd profession missing, converting an enemy Shepherd never sends the Shepherd
      location, on the tick it arrives or while the evicted villager is still listed.
- [x] Villager job locations are still checked within the 2 s timer once their profession is held.
- [x] A fight in which no unit arrives in a locked villager job never calls `EvictProfessions`.
- [x] Pavilion mercenaries are still never cavemanified.
- [ ] At about 200 P1 units in a fight, the rule doesn't move the `highFrequency` tick rate outside
      a baseline's noise, by #33's method.

      > **Resolved by run D, and it does not pass as worded.** Baseline noise is 1.5%; the rule
      > costs **8.0%** at 205 units with two new ids a tick (windows 4 and 6: 8.6%, 7.4%), and
      > **5.4%** idle with no new units at all (5.2%, 5.6%). A calibration workload of 200
      > struct reads a tick was measured at 37.9% and 38.6%, so the meter resolves cost and
      > reproduces it. Of the 8%, 5.4 points are the fixed per-tick walk and only 2.6 are the
      > new-unit work this ticket added. For comparison, #33 measured a full pass every tick at
      > a 44% cost. **Maintainer call:** accept 8%, or reword the criterion against #33's 44%
      > rather than against baseline noise. See *Run D results* in `spikes/10/README.md`.
- [x] `./xs-check.exe -I . -- AP_<Scenario>.xs` is clean for every scenario entry point (run from
      the xs folder; needs v0.2.30 or later).

> Ten boxes above are ticked by the XsTesting harness runs A, B and C of 2026-10-27, not by a live
> scenario. See *Harness run A* in the Comments and
> [`spikes/10/README.md`](../spikes/10/README.md) for exactly what each rests on.

**Out of scope:**

- Putting a garrisoned unit's replacement back in its container: [#41](41-cavemanify-garrisoned-units.md).
- What `EvictProfessions`, `evictProfession` or `RefreshProfessions` do, beyond the rule learning
  which ids they removed. That includes eviction of garrisoned villagers.
- Making `originalTypeOf` O(1), or changing the ledger's capacity.
- Which units are caveman-exempt, and what `cavemanTarget` picks, Militia fallback included.
  Settled in #01 and #16.
- Any apworld change.

## Agent Brief (superseded)

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
