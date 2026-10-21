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

**Status:** done (mechanism superseded by 03; verified there)

- [x] `StorageHandler` writes one `APData/state_<tag>_<player>.json` holding both the spent
      mercenary records and the mark
- [~] Superseded by 03: there is no legacy handling at all. An old file is simply not read,
      and an unreadable record defers to the server, which needs no migration code
- [~] Superseded by 03: one key `{team}_{slot}_spent`, merged with `replace` rather than
      `max`, since the local record is authoritative for what is spent
- [~] Superseded by 03: there is no high-water mark. The record is a bitmask over stream
      indices, and delivery sets a bit per one-shot entry the cursor has passed
- [x] `send_items` writes nothing at all until the mark's reply has landed
- [x] Filler `Resources` and `Trap` entries that are spent go out as `SKIP_ITEM_ID`; flag
      items do not (`ITEM_SKIP` was renamed; the behaviour is unchanged)
- [x] Tests: sentinel substitution, the `storage_ready` gate, the new file shape, the old file's
      removal
- [x] `mercenaries: null` keeps "no local record" distinguishable from "nothing is spent",
      now that the file exists for the mark's sake
- [x] Verified under 03, which carries the same check: receive a trap, reconnect, no re-fire

## Outcome

Closed as superseded. What survives from this ticket is the gate (`send_items` writes nothing
until the stored record has come back), the skip sentinel, and the rule that spent state has to
outlive a disconnect. How it is stored and merged was rewritten by
`03-one-spent-record.md`, which carries the in-game verification for both.
