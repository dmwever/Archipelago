# 10: Caveman is late to knock a unit down (Knight held a long time, then became Militia)

**Reported:** 2026-10-20, playtesting

**Status:** needs-info

## Report

On caveman mode, a Knight stayed a Knight for a long time, then turned into a Militia. The reporter
suspects either a missed check when the unit count goes up, or something specific to conversion.

## Needs from reporter

- How the Knight was obtained: trained, converted, granted by a trigger, or a mercenary?
- Was a lot going on at the time (constant training, fighting, deaths)?
- What happened just before it turned: a research, an item, a unit dying or being made?

## Audit (from code, not verified in game)

The caveman sweep runs in the `UnitsanityChecks` rule (`Unitsanity.xs:323-366`), once a second.
Two things mark the unit list dirty, and each of them **returns early** instead of sweeping:

```
if (owned != unitsOwned) { unitsOwned = owned; unitsDirty = true; return; }
if (researched > unitsResearchCount) { ...; unitsDirty = true; return; }
```

`ApplyCaveman` only runs on a tick where neither the unit count nor the research count changed since
the previous tick. Two ways that delays it:

1. **Busy games starve the sweep.** While the unit count changes every second (training queues,
   deaths in a fight, units created by triggers), every tick takes the early return and the sweep
   never runs. A new Knight stays a Knight until there's a quiet second. That fits "a long time,
   then it changed".
2. **A one-for-one swap is never seen.** Dirtiness only compares the *total* count. If a Knight
   joins (conversion, trigger, training) in the same second another unit is lost, the count doesn't
   change and nothing marks the list dirty. The Knight is only swept when some *later*, unrelated
   change happens. Conversion is especially likely to coincide with losses, since it happens in
   combat. That fits the conversion hunch, but the gap isn't conversion-specific.

Not the cause, as far as the code shows: conversion itself. A converted Knight is an ordinary
player-1 unit of type Knight, picked up by `xsGetPlayerUnitIds(1, -1, ...)`, not immune, and its
row isn't caveman-exempt. Mercenary spawns are immune by design (`MercenarySpawn.xs:77`), so a
mercenary Knight would *never* be knocked down. If this one came from the pavilion and still
turned, the immunity list is the thing to look at.

## Likely shape of a fix

Sweep on the same tick the change is noticed, instead of returning first. Or compare the set of unit
ids rather than the count (cheap enough at one sweep per second), so a swap is also caught. Also
consider a slow unconditional sweep (every few seconds) as a backstop, the way
`PROFESSION_SWEEP_SECONDS` already does for professions.
