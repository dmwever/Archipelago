# 78: harness for the round-2 in-game checks

[#78](../../issues/78-in-game-checks-round-2.md) is a list of about thirty checks across nine
finished tickets. Most of them do not need a human eye. This harness splits them by what the
check actually observes, so only the irreducible ones are played.

Precedent: [#51](../../issues/51-in-game-checks.md) ran two mechanisms — fork scenarios that put
the player at the check point, and an `.xsdat` ledger decoded with the kit. Both are reused here,
with a third layer added in front that needs no game at all.

## Layer 1 — static, no game

`static_checks.py` asserts #78's scenario-trigger checks straight off the shipped
`.aoe2scenario` files with aoe2kit. Run it any time; it needs nothing but the kit.

```
py -3 static_checks.py
```

Exits non-zero on any failure. Override `AOE2KIT` and `AP_SCENARIO_DIR` if the paths move.

| check | covers | why it is static |
| --- | --- | --- |
| `AP Give Boats` creates 2 Transport Ships for P1 at (14,85) and (15,85) | #58 | a `create_object` effect's unit, owner and tile are in the file |
| `[D0] Finding Boats` has exactly one effect, its message | #58 | effect count and type are in the file |
| both Attila 3 gold tributes are 3000 gold, P4 to P1 | #66 | a `tribute` effect's source, target, resource and quantity are in the file |
| Joan 6 `Easy` and `Easy and Moderate` spawn their siege as Gaia, still enabled | #70 | `source_player` is the single field #70 changed |
| both AP grant areas cover their spawn tiles | #70 | tiles and areas are both in the file |
| Joan 5 `AP Victory` asks for Joan and six refugees escorted | #68 | conditions are in the file |
| only `Joan in Area` writes var 2, and it does not loop | #68 | the double-count #68 filed is a structural property |

**Result, 2026-11-06: 14 of 14 pass**, after the maintainer repointed `AP Victory` at variable 1.
The one failure this found was filed as
[#79](../../issues/79-joan5-victory-counts-refugees-located-not-escorted.md): `AP Victory` counted
refugees *located* (var 0) rather than *escorted* (var 1).

### `install_checks.py` — the installed seed

`static_checks.py` reads the shipped scenarios, which change rarely. `install_checks.py` reads
the per-seed `UnitData.xs` and `TechData.xs` that `/install` writes, which change every seed, and
asserts the invariants #73 and #74 turn on. **Run it after every `/install`, before layer 2.**

```
py -3 install_checks.py
```

| check | covers |
| --- | --- |
| all three files carry the same seed, and the options are unitsanity `all` / techsanity `all` / caveman on | the layer-2 preconditions |
| no row asks for an upgrade item the seed never created | #73, across every row rather than the one that surfaced |
| the Elite Leitis row carries no upgrade item | #73 |
| no line is missing the tier-0 head its enable would land on | #74 |
| no row is trainable, unenableable and has no upgrade tech to promote it | #74 |
| every row the layer-2 harness drives is where it expects | the harness itself |

**Result, 2026-11-06 after a fresh `/install`: 5 of 7 pass.** #73 is clean across all 107 rows.
The two failures answer spike Q1 in the negative and are filed as
[#80](../../issues/80-camel-rider-stranded-by-the-tier-0-enable-gate.md): line 884 has no tier-0
head, so the `tier == 0` gate strands Mongols' Camel Rider.

What stays in game from these tickets: that the triggers actually fire, and #66's real question —
whether player 4 holds 3000 gold when the tribute runs. Layer 2 covers both.

## Layer 2 — engine-verified, one boot

Built. `Test.xs` in the Ageipelago xs folder (gitignored, and the live game folder), run by
`XsTesting.aoe2scenario`. It writes `profile/default1.xsdat`; `read.py` decodes that with
`kit xsdat decode --ledger` and prints the same PASS/FAIL table layer 1 does. **21 checks.**

### Running it

1. `/install` the seed first. The harness reads the installed `SlotData.xs`, `UnitData.xs` and
   `TechData.xs`, and needs unitsanity `all`, techsanity `all` and caveman on. It records all
   three in the sidecar and fails loudly on the wrong seed, so a mistake reports itself.
2. Start `XsTesting` at any speed and leave it alone. Eight cases, about two minutes.
3. When the chat turns green — *"AP78 done, file closed"* — quit the scenario so the file flushes.
4. `py -3 read.py`. With no argument it reads `profile/default1.xsdat` directly.

`selftest.py` proves the reader without the game: it builds a synthetic sidecar, checks a
known-good run passes 21/21, and checks three seeded faults are each caught by the right row.
Run it after any change to `read.py`.

### What it covers

| case | covers | what is asserted |
| --- | --- | --- |
| deathmatch item under `scenarioId` 101 and 105 | #71 | the resource delta is 0 elsewhere and exactly 7000/1000/500/7250 in Attila 5 |
| ten Elite Leitis spawned, Leitis Line item delivered, caveman pass run | #73 | all ten keep type 1236, none become Militia, location 441 sends, and the installed row's `upgradeItemId` is -1 |
| Capped Ram → Siege Ram, item first then research | #72 | three units reach type 548 and location 363 sends |
| Onager → Siege Onager, item first then research | #72 | type 588, location 376 |
| Man-at-Arms → Long Swordsman, item first then research | #72 | the non-siege control: type 77, location 320 |
| Pikeman → Halberdier, **research first then item** | #72 | the mirror ordering still works: type 359, location 341 |
| a Wonder for P2, then a second, then Atheism, then destroy one | #60 | **skipped here** - see below; the case still captures the timer string and proves the Wonder is complete and owned |

The timer *message* is captured as a string and asserted to read `<colour><name> Wonder <TIMER>`.

**Result, 2026-11-06, run 4: 20 of 20 passed, 6 skipped.** #71, #73 and #72 are verified in full.

### #60's countdowns are not stageable here

`InitVictoryThreats` sizes its owner array with `xsGetNumPlayers()`, which excludes Gaia, but
indexes it by player number. `XsTesting` has two players, so `EnableWonderThreat(2)` is refused
and no threat is ever armed. The sidecar proves it by calling the mod's own functions:
`xsGetNumPlayers=2`, `xsGetUnitOwner=2`, `IsWonderComplete=1`, `FindWonderSlot=-1`. Filed as
[#81](../../issues/81-wonder-threat-owner-array-is-one-slot-short.md); the shipped scenarios are
unaffected because they arm players below the top of their range.

`read.py` reports those six rows as SKIP with the reason, so layer 2 exits clean. They are layer
3 work on a real Attila 6 or Genghis 3, where the fog and the on-screen rendering need an eye
anyway.

### Two things it cannot settle

- **Whether `cAttrSetState Done` bumps `cAttributeResearchCount`.** `TechsanityUpdate` only
  reacts when that count rises, and the harness researches by writing the tech state. If the
  write does not move the counter the #72 cases report `upgraded=0` with `techState=3` and an
  unchanged `researchCount` — which is a *harness* miss, not a failed fix, and the detail column
  says so. If that happens the cases need a real research instead, which makes them layer 3.
- **The private arrays in `VictoryThreats.xs`.** XS globals are file-private, so the harness
  reads the public surface instead: `xsUnsyncGetTimerTimeRemaining` per timer id, and a count of
  map revealers owned by P1. That is the engine-visible effect rather than the mod's
  bookkeeping, which is the better thing to assert anyway.

Still in game from #60: the fog actually lifting, and the announcement and timer *rendering*.
Also "defeating a city clears its Wonder's countdown" — that needs a player genuinely out of the
game, which `XsTesting` cannot stage.

## Layer 3 — fork scenarios, played

Not built yet. The #51 `build.py` pattern: a fork of the live AP scenario with map, AI, civs and
triggers intact, and only the start position, age and item flags changed, so each check is a
few seconds of looking rather than a playthrough.

This layer exists because **XS cannot read whether an object is enabled**. `cEnableObject` is a
write-only effect; there is no `xsGetObjectEnabled`. So "does the Barracks offer Pikeman" is
irreducibly a human looking at a building, and the harness's job is to make that look cheap.

Checks that land here: #74 spikes Q1-Q4 and the trainability bullets, plus #60's fog reveal and
on-screen timer text.

## Prerequisite: the installed seed predates the #73 fix

`UnitData.xs` in the live xs folder still carries

```
addUnit(441, 1236, 868, 28, 1, 3800, 0);
```

`upgradeItemId` **3800**, the phantom tech item #73 was filed for. The AP-side fix is in
(`client/handlers/install/UnitData.py` now guards `tech not in self._techs`), but this install
was written before it. Until `/install` is re-run for this seed, #73's in-game check measures
the old behaviour and the Elite Leitis will cavemanify. `read.py` asserts the row directly, so
a stale install reports itself rather than looking like a failed fix.

## Prerequisite, resolved 2026-11-06

#74's candidate fix — the `tier == 0` gate in `setUnitDisable` — was committed as `7584f72` on
`origin/0.3.0` but the local Ageipelago checkout, which *is* the live game folder, sat one commit
behind at `fde97e9`. The game was running without the gate, so every #74 check would have tested
the old behaviour. The maintainer pulled; the gate is live.

### Case 8: the relic probe (groundwork)

`EnableRelicThreat()` has no caller, so `RelicThreatWatch` never runs in play and the relic half
of `VictoryThreats.xs` is unreachable today. This case is groundwork for when it is wired up.

It measures **player attribute 55, `ALL_RELICS_CAPTURED`** (`AoE2ScenarioParser/datasets/
trigger_lists/attribute.py`, boolean, beside `ALL_MONUMENTS_CAPTURED = 54`). If the engine
maintains that flag usefully, it replaces most of `FindRelicHolder`: the per-player relic scan,
`FindRelicMonastery`, and the bail on a relic that is not in a monastery all go away, and the
threat agrees with vanilla's relic victory by construction.

Three readings, for every player, of `attribute 55`, the relic count and the monastery count,
with `FindRelicHolder()`'s own answer beside them:

| stage | state |
| --- | --- |
| 0 | baseline, before anything is created |
| 1 | three relics created owned by P2 |
| 2 | and a Monastery for P2 |

**What it cannot answer.** XS has no garrison command, so a relic cannot be put inside the
monastery from script - stage 2 tests ownership plus a monastery standing, not capture. And
`XsTesting` has two players, so the team case (two allied enemies splitting the relics) needs a
larger scenario. Those stay open.

What it does settle cheaply: whether attribute 55 is readable from XS at all, and whether it
flips on ownership alone or needs a real capture.
