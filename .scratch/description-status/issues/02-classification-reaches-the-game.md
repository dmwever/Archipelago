# 02: Classification reaches the game

**What to build:** At connect the client asks the server what sits at each of its own locations,
without creating hints, and hands the reply to `LocationHandler`'s classification channel (09),
which writes a flat file of ints into the profile folder beside the building, technology and unit
files. Each entry says
which of the three colour classes the item at that location wears: progression, useful or filler.
A trap wears one of those same three, derived from the seed and the location id, so the same trap
reads the same way on every reconnect, reload and session and cannot be told from a genuine item of
that class. The reply is also the record of which locations this seed has at all, so a location the
server does not report is absent from the file rather than written with a default. Nothing in the
game reads the file yet.

**Blocked by:** 09 (the handler this channel is written on).

**Status:** ready-for-agent

- [ ] Connecting requests a scout of the world's own locations with hint creation suppressed
- [ ] The handler writes one entry per scouted location and is tested the way the unit handler is:
      construct it, point it at a temporary folder, hand it scouted locations, read the file back
      as little-endian ints
- [ ] A location of each classification, a trap, an empty reply, and locations the handler should
      ignore are all covered
- [ ] The same seed and location id yield the same trap class across repeated calls and across
      fresh handler instances; no random source is reached for anywhere
- [ ] The handler is handed its folder the way the other startup handlers are, and its file is
      cleared alongside theirs when the client flushes or disconnects
- [ ] The classification channel is written once at connect and never from the per-tick path. It
      shares `LocationHandler` with the checked-locations writer but not its cadence or its file;
      see the amended ruling in 09
- [ ] The pre-commit subset for the files touched passes
