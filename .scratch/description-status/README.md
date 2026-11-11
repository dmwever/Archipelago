# description-status

In-game description status lines for units, technologies and buildings.

**Status:** ready-for-agent

Spec: [`worlds/age2de/docs/spec-description-status.md`](../../worlds/age2de/docs/spec-description-status.md)
Decision record: [`worlds/age2de/docs/adr/0006-an-unchecked-location-is-coloured-by-its-item-classification.md`](../../worlds/age2de/docs/adr/0006-an-unchecked-location-is-coloured-by-its-item-classification.md)
Vocabulary: `worlds/age2de/CONTEXT.md` — **checked**, **unlocked**, **researched**, **active**

Seams agreed with the maintainer: the game context, a new classification handler, and the install
row generators. The game half of the work lives in the Ageipelago checkout and is covered by the
linter rather than by tests.

## Issues

| # | Ticket | Status |
| --- | --- | --- |
| 01 | [The checked set is read when a scenario starts](issues/01-arm-the-checked-set-read.md) | done |
| 02 | [Classification reaches the game](issues/02-classification-reaches-the-game.md) | ready-for-agent |
| 03 | [The install bakes the extended tooltip id](issues/03-bake-the-extended-tooltip-id.md) | ready-for-agent |
| 04 | [A technology's description says where it stands](issues/04-technologies-carry-a-status-line.md) | ready-for-agent |
| 05 | [Units, buildings and ages carry a status line](issues/05-units-buildings-and-ages.md) | ready-for-agent |
| 06 | [Status lines survive an age advance](issues/06-status-lines-survive-an-age-advance.md) | ready-for-agent |
| 07 | [The Villager shows the profession row](issues/07-the-villager-shows-the-profession-row.md) | ready-for-agent |

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
