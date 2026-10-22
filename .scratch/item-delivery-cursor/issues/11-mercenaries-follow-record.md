# 11: Mercenaries follow the spent record

**What to build:** Three gaps between the mercenary ack and the spent record.

**The ack waits for the spend to be recorded.** The game's ledger is a 4-slot FIFO. It reports the
head in every packet and drops the head once the client's ping echoes the same id back.
`ping_game` echoes it unconditionally today. So the spend is lost whenever the client couldn't
record it: the item stream hasn't arrived yet, the record isn't known yet, or a save failed. For a
known id, echo the ack only once the spend is in the in-memory record. That requires `record_known`
and an item stream that has arrived. Until then, send no ack, and the game keeps reporting the
completion.

An id this apworld doesn't know is acked anyway, with the existing warning. It can never be
recorded, and holding it would block the ledger for good. The client can't seat a mercenary it
doesn't know, so nothing is paid out twice.

**Mark once each time the reported head changes.** The game writes its packet every second but
reads acks every 2–4 s, so the same completed id shows up in several packets on purpose. Today, a
slot with two copies of one mercenary (from `start_inventory` or `!getitem`) marks the second copy
on the repeat. Remember the id last recorded. While packets keep showing it, re-send the ack but mark
nothing. Mark again only after the head has changed.

Accepted edge case: `MarkMercenaryComplete` already merges a completion whose id is already pending.
Two copies of one mercenary finishing back to back therefore count as one in the game. This ticket
matches that behaviour and doesn't change the XS.

**The pavilion follows the mask both ways.** `try_sync_mercenaries` only ever sets `used=True`. When
the cut to the stream length clears a mercenary's bit mid-session, that mercenary stays out of the
pavilion until the client reconnects. Set `used` from the mask in both directions.

**Blocked by:** 08, 09

**Status:** ready-for-agent

- [ ] A known completion is acked only after its bit is in the in-memory record
- [ ] Before `record_known`, a completion is neither marked nor acked
- [ ] An unknown id is acked with the existing warning
- [ ] A repeated head re-sends the ack and marks nothing; a new head marks once
- [ ] `used` follows the mask both ways; a cleared bit returns the mercenary to the queue
- [ ] Tests: a completion arriving before `ReceivedItems` is held, then recorded and acked; a
      repeated head marks once with two copies in the stream; an unknown id is acked; a cleared bit
      releases the mercenary
- [ ] In game: finish a mercenary while reconnecting, and confirm it stays spent and out of the
      pavilion
