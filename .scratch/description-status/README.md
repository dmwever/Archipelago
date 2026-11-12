# description-status

In-game description status lines for units, technologies and buildings.

**Status:** ready-for-agent

Spec: [`worlds/age2de/docs/spec-description-status.md`](../../worlds/age2de/docs/spec-description-status.md)
Decision record: [`worlds/age2de/docs/adr/0006-an-unchecked-location-is-coloured-by-its-item-classification.md`](../../worlds/age2de/docs/adr/0006-an-unchecked-location-is-coloured-by-its-item-classification.md)
Vocabulary: `worlds/age2de/CONTEXT.md` — **checked**, **unlocked**, **researched**, **active**

Seams agreed with the maintainer: the game context, the location handler (09), and the install
row generators. The game half of the work lives in the Ageipelago checkout and is covered by the
linter rather than by tests.

## Issues

| # | Ticket | Status |
| --- | --- | --- |
| 01 | [The checked set is read when a scenario starts](issues/01-arm-the-checked-set-read.md) | done |
| 02 | [Classification reaches the game](issues/02-classification-reaches-the-game.md) | done |
| 03 | [The install bakes the extended tooltip id](issues/03-bake-the-extended-tooltip-id.md) | done |
| 04 | [A technology's description says where it stands](issues/04-technologies-carry-a-status-line.md) | ready-for-agent |
| 05 | [Units, buildings and ages carry a status line](issues/05-units-buildings-and-ages.md) | ready-for-agent |
| 06 | [Status lines survive an age advance](issues/06-status-lines-survive-an-age-advance.md) | ready-for-agent |
| 07 | [The Villager shows the profession row](issues/07-the-villager-shows-the-profession-row.md) | ready-for-agent |
| 08 | [A checked location's trigger clears itself](issues/08-checked-triggers-clear-themselves.md) | ready-for-agent |
| 09 | [The client's location channel is a handler](issues/09-the-location-channel-is-a-handler.md) | done (classification channel carried by #02) |

## Rulings

- 2026-11-10: Three seams, not two. The classification channel stays separate from the per-tick
  checked-locations writer.
- 2026-11-10: Classification is fetched by scouting at connect, never baked into an installed file.
- 2026-11-10: String ids for reading vanilla text are baked at generation; the game never derives
  them from a runtime attribute.
- 2026-11-10: The baked string ids come from the game dat read through aoe2kit, by a maintainer-run
  tool, into a checked-in source module.
- 2026-11-10: Professions show all twelve jobs always, colour when checked and greyscale when not.
  No text, no outstanding-only filtering.
- 2026-11-10: A job counts as checked only when both its male and female locations are checked.
- 2026-11-10: Mercenary seats and the resource hover panel are out of scope.
- 2026-11-11: The checked-set read is acked by the game, not armed once at connect. `CheckedLocationsCount`
  joins the packet from the reserved block; the client asks while it disagrees with the set it writes.
- 2026-11-11: No `world_version` bump for feature work; the bump belongs to a genuine release.
- 2026-11-11: The writer follows the bulk `serverComplete` pass as well as the single-id sites.
  Acceptance sits on 04 and is inherited by 05. It is also what covers a save loaded into a checked
  set that grew after it was saved, which 06's no-hook resume does not reach.
- 2026-11-11: A location already checked on the server clears its scenario trigger through an OR'd
  `script_call` condition, in 08. The XS flags are not collapsed and `CONTEXT.md`'s **Checked**
  entry stands.
- 2026-11-11: The 2026-11-10 separation ruling is amended, in 09. The checked-locations writer and
  the scouted classification table are one handler with two channels: separate file and separate
  cadence, same class. 02's acceptance and the spec are rewritten to match.
- 2026-11-11: Save and load is acceptance on 08, not a ticket of its own. A save carries the game's
  XS state and a reload brings the scenario triggers back as they were saved, so the gap is the
  player redoing an objective the server already holds, not a lost checked set.
- 2026-11-12: A mid-session flush leaves `classification.xsdat` alone; only a disconnect clears it.
  The file carries no per-scenario state and nothing else would rewrite it, so clearing it on a
  scenario switch would strip the colour off every unchecked status line for the rest of the
  session. Settled on 02, which also gave 09 its sixth acceptance line.
- 2026-11-12: Baked tables carry no provenance stamp. `GameStrings.py` was built with one and it
  was removed, and `GameCosts.py`'s `GAME_DATA_SOURCE` went with it, along with the test that
  asserted it was non-empty. The regenerating tool's docstring says where the data comes from and
  git history says when it was read. 03's first acceptance line was amended to drop the clause.
- 2026-11-12: Ages are baked in 03 alongside technologies, units and buildings, as
  `AGE_NAME_STRINGS` over `SHUFFLED_AGES`. An age advance's description is the age-up technology's,
  so 05 needs 28101 / 28102 / 28103, and the age-up techs are not `Age2TechData` members. The three
  dat tech ids live in the maintainer tool, not on `Age2AgeData`: nothing on the apworld side reads
  a genie tech id. How they reach the game is 05's to choose; there is no age table in XS yet.
