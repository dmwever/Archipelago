# 10: `/install` returns the record to unknown and fetches it again

**What to build:** `/install`'s clear zeroes the spent mask but leaves `record_known` True. On the
next tick, every one-shot below the game's `appliedItemCount` looks delivered and unspent, gets
marked again, and is pushed. Spends above the cursor and spent mercenaries are lost from the local
record, and ticket 03's promise that "a server that still holds real spends hands them straight
back" never happens.

The clear should:
1. clear the local file, as it does now;
2. set `record_known` to False, so delivery and mercenary syncing pause;
3. ask the server for the spent key again.

The client has no `Get` path, and `set_notify` doesn't re-fetch a key it is already watching. So step
3 re-sends the spent key's `Set` with a `default` operation and `want_reply`, the same request
connect already uses. The `SetReply` runs reconcile, which restores the server's spends before any
window is written.

`/install` stays allowed while a scenario is attached. Delivery simply waits for the reply.

**Blocked by:** 08, 09

**Status:** ready-for-human

- [x] The clear sets `record_known` to False and requests the spent key with `default` and
      `want_reply`
- [x] No window is written and no mercenary is synced between the clear and the reply
- [x] The reply reconciles, and the server's bits come back
- [x] The clear still pushes nothing to the server
- [x] Tests: a clear followed by a reply restores the server mask; a tick between the two writes
      nothing
- [ ] In game: spend a mercenary, run `/install` with the scenario attached, and confirm the
      mercenary stays out of the pavilion and spent traps don't re-fire
