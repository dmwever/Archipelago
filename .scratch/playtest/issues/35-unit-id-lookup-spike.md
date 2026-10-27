# 35: Spike: can the unitsanity rule find P1's new units by id on every tick?

**Reported:** 2026-10-27, triage of [#10](10-caveman-sweep-delayed.md)

**Type:** spike

**Status:** done

**Blocks:** #10

## Question

#10 makes the `UnitsanityChecks` rule run on every tick (`highFrequency`) and do the expensive work
only for units that are **new to P1**: ids in this tick's `xsGetPlayerUnitIds(1, -1)` list that
were not in last tick's. It cavemanifies those units and checks their locations. A full pass runs
only when an item arrives or a research finishes.

To find the new units, the rule needs a fast way to look up a unit by its id. Each unit it
cavemanifies also needs its **original unit**. Today that is the caveman ledger, and #33 measured
its linear scan as the main cost of a full pass. Three designs are possible:

- **Sorted walk:** if the list comes back in id order, walk this tick's list and last tick's list
  side by side. No big array is needed.
- **Id-indexed array:** one int slot per unit id, holding "not seen", "seen", or the original unit.
- **Hash table:** a fixed number of slots, keyed by unit id.

The KB doesn't record the facts that pick one (see the Explore report summarised in #10's
2026-10-27 triage notes). This spike measures them.

## What is known

- **Unit ids only go up** (maintainer, 2026-10-27). They grow as far as the game needs, with no
  fixed top.
- **Measured (KB):** the ids are the scenario editor's reference ids, and listing a player's unit
  ids on every tick costs too little to measure (`XS_MEASURED_BEHAVIOR.md:256-259, 280-284`).
- **Documented only:** `xsArrayResizeInt(arrayId, newSize)` exists. Its cost and any size limit are
  not recorded.
- **Not recorded:** the size limit of an XS array, the order of `xsGetPlayerUnitIds`, whether a
  removed unit still shows later in the same tick, and whether garrisoned units or buildings are in
  the list.
- **From #33:** a full cavemanify pass costs about 20 game-ms at 200 units with an empty ledger and
  about 130 with a full one. A struct read costs about 70–80 µs per unit. These are the figures to
  beat.

## Questions

1. **Id range.** What is the highest unit id near the end of a long scenario (an Attila or Genghis
   scenario played to the end)? Do projectiles or corpses use up ids?
2. **Array cost.** What does an int array of that size cost to create? What does `xsArrayResizeInt`
   cost as it grows in steps? What do 200 reads cost on every tick?
3. **List order.** Does `xsGetPlayerUnitIds` return ids in rising order? Where does a unit with an
   old id that P1 has just converted appear in the list?
4. **Removed units.** After `xsRemoveUnit`, does the unit still appear in `xsGetPlayerUnitIds`, or
   pass `xsDoesUnitExist`, or return its type from `xsGetUnitObjectId`, later in the same tick? And
   on the next tick?
5. **Garrisons and buildings.** Does the list include units garrisoned in a building or a
   transport? Does it include buildings when the type is `-1`?

## Method

- Put the harness in a throwaway XS file that `.gitignore` covers, never in a live module. Delete it
  once the numbers are recorded. The `XsTesting.aoe2scenario` setup from #33 suits questions 2–5.
- **Q1:** in the long scenario, log every 30 game seconds the highest id across all players' lists.
  Also create and remove one throwaway unit and log its id, which shows the next id the game will
  hand out, including ids used by objects no list shows.
- **Q2:** use #33's tick-rate method: firings of one `highFrequency` rule per ~10 game seconds,
  baseline against phase, extra game-ms per firing. Phases: create an array at the Q1 size and at
  twice it; grow one with `xsArrayResizeInt` in steps of 1,000; 200 reads of it per tick.
- **Q3:** log the list for a few ticks at about 200 units. Then convert a unit with a Monk and log
  the list again.
- **Q4:** remove a unit, query the three functions straight after in the same rule, then again on
  the next tick.
