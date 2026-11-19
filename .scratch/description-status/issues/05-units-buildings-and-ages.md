# 05: Units, buildings and ages carry a status line

**What to build:** A unit, a building and an age advance each carry the first segment of the status
line and nothing else: the checked or unchecked mark, Checked in green or Unchecked in the colour of
the class of item waiting there. They have no effect state worth reporting — an age's is something
the resource bar already shouts, and a unit's or a building's is just whether it is trainable or
buildable. A building this seed did not shuffle carries no line even though the game registers all
thirty-five buildings in every seed; the scout reply is what reconciles the two. Gaia objects are
left alone: they reject the description write and report no name id.

**Blocked by:** 04 (the writer and the status-line shape).

**Status:** done

- [x] A unit location, a building location and an age advance each carry a first segment, coloured
      by classification while unchecked and green once checked
- [x] None of the three carries a second segment
- [x] With Buildsanity partially enabled, a building outside the shuffled categories carries no line
- [x] Gaia objects are never written to
- [x] Lines are written in the init pass and rewritten per object from the sites that know which id
      changed, the bulk `serverComplete` pass in 04 included
- [x] Vanilla description text is intact beneath each line
- [x] The xs lints from the xs folder against the entry point

## Rulings

- 2026-11-13: Duplicate ledger entries for one location id are not a defect, and 05 does not change
  how any module registers locations.
- 2026-11-13: Ages reach the game as three `extern const` in `AP_Constants.xs`, not through a table.
- 2026-11-13: An object with no extended tooltip string gets no status line.

## Comments

- 2026-11-13: Built on 04's seam without widening it. `RefreshLocationDescription` in `AP.xs` reads
  the id once and routes to one of four functions, one per module, on the `GiveItem` band-dispatch
  pattern `ItemHandler.xs` already uses. A first pass called all four and let each bail on anything
  that was not its own, which cost four `structGetInt` per ledger entry on the full pass - and that
  is a `findIndexString` over the attribute names every time. Routing makes it one plus one.
  It invents no bands: the id legend and its `AP_*_ITEM_MIN`/`MAX` constants moved out of
  `ItemHandler.xs` into `AP_Constants.xs`, where rule 3 says a shared `extern const` belongs, and the
  dispatcher reads the same ones `GiveItem` does. `AP_PROGRESSION_ITEM_MIN` is already the end of the
  unit band and `AP_BUILDING_ITEM_OFFSET` already the 200, so a first pass that added
  `UNIT_LOCATION_FIRST`, `UNIT_LOCATION_CAPACITY` and `BUILDING_LOCATION_FIRST` was duplicating
  numbers the file already had; all three are gone. `locationRowHead` is sized and indexed off the
  band the same way `techByItem` is - `AP_PROGRESSION_ITEM_MIN - AP_UNIT_ITEM_OFFSET` long, indexed
  by `locationId - AP_UNIT_ITEM_OFFSET` - which also took it from 1000 entries to 700.
  Checked over every real range rather than by eye: ages 26-28, buildings 200-234, units 300-934 and
  techs 3600-3999 each reach exactly one handler, while 0-24, the 30-199 civ band, 1000-3599,
  4000-5099 and the scenario locations at 10100+ reach none. The four keep their own guards because each is also called directly -
  `RefreshTechStatusLine` from `Techsanity.xs`, `RefreshUnitStatusLine` from `MarkRowOwned`,
  `RefreshBuildingStatusLine` from `BuildsanityChecks` and `RefreshAgeStatusLine` from
  `ShuffleAgesUpdate` - so the dispatch is a fast path, not their only gate. No module learned about
  another.
- 2026-11-13: The unit side carries no location index and caches nothing. A first pass gave `addUnit`
  a head/next chain so a location could find its rows; a second hung the `Location` vector on each
  `Unit`. Both were wrong. The chain was machinery for a direction the row already knew, and the
  cached vector aliased one shared mutable struct onto five rows - a Champion is not a Militia, and
  a field like that invites per-unit state to be written through it and hit the whole line.
  `RefreshUnitStatusLine` now takes the location, reads its id, resolves the canonical entry with
  `FindLocationById` and writes every row whose location id matches, found through one 400-int
  mirror of the rows' location ids. The only state that is shared is the location's own, which is
  what a unit line genuinely is; everything per-unit - `typeId`, `tooltipId`, `hasStatusLine` -
  stays on the row.
- 2026-11-13: Resolving by id is also why the duplicate ledger entries stop mattering, rather than
  needing to be removed. Whichever copy the full pass hands in, the write comes from the first match,
  which is the only copy `LoadClassification` and the two `Set*Complete` ever reach. Traced against a
  five-deep duplicate set: visiting every copy leaves all five rows correctly decorated.
  `InitUnitsanity` is untouched.
