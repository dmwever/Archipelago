# 03: One spent record, as a bitmask over stream indices

**What to build:** Spent mercenaries and spent items are one idea -- a record of what must not be
paid out twice -- stored two different ways, merged two different ways, behind two different server
keys and two reply paths. Collapse them into one record. The split belongs in the game context once
`ItemHandler` and `MercenaryHandler` exist (ticket 06), not in storage.

A mercenary is spent by marking the stream index it arrived at, exactly as a trap or a filler
resource already is. That retires `DataStorage.mercenary_bit` and `mercenary_field`, and moves
mercenary identity from item ids to stream position.

**One bitmask, no separate high-water.** A mark only ever gates one-shot entries, so an exact set of
spent indices makes the same decision a high-water would, and nothing reads a persisted cursor:
`acked_items` is in-memory today and becomes the game's `appliedItemCount` in ticket 04. Bit `i` set
means "stream index `i` has been paid out and must not be sent again".

Bitwise, not a list, so one data-storage field carries the whole record. Archipelago encodes with
the stdlib `JSONEncoder`, and a 1500-bit int round-trips exactly -- verified. A JS reader would lose
precision, but nothing outside this client reads the key, and `scenario_complete` and
`mercenaries_used` are already bitfields on the same footing.

**Merge policy: `replace`, local authoritative, with a null record meaning "no local copy".** That is
the mercenary rule generalised, and it is what keeps `/install`'s clear local-only: a cleared record
is null, so it pushes nothing, and a server that still holds real spends hands them straight back.
The client restores server storage that has been reset; it never destroys storage that has not.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md` (Persistence).

**Blocked by:** None (reshapes 02's persistence before 04 builds on it)

**Status:** done

- [x] One server key, `{team}_{slot}_spent`, replacing `mercenaries_used` and `items_spent`
- [x] One local field, a bitmask, in `state_<tag>_<player>.json`; null still means "no local record"
- [x] `reconcile_spent` generalises from a set of ids to a bitmask, keeping all four of its cases
- [x] One `storage_ready` gate and one reply path, not two
- [x] A mercenary is spent at the stream index it arrived at; `is_used` resolves through
      `unlocked_items`
- [x] `DataStorage.mercenary_bit` and `mercenary_field` are gone
- [x] `id_for_game` tests the bit instead of comparing against a high-water
- [x] Delivery sets bits only for one-shot entries; replayable flag items never set one
- [x] `/install`'s clear still touches nothing on the server
- [x] Mercenary seats are not synced from a mask before `ReceivedItems` has landed, or the mask is
      read against an empty stream
- [x] In game: spend a mercenary, reconnect, confirm it is still spent and still out of the pavilion
- [x] In game: receive a trap, reconnect, confirm it does not re-fire

## Amendment

After this ticket was written, `reconcile_spent` gained one line:

    spent &= (1 << len(self.client_status.unlocked_items)) - 1

Bits past the received stream describe a playthrough that no longer exists, because the
server was reset or rolled back. The stream is append-only, so whatever is still in range
really was spent and is kept; a full reset empties the stream and the record falls to zero on
its own.

This restores the ground `MercenaryHandler._forget_unreceived` used to cover and that this
ticket removed on the mistaken argument that stream indexing made it unnecessary. Indexing
makes a stale bit inert *at that moment*, not once the stream refills and the bit names a
real entry again. The replacement is decisive rather than progressive, repairs the record
rather than only the pavilion queue, and covers traps and filler, which were never covered.

`ApClient` gates reconciliation on the full `ReceivedItems` having landed, because an empty
stream and a stream that has not arrived yet are the same observation and the record is
truncated against it.

A rollback that lands on exactly the same stream length has no signal. Accepted.