- **Q5:** compare the list before and after garrisoning a unit in a building and in a Transport
  Ship. Count the buildings in the list.

## Harness

**Q1 is synthetic** (maintainer, 2026-10-27): rather than logging a long Attila or Genghis
scenario, two players fight in XsTesting with their units within 4 tiles of each other. The
answer is a rate (ids used per unit killed, per shot), not the highest id at a real scenario's end.

- **Script:** `Test.xs` in the Ageipelago xs folder (gitignored), run by `XsTesting.aoe2scenario`.
  Delete it back to its stub once the numbers are recorded.
- **Ledger:** `.scratch/playtest/spikes/35/ledger.json`. Decode the run with
  `kit xsdat decode default1.xsdat --ledger ledger.json --text`.
- **Run:** start XsTesting at any speed and leave it alone. The chat shows each stage.
  When it says *done, file closed*, quit the scenario so the file flushes. Copy
  `profile/default1.xsdat` to `spikes/35/run1.xsdat`. It takes about 5–6 game minutes.
- **What it does, in order:**
  - **Q3/Q4/Q5, quiet map:** 200 P1 units in rotating types (Militia, Archer, Villager, Scout),
    created after one P2 Villager so that Villager's id is older than all of them.
    - **Q3:** logs the list on 3 ticks. Converts one P2 Villager by script and another with a
      Monk, then logs where each lands in the list, on that tick and on the next.
    - **Q4:** removes one unit. Then removes another and creates its replacement in the same tick,
      the way cavemanify does. Each is queried on that tick and on the next.
    - **Q5:** garrisons a Militia in a Castle and another in a Battering Ram, then ungarrisons
      both, logging list membership at each step. Logs whether the Town Center, Castle and Ram
      are in the `-1` list.
  - **Q2, tick rate:** 10-second windows, with a baseline before each phase:
    1. 200 reads of a 200-slot array (control)
    2. resize 1 → 10k → 1, every tick
    3. resize 1 → 50k → 1
    4. resize 1 → 100k → 1
    5. resize 1 → 200k → 1
    6. grow by 1,000 every tick
    7. 200 reads of a 200k array
    8. **the sorted walk itself:** list P1's units and walk them against last tick's list
    9. **the id-indexed design itself:** list P1's units and read and write a 200k `seen` array
  - **Q2, size limit:** creates arrays of 10k, 50k, 100k, 200k, 400k, 1M and 4M ints, then reads
    each one's size and last slot.
  - **Q1, fights:** 60 Militia against 60 Militia (corpses, no projectiles), then 60 Archers
    against 60 Archers. Each side stands in two rows of 30, 2–4 tiles from the other side.
    Every 5 s for 60 s, the harness creates and removes a Gaia probe unit to read the next id,
    and logs it with the highest listed id, each side's survivors, and the count of units the
    script has created. Ids used beyond the script's own count come from corpses or projectiles.

## Answer this spike must give

| Result | What #10 then does |
| --- | --- |
| The list is in rising order, converted units included | **Sorted walk.** No big array. Only new units search the ledger, and there are few per tick, so the ledger can stay a list. A full pass, on an item or a research, stays a rare one-off cost. |
| Not in order, and the id-indexed array is cheap at the real id range | **Id-indexed array** for both "seen" and the original unit. The ledger list stays only to clear out dead units. |
| Not in order, and the array is too costly at the real id range | **Hash table.** It is more code, so #10 is re-triaged. |
| A removed unit still appears later in the same tick | The stop-after-cavemanify guard stays essential. The new-units comparison must not treat the removed id as still owned. |
| Garrisoned units are not in the list | A unit leaving a garrison shows up as new and gets a pass. That is cheap and correct. #10's garrison note becomes measured. |
| Buildings are in the list | Only a volume cost. `findUnit` skips them, as it does today. |

Record the numbers here under `## Answer`, then re-triage #10.

## Answer

> *This was generated by AI from one in-game run on 2026-10-27 (`spikes/35/run1.xsdat`, which
> passed 581 of 581 ledger checks with its footer present).*

