# 07: The Villager shows the profession row

**What to build:** Villager professions are checked by accident as often as on purpose and nothing
in the game names them, so the Villager's own description carries a row of twelve job icons — job
variants are not trainable and have no description of their own, which is why the row hangs off the
Villager. Each job shows its vanilla icon once checked and a greyscale icon until then; the
greyscale materials already ship in the Ageipelago UI mod. A job counts as checked only when both
its male and female locations are checked, so the row never claims a job is finished when half of
it is not. Only the jobs this seed generated appear, which the scout reply decides. No text, and no
filtering down to the outstanding jobs.

**Blocked by:** 04 (the writer, and the Villager's own status line).

**Status:** ready-for-agent

- [ ] The Villager's description carries the row of job icons, with its own status line and the
      vanilla text both intact
- [ ] A job reads checked only when both of its locations are checked
- [ ] A job this seed never generated is absent from the row
- [ ] Icons are inlined by material name and are not tinted by the line's colour tags
- [ ] Without the UI mod installed the unchecked icons render as nothing and everything else still
      works
- [ ] The xs lints from the xs folder against the entry point
