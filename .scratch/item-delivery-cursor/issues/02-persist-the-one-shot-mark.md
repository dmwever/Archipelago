# 02: Persist the one-shot delivery mark

**What to build:** `ClientStatus.acked_items` is wiped by `Age2GameContext.disconnect`, so a
reconnect restreams from index 0 and every trap fires again. Persist a monotone high-water mark of
how far one-shot delivery has got, and send `AP_ITEM_SKIP` in place of any filler resource or trap
below it. Client-only: `-2` already falls through every band in the existing `GiveItem`, and the
current ack and free paths treat it like any other id, so this lands against an unmodified install.

Must come before ticket 03. Once the cursor can rewind, anything additive replays, and this is what
stops it.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md` (Persistence, Skipping without breaking the index). Fixes
`.scratch/playtest/issues/08-traps-resent-on-server-reconnect.md`.

**Blocked by:** None (independent of 01)

**Status:** ready-for-agent

- [ ] `StorageHandler` writes one `APData/state_<tag>_<player>.json` holding both the spent
      mercenary records and the mark
- [ ] Any `APData/mercenaries_<tag>_<player>.json` found is deleted, not migrated; spent mercenaries
      come back from the server through `reconcile_spent(None, server)`
- [ ] `{team}_{slot}_items_spent` is set with `{"operation": "max"}`, `set_notify`'d, and read
      back in `_handle_set_reply`
- [ ] The mark advances to `max(spent, acked_items)` on every pass that moves the cursor
- [ ] `send_items` writes nothing at all until the mark's reply has landed
- [ ] Filler `Resources` and `Trap` entries below the mark go out as `ITEM_SKIP`; flag items do not
- [ ] Tests: sentinel substitution, the `storage_ready` gate, the new file shape, the old file's
      removal
- [ ] In game: receive a trap, disconnect and reconnect mid-scenario — no trap re-fires