**Short version:**
- **#10 takes row 1, the sorted walk.** `xsGetPlayerUnitIds(1, -1)` returned ids in strictly
  rising order on every tick. Units of four types were created interleaved, and the list still
  wasn't grouped by type. An old-id unit that P1 converted showed up at its sorted place, not at
  the end.
- **A removed unit is still listed, still exists and still has its type on the next tick too,**
  not just later in the same tick. The stop-after-cavemanify guard stays essential.
- **Projectiles use ids: about one per arrow.** Corpses use about one per death. Even an idle
  map uses about 1–1.5 ids per game second.
- **Buildings are in the `-1` list.**
- **Garrisoned units stay in the list.** Both Militia went in (maintainer, watching the run) and
  were listed throughout, so leaving a garrison is not a new unit.
- **Q2 hit the meter's ceiling.** No phase moved the tick rate, so this run gives only an upper
  bound on each cost, not a per-call figure.

### Q3: list order

| Record | Count | Rising | Where the id landed |
| --- | --- | --- | --- |
| ticks 1–3 | 206 | yes, 0 descents | ids 91 (Town Center) to 693 |
| script convert of id 491, same tick | 207 | yes | index 5 (sorted place), listed at once |
| the same, next tick | 207 | yes | index 5 |
| Monk convert of id 492 (8 s) | 208 | yes | index 6 (sorted place) |
| the same, next tick | 208 | yes | index 6 |
| newly created id 708 | 209 | yes | index 208, the end |

- The 200 quiet units rotated Militia, Archer, Villager and Scout as they were created, so a
  list grouped by type would have shown descents. It showed none.

### Q4: removed units

| Case | Tick | `xsRemoveUnit` | In list | `xsDoesUnitExist` | Object id | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| remove 709 | same | true | yes | true | 74 | 1 |
| remove 709 | next | — | yes | true | 74 | 1 |
| remove 710, create 711 there | same | true | yes | true | 74 | 1 |
| remove 710, create 711 there | next | — | yes | true | 74 | 1 |

- The replacement, 711, was in the list on the tick it was created.
- When the removed ids finally drop out is not pinned down. The list count two ticks later fits
  both removals having taken effect, but only if id 713, which went to something the script did
  not create next to the Castle, is a listed P1 object.

### Q5: garrisons and buildings

- **Buildings:** the Town Center (91) and the new Castle (712) were in the `-1` list. So was the
  Ram (714).
- **Garrisons:**
  - Both Militia (715 into the Castle, 716 into the Ram) were still listed, existing and owned
    after the full 20 s wait. The wait ended on its timeout, not because they left the list.
  - 8 s after the ungarrison order, they were still listed.
  - The maintainer saw both go in. So garrisoned units stay in the list, in a building and in a
    transport alike.

### Q2: array cost and size limit

Firings per 10-second window, at 60 firings per game second:

| Window | Phase | Firings |
| --- | --- | --- |
| baselines (10) | — | 592–601 |
| 1 | 200 reads, 200-slot array | 596 |
| 3 | resize 1 → 10k → 1, every tick | 597 |
| 5 | resize 1 → 50k → 1 | 599 |
| 7 | resize 1 → 100k → 1 | 597 |
| 9 | resize 1 → 200k → 1 | 601 |
| 11 | grow by 1,000 every tick (reached 600,000) | 599 |
| 13 | 200 reads, 200k array | 596 |
| 15 | sorted walk against last tick's list (206 ids) | 595 |
| 17 | id-indexed `seen` read and write (206 ids) | 597 |

- **Every phase sits inside the baselines' ±0.75%.** The rate was pinned at 60 firings per game
  second, the engine's turn cap. In #33 the rate moved from 34 to 45, which is why costs showed
  there.
- So the method can't resolve a per-call cost here. It shows that none of these phases pushed a
  turn past its budget, at about 200 units on a quiet map.
- **Size limit:** none found up to 4,000,000. Arrays of 10k, 50k, 100k, 200k, 400k, 1M and 4M
  were created at full size and read back their last slot.

