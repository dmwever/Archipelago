# 03: The install bakes the extended tooltip id

**What to build:** Reading an object's vanilla description text in game needs the extended tooltip
string id, which is the dat's name string id plus a fixed offset. The runtime attribute that looks
like that id is not it: for the Villager it reports a different number whose derived tooltip does
not exist, and for Gaia objects it reports nothing. So the ids are baked rather than derived at
runtime. A checked-in source module holds the name string id for every technology, unit and
building the seed can install, stamped with where the data came from the way the game-cost table is,
and a maintainer-run tool regenerates it by reading the game dat through aoe2kit. The technology
and unit row generators emit the extended tooltip id per installed row, and the game's
thirty-five-building table carries one per building. Nothing reads the ids yet.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] A source module holds the ids and names its provenance; a tool beside the other maintainer
      tools regenerates it from the game dat and says how to run it the way they do
- [x] Every decorated technology row and unit row carries the extended tooltip id, and a row the
      seed does not install carries none
- [x] The ids the rows carry agree with the source module rather than being invented or computed
      from a runtime value
- [x] The building table carries one id per building, from the same source
- [x] The table loaders in the game accept the extra field, and the xs lints from the xs folder
      against the entry point
- [x] Covered as the technology and unit catalogues already are: build the table, assert on the rows
- [x] The pre-commit subset for the files touched passes, plus the technology and unit catalogue
      tests

## Comments

- 2026-11-12: Built. `locations/connections/GameStrings.py` holds the name string id for every
  technology, age advance, unit, villager job, hero, escort and building, keyed by the `Age2*`
  member, and asserts at import that each kind and its ids agree.
  `tools/recapture_string_ids.py` regenerates the whole file from the dat through `kit dat units`
  and `kit dat tech`; the run takes about nine minutes because every technology costs a full dat
  parse. `EXTENDED_TOOLTIP_OFFSET` is 21000.
- 2026-11-12: Exactly one technology carries `language_dll_name` 0 and only an extended help id:
  `CHAMPI_SCOUT`, which is dat tech 1350, "Champi Scout (Make avail)", help 107487. The tool falls
  back to the help id less 100000, giving 7487, whose tooltip 28487 reads "Upgrade to Champi
  Runner" - the catalogue's name for that tech is the odd part, not the id. Measured by reading all
  298 technology records; an earlier note here said fifteen, which confused this with the fifteen
  technologies whose name string is legitimately six digits. Checked afterwards against the game's
  own `key-value-strings-utf8.txt`: all 298 technology ids and all 35 building ids resolve both as a
  name and, plus the offset, as an extended tooltip, so nothing in the table is invented. The 28
  units with no English name string are Chronicles-era; the jobs, heroes and escorts have no create
  tooltip, which is the game's own shape rather than a gap here.
- 2026-11-12: The offset is pinned by test in all three bands the dat uses, each literal read out
  of the strings file rather than recomputed: vanilla 5xxx/7xxx (Loom 28022, Archer 26083, House
  26344), antiquity 405xxx (Hoplite 426007) and late-DLC 507xxx (Ordonnance Companies 528025).
- 2026-11-12: "A row the seed does not install carries none" is the technology grant-only row,
  which gets `NO_TOOLTIP`. Every unit row is a location, so the unit side has nothing to withhold.
- 2026-11-12: The building table is the one hand-kept mirror. All 35 literals in `Buildsanity.xs`
  were checked against `BUILDING_NAME_STRINGS` programmatically and agree, but per the no-cross-repo
  tests rule nothing guards them; the XS half is covered by the linter, which is clean against
  `AP_Attila_1.xs`, `AP_Joan_1.xs` and `AP_Genghis_1.xs` (only the pre-existing `DiscardedFn` and
  `FirstOprArith` warnings remain). `addTech`, `addUnit` and `createLocationLock` all gained a
  defaulted `tooltipId`, and the `mutable` stubs in `AP_Headers.xs` were moved with them — a stub
  left behind is a `NameError` from the linter, not a silent miss.
- 2026-11-12: Ages do carry an entry, as `AGE_NAME_STRINGS` over `SHUFFLED_AGES`. #05 writes the
  first segment onto an age advance, whose description is the age-up technology's, so it needs
  28101 / 28102 / 28103 and could not have reached them: the age-up techs are not `Age2TechData`
  members and ages are not rows in either generator. The three dat tech ids live in the tool as
  `AGE_UP_TECHS`, not on `Age2AgeData` - nothing on the apworld side reads a genie tech id, so the
  mapping is the tool's business. The XS side has no age table yet; #05 chooses how the three ids
  reach the game.
- 2026-11-12: The provenance stamp the first acceptance line asks for is deliberately absent, at
  the maintainer's instruction. `GameCosts.py`'s `GAME_DATA_SOURCE`, the precedent it named, was
  removed in the same pass along with the test that asserted it was non-empty. Where the ids came
  from is in the tool's module docstring, and when they were read is in the git history.
