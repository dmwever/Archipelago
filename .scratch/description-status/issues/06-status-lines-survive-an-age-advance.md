# 06: Status lines survive an age advance

**What to build:** The engine clears every written description when an age advances, so without
this the whole feature quietly stops working the moment the player reaches Feudal. The age module
triggers one full re-apply after the advance, covering technologies, units, buildings and the age
advances themselves. Saving and reloading does not clear descriptions, so resume needs no hook of
its own.

**Blocked by:** 04, 05 (so the re-apply covers every kind of line that exists).

**Status:** ready-for-agent

- [ ] After advancing an age, every status line that was there before is there again
- [ ] The re-apply runs once per advance, not on a timer, and adds no per-tick work
- [ ] Saving and reloading leaves the lines in place with no further work
- [ ] The xs lints from the xs folder against the entry point
