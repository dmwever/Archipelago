# 08: The spent record has one owner, marked and written in one pass

**What to build:** The spent record lives in two copies today, `ClientStatus.spent_mask` and
`StorageHandler._spent`. Mark, reconcile and clear each have to keep both in step, and the two copies
already drift when a save fails. Make `StorageHandler` the single in-memory owner of the record. It
holds the mask and `record_known`, marks bits, flushes to disk, and hands back the mask to push to
the server.

**A failed save doesn't stop delivery.** Today a failed flush makes `mark_items_spent` return
False. The delivered one-shots then stay unmarked, and because `try_sync_items` holds the window back
while any are unmarked, all delivery stalls, progression items included. With one in-memory owner,
a mark always lands in memory. A failed flush is logged once, naming the path, and retried on the
next tick. The server push still persists the spend.

**One pass, no one-tick wait.** `try_sync_items` currently reports delivered one-shots and holds the
window back until the caller marks them on a later tick. That wait has no stated reason. It replaced
in-handler marking in commit `fab4cf4c9`, and its only real effect was the stall above. Delivered
indices sit below the cursor and the window starts at the cursor, so marking can never change an id
in the window being written. In one sync, `ItemHandler` reads `appliedItemCount`, marks the delivered
one-shots in the record, and writes the window from the updated record.

**Remove dead code.** `set_current_item_index`, `current_item_index`, `reset_delivery` and
`GameClient.update_current_item_index` look like guards on delivery state, but the packet-driven
sync overwrites that state every tick. Delete them and their call sites.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md` (Persistence).

**Blocked by:** 07 (it also edits `ItemHandler`; it lands first and this builds on it)

**Status:** done

- [x] `ClientStatus.spent_mask` is gone; every read and write of the spent record goes through
      `StorageHandler`
- [x] `record_known` lives with the record
- [x] A mark always updates the in-memory record, even when the flush to disk fails
- [x] A failed flush warns once with the path, is retried on the next tick, and clears the warning
      once it succeeds
- [x] One sync marks the delivered one-shots and writes the window; nothing is held back a tick
- [x] `set_current_item_index`, `current_item_index`, `reset_delivery` and
      `update_current_item_index` are deleted
- [x] Tests: an unwritable APData folder still delivers every window; mark and write in the same sync
- [ ] Existing client tests stay green (all but `test_the_window_carries_the_cursor_it_was_written_for`, which still reads `Items.ITEM_WINDOW` after commit 60943c29b removed it)
