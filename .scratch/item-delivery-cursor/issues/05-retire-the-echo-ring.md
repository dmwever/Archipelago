# 05: Retire the echo ring

**What to build:** `windowBase` makes the twelve-slot echo redundant, so delete it. This is pure
deletion with no behaviour change — if anything differs in game after this ticket, the deletion was
wrong, which is why it is reviewed apart from 03.

The twelve item ints stay in the game → client packet, written as `-1`. `ScenarioId` has to stay at
byte offset 72 for `find_active_campaign`'s hardcoded `skip_int(fp, 18)`.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md` (Window base).

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] `itemArray` and the `FreeItems` rule are gone from `AP.xs`, along with the `Free Items` read
      in `AP_Read`
- [ ] `AP_Write` writes twelve `-1`s, and `test_mercenary_packet` still pins byte 72
- [ ] `ack_items`, `free_items`, `in_flight` and the `Free Items` write in `ping_game` are gone
- [ ] `free_items.xsdat` is no longer written and is dropped from `flush_files`
- [ ] `Age2Packet` skips the twelve ints rather than parsing them
- [ ] `InitAP` no longer needs its "session state was lost" path for this array
- [ ] `docs/communication_protocol.md` loses the `free_items.xsdat` row and the flag; the window
      section is rewritten around `windowBase`
- [ ] In game: a full scenario start to finish behaves exactly as it did after 03
