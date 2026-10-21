# 04: Move the delivery cursor into the game

**What to build:** The cursor lives in client memory, so it survives neither a save nor a reconnect.
Move it into XS state as `appliedItemCount` — a plain `int` global, confirmed in game to survive a
save — ship it in the packet, and have `send_items` take its window base from the packet instead of
from `ClientStatus.acked_items`. Address the window with a leading `windowBase` int so the game
applies it only when the base matches, all of it or none, and a reread is a no-op.

Write `windowBase` negative-encoded (`-(base + 1)`): every negative value falls through the old
`GiveItem` band dispatch, so a stale 0.3.0 install that missed the `/install` does nothing rather
than reading the base as a resource item id.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md` (The mechanism, Window base). Fixes
`.scratch/playtest/issues/06-reload-misses-scenario-items.md`.

**Blocked by:** 03

**Status:** ready-for-agent

- [x] `AP_ITEM_SKIP` and `AP_ITEM_WINDOW = 64` live in `AP_Constants.xs`, with `GiveItem` returning
      early on the sentinel
- [x] `appliedItemCount` is written after `ConsumedQueueSerial()`; the reserved loop drops 27 → 26
- [x] `ReadItems` decodes `windowBase`, returns unless it equals `appliedItemCount`, applies every
      entry, then advances by the count it read
- [x] `Age2Packet` reads `applied_item_count` and skips 26; `acked_items` is derived from it
- [x] `test_mercenary_packet` still pins `FIXED_INTS = 49` and `scenario_id` at byte 72, and pins
      the new field
- [x] Tests: a rewound cursor replays the gap; a mismatched `windowBase` applies nothing
- [ ] In game: save in Genghis 1, play Attila 1, receive Kereyid Tribe, reload Genghis 1 — the
      blue-tribe check is live, and reloading again doubles nothing
