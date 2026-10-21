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

**Status:** ready-for-agent (storage shape superseded by 03)

- [x] `StorageHandler` writes one `APData/state_<tag>_<player>.json` holding both the spent
      mercenary records and the mark
- [~] Superseded by 03: there is no legacy handling at all. An old file is simply not read,
      and an unreadable record defers to the server, which needs no migration code
- [x] `{team}_{slot}_items_spent` is set with `{"operation": "max"}`, `set_notify`'d, and read
      back in `_handle_set_reply`
- [x] The mark advances to `max(spent, acked_items)` on every pass that moves the cursor
- [x] `send_items` writes nothing at all until the mark's reply has landed
- [x] Filler `Resources` and `Trap` entries below the mark go out as `ITEM_SKIP`; flag items do not
- [x] Tests: sentinel substitution, the `storage_ready` gate, the new file shape, the old file's
      removal
- [x] `mercenaries: null` keeps "no local record" distinguishable from "nothing is spent",
      now that the file exists for the mark's sake
- [ ] In game: receive a trap, disconnect and reconnect mid-scenario — no trap re-fires
