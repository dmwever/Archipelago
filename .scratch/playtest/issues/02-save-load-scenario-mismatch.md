# 02: Switching scenarios by save/load reports a scenario mismatch

**Reported:** 2026-10-19, playtesting

**Status:** done

## Report

Switching from one scenario to another by loading a save gives a scenario mismatch error.

## Resolution

Fixed and verified in game 2026-10-20 by slice 01 of the delivery-cursor change. Spec:
`worlds/age2de/docs/spec-item-delivery-cursor.md`; fixed by slice 01. Three parts, all in that ticket's spec:

- `AP_Read` validates identity (world version, slot id, seed halves) *before* the scenario id,
  so a wrong-seed install is reported as one instead of being masked by a mid-switch scenario
  mismatch. Those checks keep routing through `ReportMismatch` and keep disabling `ReadAP`.
- The scenario id comparison drops to a quiet "not addressed to me" return with a single
  one-shot yellow line, instead of the red pair on every read.
- The client re-scans the unlocked scenario files for a fresher ping on every pass while the
  packet is a repeat, rather than waiting out the 10-repeat (~5 s) threshold.

The "needs from reporter" questions below are no longer blocking; the audit identified the
message and the path.

## Original report detail

- The exact text, and whether it shows in game chat (red) or in the client log
- Whether it clears on its own after a few seconds or keeps repeating
- Whether the two scenarios are in the same campaign

## Audit (not verified in game)

The likely message is the game-side one in `AP.xs:93-97`:
`Wrong Scenario ID from Client: <old>` / `Expected Scenario Id: <new>`.

Probable sequence:

1. The client is attached to scenario A and keeps writing A's id as the first int of `AP.xsdat`
   (`client/GameClient.py:420`, `ping_game`).
2. The loaded save is scenario B. Its `AP_Read` sees A's id and prints the red pair on every read,
   then returns before taking the ping, so B gets no items or messages.
3. The client only notices the switch through A's own packet file. The check at
   `GameClient.py:500` compares the packet's `scenario_id` with the active scenario, but it reads
   A's file, which always holds A's id, so it never fires for a switch to a different file.
   Recovery depends on the stale-packet path instead: 10 repeats (~5 s,
   `GameClient.py:509-512`) → deactivate → `paused`, then `find_active_campaign` every 5th repeat
   (`GameClient.py:477-483`).

So at best there are ~5 s of red errors on every switch. If that recovery path doesn't pick B up
(e.g. A's packet file is still being found as active), it persists.

Neither side treats "client is on another scenario" as an expected state: the game-side message
reads like an install error, and it is printed on every read, not once.