### Q1: how fast ids are used

The harness created its first unit at id 491. The ids below that went to the map's own objects.

| Fight | Ids used in 60 s | Deaths | Ids per 5 s at the peak |
| --- | --- | --- | --- |
| Militia, 60 against 60 | 171 (1074 → 1245) | 82 | 25 |
| Archers, 60 against 60 | 1,178 (1366 → 2544) | 104 | 309 |

- **Background:** with no deaths and no shots, ids still went up 4–12 per 5 s, beyond the probe
  itself. Over the 3½ quiet minutes of Q2, about 240 ids went this way. The source is unknown.
- **Corpses:** in the Militia fight, each 5-second step used about one id per death on top of
  that background.
- **Projectiles:** in the Archer fight's first 10 s, about 117 archers used about 515 ids beyond
  deaths and background. That is roughly one id per arrow at a 2-second reload.
- **Not the highest id:** this run gives rates, not the highest id at a real scenario's end. A
  long fight with sustained archery, towers or castles can use thousands of ids a minute, so a
  real scenario could plausibly reach six figures. That doesn't matter for row 1, because the
  sorted walk needs no array sized to the ids.

### Against the table

| Result | Verdict |
| --- | --- |
| The list is in rising order, converted units included | **Yes.** #10 takes the sorted walk. |
| Not in order, and the id-indexed array is cheap | Not needed. For the record: no phase, even 600k slots, moved the capped tick rate. |
| Not in order, and the array is too costly | No. |
| A removed unit still appears later in the same tick | **Yes, and on the next tick too.** The guard stays. Since a removed id is in both ticks' lists, the walk never treats it as new. A full pass, though, would still see it. |
| Garrisoned units are not in the list | **No, they stay listed.** A unit leaving a garrison is not new, so the walk gives it no pass. A unit trained or converted gets its pass when it first appears, garrisoned or not. What cavemanify does to a unit inside: see the follow-up below. |
| Buildings are in the list | **Yes.** It's a volume cost only. |

## Follow-up: cavemanify on a garrisoned unit

> *This was generated by AI from one in-game run on 2026-10-27 (`spikes/35/garrison-run1.xsdat`,
> which passed 218 of 218 checks against `garrison-ledger.json`).*

- **Setup:** one Man-at-Arms garrisoned in a Castle, one in a Battering Ram, and one left outside
  as a control. Each was swapped for a Militia exactly as `transformUnit` does it: read the
  position, `xsRemoveUnit`, then `xsCreateUnit` at that position with `checkCollision` false.
- **Then:** the new Militia were ordered to walk 20 tiles south, and both containers were told to
  ungarrison.

| | Castle | Ram | Control |
| --- | --- | --- | --- |
| Garrisoned in (`xsGetGarrisonedInUnitId`) | Castle, after 2 s | Ram, after 2 s | −1 |
| Position read while inside | the Castle's centre (30, 60) | the Ram's centre (45, 70) | its own |
| Same tick as the swap: old unit garrisoned in / container holds | −1 / 0 | −1 / 0 | — |
| Same tick and next tick: old unit listed, exists | yes, yes | yes, yes | yes, yes |
| 2 s later: old unit listed, exists | no, no | no, no | no, no |
| New unit garrisoned in | never | never | never |
| New unit 15 s after the move order | **still at (30, 60)** | (45.5, 60.0), walking | **gone** |
| 8 s after ungarrison | still at (30, 60) | (45.5, 52.8) | gone |
| Old unit back out after ungarrison | no | no | no |

- **Removal takes a garrisoned unit out of its container on the same tick.** The container is
  empty at once, the old unit is gone within 2 s, and ungarrisoning brings nothing back.
- **The replacement lands on the container's centre, not inside it.**
  - From a Castle, it sat at the Castle's centre for 23 s despite its move order, stuck in the
    footprint.
  - From a Ram, it walked off.
- **The control's replacement vanished** between 2 s and 17 s. It no longer existed and was no
  longer listed. Nothing in the harness removes it.
