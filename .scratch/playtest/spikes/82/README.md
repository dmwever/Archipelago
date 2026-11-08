# 82: layer 3, the forks a person plays

[#82](../../issues/82-layer-3-in-game-checks.md) is the nine checks left over from
[#78](../../issues/78-in-game-checks-round-2.md) that neither aoe2kit nor `XsTesting` can reach.
They need a real scenario and an eye. This is the harness that makes each one a few seconds of
looking instead of a playthrough.

It is a rebuild of the [#51](../../issues/51-in-game-checks.md) fork harness, whose `build.py`
and `read.py` were deleted when that ticket closed. Nothing of it survived in git, so nothing
here is a re-run of it.

## What a fork is

A fork is the live AP scenario with the map, the AI, the civs, the techs, the grant triggers and
the AP trigger block all intact. Two things change, and nothing else:

- **Where the check is.** Starting units are moved, the ground is revealed, and the buildings or
  Wonders a check needs are created on the spot.
- **What has arrived.** The fork calls `GiveItem` for exactly the items the check turns on, and
  for nothing else.

Each fork is a pair: `PT82_<KEY>.aoe2scenario` in the scenario folder and `PT82_<KEY>.xs` beside
the live modules. Both are generated. `PT82_<KEY>.xs` is the live entry file with
`GiveScenarioItems()` and `main()` rewritten and a staging block spliced in, so every location
wrapper, age and pavilion override stays in step with the live file by construction - rebuild
after an edit to `AP_Joan_3.xs` and the fork carries it.

**No client, no server, no seed roll.** `main()` still calls `InitAP()`, so caveman, unitsanity,
techsanity, the pavilion and the victory threats all initialise exactly as they do in play. The
staging block then disables `ConnectAP` and `WriteAP`, which are the only two rules that need the
Archipelago client, and grants the items itself. That makes a fork reproducible from what is
committed here plus one installed seed.

## Running it

### 1. Install the seed

The forks read `SlotData.xs`, `UnitData.xs` and `TechData.xs` out of the live xs folder, and need
unitsanity `all`, techsanity `all` and caveman on. `spikes/78/install_seed.py` writes all three
offline:

```
py -3 ../78/install_seed.py --unitsanity all --techsanity all --caveman yes
```

`build.py` refuses to build against any other seed, and every fork records the three option values
in its sidecar, so a wrong seed reports itself twice over.

### 2. Build

```
py -3 build.py              # all seven
py -3 build.py G3W A6W      # or just these
py -3 build.py --list
py -3 build.py --clean      # delete every PT82_* file again
```

`build.py` checks each fork's pinned facts against the source scenario first: that every pinned
unit reference is still that player's unit of that type, and that every pinned trigger name is
still there. A scenario edit that moves one fails the build by name rather than producing a fork
that quietly tests nothing.

It then patches the scenario, and **chooses the tiles for created buildings out of the patched
file**, which is the only state that accounts for the unit moves the recipe just made. A `Create`
carries a search rectangle, a preferred tile and a footprint; the build scans the rectangle for a
footprint whose every tile is on allowed terrain and holds no unit of any player, orders what
survives by distance from the preferred tile, and writes those into the fork. If nothing is
clear, the build fails by name - a fork that cannot place its buildings is a build error, not a
red chat line forty seconds into a run.

Two things that rule has to get right, both learned the hard way:

- **A Dock sits across the shoreline.** Requiring its whole 3x3 on beach can never match a
  one-tile-wide beach, so the footprint is allowed to mix beach and water and must contain at
  least one of each.
- **Terrain 23 is `WATER_MEDIUM`, not beach**, and `FOREST_OAK` (10), `FOREST_OAK_BUSH` (20) and
  the farm terrains are land but not buildable. The sets in `forks.py` come from
  `AoE2ScenarioParser/datasets/terrains.py`, not from memory.

Building footprints are hand-set in `FOOTPRINT` (Archery Range 3, Dock 3, **Wonder 5**).
`2 x collision_size_x` off `empires2_x2_p1.dat` is the rule, and it holds for the Wonder too:
2.5 gives 5. **Corrected 2026-11-08.** This file previously said the rule was wrong here and the
real footprint was 6, measured in game for
[#84](../../issues/84-wonder-foundation-is-never-tracked.md). That measurement came off a spike
that created the Wonder at whole-integer coordinates - a tile corner - where a building with a
2.5 half-extent sits half a tile off the grid and straddles six columns and six rows. The engine
still gets the last word: `PT82CreateNear` rings outward from the chosen tile, enables the object
for that owner first, and chats the tile it managed to use.

**Where a Wonder goes is in the scenario, not in a guess.** Attila 6 has a `place_foundation`
effect per city giving the plot the game itself picked: (216,24) Red, (33,55) Green, (136,178)
Orange, (123,72) and (129,78) Purple. Genghis 3 has none - vanilla has no Wonder there - but the
Jin keep nine Blacksmiths in a 3x3 grid three tiles apart, and that block is the plot the AI
builds on once cleared. `G3W` removes the nine and builds at its centre. A scenario edit that moves one of those fails
the build by name rather than producing a fork that quietly tests nothing. It then runs
`xs-check` over the generated XS and verifies the patched scenario points at it.

### 3. Clear the profile

```
py -3 build.py --clear-profile
```

A real session leaves `items.xsdat`, `techs.xsdat`, `units.xsdat`, `buildings.xsdat` and the
per-scenario item files in the profile folder. `GiveStartupTechs` and friends read those on the
first tick, so a leftover file leaks items into a fork that is supposed to hold exactly what it
grants. Clear them before the first run.

It will not delete a `default1.xsdat` that carries the `424282` magic, because that is a fork run
nobody has decoded yet. Read it first, or pass `--force`.

### 4. Play

Start the fork from Single Player as a loose scenario. The first chat line is
`PT82 <KEY> staged: <title>`; after that the fork chats each staged step as it runs. Quit when
the check is answered - **the sidecar is only flushed on unload**.

If the fork reaches victory, give it a couple of seconds before quitting. `GiveVictory()` calls
`AP_Write()`, which writes the apworld's own packet over the same file; the fork's `Victory()`
wrapper records again immediately, and `PT82Stage` records once a second after that, but a quit
inside that window leaves the wrong file behind. `read.py` recognises that case by name.

### 5. Read

```
py -3 read.py
```

With no argument it reads `profile/default1.xsdat`, which is what DE names a loose scenario's
sidecar. The reader prints the mod's side of the check as a PASS/FAIL table, then prints the part
only a person can answer and the caveats that go with it.

The sidecar carries a `424282` magic, the fork id, the scenario id and the three seed options, and
ends in `424242`. Reading the wrong run, a run that never finished a write, or a sidecar from
before a rebuild each report themselves instead of passing quietly.

`selftest.py` proves the reader without the game: synthetic sidecars for all seven forks, plus
eight seeded faults.

```
py -3 selftest.py
```

## The forks

| key | scenario | covers | what the fork stages | what the eye decides |
| --- | --- | --- | --- | --- |
| `J3B` | Joan 3 | #58 | Transport Ships item, the boat ground revealed | two Transport Ships appear for P1 at (14,85) and (15,85); `[D0] Finding Boats` shows its message and nothing else |
| `A3G` | Attila 3 | #66 | both gold items, then both Town Centers razed at t+8s | whether each tribute actually pays 3000 |
| `J5V` | Joan 5 | #68, #79 | six refugees already inside Compiegne, Joan three tiles west | no victory without Joan, victory the moment she walks in |
| `J6S` | Joan 6 | #70 | French Army and French Artillery items, both spawn areas revealed, P1 moved beside them | the siege spawns in Gaia's colour and the grants take it |
| `G3W` | Genghis 3 | #60, #84 | a Jin Wonder foundation on the Jin building plot, driven to 10% built fifteen seconds later, then a finished Jin Wonder forty tiles away | nothing lit while the foundation is untouched, its construction site lit once work starts, the timer arming, the timer going when the Wonder falls |
| `A6W` | Attila 6 | #60 | a finished Wonder for Patavium, then Patavium defeated outright at t+40s | the countdown clearing although the Wonder still stands |
| `J4M` | Joan 4 | #74 Q3 | Skirmisher, Galley and Demolition line items plus their three upgrade tech items, an Archery Range and a Dock, P1 moved beside them | the train menu offers the base tier and each upgrade sits unresearched |

`J6S` is played twice. Difficulty is chosen in the launch menu, not stored in the file: `Easy`
fires on Easy only, `Easy and Moderate` fires on both, so Moderate is the run that tells them
apart.

## Why these cannot be automated

**XS cannot read whether an object is enabled.** `cEnableObject` is a write-only effect and there
is no `xsGetObjectEnabled`, so "does the Dock offer Galley" is irreducibly a person looking at a
building. The same split runs through #60: the mod's *decision* is in the sidecar, its *rendering*
- the fog, the on-screen countdown, the announcement - is not. `xsGetPlayerUnitIds` cannot
enumerate map revealers for any player and `xsGetObjectCount` returns -1 for them, so the reveal
has no reading at all.

Each fork therefore records what it *can* read beside what it cannot, and `read.py` prints both
together. A probe with an expectation is asserted; a probe without one is recorded for the write-up. A unit
count reads **-1** when `xsGetPlayerUnitIds` refused the query rather than returning an empty
array - each count has its own scan array and its own cached answer, so a refusal can never be
reported as another probe's number. That matters most for the Gaia counts in `J6S`: Gaia
enumeration is not dependable, and -1 there hands the question to the screen instead of to a
number.

Slots are looked up through `PT82Slot`, never `FindWonderSlot` directly. `FindWonderSlot(-1)`
returns the first **free** slot - that is how `TrackWonder` allocates one - so asking it about a
Wonder that failed to place would name somebody else's countdown.

## The 200-year countdown

One #60 bullet is "letting the countdown run out defeats P1", and the armed timer starts at
`THREAT_BASE_YEARS = 200`.

```
py -3 build.py G3W --shorten
```

adds one step to `G3W`: fifty seconds in it asks `FindWonderSlot` which slot the finished Wonder
took and calls `xsDisplayTimer` on it with three years, which is the same call
`StartWonderCountdown` makes. `HasCountdownExpired` then trips and `LoseToThreat` runs. The slot
is looked up rather than assumed, so a Wonder that failed to place says so instead of shortening
somebody else's timer.

That proves **expiry defeats P1**. It does not prove the engine counts 200 years correctly - for
that the fork has to be left alone without `--shorten`. Both are honest; say which one was run.

## What this harness does not settle

- **Which Attila 6 Wonder location belongs to which colour.** `A6W` records all six of
  `10607`-`10611` and `10601` rather than pinning one, so the result is read off rather than
  assumed.
- **Patavium's defeat is staged with `xsDeclareVictory`**, not fought down. What the mod reads is
  `xsGetPlayerInGame`, which is the same either way, but the city is not eliminated the way a
  player would eliminate it.
- **`A3G` razes both Town Centers eight seconds in**, which is the earliest the tribute can ever
  run and so the worst case for P4's purse. P4 starts on 500 gold and P3 on 600; the shipped
  effects tribute 3000 *from P4* for both items.
- **A moved start can trip the scenario's own triggers.** `J5V`, `J6S` and `J4M` relocate P1
  units, and a scenario trigger keyed on one of them being somewhere may fire early or never.
  Nothing here suppresses that. If a fork behaves oddly before its staged step runs, suspect the
  move first; `kit scen triggers <fork> --grep "<name>"` reads the trigger as patched.
- **`J5V` hands the six refugees to P1 in the file**, so `Locate Refugee 1`-`6` fire at once and
  variable 0 is satisfied immediately. What is under test is variable 1 against variable 2, which
  is where #79 repointed `AP Victory`.

## Files

| file | what it is |
| --- | --- |
| `forks.py` | the catalog: one `Fork` per check, with its items, reveals, creations, unit edits, pinned facts, staged steps, probes and the lines the person reads |
| `build.py` | verifies the pins, generates `PT82_*.xs`, lints it, patches `PT82_*.aoe2scenario`; also `--clean` and `--clear-profile` |
| `read.py` | decodes a fork sidecar and prints its probes beside what the eye must decide |
| `selftest.py` | proves `read.py` against synthetic sidecars and seeded faults, with no game |

`PT82_*.xs` and `PT82_*.aoe2scenario` land in the live game folder, which is the Ageipelago
checkout. Both patterns are in that repo's `.gitignore`: the forks are build output, and this
folder is what is committed.

`spikes/78/` stays useful alongside this: `static_checks.py` for what the shipped files already
prove, `install_checks.py` after every install, and `read.py` there for the layer-2 sidecar.
