# 14: Castle Age missing in Joan 2

**Reported:** 2026-10-20, playtesting

**Status:** needs-info

## Report

Castle Age is missing from Joan 2.

## Needs from reporter

- In game (the Town Center has no Castle Age button), or in logic (something is in logic without
  Castle Age)? This write-up assumes in game.
- Was the Castle Age item received before starting Joan 2, while another scenario was running or
  with no scenario open?

## Audit (from code, not verified in game)

Joan 2 opens in Feudal with a Castle cap (`AP_Joan_2.xs`: `SetVanillaAge(FEUDAL_AGE)`,
`SetMaxAge(CASTLE_AGE)`; the apworld agrees in `locations/Scenarios.py:61`), so Castle Age is
allowed there.

Under `shuffle_ages`, a fresh scenario start locks every age (`InitAges` → `lockAge`). Castle comes
back only through `UnlockAge`, which runs from `GiveItem` for ids 25–29. Age items have **no bulk
file**. `ConnectAP` re-reads buildings (`buildings.xsdat`), techs, units, `startup.xsdat`
(starting/TC resources only, `GameClient.sync_starting_resources`) and the scenario's own file. None
of them carries age items. The only way an age item reaches a scenario is the shared item window.

The window cursor (`acked_items`) is global (see 06). If Castle Age was received and acked while an
earlier scenario was running, the window has moved past it and never sends it again. Joan 2 then
starts with Castle locked and nothing that unlocks it.

So this should hit **every** scenario started after the age items were consumed elsewhere. It isn't
Joan 2 specific; Joan 2 is just the first scenario with a Castle cap the player tried after
receiving it.

## Relation to other issues

Same root cause as **06**, and its agreed design already names ages as the band with no bulk file.
Under that design the game owns the cursor, and a fresh start replays the stream from 0, which
re-delivers age items. Fixing 06 should fix this; worth re-testing Joan 2 afterwards.
