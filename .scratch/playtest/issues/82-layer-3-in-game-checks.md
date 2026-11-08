# 82: the in-game checks that only a person can make

**Reported:** 2026-11-07, split out of [#78](78-in-game-checks-round-2.md)

**Status:** done

**Related:** [#78](78-in-game-checks-round-2.md) (layers 1 and 2),
[#51](51-in-game-checks.md) (the fork harness this needs),
[`spikes/82/`](../spikes/82/README.md) (the harness, built),
[`spikes/78/`](../spikes/78/README.md), [`spikes/80/`](../spikes/80/README.md)

## Report

#78 split its checks by what each one observes. Layer 1 reads the shipped `.aoe2scenario` files
with aoe2kit and needs no game. Layer 2 runs `Test.xs` in `XsTesting` and reads a `.xsdat`
sidecar. Both are done: **18 of 27 boxes**, covering #71, #72, #73, #74 and most of #60.

What is left cannot be reached either way. These nine need a real scenario and a person looking
at the screen, which is layer 3 - the fork harness #51 built and then deleted.

## The checks

### Scenario triggers fire (#58, #66, #68, #70)

Layer 1 proved the trigger *content* on disk - units, owners, tiles, conditions, effect counts -
but `structure_verified` is not `engine_verified`, and nothing has watched one fire.

- [x] **#58** (`J3B`) Joan 3: once the boats item has arrived and object 679 is visible, `AP Give Boats`
      creates two Transport Ships for P1 at (14,85) and (15,85), and `[D0] Finding Boats` shows
      only its message. **Passed**, see Comments.
- [x] **#66** (`A3G`) Attila 3: both gold tributes pay P1 the full 3000. **Passed**, after the
      source was changed from player 4, who held 500, to player 2 Constantinople, who holds
      50,000. See Comments.
- [x] **#68** (`J5V`) Joan 5: six refugees reaching Compiegne without Joan does not win; Joan arriving as
      well does. The condition now reads variable 1 `RefugeesEscorted` after
      [#79](79-joan5-victory-counts-refugees-located-not-escorted.md). **Passed**, see Comments.
- [x] **#70** (`J6S`) Joan 6 on Easy, and on Easy and Moderate: the Bombard Cannons and Packed Trebuchet
      spawn as Gaia inside the French Artillery and French Army areas, and the AP grants pick
      them up. **Passed.** What the run also turned up is that those four are capturable, which
      is [#83](83-joan6-difficulty-siege-is-capturable.md) and not this box.

### Victory threats, the part a sidecar cannot see (#60)

Layer 2 verified the countdown machinery: the threat arms, one Wonder starts one timer near 200
years, two Wonders run two independent timers, Atheism adds 100 years to each, and destroying one
releases its slot while the other stays tracked. These four are what is left.

- [x] (`G3W`) Genghis 3: a Jin Wonder foundation reveals about 10 tiles around it. **Map revealers cannot
      be enumerated from XS at all** - not by `xsGetPlayerUnitIds` for any player, and
      `xsGetObjectCount` returns -1 - so the fog is only visible to an eye.
      **Failed**: no revealer spawns for a foundation at all. Filed as
      [#84](84-wonder-foundation-is-never-tracked.md).
- [x] (`G3W`) Destroying the Wonder clears the timer and objective, and a rebuilt Wonder restarts the
      cycle. The slot release is proven; `xsClearTimer` stops the display without resetting
      `xsUnsyncGetTimerTimeRemaining`, so the timer *disappearing* is a visual check.
      **Passed.**
- [x] (`G3W`, or `G3W --shorten`) Letting the countdown run out defeats P1. Needs 200 game-years.
      **Passed.**
- [x] (`A6W`) Attila 6: defeating a city clears its Wonder's countdown even if the Wonder still stands,
      and its "Prevent or Destroy" and "Defeat" locations still credit. **Passed** on Aquileia
      (P2, Red); see Comments.

### The train menu (#74 Q3)

- [x] (`J4M`) Spike Q3, a fresh Joan 4 start, not the old save: the Archery Range offers Skirmisher, the
      Dock offers Galley and Demolition Raft, and each upgrade's research button is present and
      unresearched. **Passed**, see Comments.

## Why these cannot be automated

**XS cannot read whether an object is enabled.** `cEnableObject` is a write-only effect; there is
no `xsGetObjectEnabled`. So every "does this building offer that unit" question is a person
looking at a train menu. That single fact is what created layer 3.

The same shape applies to the fog and to the on-screen timer: the mod's *decision* is readable
from the sidecar, its *rendering* is not.

## What this needs

The fork harness from [#51](51-in-game-checks.md): a throwaway fork of each live AP scenario with
map, AI, civs, techs and grant triggers intact, and only the start position, age and item flags
changed, so each check is a few seconds of looking rather than a playthrough. One seed served all
ten forks in #51. Its `build.py`, `read.py` and recipe were deleted when that ticket closed, so
this is a rebuild, not a re-run.

**Built, 2026-11-07: [`spikes/82/`](../spikes/82/README.md).** Seven forks, keyed above against
the check each one answers. `py -3 build.py` makes them, `py -3 read.py` decodes the run.

`spikes/78/Test.xs` stays useful alongside it: the sidecar still records the mod's side of any
check while the person judges the screen.

## Acceptance criteria

- [x] A fork exists for each check above, built from the live scenario by recipe rather than by
      hand in the editor. **Seven forks, all nine checks**; see Comments.
- [x] **All 9 checks played.** 8 passed. The one failure is the Wonder foundation reveal, filed
      as [#84](84-wonder-foundation-is-never-tracked.md). `J6S` raised
      [#83](83-joan6-difficulty-siege-is-capturable.md), fixed and committed; `A3G`'s question
      was answered on disk and fixed in `a187fd7`.
- [x] Each result is recorded under *Comments* here, with a follow-up ticket for anything that
      fails. One failure, one ticket: [#84](84-wonder-foundation-is-never-tracked.md).
- [x] The forks and the seed that drives them are reproducible from what is committed, so the
      next round does not rebuild them from nothing. `spikes/82/` plus
      `spikes/78/install_seed.py`.

## Comments

### The harness is built (2026-11-07)

`spikes/82/` - `forks.py` (the catalog), `build.py`, `read.py`, `selftest.py`, `README.md`.
Seven forks cover the nine checks:

| key | scenario | checks |
| --- | --- | --- |
| `J3B` | Joan 3 | #58 |
| `A3G` | Attila 3 | #66 |
| `J5V` | Joan 5 | #68 |
| `J6S` | Joan 6 | #70, played twice for Easy and Moderate |
| `G3W` | Genghis 3 | #60's fog, timer, destroy/rebuild and expiry |
| `A6W` | Attila 6 | #60's city defeat |
| `J4M` | Joan 4 | #74 spike Q3 |

**No client, no server, no seed roll.** A fork is the live scenario with its `script_name`
repointed at a generated `PT82_<KEY>.xs`, which is the live entry file with `GiveScenarioItems()`
and `main()` rewritten and a staging block spliced in. `main()` still calls `InitAP()`, so caveman,
unitsanity, techsanity, the pavilion and the victory threats initialise as they do in play; the
staging block then disables `ConnectAP` and `WriteAP` - the only two rules that need the client -
and grants the items itself. One installed seed from `spikes/78/install_seed.py` drives all seven.

Because the fork XS is *derived* from the live entry file rather than copied, a change to
`AP_Joan_3.xs` flows into the next build. The build also pins the facts each fork leans on - unit
references by player and type, trigger names, and terrain under every created building - and fails
by name if one moved. Those pins already earned their keep: they caught Attila 3's Town Centers
pinned to the wrong players (852 is Red/P4, 2705 is Green/P3) and six Joan 5 refugee references
that were neither the right refugees nor the right owner.

`read.py` decodes the sidecar - `424282` magic, fork id, scenario id, the three seed options, a
`424242` footer - and prints the mod's side as a PASS/FAIL table beside the part only an eye can
answer. `selftest.py` proves it without the game: 22 of 22, covering all seven forks and eight
seeded faults. `python -m ruff check --select F,E9` is clean and `xs-check` is clean on all seven
generated entry files.

**Still open, and deliberately.** Nine results. Nothing here has been played.

Two things the harness changes about what a check proves, both recorded in its README and
reprinted by `read.py` after every run:

- **`G3W --shorten`** rewrites the armed timer to three years with the same `xsDisplayTimer` call
  `StartWonderCountdown` makes. That proves expiry calls `LoseToThreat`; it does not prove the
  engine counts 200 years. Without the flag the fork waits the full countdown. Say which was run.
- **`A6W`** takes Patavium out with `xsDeclareVictory(2, false)` rather than fighting it down.
  What the mod reads is `xsGetPlayerInGame`, which is the same either way, but the city is not
  eliminated the way a player would eliminate it.

A `/code-review` pass over the spike found seven issues and all seven are fixed: `FindWonderSlot(-1)`
returns the first *free* slot, so every lookup now goes through a `PT82Slot` wrapper that answers
-1 for a unit that never placed; one asserted probe could not pass on a healthy run and is now
recorded only; a shared unit-scan array could report one query's answer as another's, so each
count has its own array and its own cached answer and reads -1 when the engine refuses; the
verified terrain tiles were computed and then discarded, so a Dock could have been built inland
and still passed; `GiveVictory()` calls `AP_Write()` over the same sidecar, so the generated
`Victory()` re-records and `read.py` names that case; a seed mismatch printed but exited 0; and
`--clear-profile` would have deleted an unread fork run.

`A3G` razes both Town Centers eight seconds in, which is the earliest the tribute can run and so
the worst case for P4's purse: P4 starts on 500 gold, P3 on 600, and the shipped effects tribute
3000 **from P4** for both items. The fork records P1's, P3's and P4's gold before and after.

### #58 passed (2026-11-07)

Played `PT82_J3B`. `AP Give Boats` creates the two Transport Ships for P1 and `[D0] Finding Boats`
shows only its message. The box is ticked; no follow-up.

### J6S raised #83 (2026-11-07)

Playing `PT82_J6S` turned up something beside the check it was built for: Joan 6's `Easy` and
`Easy and Moderate` triggers `create_object` their extra siege for Gaia, and a `create_object`
effect has no capture-flag field. The 60 Gaia objects #31 handed to the items carry
`capture_flag = 0` on the map - including the three Bombard Cannons at (104.5-106.5, 120.5) - but
the pieces the difficulty triggers spawn at (103,120), (107,120), (108,120) and (136,125) get the
engine default and can be walked up to and taken. One artillery row, two rules.

Filed as [#83](83-joan6-difficulty-siege-is-capturable.md) with the parser reading behind it.
**#70 itself passed**, per the maintainer on 2026-11-07: the siege spawns as Gaia inside the
grant areas and the grants pick it up, and the difficulty handling is correct. #83 is about the
capture flag on those four units only.

### A3G's question is answered on disk: the tribute should come from Gaia (2026-11-07)

Raised by the maintainer asking who pays the gold for Attila 3's *other* tribute triggers. There
are none - the scenario has 60 effects and exactly two are `tribute`, both AP's, and no
`modify_resource` at all. Vanilla's gold extortion is the AI scripts named in the player slots
(`Attila-scn3 player 3.ai`, `Attila-scn3 player 4.ai`), not triggers.

But the shipped set does carry two vanilla tributes, and they settle it:

| scenario | trigger | source | target | amount |
| --- | --- | --- | --- | --- |
| Joan 3 | `[D9] Fastolf Attacks` | **Gaia (0)** | 4 | 2000 food + 2000 gold |
| Genghis 6 | `[D1] T - 20` | **Gaia (0)** | 2 | 2000 food + 2000 gold |
| Attila 3 | `AP Give Green TC Gold` | **4** | 1 | 3000 gold |
| Attila 3 | `AP Give Red TC Gold` | **4** | 1 | 3000 gold |

Vanilla's idiom for handing a player resources is to tribute **from Gaia**, which is a mint rather
than a purse. The two AP tributes draw on Philippopolis instead, who holds 500.

So #66's open question - "does player 4 actually hold 3000 when the trigger runs" - is the wrong
question: P4 should never have been the source. Two further details fall out of the same reading:

- `AP Give Green TC Gold` fires on the destruction of ref 2705, which is **P3 Marcianopolis's**
  Town Center, but draws from P4. Even on a "the owner pays" reading it names the wrong player.
- Neither candidate can fund it: P3 holds 600, P4 holds 500. Only P2 Constantinople (50,000)
  could, and nothing in the shipped set tributes from a live player for this purpose.

It matters to the apworld, not just the game: `Attila3StartingState` sets
`easy_resource_sources[Resource.GOLD]` on either item, so the rules assume a real gold lump
arrives.

`A3G` still has a job - confirming the fix in game - but the diagnosis no longer needs it.

### #68 passed (2026-11-07)

Played `PT82_J5V`. Six refugees inside Compiegne do not win on their own; Joan walking in
declares victory. #79's repoint of `AP Victory` onto variable 1 holds.

### A3G rebuilt for the new payer (2026-11-07)

The maintainer fixed Attila 3 in the editor rather than by script: both AP tributes now source
**P2 Constantinople**, who holds 50,000 gold. Committed in Ageipelago `a187fd7`,
*"Att 6 fix bonus troops, Att 3 give gold from p2"* - the same commit that swaps in #83's Joan 6
rewrite and carries the `PT82_*` gitignore lines. The working tree holds one further editor save
of Attila 3 on top, which `kit scen diff` reports as `next_unit_id_to_place`, the save timestamp
and the editor camera, and no semantic change.

P2 rather than Gaia is a departure from the two vanilla tributes in the shipped set, which both
source Gaia. It is a defensible one: Constantinople is the city the scenario is about extorting,
and 50,000 covers 6,000 many times over. The only consequence is that the gold is finite where
Gaia's would not be, which at that ratio is not a practical risk.

`A3G` is rebuilt against the fixed scenario and its probes follow the payer: it now records P1's
and P2's gold at the moment the tributes run and after, with P3 and P4 as controls that should
not move. The check itself changed shape - #66 asked "does P4 hold 3000", and the answer is that
P4 was never the right source.
### #66 passed (2026-11-07)

Played `PT82_A3G` against the fixed Attila 3: both tributes pay, now that Constantinople is the
source. The check that #66 actually asked - whether the payer holds 3000 - was answered by
reading the file rather than by playing it, and the answer was that the payer was wrong.

### J4M could not place its buildings (2026-11-07)

Reported from the game: the Archery Range and Dock never appeared. The fork chats a red line when
`xsCreateUnit` refuses every candidate, which is what happened.

**My bug, and the build should have caught it.** `J4M` moves P1's starting army to the shore with
`move_units_in_area`, and the Archery Range candidates were inside the block it lands on. The
build-time check only looked at *terrain*; it never asked what was standing on the tile, and it
checked the **source** scenario rather than the patched one, so the move it had just ordered was
invisible to it. Every 3x3 footprint overlapped either P1's units or Gaia decoration.

Fixed by making the build choose the tiles rather than taking them from a hand-written list:

- `build.py` now patches the scenario **first**, then reads units and terrain back out of the
  patched file, so everything the recipe did is accounted for.
- A `Create` carries a `search` rectangle, a `prefer` tile and a footprint instead of five
  guesses. The build scans the rectangle for a footprint whose every tile is on allowed terrain
  and holds no unit of any player, adds the water-adjacency test for the Dock, orders what
  survives by distance from `prefer`, and writes those tiles into the fork.
- If nothing in the rectangle is clear, the build fails by name. A fork that cannot place its
  buildings is now a build error rather than a red line forty seconds into a run.

Footprints are hand-set (`FOOTPRINT` in `forks.py`: Archery Range 3, Dock 3, Wonder 4). There is
no `empires2_x2_p1.dat` on this machine, so `collision_size` could not be read from the game data.

### A6W named the wrong city, and its Wonder was blocked too (2026-11-07)

Both reported from the game.

**The city.** Attila 6's players are P2 **Aquileia** (Red), P3 Mediolanum (Green), P4 Verona
(Orange), P5 **Patavium** (Purple), P6 the Western Roman Empire (Blue). `A6W` defeats P2 and
called it Patavium throughout. P2 is Aquileia; Patavium is P5. Relabelled.

Reading the trigger properly also turned the check from "record all six and read them off" into
something assertable. `AP Defeat Aquileia` is one `player_defeated` condition whose single
`script_call` runs `DefeatAquileia()` **and** `DestroyRedWonder()` together - that is what
"prevent or destroy" means here, one effect rather than two paths. So the fork now asserts that
10603 and 10609 both credit and that the other seven do not, and the caveat saying the mapping
was unpinned is gone. The mapping is: 10601/10607/10611 are P5 Purple, 10602/10608 P3 Green,
10603/10609 P2 Red, 10604/10610 P4 Orange.

**The Wonder.** Blocked the same way `J4M`'s buildings were, and fixed by the same change: the
build now picks the tile out of the patched scenario with the footprint cleared of units, rather
than trying five hand-written guesses at run time.

Genghis 3 was checked at the same time and needs no relabelling: `EnableWonderThreat(4)` and
P4 **Jin** (Yellow) agree, so `G3W`'s wording was already right. Its Wonders go through the same
new tile chooser.

### Two more things the tile chooser had to learn (2026-11-07)

Tightening the terrain sets broke `J4M`'s Dock, loudly, which is what the new build error is for.

- **A Dock sits across the shoreline.** Joan 4's beach is one tile wide, so no 3x3 footprint can
  be all beach. The rule is now that a dock footprint may mix beach and water and must contain at
  least one of each. It lands at (87,110).
- **The terrain sets were partly wrong.** `BEACH` held 23, which
  `AoE2ScenarioParser/datasets/terrains.py` calls `WATER_MEDIUM` - so the Dock could have been
  placed in open water and satisfied its own water-adjacency test from its own tiles. `LAND` held
  `FOREST_OAK` (10), `FOREST_OAK_BUSH` (20) and two farm terrains, which are land but not
  buildable. Both sets are now read off that dataset rather than from memory.

All seven forks build, `xs-check` clean, `selftest.py` 22 of 22, ruff clean.

### #74 Q3 passed (2026-11-07)

Played `PT82_J4M` after the tile chooser landed, on a fresh Joan 4 start rather than the old
save. The Archery Range offers Skirmisher and the Dock offers Galley and Demolition Raft, with
Elite Skirmisher, War Galley and Demolition Ship each present as an unresearched research button.
That is spike Q3 answered, and the `tier == 0` gate in `setUnitDisable` holding in the engine
rather than only in the file.

This was the check that created layer 3 in the first place: `cEnableObject` is write-only and
there is no `xsGetObjectEnabled`, so "does the Dock offer Galley" was never reachable from a
sidecar. The fork's own probes cover the half that is readable - both buildings alive, Castle Age
reached, and each upgrade tech's state recorded with 3 (Done) forbidden.

### The Wonders were blocked because I was guessing where they go (2026-11-07)

Both `G3W` and `A6W` still refused to place their Wonders after the tile chooser landed. Terrain
clear, elevation flat and uniform, nothing within two tiles - and still refused. Two rounds of
modelling placement statically had both been wrong, so the model was the problem.

**The scenarios already say where a Wonder goes.** Attila 6 carries a `place_foundation` effect
per city, and those tiles are the authority:

| city | player | colour | Wonder plot |
| --- | --- | --- | --- |
| Aquileia | 2 | Red | **(216,24)** |
| Mediolanum | 3 | Green | (33,55) |
| Verona | 4 | Orange | (136,178) |
| Patavium | 5 | Purple | (123,72) and (129,78) |

`A6W` was searching (188,25)-(204,41), anchored on Aquileia's Town Center at (201,37). The real
plot is (216,24) - fifteen tiles away, outside the box, and the box itself was inside a built-up
town. It now uses the shipped tile.

**Genghis 3 has no `place_foundation`**, because vanilla has no Wonder there at all; the threat is
AP's addition. What it has instead is the Jin's **building plot**: nine Blacksmiths in a 3x3 grid
at x 122/125/128 by y 165/168/171, spaced exactly three tiles apart, which is a Blacksmith's own
footprint. Clear that block and the AI builds on the middle of it. The fork now removes those
nine by reference id - `kit scen plan` confirms no trigger references them, 8339 units to 8330 -
and puts the foundation at the centre, (125,168). The tenth Blacksmith, ref 9959, is outside the
block and stays. The nine are pinned, so a scenario edit that moves them fails the build.

The finished Wonder goes to (167,165), the nearest clear flat 6x6 at least 24 tiles from the
plot. **Corrected 2026-11-08: a Wonder is 5x5, so `FOOTPRINT[WONDER]` is now 5 and the search
is 5x5; see [#84](84-wonder-foundation-is-never-tracked.md). The 6 reserved a tile more than
it needed, which is why no placement ever failed on it.**
plot. `THREAT_REVEAL_RADIUS` is 10, and the Jin town has no clear ground between 24 and 45 tiles
out, so the two fog patches would otherwise overlap and the first check would be unreadable.

**Kept as a safety net:** `PT82CreateNear` now rings outward from the chosen tile up to eight
tiles, enables the object for that owner first (`cEnableObject`), and chats where it landed. The
static chooser still gates the search area, but the engine has the last word on whether a tile
works - which is the lesson from three rounds of my getting the geometry wrong.

### #60's city-defeat bullet passed (2026-11-07)

Played `PT82_A6W` once the Wonder went to Aquileia's own plot at (216,24). Defeating P2 outright
at forty seconds clears the countdown although the Wonder is still standing, and the locations
credit.

This was the bullet #78 could not reach at all: it needs a player genuinely out of the game, and
`XsTesting` has two players, so `EnableWonderThreat(2)` was refused there and no threat ever
armed (that refusal became [#81](81-wonder-threat-owner-array-is-one-slot-short.md)). A real
six-player scenario was the only way.

The sidecar does most of the judging here - nine of its sixteen probes are asserted location
outcomes: 10603 `DefeatAquileia` and 10609 `DestroyRedWonder` must both credit, and the seven
belonging to Mediolanum, Verona and Patavium must not. `RetireWonderOwner` releasing the slot
shows up as `wonder_slot_now` going to -1 while `wonder_alive` stays 1, which is the whole claim
in two numbers. The eye is only needed for the timer and its objective line disappearing from the
screen, which `xsClearTimer` does not make readable.

### G3W: two passed, the fog check failed (2026-11-07)

Played `PT82_G3W`. The finished Wonder at (167,165) arms its countdown, destroying it clears the
timer and objective, a rebuilt one restarts the cycle, and letting it expire defeats P1. The
blacksmith-plot reading held: clearing the nine lets a Wonder go up on the middle of it.

**The fog bullet failed, and not in the way the ticket expected.** The ticket asked whether a
foundation reveals about ten tiles. It reveals nothing: no map revealer spawns for a foundation
at all. Filed as [#84](84-wonder-foundation-is-never-tracked.md).

That closes #82's list. Nine checks played, eight passed, one ticket.
