# 85: the Wonder countdown is a fixed 200 years, but the game's scales with map size

**Reported:** 2026-11-07 by the maintainer, noticed while playing `PT82_G3W` on Genghis 3

**Status:** done

**Related:** [#60](60-genghis3-jin-wonder-no-threat.md) (the victory threats),
[#82](82-layer-3-in-game-checks.md) (the run it surfaced in),
[#84](84-wonder-foundation-is-never-tracked.md) (the other `VictoryThreats.xs` finding from the
same run)

## Report

`AP_Constants.xs` pins the countdown:

```
extern const int THREAT_BASE_YEARS = 200;
extern const float THREAT_MODIFIER_PER_YEAR = 10.0;
```

and `CountdownYears` adds `modifier / 10` on top, which is how Atheism's Hun Wonder bonus becomes
extra years. The number is the same whatever scenario it runs in.

**The game's own Wonder countdown depends on map size.** The maintainer saw the discrepancy on
Genghis 3. The mod's timer therefore reads differently from what a player who knows the game
expects, and differently again from scenario to scenario.

The eighteen AP scenarios are four of the editor's size presets. The preset table is aoe2kit's
measured one (`pkg/scenario/writer.go`): Tiny 120, Small 144, Medium 168, Normal 200, Large 220,
Huge 240, Giant 252, Massive 276, Enormous 300, Colossal 320, Incredible 360, Monstrous 400,
Ludicrous 480.

| preset | side | scenarios |
| --- | --- | --- |
| **Small** | 144 | Attila 1, Attila 3, Joan 1, Joan 4, Joan 6, Genghis 2, Genghis 5, Genghis 6 |
| **Medium** | 168 | Attila 2, Attila 4, Joan 3, Genghis 1 |
| **Normal** | 200 | Attila 5, Joan 2, Joan 5, **Genghis 3** |
| **Large** | 220 | **Attila 6**, Genghis 4 |

So a single constant is wrong on most of them, and the Wonder checks in
[#82](82-layer-3-in-game-checks.md) were read against it.

## The two readings so far

The maintainer read the game's own countdown in two scenarios:

| preset | side | observed |
| --- | --- | --- |
| Normal | 200 | **300 years** (Genghis 3) |
| Large | 220 | **350 years** (Attila 6) |

Both are the *game's* countdown, not the mod's - the mod would have shown 200 in each, since
`THREAT_BASE_YEARS` does not vary.

**There is no formula.** The game carries a hard-coded table of years per map size, which the
maintainer confirmed after two guessed rules - +50 per preset, and 2.5 x side - 200 - both of
which fit Normal and Large and are both wrong. The search values below break them immediately:
Tiny is 200, not 150 or 100, and Miniature is 100.

The table, from the maintainer. Sides and years both; the starred presets are the ones that need
the `MORE_MAP_SIZES` launch parameter.

| preset | side | years | |
| --- | --- | --- | --- |
| Mini / Miniature | 80 | 100 | * |
| Tiny | 120 | 200 | |
| **Small** | 144 | **200** | |
| **Medium** | 168 | **200** | |
| **Normal** | 200 | **300** | 25:00 |
| **Large** | 220 | **350** | 29:10 |
| Huge | 240 | 400 | **was called Giant** |
| Giant | 252 | 400 | * |
| Massive | 276 | 400 | * |
| Enormous | 300 | 450 | * |
| Colossal | 320 | 450 | * |
| Incredible | 360 | 450 | * |
| Monstrous | 400 | 500 | * |
| Ludicrous | 480 | 500 | |

**The sides check out against the game's own data.** aoe2kit grounds its preset list in the
shipped DE string table keys `MAPSIZE_*` at 25080..25480, whose low three digits encode the map
edge - 25080 is 80, 25480 is 480 - and its table matches this one entry for entry, including
`MAPSIZE_MINI` at 80, which it names *Mini*. The seven starred presets are also exactly the seven
missing from the kit's `editorResizePresets`, which holds only tiny, small, medium, normal,
large, huge and ludicrous. Two independent things agreeing on the same split.

**Huge was previously called Giant**, and today there is also a Giant at 252. An older table
saying "Giant 240" means today's **Huge**; "Giant" now means 252. Both are 400 years, so the trap
costs nothing here, but it will bite anyone reading an older source for a different field.

Sizes share values in runs - 200 across Tiny, Small and Medium; 400 across Huge, Giant and
Massive; 450 across Enormous, Colossal and Incredible; 500 across Monstrous and Ludicrous - which
is why no formula on side length can fit it.

**`THREAT_BASE_YEARS = 200` is right for twelve of the eighteen scenarios.** An earlier note here
said it matched Tiny and was wrong everywhere; that was wrong, and this supersedes it. Small and
Medium are 200 as well, so the constant is correct for every Small and Medium scenario and wrong
only for these six:

| scenario | preset | shows | should show |
| --- | --- | --- | --- |
| Attila 5 | Normal | 200 | **300** |
| Joan 2 | Normal | 200 | **300** |
| Joan 5 | Normal | 200 | **300** |
| Genghis 3 | Normal | 200 | **300** |
| Attila 6 | Large | 200 | **350** |
| Genghis 4 | Large | 200 | **350** |

Of those six, only Genghis 3 and Attila 6 arm a Wonder threat today, so only those two show the
wrong number in play - which is exactly where the maintainer saw it. The other four would be
wrong the moment a threat is armed there.

**Years convert to real time at a flat rate.** 300 years in 25:00 and 350 years in 29:10 are both
12 years per minute, so the per-size difference is in the *years*, not in how long a year lasts.
Settled by the maintainer: under `cTimerUnitYears` only the count varies, the engine's year does
not. So `xsDisplayTimer` needs the right number of years and nothing else; the conversion is not
this ticket's problem and does not need checking while implementing.

## Not yet established

- [x] Whether the relic countdown scales the same way. **It is identical to the Wonder's**, per
      the maintainer - same table, same values. And `CountdownYears` is already shared: called
      from `StartWonderCountdown` at `VictoryThreats.xs:147` and from the relic path at
      `VictoryThreats.xs:380`. So one change to that one function fixes both threats, with no
      branching between them.

## The fix

`xsGetMapWidth()` and `xsGetMapHeight()` both exist and return ints, so the size is readable.

**The whole change is `CountdownYears`.** It is the single place both threats get their number:
`StartWonderCountdown` calls it at `VictoryThreats.xs:147`, the relic path at
`VictoryThreats.xs:380`, and relic times are identical to Wonder times, so neither caller needs
to know anything about this. Nothing else in the file moves.

Replace the constant with a lookup on the side length, keeping `THREAT_MODIFIER_PER_YEAR` for the
Atheism adjustment on top. A table, not a formula - the values sit in runs, not on a line.
Thresholds rather than equality, so a size nobody anticipated still lands somewhere sensible:

| side at most | years |
| --- | --- |
| 80 | 100 |
| 168 | 200 |
| 200 | 300 |
| 220 | 350 |
| 276 | 400 |
| 360 | 450 |
| anything larger | 500 |

Seven branches, total over every size the game has.

## Acceptance criteria

- [x] The rule is written down, with where it came from. The table above, from the maintainer,
      off the wiki's Wonder page; Normal and Large independently match their own in-game
      readings.
- [x] The countdown matches the game's own on at least two different map sizes, checked in game.
      `PT82_G3W` is 200x200 and `PT82_A6W` is 220x220, so the two forks already cover two sizes.
      *(Verified in game by the maintainer, 2026-11-08: 300 on `PT82_G3W`, 350 on `PT82_A6W`.)*
- [x] `THREAT_BASE_YEARS` is gone, or demoted to the floor of the new table. Its current value
      of 200 is the right answer for Tiny, Small and Medium, so twelve scenarios should not move
      at all. *(Gone 2026-11-08, replaced by the table below. 200 survives as
      `THREAT_YEARS_MEDIUM`, so Small and Medium scenarios do not move.)*

## Comments

### 2026-11-08 - implemented

`THREAT_BASE_YEARS` is replaced in `AP_Constants.xs` by six `THREAT_SIDE_*` / `THREAT_YEARS_*`
pairs plus `THREAT_YEARS_LUDICROUS`, and `ThreatBaseYears()` in `VictoryThreats.xs` does the
lookup. `CountdownYears` calls it; `StartWonderCountdown` and `StartRelicCountdown` are
untouched, so the relic timer moves with the Wonder's.

Seven branches, fourteen presets. Each pair is named after the largest preset in its run, since
the values sit in runs:

| constant pair | side at most | years | presets covered |
| --- | --- | --- | --- |
| `*_MINI` | 80 | 100 | Mini 80 |
| `*_MEDIUM` | 168 | 200 | Tiny 120, Small 144, Medium 168 |
| `*_NORMAL` | 200 | 300 | Normal 200 |
| `*_LARGE` | 220 | 350 | Large 220 |
| `*_MASSIVE` | 276 | 400 | Huge 240, Giant 252, Massive 276 |
| `*_INCREDIBLE` | 360 | 450 | Enormous 300, Colossal 320, Incredible 360 |
| `THREAT_YEARS_LUDICROUS` | - | 500 | Monstrous 400, Ludicrous 480 |

`ThreatBaseYears()` takes the larger of `xsGetMapWidth()` and `xsGetMapHeight()`, so a
non-square map still lands somewhere sensible.

`Test.xs` logs `ThreatBaseYears()` in place of the dead constant in its `REC_STAGE` record, so
the harness reports the map-derived number.

`xs-check -I .`: 0 errors on all 18 entry points and `Test.xs`; warnings unchanged at 6 per
scenario and 7 for `Test.xs`, none in `VictoryThreats.xs`.

Still open: the in-game check. `PT82_G3W` (200x200) should read **300** and `PT82_A6W`
(220x220) should read **350**. Note that [#84](84-wonder-foundation-is-never-tracked.md) was
reopened the same day over the Wonder's footprint, and its fix touches `VictoryThreats.xs` and
`Test.xs` too - one `PT82_G3W` run can close criteria on both.

### 2026-11-08 - closed

Verified in game by the maintainer: `PT82_G3W` reads 300 and `PT82_A6W` reads 350, matching
the game's own countdown. Ticket closed.
