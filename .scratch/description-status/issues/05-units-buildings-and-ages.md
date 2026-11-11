# 05: Units, buildings and ages carry a status line

**What to build:** A unit, a building and an age advance each carry the first segment of the status
line and nothing else: the checked or unchecked mark, Checked in green or Unchecked in the colour of
the class of item waiting there. They have no effect state worth reporting — an age's is something
the resource bar already shouts, and a unit's or a building's is just whether it is trainable or
buildable. A building this seed did not shuffle carries no line even though the game registers all
thirty-five buildings in every seed; the scout reply is what reconciles the two. Gaia objects are
left alone: they reject the description write and report no name id.

**Blocked by:** 04 (the writer and the status-line shape).

**Status:** ready-for-agent

- [ ] A unit location, a building location and an age advance each carry a first segment, coloured
      by classification while unchecked and green once checked
- [ ] None of the three carries a second segment
- [ ] With Buildsanity partially enabled, a building outside the shuffled categories carries no line
- [ ] Gaia objects are never written to
- [ ] Lines are written in the init pass and rewritten per object from the sites that know which id
      changed, the bulk `serverComplete` pass in 04 included
- [ ] Vanilla description text is intact beneath each line
- [ ] The xs lints from the xs folder against the entry point
