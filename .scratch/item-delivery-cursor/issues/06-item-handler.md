# 06: Move item delivery into its own handler

**What to build:** `Age2GameContext` owns the packet and the status loop, but the item stream — one
coherent job — is spread across it as half a dozen methods and four `ClientStatus` fields. Move it
into an `ItemHandler`, named to mirror `ItemHandler.xs` the way `BuildingHandler` mirrors
`buildings.xsdat`.

No behaviour change. This ticket is only sound if nothing differs in game and the suite stays green.

Deliberately after 05: that ticket deletes `ack_items`, `free_items` and `in_flight` outright, and
moving code two slices before deleting it is wasted motion. Deliberately before 07, so the
`startupBaseline` work is written in its final home rather than moved afterwards.

Mercenaries stay separate. `MercenaryHandler` owns a model — a queue, four seats, and the status
`/mercenaries` renders. `ItemHandler` owns a cursor: a position, a window and a high-water mark,
with nothing user-facing. One class answering both questions would be one class with two jobs. What
they genuinely share is persistence, and `StorageHandler` already is that.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md`.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] `ItemHandler(FolderHandler)` owns `items.xsdat` and `startup.xsdat`, with its own
      `try_flush_from_folder`, and `flush_files` defers to it
- [ ] `send_items`, `wire_id`, `note_delivered`, `adopt_items_spent` and `sync_starting_resources`
      move off `Age2GameContext`
- [ ] `acked_items`, `items_spent` and `storage_ready` move off `ClientStatus` into the handler
- [ ] `unlocked_items` stays on `ClientStatus` — six handlers read it — and `ItemHandler` takes it
      as a parameter, matching the existing `try_sync_*(unlocked_items)` shape
- [ ] `StorageHandler` is untouched: it stays the persistence layer for both the mark and spent
      mercenaries
- [ ] `_handle_received_items`'s cursor clamp goes through the handler rather than reaching into
      `ClientStatus`
- [ ] `Age2GameContext` is left owning the packet and the loop, and nothing else about items
- [ ] Every existing test passes, changed only where it names a moved method
- [ ] In game: a full scenario start to finish behaves exactly as it did after 04
