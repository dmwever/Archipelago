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

**Status:** ready-for-agent

- [ ] Each of the six checked / unlocked / active combinations renders its two segments as the spec
      says, and each segment is terminated so no colour tag bleeds into the vanilla text below
- [ ] A technology with no effect reads Active
- [ ] A technology absent from the scouted set carries no line
- [ ] An unchecked location whose classification has not arrived renders its first segment with no
      colour
- [ ] The vanilla description text is intact beneath the line
- [ ] The full pass runs at scenario init; a state change rewrites only the object that changed and
      adds no per-tick work
- [ ] A bulk `serverComplete` pass rewrites every line it flips, not only the single-id sites: at
      scenario start, on an ack mismatch, and when a save is loaded into a checked set that grew
      after it was saved. A settled pass flips nothing and so rewrites nothing
- [ ] The item at a location is never named
- [ ] The xs lints from the xs folder against the entry point; the game half carries no tests in
      this repo