- 2026-11-13: A location maps to several unit rows, so the unit side needs location -> rows. A plain
  scan was measured as the wrong shape rather than assumed: `structGetInt` in `structs.xs` runs
  `findIndexString` over the attribute names on every field read, so a 400-row scan per ledger entry
  is millions of string comparisons at init and again on every age advance. `addUnit` now threads an
  intrusive list, `locationRowHead` keyed by location id and `nextRowSharingLocation` keyed by row,
  which also gave `InitUnitsanity` its one-location-per-id sweep for free.
- 2026-11-13: Ages carry no `hasStatusLine` and the other three do. Not an oversight: `ageRegistered`
  already says the age is this seed's, and a registered age is always decorated in the init pass
  because `classificationLoaded` is still false there, so the flag could never be false where it was
  read. A `xsArrayCreateBool` for it was written and taken back out. There is no `Age` struct to
  hang a field on, which is what made the side array the only alternative.
- 2026-11-13: `ShuffleAgesUpdate` is level-triggered: it re-runs `AP_Check_Location(age)` every tick
  until the rule disables itself. Hanging the refresh off that directly would write a description per
  tick, against the spec's no-new-per-tick-work line, so the refresh fires only on the transition.
  `AP_Check_Location(age)` is left exactly as it was. The honest cost is one extra `FindLocationById`
  per reached age per tick while the rule lives — `AP_Check_Location` already does one through
  `SetScenarioLocationComplete`, so it is 2 scans where there was 1, not a new kind of work.
- 2026-11-13: Rejected in review: moving the refresh into `AP_Check_Location` to collapse the five
  call sites. `onTechResearched` calls `tryApplyEffect` between the check and the refresh, and that
  is what sets the `effectDone` the second segment reads, so a hoisted refresh would leave a freshly
  researched tech reading Must Research until some later event corrected it. It would also put a
  ledger scan and four dispatches on all 175 scenario-trigger checks, whose ids have no description
  target at all. The ticket asks for rewrites from the sites that know which id changed, which is
  this shape rather than a blanket hook.
- 2026-11-13: Rejected in review: deriving the age tooltip as `28000 + ageTechFor(age)`. The
  arithmetic does hold for these three, but it is a dat numbering coincidence, and 03 settled that
  the ids are baked and the game never computes them. The three were read back out of the game's own
  `key-value-strings-utf8.txt` instead: 28101, 28102 and 28103 are the real age-up tooltips.
- 2026-11-13: Rejected in review: extracting the four same-shaped `Refresh*StatusLine` bodies. XS has
  no polymorphism and no function pointers, so the shared part would have to become a switch on a
  kind int - one smell traded for another. `CheckedStatusText` extracts the half that can be shared.
- 2026-11-13: The unit table is the only one whose rows are not all the same kind of thing, and its
  tooltip ids show it. Counted against the game's own `key-value-strings-utf8.txt`: techs resolve
  298/298, buildings 35/35, ages 3/3, but of the five enums behind `UnitLocation` only the two
  trainable ones hold up - jobs resolve 4/24, heroes 9/16, escorts 0/2. The extended tooltip is the
  train-button tooltip, and a job, hero or escort is a location you reach by owning the unit, not by
  training one, so the game never wrote it a Create string.
- 2026-11-13: Worse than absent, in thirteen cases. A first pass here claimed the job, hero and
  escort ids simply resolve to nothing, from a four-id spot check; reading all 42 says otherwise.
  `HERDER` is name 5897, and 26897 is a real string - "Build Chief's Yurt", a building tooltip.
  `OYSTER_GATHERER` and nine Joan heroes land in the 21xxx campaign band, where +21000 reaches the
  42xxx scoreboard strings: 42304 is "Total Score is the overall total...", 42306 is the literal
  text `42306`. So the writer's empty-`xsGetString` guard catches the 29 that are absent and cannot
  catch the 13 that are merely wrong. What keeps all 42 invisible is that none has a train button,
  which is the same reason the game never gave them a Create string. Both facts were measured, not
  assumed, and the guard is still worth its two lines for the 29.
- 2026-11-13: `xsSetObjectDescription` returns a bool and it is ignored on purpose; the spec records
  that it returns true even when nothing is displayed, so it proves nothing. `hasStatusLine` records
  that a write was attempted, which is all the undecorate path needs. Four `bool written = ...`
  locals were written to dodge a `DiscardedFn` warning and removed once the linter was actually
  asked: the six warnings on a clean entry point are all pre-existing sites and none is this call.
- 2026-11-13: Unverified in game, as 04's newline note still is. Nothing here was seen rendered: the
  checkbox materials, the colour tags and the prepended line are all inherited from 04, and what 05
  adds is which objects get one. Worth a look on the next playtest alongside 04's `"
"`.
