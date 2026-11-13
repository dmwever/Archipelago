# 01: The checked set is read when a scenario starts

**What to build:** A scenario entered after checking nothing new still knows everything the player
has already checked. Today the game ingests the checked-locations file only when the ping says the
game has just sent locations, so a scenario entered cold reports every location unchecked until the
first new check lands, and a technology checked hours ago in an earlier scenario looks untouched.
The game context arms that read once per connect, so the first ping after connecting asks for it
even though the game has sent nothing. A reconnect arms it again. Nothing is decorated yet; this is
the correctness fix the rest of the feature stands on, and it is observable on its own.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] Connecting arms the read once, and the first ping written afterwards asks the game to read
      the checked-locations file although no location ids came from the game
- [x] Later pings in the same session go back to asking only when the game has just sent locations
- [x] Reconnecting arms it again
- [x] A location checked in an earlier scenario reads as checked on entering the next one, with no
      new check in between
- [x] Covered by constructing the context directly, in the style of the existing game-loop and
      ping-packet tests
- [x] The pre-commit subset for the files touched passes

## Rulings

- 2026-11-11: The game acks the read. `CheckedLocationsCount` comes out of the reserved block and reports
  how many ids the last read of `locations.xsdat` took in. The client holds the flag set while that
  disagrees with the set it is writing.
- 2026-11-11: No `world_version` bump for this change. The bump belongs to a genuine release.

## Comments

- 2026-11-11: Built connect-only arming first, exactly as the spec ruled it, and it passed its own
  acceptance tests. Reading `AP.xs` afterwards showed the ruling could not reach the fourth
  acceptance box:
  - `MarkServerLocations` ends in `xsDisableSelf` and every scenario starts a fresh XS context, so
    the read has to be asked for once per **scenario**. Entering the next scenario without
    reconnecting left it unasked.
  - `ConnectAP` does not enable `ReadAP` until it has approved the first ping, so the flag in that
    ping went into a file nothing was reading yet. Spending the arm on the first ping written was a
    race the game usually lost.
  Maintainer chose the packet ack (option D) over a grace window or a follow-up ticket.
- 2026-11-11: Both failure modes have their own test. Neutralising `confirm_checked_set` fails
  `TestTheClientWaitsForTheGameToListen` and `TestANewScenarioAsksAgain` and nothing else.
