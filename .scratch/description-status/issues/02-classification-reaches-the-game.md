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

**Status:** done

- [x] Connecting requests a scout of the world's own locations with hint creation suppressed.
      `Age2GameContext.connect` asks `client_interface.scout_locations()`, the way it already asks
      `fetch_spent()`; `Age2Context.scout_locations` sends `LocationScouts` for `server_locations`
      with `create_as_hint` 0, and the `LocationInfo` reply goes straight to the channel
- [x] The handler writes one entry per scouted location and is tested the way the unit handler is:
      construct it, point it at a temporary folder, hand it scouted locations, read the file back
      as little-endian ints. `classification.xsdat` holds the id then its class, ordered by id,
      with `PROGRESSION`, `USEFUL` and `FILLER` as 1, 2 and 3
- [x] A location of each classification, a trap, an empty reply, and locations the handler should
      ignore are all covered. An item carrying progression and useful at once reads as progression,
      and a location id this apworld cannot name is left out rather than written
- [x] The same seed and location id yield the same trap class across repeated calls and across
      fresh handler instances; no random source is reached for anywhere. The disguise is sha256 over
      the seed tag and the location id, and the test pins three literals so a process-salted hash
      cannot creep in
- [x] The handler is handed its folder the way the other startup handlers are, and takes the seed
      tag in the same place. Its file is cleared on disconnect and left alone by a mid-session
      flush; see the ruling below
- [x] The classification channel is written once at connect and never from the per-tick path. It
      shares `LocationHandler` with the checked-locations writer but not its cadence or its file;
      see the amended ruling in 09
- [x] The pre-commit subset for the files touched passes, plus the test files the change touches:
      173 passed

## Comments

- 2026-11-12: Raised while building 09. `Age2GameContext.flush_files` is not disconnect-only:
  `status_tick` calls it when it starts following a live scenario and again when the game switches
  scenario. `locations.xsdat` survives that only because the top of the next tick rewrites it. A
  classification file written once at connect has nothing to rewrite it, so clearing it on every
  flush would strip the colour off every unchecked status line from the first scenario switch until
  the player reconnects -- the later-scenario case stories 4 and 28 are about. Either the flush
  leaves the file alone, since it carries no per-scenario state, or the handler keeps the scout
  reply and rewrites the file after each flush. 09 clears only `locations.xsdat` and names no
  classification file, so the choice is open.

- 2026-11-12: Ruled, and built. A mid-session flush leaves `classification.xsdat` alone and the
  disconnect clears it, through `try_clear_classification` called from `Age2GameContext.disconnect`
  rather than from `flush_files`. The file carries no per-scenario state, so the scenario switch has
  nothing to rewrite and nothing to lose; clearing on disconnect is what keeps one seed's colours
  out of the next one's profile folder. 09's sixth acceptance line is ticked to match, and the
  spec's classification paragraph now carries the file layout and this cadence.
- 2026-11-12: `/set_user_folder` re-syncs the channel. A player who connects before pointing the
  client at their Age2 folder would otherwise have no colours for the whole session: every other
  startup file is rewritten by the next tick, and a scout-once file is not. `Age2Context`'s
  `sync_classification` is called from both the `LocationInfo` reply and the command, and does
  nothing until the reply has landed.
- 2026-11-12: Review findings. Two taken, one rejected. `/set_user_folder` now clears the old
  profile folder before the handler is repointed, so a seed's class map is not left behind in an
  install the player has walked away from; the ruling clears on disconnect, and that path would
  otherwise never be cleared at all. The "absent rather than defaulted" test was a copy of the one
  above it and now names a location the reply left out. The rejected one wanted the write staged
  through a temp file and `os.replace`d, against a torn write this file cannot recover from the way
  the per-tick files do: no other handler in the client does that, and it puts a foreign name in
  the profile folder for a failure none of the sibling writers guard against either.
