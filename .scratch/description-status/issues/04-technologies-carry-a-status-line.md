# 04: A technology's description says where it stands

**What to build:** Hovering a technology this seed made into a location shows one line above the
vanilla text, which stays intact. The line reads the location's state first and the effect's state
second, two segments joined by a dash: a checked or unchecked mark with Checked in green or
Unchecked in the colour of the class of item waiting there, then Awaiting Item in red, Must Research
in yellow, or Active in green. A technology with no effect reads Active, because there is nothing
left to wait for. A technology this seed did not make a location carries no line at all, whatever
the game registered locally — the scout reply decides. In the moment between connect and that reply
the first segment renders with no colour rather than a wrong one. Every technology is written at
scenario init, and after that only the technology that moved is rewritten, from the sites that
already know which id changed. Nothing sweeps on a timer. One of those sites is a bulk one:
`MarkServerLocations` flips `serverComplete` for many ids in a single loop, at every scenario start
and whenever the game's `CheckedLocationsCount` disagrees with the client's checked set, so the writer has
to follow that loop and not only the single-id sites.

**Blocked by:** 01 (the checked set), 02 (classification), 03 (the tooltip ids).

**Status:** done

- [x] Each of the six checked / unlocked / active combinations renders its two segments as the spec
      says, and each segment is terminated so no colour tag bleeds into the vanilla text below
- [x] A technology with no effect reads Active
- [x] A technology absent from the scouted set carries no line
- [x] An unchecked location whose classification has not arrived renders its first segment with no
      colour
- [x] The vanilla description text is intact beneath the line
- [x] The full pass runs at scenario init; a state change rewrites only the object that changed and
      adds no per-tick work
- [x] A bulk `serverComplete` pass rewrites every line it flips, not only the single-id sites: at
      scenario start, on an ack mismatch, and when a save is loaded into a checked set that grew
      after it was saved. A settled pass flips nothing and so rewrites nothing
- [x] The item at a location is never named
- [x] The xs lints from the xs folder against the entry point; the game half carries no tests in
      this repo

## Rulings

- 2026-11-13: The status line reaches the game through `Descriptions.xs`, included by `AP.xs` with the
  other top-level modules. `AP_Headers.xs` was hoisted out of `Buildsanity.xs` to sit directly under
  `AP_Constants.xs` to make that possible: the ledger, the structs and the stubs are then above
  everything, and `Descriptions.xs` can sit above `ItemHandler.xs`, which is where `Techsanity.xs`
  reads it. Measured, not assumed - see the next comment. Classification lands on the `Location`
  struct as a `classification` field rather than in a table of its own, so the one `FindLocationById`
  a line already needs answers both checked and colour.
- 2026-11-13: The include graph was pinned with the linter rather than by reading. `Descriptions.xs`
  below `ItemHandler.xs` is two `NameError`s in `Techsanity.xs`, which loads inside it;
  `Descriptions.xs` above the ledger is ten, for `structGetInt` and friends; `AP_Headers.xs` above
  `AP_Constants.xs` is seven, for the age constants `ageReached()` reads and the class constant
  `ScenarioLocations.xs` now defaults with. `AP_Headers.xs` above `SlotData.xs` and `AP_Globals.xs`
  is fine - it uses neither.
- 2026-11-13: The scout reply is read once, by `ConnectAP`, at the point it has the client and the
  scenario's items and is about to hand off to `ReadAP`. No ping flag carries the file and it gets no
  rule of its own. A reply that has not landed by then leaves the lines uncoloured for the scenario,
  which is the fallback the spec already designed; a retry loop is not worth its weight.
- 2026-11-12: Filler is `<AQUA>`. The spec says cyan and the engine has no `<CYAN>` tag; the
  hard-coded list in `AoE2DE_s.exe` is the eight player colours plus `<DEFAULT>`, `<WHITE>`,
  `<BLACK>` and `<COL11>`-`<COL16>`.

## Comments

- 2026-11-13: Built around one seam, `mutable void RefreshLocationDescription(vector location)` in
  `AP_Headers.xs`, defined in `AP.xs` beside `AP_Check_Location`. The two are the same shape: the
  location-level entry points, declared as stubs so anything in the include chain can reach them and
  defined in the bridge, which is the only file that sees every module. #05 adds units and buildings
  to that one body. Everything takes the `Location` vector rather than a location id, so nothing
  looks the ledger up twice: `RefreshTechStatusLine(location)` in `Techsanity.xs` is the only
  tech-side function, indexing `techByItem` directly, and `RefreshDescriptions` in `Descriptions.xs`
  is a walk of the ledger that knows nothing about techs at all.
- 2026-11-13: `ItemHandler.xs` is untouched by this ticket. Both the dispatcher and the include sat
  there first, on the grounds that it is the file that sees every sanity module, but that is include
  order talking: the file is about items, and a status line is not one. `Buildsanity.xs` loses its
  `AP_Headers.xs` include in the hoist and now receives those symbols the way `Ages.xs` and the
  mercenary files already do.
- 2026-11-12: A first pass routed by `int locationId` and ended up with five functions for one job -
  three in `Techsanity.xs`, two of them a letter apart, plus two forwarders in `ItemHandler.xs` that
  were not the `mutable` seam this codebase already uses. Passing the vector collapsed it to one
  function per module and took the linear `FindLocationById` out of the full pass.
- 2026-11-12: A tech decorated before the scout reply arrives has to be able to lose its line, because
  the reply may not name it. `hasStatusLine` on the `Tech` struct records whether we wrote one, so the
  undecorate path puts the vanilla text back and never touches a tech we never touched.
- 2026-11-13: `MarkServerLocations` only rewrites what it flips, through the ledger's own
  `IsServerLocationComplete` then `SetServerLocationComplete`. The rule still resolves the location
  itself first - silently for a global id, through `GetLocationById` for one of this scenario, where
  a missing entry is a real fault worth chatting - so neither of the two ever reaches its own error
  path. A `MarkServerComplete` helper was added here and taken back out: the pair already says it.
- 2026-11-12: The marks are `<CheckBoxChecked>` and `<CheckBoxUnchecked>`, read out of
  `AoE2DE/widgetui/materials.json`, where they are atlas materials off `defaultwidgets`. A first pass
  used `checkbox_tick_yellow`, which is a WPF `StaticResource` brush key in
  `wpfg/systemresourcescheckbox.xaml` and not a material name at all - it would have rendered as
  nothing, silently. Swapping them for Archipelago art is one line in each of the two mark functions.
- 2026-11-12: Not every tech that is a location in this seed carries a line, and that is intended. A
  tech only gets a `Location` ledger entry from `initTech`, which skips anything already
  `cTechStateDone`, and `InitTechsanity` skips what `reconstructStartingState` granted. Every tech in
  that set is done in the engine - `completeIfPending` forces `STATE_DONE` - or invalid for the
  player's civ, so none of them has a button left to hover. Raised in review against the ADR's
  "absent from the reply gets no status line"; the converse case it names has no hover target.
- 2026-11-12: Unverified in game, and only a person can see it: the `"
"` between the status line
  and the vanilla text is the only string escape in the XS tree. The linter accepts it and the game's
  own `key-value-strings-utf8.txt` writes description line breaks the same way, so either the XS lexer
  emits a newline or the renderer reads the two characters - both give a break. A failure here is
  silent, so it wants a look on the next playtest.