- **Seen (maintainer):** the Castle's Militia stood stuck on the Castle. The control's Militia
  most likely died, so its row says nothing about transforming.

### Re-garrisoning the replacement

> *Generated by AI from one in-game run on 2026-10-27 (`spikes/35/regarrison-run1.xsdat`,
> which passed 218 of 218 checks against `regarrison-ledger.json`).*

- **The maintainer's suggestion:** after the swap, order the replacement into the container the
  old unit was in. XS can't create a unit already garrisoned, so it takes a separate
  `xsTaskUnits(…, cActionTypeGarrison, …, containerId)` order.
- **The cases:** a Castle and a Ram with the replacement created at the container's centre, as
  `transformUnit` does today, and a second Castle with the replacement created 3 tiles out.

| | Castle, centre | Ram, centre | Castle, 3 tiles out |
| --- | --- | --- | --- |
| Replacement garrisoned in, on the swap tick | the Castle | the Ram | the Castle |
| Container holds, on the swap tick | 1 | 1 | 1 |
| The same on the next tick, at 2 s and at 10 s | unchanged | unchanged | unchanged |
| After ungarrison | out at (34.8, 63.9), alive | out at (44.8, 71.1), alive | out at (84.8, 83.9), alive |

- **It works, and on the same tick.** The garrison order took effect before the rule's next
  line. The replacement was inside, the container held one, and the old unit was out. Even the
  Castle-centre replacement, which last run was stuck in the footprint, went straight in.
- **Ungarrisoning brings out the replacement, alive and free to move.** The old unit never
  reappears.
- **Where the replacement is created makes no difference.** The fallback spot isn't needed.
- **Not covered:**
  - A full container. The old unit's slot is freed on the same tick, so the replacement should
    fit, but this wasn't run.
  - A replacement the container won't accept. For example, a Ram only takes infantry. Cavemanify
    keeps a unit in its line, so the class should match, but a line that crosses classes would
    be left standing on the container's centre.

**For #10:** when the unit being transformed has `xsGetGarrisonedInUnitId` of 0 or above,
`transformUnit` should order the replacement into that container on the same tick. It then
stays garrisoned, and there is no stuck unit and no deferred list. The walk's garrison rule
stands: a unit gets its pass when it first appears, garrisoned or not.

### Which containers take a garrison order

> *This was generated by AI from `spikes/35/containers-run2.xsdat`, run on 2026-10-27 in
> `TS_Spike.aoe2scenario` (XsTesting plus a water square at 90–119 on both axes). The run passed
> 555 of 555 checks against `containers2-ledger.json`. Garrison fields are from
> `kit dat unit <dat> 1 <id>`.*

- **Method:** each unit was created on its container's own spot and ordered in on the same tick.
  Nothing had to walk.
  - `containers-run1.xsdat`, an earlier run that spawned units 2–5 tiles out, is void for the
    refusals: a unit that never moved there can't tell refusal from pathing.
- **Then:** each unit was swapped by `transformUnit`'s steps, and the replacement was ordered back
  into the container on the swap tick.

| Container | `garrison_type` in the dat | Unit | Got in (10 s) | Replacement re-garrisoned | Out on ungarrison |
| --- | --- | --- | --- | --- | --- |
| Town Center | 11 | Man-at-Arms | yes | yes, same tick | yes |
| Watch Tower | 11 | Man-at-Arms | yes | yes, same tick | yes |
| Donjon | 11 | Pikeman | yes | yes, same tick | yes |
| Siege Tower | (unit) | Man-at-Arms | yes | yes, same tick | yes |
| Transport Ship | (unit) | Man-at-Arms | yes | yes, same tick | yes |
| Castle (earlier run) | 15 | Man-at-Arms | yes | yes, same tick | yes |
| Battering Ram (earlier run) | (unit) | Man-at-Arms | yes | yes, same tick | yes |
| Barracks | 0 | Man-at-Arms | **no** | — | — |
| Archery Range | 0 | Crossbowman | **no** | — | — |
| Stable | 0 | Knight | **no** | — | — |
| Monastery | 0 | Monk | **no** | — | — |
| Dock | 64 | War Galley | **no** | — | — |

