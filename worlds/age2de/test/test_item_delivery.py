"""Item delivery over items.xsdat / free_items.xsdat.

These exercise the client half of the one-time item channel: the sliding window
in send_items, the acknowledgement cursor in ack_items, and the release echo in
free_items. FakeGame below stands in for AP.xs's ReadItems / FreeItems rules so a
full delivery can be driven without the game running.

Regression cover for the defect where ack_items advanced acked_items once per
occupied echo slot per tick, over-running the send window and stranding every
item past it.
"""

import os
import struct
import tempfile
import unittest

from ..campaign import XsdatFile
from ..client.GameClient import (
    AGE2_USER_PROFILE,
    Age2GameContext,
    DefaultClientInterface,
)
from ..items import Items
from ..items.Items import Age2ItemData

ITEM_WINDOW = 12


def read_ints(path: str) -> list[int]:
    if not os.path.exists(path):
        return []
    with open(path, "rb") as fp:
        data = fp.read()
    return [struct.unpack("<i", data[i:i + 4])[0] for i in range(0, len(data), 4)]


class FakeGame:
    """The XS side of the handshake, as AP.xs implements it after the fix.

    ReadItems grants an id only into a free slot; FreeItems releases one slot per
    id echoed back by the client.
    """

    def __init__(self) -> None:
        self.slots = [-1] * ITEM_WINDOW
        self.granted: list[int] = []
        self.discarded: list[int] = []

    def read_items(self, folder: str) -> None:
        for i, item_id in enumerate(read_ints(folder + "items.xsdat")[:ITEM_WINDOW]):
            if self.slots[i] == -1:
                self.granted.append(item_id)
                self.slots[i] = item_id
            else:
                self.discarded.append(item_id)

    def free_items(self, folder: str) -> None:
        for item_id in read_ints(folder + "free_items.xsdat"):
            for j in range(ITEM_WINDOW):
                if self.slots[j] == item_id:
                    self.slots[j] = -1
                    break

    def echo(self) -> list[int]:
        return list(self.slots)


