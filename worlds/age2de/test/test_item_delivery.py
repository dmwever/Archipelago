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
        self.ctx.client_status.user_folder = self._tmp.name
        self.folder = self.ctx.user_folder()
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


if __name__ == "__main__":
    unittest.main()
