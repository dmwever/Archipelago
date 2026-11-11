"""The mercenary ack waits for the spend to be recorded.

The game's ledger is a 4-slot FIFO: it reports the head in every packet and drops it once the ping
echoes the same id back. An ack the client sends before the spend is in its record loses the spend
for good, so a known completion is held until the record is known and the bit is set.
"""

import os
import tempfile
import unittest

from ..client.GameClient import AGE2_USER_PROFILE, Age2GameContext, DefaultClientInterface
from ..client.handlers.MercenaryHandler import NO_MERCENARY
from ..items.Items import Age2ItemData


class MercenaryAckTestBase(unittest.TestCase):
    MERCENARY = Age2ItemData.AP_ATTILA_1_MANGUDAI

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        os.makedirs(self._tmp.name + AGE2_USER_PROFILE, exist_ok=True)

        self.ctx = Age2GameContext(DefaultClientInterface())
        self.ctx.update_game_user_folder(self._tmp.name)
        self.pushes: list[int] = []
        self.ctx.client_interface.on_item_spent = self.pushes.append

    def unlock(self, *items: Age2ItemData) -> None:
        self.ctx.client_status.unlocked_items.extend(items)

    def complete(self, item_id: int) -> int:
        """One packet reporting item_id at the head of the ledger; returns what the ping echoes."""
        self.ctx.sync_mercenary_completion(item_id)
        return self.ctx.mercenary_handler.ack()

    def spent(self) -> int:
        return self.ctx.storage_handler.spent_mask()


class TestTheAckWaitsForTheRecord(MercenaryAckTestBase):
    def test_a_completion_before_the_items_arrive_is_held_then_recorded(self) -> None:
        self.assertEqual(NO_MERCENARY, self.complete(self.MERCENARY.id),
                         "acked before the item stream arrived, so the spend has nowhere to go")
        self.assertEqual(0, self.spent())

        self.unlock(self.MERCENARY)
        self.ctx.reconcile_spent(0)

        self.assertEqual(self.MERCENARY.id, self.complete(self.MERCENARY.id))
        self.assertEqual(0b1, self.spent())
        self.assertEqual([0b1], self.pushes)
        self.assertTrue(self.ctx.mercenary_handler.is_used(self.MERCENARY))

    def test_an_unknown_id_is_acked_so_it_never_blocks_the_ledger(self) -> None:
        unknown = 4999
        with self.assertLogs("Client", level="WARNING"):
            self.assertEqual(unknown, self.complete(unknown))
        self.assertEqual(0, self.spent())


class TestARepeatedHeadMarksOnce(MercenaryAckTestBase):
    """The game writes every second but reads acks every 2-4 s, so one head shows up repeatedly."""

    def setUp(self) -> None:
        super().setUp()
        self.unlock(self.MERCENARY, self.MERCENARY)
        self.ctx.reconcile_spent(0)

    def test_a_repeated_head_re_sends_the_ack_and_marks_nothing(self) -> None:
        for _ in range(3):
            self.assertEqual(self.MERCENARY.id, self.complete(self.MERCENARY.id))
        self.assertEqual(0b01, self.spent(), "a repeat of one completion spent the second copy")
        self.assertEqual([0b01], self.pushes)

    def test_a_new_head_marks_again(self) -> None:
        self.complete(self.MERCENARY.id)
        self.complete(NO_MERCENARY)
        self.complete(self.MERCENARY.id)
        self.assertEqual(0b11, self.spent())


class TestThePavilionFollowsTheMask(MercenaryAckTestBase):
    def test_a_cleared_bit_returns_the_mercenary_to_the_pavilion(self) -> None:
        """A server rollback shortens the stream, the cut clears the bit, and the stream regrows."""
        self.unlock(self.MERCENARY)
        self.ctx.reconcile_spent(0)
        self.complete(self.MERCENARY.id)
        self.ctx.sync_delivery(0)
        self.assertTrue(self.ctx.mercenary_handler.is_used(self.MERCENARY))

        self.ctx.client_status.unlocked_items.clear()
        self.ctx.reconcile_spent(0b1)
        self.unlock(self.MERCENARY)
        self.ctx.sync_delivery(0)

        handler = self.ctx.mercenary_handler
        self.assertFalse(handler.is_used(self.MERCENARY))
        self.assertIn(self.MERCENARY, handler.seated() + handler.queued(),
                      "the record no longer holds the spend, so the pavilion must offer it again")


if __name__ == "__main__":
    unittest.main()