class TestItemDelivery(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        os.makedirs(self._tmp.name + AGE2_USER_PROFILE, exist_ok=True)

        self.ctx = Age2GameContext(DefaultClientInterface())
        # Goes through the real setter so the storage handler writes into the temp folder
        # too; mark_delivered_spent persists the record on every tick.
        self.ctx.update_game_user_folder(self._tmp.name)
        # These exercise the window, not the gate on it. TestOneShotSkipping covers that.
        self.ctx.client_status.storage_ready = True
        self.folder = self.ctx.profile_folder()
        self.game = FakeGame()

    # -- helpers ---------------------------------------------------------

    def unlock(self, *items: Age2ItemData) -> None:
        self.ctx.client_status.unlocked_items.extend(items)

    def set_echo(self, echoed: list[int]) -> None:
        self.ctx.current_packet.item_ids = list(echoed) + [-1] * (ITEM_WINDOW - len(echoed))

    def client_tick(self) -> None:
        """The item phase of status_loop, in the same order."""
        if any(x != -1 for x in self.ctx.current_packet.item_ids):
            self.ctx.ack_items()
            self.ctx.mark_delivered_spent()
        if self.ctx.client_status.acked_items < len(self.ctx.client_status.unlocked_items):
            self.ctx.send_items()
        self.ctx.free_items()

    def full_tick(self) -> None:
        """One client tick plus the game's response to it."""
        self.set_echo([x for x in self.game.echo() if x != -1])
        self.client_tick()
        # ping_game arms the game's ReadItems rule only while a window is
        # outstanding, so a stale items.xsdat is never re-read.
        if len(self.ctx.client_status.in_flight) != 0:
            self.game.read_items(self.folder)
        self.game.free_items(self.folder)

    def sent_items(self) -> list[int]:
        return read_ints(self.folder + "items.xsdat")

    # -- tests -----------------------------------------------------------

    def test_ack_does_not_advance_twice_for_one_window(self) -> None:
        """The same echo on consecutive ticks must advance the cursor once."""
        self.unlock(*list(Age2ItemData)[:20])

        self.ctx.send_items()
        window = self.sent_items()
        self.assertEqual(len(window), ITEM_WINDOW)

        self.set_echo(window)
        self.ctx.ack_items()
        self.assertEqual(self.ctx.client_status.acked_items, ITEM_WINDOW)

        self.ctx.ack_items()
        self.assertEqual(
            self.ctx.client_status.acked_items,
            ITEM_WINDOW,
            "a second tick on the same echo re-acked items that were never sent",
        )

    def test_full_window_acks_exactly_twelve(self) -> None:
        self.unlock(*list(Age2ItemData)[:ITEM_WINDOW])
        self.ctx.send_items()
        self.set_echo(self.sent_items())
        self.ctx.ack_items()
        self.assertEqual(self.ctx.client_status.acked_items, ITEM_WINDOW)

    def test_no_send_while_game_still_holds_a_window(self) -> None:
        self.unlock(*list(Age2ItemData)[:20])
        self.ctx.send_items()
        first = self.sent_items()

        # The cursor has moved on, but the game has not released the slots yet.
        self.set_echo(first)
        self.ctx.ack_items()
        self.assertEqual(self.ctx.client_status.acked_items, ITEM_WINDOW)

        self.ctx.send_items()
        self.assertEqual(
            self.sent_items(),
            first,
            "a new window was written while the game still held the previous one",
        )

    def test_every_item_is_delivered(self) -> None:
        """20 items across two windows: all 20 reach the game, none skipped."""
        items = list(Age2ItemData)[:20]
        self.unlock(*items)

        for _ in range(30):
            self.full_tick()
            if self.ctx.client_status.acked_items >= len(items):
                break

        self.assertEqual(self.game.discarded, [], "the game discarded ids it was sent")
        self.assertEqual(
            self.game.granted,
            [item.id for item in items],
            "not every unlocked item reached the game",
        )
        self.assertEqual(self.ctx.client_status.acked_items, len(items))

    def test_duplicate_ids_in_one_window(self) -> None:
        """Filler resources repeat; acking must count them, not collapse them."""
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(*([wood] * 5))

        for _ in range(20):
            self.full_tick()
            if self.ctx.client_status.acked_items >= 5:
                break

        self.assertEqual(self.game.granted, [wood.id] * 5)
        self.assertEqual(self.ctx.client_status.acked_items, 5)

    def test_free_items_does_not_release_unacked_ids(self) -> None:
        """Nothing may be freed from the game's slots before the cursor passes it."""
        items = list(Age2ItemData)[:ITEM_WINDOW]
        self.unlock(*items)
        self.ctx.send_items()

        # The game has taken only part of the window so far.
        partial = self.sent_items()[:4]
        self.set_echo(partial)
        self.ctx.ack_items()
        self.ctx.free_items()

        freed = read_ints(self.folder + "free_items.xsdat")
        self.assertEqual(
            freed,
            partial,
            "free_items released ids the client had not acknowledged",
        )

    def test_an_unknown_item_id_is_skipped_not_raised(self) -> None:
        """An id this world does not know must not take the connection down with it."""
        from NetUtils import NetworkItem

        from ..client.ApClient import Age2Context

        ap = Age2Context.__new__(Age2Context)
        ap.game_ctx = self.ctx

        known = list(Age2ItemData)[1:3]
        packet = {"index": 0, "items": [NetworkItem(999999, 0, 0, 0)]
                  + [NetworkItem(item.id, 0, 0, 0) for item in known]}

        ap._handle_received_items(packet)

        self.assertEqual(
            self.ctx.client_status.unlocked_items,
            known,
            "an id the world does not know killed the ReceivedItems handler",
        )

    def test_index_zero_resync_does_not_duplicate_the_item_list(self) -> None:
        """A mid-session resend replaces the list; the cursor stays valid over it."""
        from NetUtils import NetworkItem

        from ..client.ApClient import Age2Context

        ap = Age2Context.__new__(Age2Context)
        ap.game_ctx = self.ctx

        items = list(Age2ItemData)[1:5]
        packet = {"index": 0, "items": [NetworkItem(item.id, 0, 0, 0) for item in items]}

        ap._handle_received_items(packet)
        self.assertEqual(len(self.ctx.client_status.unlocked_items), len(items))

        self.ctx.client_status.acked_items = 2
        ap._handle_received_items(packet)
        self.assertEqual(
            len(self.ctx.client_status.unlocked_items),
            len(items),
            "a resync appended a second copy of every item",
        )
        self.assertEqual(self.ctx.client_status.acked_items, 2)

    def test_free_items_releases_orphans_from_a_previous_session(self) -> None:
        """After a reconnect the game may hold ids this session never sent."""
        self.unlock(*list(Age2ItemData)[:4])
        self.set_echo([999, 998])
        self.client_tick()

        self.assertEqual(
            read_ints(self.folder + "free_items.xsdat"),
            [999, 998],
            "stale slots were never released, so no new window can be sent",
        )


class TestOneShotSkipping(TestItemDelivery):
    """Filler resources and traps add rather than set, so a replayed stream must not re-send them.

    The window is positional, so they are replaced in place by SKIP_ITEM_ID, not dropped.
    """

    FILLER = Age2ItemData.FILLER_WOOD_SMALL
    TRAP = Age2ItemData.TRAP_WOLOLO
    FLAG = Age2ItemData.FISH_TRAP

    def test_nothing_is_sent_before_the_stored_mark_has_come_back(self) -> None:
        self.ctx.client_status.storage_ready = False
        self.unlock(self.TRAP)

        self.ctx.send_items()

        self.assertEqual([], self.sent_items(),
                         "sending before the mark lands is exactly the reconnect trap bug")
        self.assertEqual([], self.ctx.client_status.in_flight)

    def test_a_rewound_cursor_skips_the_one_shots_it_already_paid(self) -> None:
        self.unlock(self.FILLER, self.FLAG, self.TRAP, self.FLAG, self.FILLER, self.TRAP, self.FLAG)
        # The reconnect case: the record survived, the cursor did not. Only the filler at 0
        # and 4 and the trap at 2 can carry a bit; flags are replayable and never spend.
        self.ctx.client_status.spent_mask = (1 << 0) | (1 << 2) | (1 << 4)
        self.ctx.client_status.acked_items = 0

        self.ctx.send_items()

        self.assertEqual(
            [Items.SKIP_ITEM_ID, self.FLAG.id, Items.SKIP_ITEM_ID, self.FLAG.id, Items.SKIP_ITEM_ID,
             self.TRAP.id, self.FLAG.id],
            self.sent_items(),
            "one-shots below the mark skip, flags resend, and anything above the mark is real")

    def test_skipping_does_not_shorten_the_window(self) -> None:
        """The game counts entries, so a dropped one would shift every index after it."""
        items = [self.TRAP] * 7
        self.unlock(*items)
        self.ctx.client_status.spent_mask = 0b1111111
        self.ctx.client_status.acked_items = 0

        self.ctx.send_items()

        self.assertEqual([Items.SKIP_ITEM_ID] * 7, self.sent_items())

    def test_forward_delivery_never_skips_anything(self) -> None:
        """The mark only ever reaches the cursor, so a window is always entirely unpaid."""
        items = [self.FILLER, self.TRAP, self.FLAG] * 5
        self.unlock(*items)

        for _ in range(30):
            self.full_tick()
            if self.ctx.client_status.acked_items >= len(items):
                break

        self.assertEqual([item.id for item in items], self.game.granted,
                         "a first delivery was skipped as though it had already been paid")
        spent = self.ctx.client_status.spent_mask
        for index, item in enumerate(items):
            one_shot = item in Items.ONE_SHOT_ITEMS
            self.assertEqual(one_shot, bool((spent >> index) & 1),
                             f"index {index} ({item.item_name}) should "
                             f"{'be' if one_shot else 'not be'} spent")

    def test_the_mark_follows_the_cursor_and_is_reported_once_per_move(self) -> None:
        reported: list[int] = []
        self.ctx.client_interface.on_item_spent = reported.append
        self.unlock(*[self.FLAG] * 20)

        for _ in range(30):
            self.full_tick()
            if self.ctx.client_status.acked_items >= 20:
                break

        self.assertEqual(0, self.ctx.client_status.spent_mask,
                         "flag items are replayable, so none of them is ever spent")
        self.assertEqual([], reported, "nothing was spent, so nothing to report")


class TestDecodingTheSpentRecord(TestItemDelivery):
    """spent_items turns the record back into entries, and is the only place indices are read.

    Everything downstream -- the mercenary handler in particular -- is handed items, not bits.
    """

    def test_bits_name_the_entries_they_sit_over(self) -> None:
        items = [Age2ItemData.FILLER_WOOD_SMALL, Age2ItemData.FISH_TRAP,
                 Age2ItemData.TRAP_WOLOLO]
        self.unlock(*items)
        self.ctx.client_status.spent_mask = (1 << 0) | (1 << 2)

        self.assertEqual([Age2ItemData.FILLER_WOOD_SMALL, Age2ItemData.TRAP_WOLOLO],
                         self.ctx.spent_items())

    def test_an_empty_record_names_nothing(self) -> None:
        self.unlock(Age2ItemData.TRAP_WOLOLO)
        self.assertEqual([], self.ctx.spent_items())

    def test_a_bit_past_the_received_stream_names_nothing(self) -> None:
        """A record outlives the apsave, so it can carry bits for a stream that is not back yet."""
        self.unlock(Age2ItemData.TRAP_WOLOLO)
        self.ctx.client_status.spent_mask = 1 << 40

        self.assertEqual([], self.ctx.spent_items(),
                         "a bit beyond what has been received cannot name an entry")

    def test_duplicates_are_named_once_each(self) -> None:
        """Filler repeats, so the same id can sit at several indices and spend independently."""
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(wood, wood, wood)
        self.ctx.client_status.spent_mask = (1 << 0) | (1 << 2)

        self.assertEqual([wood, wood], self.ctx.spent_items())


class TestReconcilingTheSpentRecord(TestItemDelivery):
    """The local record is authoritative for *spent*, the server for *unlocked*.

    A spend the server never stored must not be handed back, so a local record overrules it even
    when it knows less. A union would make "the server is behind" indistinguishable from "the
    server is ahead", and would mean nothing could ever be un-spent.
    """

    def saved(self, spent: int) -> None:
        self.ctx.storage_handler.try_save(spent)

    def test_no_local_record_adopts_the_server(self) -> None:
        self.assertEqual(0b101, self.ctx.reconcile_spent(0b101))
        self.assertEqual(0b101, self.ctx.client_status.spent_mask)

    def test_the_local_record_wins_over_a_server_that_is_behind(self) -> None:
        self.saved(0b101)
        self.assertEqual(0b101, self.ctx.reconcile_spent(0b001),
                         "a spend the server never stored must not be handed back")

    def test_the_local_record_wins_even_when_it_knows_less(self) -> None:
        self.saved(0b001)
        self.assertEqual(0b001, self.ctx.reconcile_spent(0b101))

    def test_an_empty_record_is_not_a_missing_record(self) -> None:
        """Both are falsy, and confusing them would silently restore every spend."""
        self.saved(0)
        self.assertEqual(0, self.ctx.reconcile_spent(0b101),
                         "a playthrough that has spent nothing still wins")

    def test_reconciling_opens_the_gate_on_sending(self) -> None:
        self.ctx.client_status.storage_ready = False
        self.ctx.reconcile_spent(0)
        self.assertTrue(self.ctx.client_status.storage_ready)


if __name__ == "__main__":
    unittest.main()
