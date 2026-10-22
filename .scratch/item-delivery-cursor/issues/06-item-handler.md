# 06: Move item delivery into its own handler

**What to build:** `Age2GameContext` owns the packet and the status loop, but the item stream — one
coherent job — is spread across it as half a dozen methods and four `ClientStatus` fields. Move it
into an `ItemHandler`, named to mirror `ItemHandler.xs` the way `BuildingHandler` mirrors
`buildings.xsdat`.

No behaviour change. This ticket is only sound if nothing differs in game and the suite stays green.

Deliberately after 05: that ticket deletes `ack_items`, `free_items` and `in_flight` outright, and
moving code two slices before deleting it is wasted motion. Deliberately before 07, so the
`startupBaseline` skip decision is written in its final home rather than moved afterwards.

Starting resources stay out. `startup.xsdat` is the starting pile, applied once per scenario start,
not part of the item stream, so writing and removing it stays on `Age2GameContext`. `ItemHandler`
only learns the baseline (07) so it can skip stream entries the pile already paid.

Mercenaries stay separate. `MercenaryHandler` owns a model — a queue, four seats, and the status
`/mercenaries` renders. `ItemHandler` owns a cursor: a position, a window and a high-water mark,
with nothing user-facing. One class answering both questions would be one class with two jobs. What
they genuinely share is persistence, and `StorageHandler` already is that.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md`.

**Blocked by:** 05

**Status:** ready-for-agent

- [x] `ItemHandler(FolderHandler)` owns `items.xsdat`, with its own `try_flush_from_folder`, and
      `flush_files` defers to it. `startup.xsdat` stays with `Age2GameContext`
- [x] `send_items`, `wire_id`, `note_delivered` and `adopt_items_spent` move off
      `Age2GameContext`; `sync_starting_resources` deliberately stays
- [x] `acked_items`, `items_spent` and `storage_ready` move off `ClientStatus` into the handler
- [x] `unlocked_items` stays on `ClientStatus` — six handlers read it — and `ItemHandler` takes it
      as a parameter, matching the existing `try_sync_*(unlocked_items)` shape
- [x] `StorageHandler` is untouched: it stays the persistence layer for both the mark and spent
      mercenaries
- [x] `_handle_received_items`'s cursor clamp goes through the handler rather than reaching into
      `ClientStatus`
- [x] `Age2GameContext` is left owning the packet and the loop, and nothing else about items
- [x] Every existing test passes, changed only where it names a moved method
- [ ] In game: a full scenario start to finish behaves exactly as it did after 04

## Amendment

Names had drifted since this was written: `wire_id` is `id_for_game`, `note_delivered` is
`mark_delivered_spent`, `adopt_items_spent` is `reconcile_spent`, `items_spent` is
`spent_mask`.

Correction (triage, 2026-10-22): not all of them moved. `reconcile_spent` is still on
`Age2GameContext`, and `spent_mask` / `record_known` are still on `ClientStatus`. Giving the spent
record a single owner is ticket 08. `sync_starting_resources` and the `startup.xsdat` removal in
`flush_files` stayed on `Age2GameContext` on purpose (see above and 07).

Three things landed slightly differently from the plan:

- The per-pass work is one call, `ItemHandler.sync(unlocked_items, applied)`, replacing three
  separate calls in `status_loop`. That is the shape the other handlers already have.
- `clear_spent_state` stayed on `Age2GameContext`. It spans two handlers -- it clears the
  record and resets the mercenary seats -- so it is coordination, not item delivery.
- `in_flight` moved with the rest and became `ItemHandler.in_flight()`, a bool for the one
  thing outside the handler that needs it: arming the game's `ReadItems`.
