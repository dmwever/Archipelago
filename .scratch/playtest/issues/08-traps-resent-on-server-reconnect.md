# 08: Traps fire again after reconnecting to the server

**Reported:** 2026-10-20, playtesting

**Status:** ready-for-agent

## Report

After the client reconnects to the Archipelago server, traps that were already received fire again
in game.

## Resolution

Same root cause as playtest 06: the delivery cursor lives in `ClientStatus.acked_items`, in client
memory, so it survives neither a reconnect nor a save load. The agreed fix moves the cursor
into XS state (`AppliedItemCount` in the packet) and adds a persisted one-shot high-water mark
(`{team}_{slot}_items_spent`, AP data storage, `max` operation) so a replayed stream sends a
skip sentinel instead of a trap. Design and task list live in
`worlds/age2de/docs/spec-item-delivery-cursor.md`; fix both together.

## Original audit

Traps have no path of their own. They go through the shared item window like every other item
(`GameClient.send_items` → `items.xsdat` → `ReadItems` → `GiveItem` → `GiveTrap`,
`TrapItems.xs:300`). Each `TRAP_*` function acts immediately, so a resent trap is a second trap.

The client tracks what the game has already been given with one in-memory counter,
`ClientStatus.acked_items` (`client/GameClient.py:140`):

1. **Disconnect wipes it.** `Age2GameContext.disconnect` (`GameClient.py:194-219`) replaces
   `client_status` with a fresh `ClientStatus`, so `acked_items` goes back to 0.
2. **Reconnect resends everything.** On connect the server sends `ReceivedItems` from index 0, and
   `_handle_received_items` (`client/ApClient.py:234-248`) rebuilds `unlocked_items` from scratch.
   The `acked_items > len(...)` clamp can only lower the counter, never restore it.
3. `send_items` then streams `unlocked_items[0:]` through the window again, 12 at a time, and the
   running scenario re-applies all of it.

The counter isn't persisted anywhere (no data storage key, no file), so restarting the client does
the same thing.

Most items are flags or unlocks, so getting them twice does no harm. Traps (5000–5008) are the
visible case. Anything else whose `GiveItem` branch adds rather than sets would also double up and
is worth checking.

## Likely shape of a fix

Persist the delivered-item index: in AP data storage, keyed per team and slot like
`scenario_completion_key`, or in the per-seed folder. Restore it on connect, then let
`_handle_received_items` keep the restored value. Alternatively, have the game report how many items
it has applied, and skip window entries below that.