- **Wherever a garrison order is accepted, the re-garrison works on the same tick.** The
  replacement comes out alive on ungarrison.
- **The refusals are the buildings whose `garrison_type` is 0.** Barracks, Archery Range, Stable
  and Monastery all have a garrison capacity of 10 but accept no order.
  - DE is understood to fill these buildings another way: a unit trained with the building's
    gather point set on itself stays inside. This is game knowledge and wasn't measured here.
  - So P1 *can* have units garrisoned there, and a re-garrison order for their replacement would
    be refused. The replacement would be left on the building's centre, trapped like the Castle
    case before re-garrisoning.
  - **Not yet run:** a unit put inside that way, then swapped.
- **The Dock refused a War Galley** despite `garrison_type` 64. That may mean only some ships, or
  only ships that sail in, can enter. Not resolved.

### Force garrison: `xsSetUnitProperty(unit, cUnitGarrisonedInId, container)`

> *This was generated by AI from `spikes/35/force-run1.xsdat`, run on 2026-10-27 in
> `TS_Spike.aoe2scenario`. The run passed 569 of 569 checks against `force-ledger.json`.*

- **Source:** `cUnitGarrisonedInId` (5) is a unit property that can be both read and set. The
  fourth argument of `xsSetUnitProperty` is documented as "force when setting garrisoned in ID"
  (the UGC guide, mirrored in AoE2_AI_Modder's `XS_Training/…/AoE2DE_UGC_Guide`, functions
  `xsSetUnitProperty` and constants §32).
- **Method:** each unit was created on its container's spot and garrisoned by the property call,
  with no walking.
  - Then `transformUnit`'s steps swapped the unit, and the replacement was garrisoned by the same
    call.
  - Last, every container was ordered to ungarrison.

| Container | Unit → replacement | Force | In, same tick | Replacement in, same tick, and at 3 s | Out on ungarrison |
| --- | --- | --- | --- | --- | --- |
| Barracks | Man-at-Arms → Militia | 0 | yes | yes | yes |
| Barracks | Man-at-Arms → Militia | 1 | yes | yes | yes |
| Archery Range | Crossbowman → Archer | 1 | yes | yes | yes |
| Stable | Knight → Scout Cavalry | 1 | yes | yes | yes |
| Monastery | Monk → Monk | 1 | yes | yes | yes |
| Dock | War Galley → Galley | 1 | yes | yes | **no, still inside at 10 s** |
| Dock | War Galley → Galley | 0 | yes | yes | **no, still inside at 10 s** |
| Castle | Man-at-Arms → Militia | 1 | yes | yes | yes |
| Battering Ram | Knight → Scout Cavalry | 1 | yes | yes | yes |
| Battering Ram | Knight → Scout Cavalry | 0 | yes | yes | yes |
| Town Center | Man-at-Arms → Militia | 1 | yes | yes | yes |
| Transport Ship | Man-at-Arms → Militia | 1 | yes | yes | yes |

- **The property call garrisons into every container tested, on the same tick.** That includes
  the five that refuse a garrison order, and cavalry into a Ram, which its garrison type
  excludes.
- **Force made no visible difference.** Force 0 got through the same restrictions. What force
  changes, if anything, is still unknown. A full container is the obvious candidate, but it
  wasn't run.
- **Ungarrisoning released every replacement alive, except from a Dock.** The Dock galleys stayed
  inside. A Dock may only release ships onto water it can reach, or need a different order. Not
  resolved.
- **Seen (maintainer):** a slowed rerun held each phase for 20 s. The maintainer watched every
  building hold its unit, then hold the replacement.

**For #10:** `transformUnit` should read `xsGetGarrisonedInUnitId(unit)` before removing it. If
the result is 0 or above, it should put the replacement into that container with
`xsSetUnitProperty(created, cUnitGarrisonedInId, container)` on the same tick. This replaces the
garrison-order approach from the follow-up above, which production buildings and Docks refuse.
