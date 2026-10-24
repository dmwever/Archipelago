# 09: The spent record is the union of local and server, cut to the stream length

**What to build:** Ticket 03 merged the spent record by `replace`, with the local file
authoritative. Every serious review finding came down to the same failure under that policy: a local
mask missing bits overwrote a server mask that had them.
- A stale file on a second machine wiped the first machine's spends.
- `/install` was followed by a `replace` from an empty mask.
- A mercenary was marked before the server's record had arrived.

Replace the policy with this rule: **the server's item stream says what exists, and the union of
every copy says what's been used, limited to what exists.**

- **Received:** the server's `ReceivedItems` stream decides which indices exist. Bits past its end
  are cut away, as in ticket 03's amendment.
- **Used:** no single copy is authoritative. The local file, the server record and every other
  machine that has pushed are all witnesses. If any of them says an index was spent, it was spent.
  A witness can add bits but never remove them.

Reconcile computes `(local | server)` and cuts it to the stream length. A null local record still
means "no local copy" and contributes nothing. Normal pushes use the server's `or` operation, so the
server does the union. A `replace` is sent only when the cut actually cleared bits, after a server
reset or rollback that left a shorter stream.

The only thing that un-spends an item is the stream getting shorter. There is no player-facing reset
command.

**Two clients on one slot converge.** Under `replace`, two clients with different records push back
and forth forever. With the union, both settle on the same value and stop pushing.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md` (Persistence). Update its merge-policy
section to match.

**Blocked by:** 08

**Status:** ready-for-agent

- [x] Reconcile yields `(local | server)` cut to the stream length; a null local contributes nothing
- [x] Pushes use the `or` operation; `replace` is sent only when the cut cleared bits
- [x] A reply that changes nothing locally pushes nothing
- [x] The spec's merge-policy text is updated; ticket 03's `replace` rule is marked superseded there
- [x] Tests: a stale local loses no server bits; a server missing bits gets them back; a shorter
      stream cuts bits and sends `replace`; two clients with different masks converge in one
      exchange each
- [ ] In game: spend a trap on one machine, connect from a second machine with an older state file,
      and confirm the trap does not re-fire
