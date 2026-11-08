# 81: the threat owner arrays are indexed by player number instead of player - 1

**Reported:** 2026-11-06, found while staging [#78](78-in-game-checks-round-2.md)'s #60 checks

**Status:** done

**Related:** [#60](60-genghis3-jin-wonder-no-threat.md), [#78](78-in-game-checks-round-2.md)

## Report

`InitVictoryThreats` sized its owner arrays with `xsGetNumPlayers()` but indexed them by player
number. **`xsGetNumPlayers()` excludes Gaia** — engine-verified: `XsTesting` has
`player_count=2` with P1 and P2 active, and `EnableWonderThreat(2)` hit the
`owner >= xsArrayGetSize(...)` guard. So the array addressed 0 to N-1 while player numbers run
1 to N, and the highest-numbered player could never be armed as a threat owner.

The shipped scenarios were unaffected: Genghis 3 arms player 4 of 6, Attila 6 arms players 2-5
of 6. It only bit the harness, which used player 2 of 2.

## Fixed (2026-11-06)

The arrays hold one slot per real player and Gaia is never a threat owner, so **player N belongs
at index N - 1**. `EnableWonderThreat` guards `owner < 1 || owner > size` and writes
`owner - 1`; `RetireWonderOwner` matches; `WonderThreatWatch` and `IsAlliedWithHolders` walk the
index and derive `owner = index + 1`; `FindRelicHolder` writes `relicHolders[monasteryOwner - 1]`.

The relic **scans** in `FindRelicHolder` and `RevealRelicMonasteries` walk players 1 to N the
same way. Gaia is not player 0 - it is handled separately and is not a slot these functions can
scan - so the original `for (player = 0; < xsGetNumPlayers())` spent one iteration on nothing and
missed the last real player.

An earlier attempt sized the arrays `xsGetNumPlayers() + 1` instead. That also works but wastes
a slot on Gaia and keeps the mis-indexing; the maintainer called it, and this is the intended
model.

`xs-check` clean on all 19 entry points. Not yet re-tested in game.

Not re-tested in game. The harness check that found it is #78's #60 row, which is layer-3 work.
