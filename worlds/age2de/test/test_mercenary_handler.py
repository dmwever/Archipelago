"""The four pavilion seats are fixed positions, not a sliding window. Spending the one in seat 1
must refill seat 1 from the head of the queue and leave seats 0, 2 and 3 exactly where they were --
the queue file carries no seat index, so position in the file *is* the seat and anything that shifts
re-points a mercenary the game has already been shown.
"""

import tempfile
import unittest
from pathlib import Path

from ..campaign import XsdatFile
from ..client.DataStorage import DataStorage
from ..client.handlers.MercenaryHandler import MercenaryHandler, SEAT_COUNT, EMPTY_SEAT
from ..items.Items import Age2ItemData, CATEGORY_TO_ITEMS, Mercenary
from ..locations.Campaigns import Age2CampaignData

EVERY_CAMPAIGN = list(Age2CampaignData)


def read_ints(path: Path) -> list[int]:
    values = []
    with open(path, "rb") as fp:
        while fp.read(1):
            fp.seek(-1, 1)
            values.append(XsdatFile.read_int(fp))
    return values


class MercenaryHandlerTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.folder = self._folder.name + "/"
        self.addCleanup(self._folder.cleanup)

    def handler(self) -> MercenaryHandler:
        handler = MercenaryHandler(CATEGORY_TO_ITEMS[Mercenary])
        handler.set_user_folder(self.folder)
        return handler

    def roster(self, campaigns: list[Age2CampaignData] = None) -> list[Age2ItemData]:
        return DataStorage(EVERY_CAMPAIGN if campaigns is None else campaigns).mercenaries


class TestSeating(MercenaryHandlerTestBase):

    def test_arrival_order_fills_the_seats(self) -> None:
        handler = self.handler()
        found = self.roster()[:SEAT_COUNT + 1][::-1]
        handler.try_sync_mercenaries(found)
        self.assertEqual(found[:SEAT_COUNT], handler.seated(),
                         "seats were not filled in the order the items arrived")
        self.assertEqual(found[SEAT_COUNT:], handler.queued(),
                         "the overflow did not stay queued in arrival order")

    def test_spending_a_seat_refills_only_that_seat(self) -> None:
        handler = self.handler()
        found = self.roster()[:SEAT_COUNT + 1]
        handler.try_sync_mercenaries(found)
        before = handler.seated()

        handler.use_mercenary(before[1])
        handler.try_sync_mercenaries(found)
        after = handler.seated()

        self.assertEqual(found[SEAT_COUNT], after[1], "seat 1 was not refilled from the queue head")
        for seat in (0, 2, 3):
            self.assertEqual(before[seat], after[seat],
                             f"seat {seat} moved when seat 1 was emptied")

    def test_a_used_mercenary_never_returns_to_the_queue(self) -> None:
        handler = self.handler()
        found = self.roster()
        handler.try_sync_mercenaries(found)
        spent = handler.seated()[0]

        handler.use_mercenary(spent)
        for _ in range(3):
            handler.try_sync_mercenaries(found)

        self.assertNotIn(spent, handler.seated(), "a spent mercenary was seated again")
        self.assertNotIn(spent, handler.queued(), "a spent mercenary went back into the queue")
        self.assertTrue(handler.is_used(spent))

    def test_only_what_was_granted_is_queued(self) -> None:
        """unlocked_items is what the server granted this slot, so it is already seed-filtered and
        the handler does not second-guess it."""
        handler = self.handler()
        granted = self.roster([Age2CampaignData.JOAN])
        handler.try_sync_mercenaries(granted)
        for mercenary in handler.seated() + handler.queued():
            if mercenary is None:
                continue
            self.assertIn(mercenary, granted,
                          f"{mercenary.item_name} was queued but never granted")

    def test_handing_a_mercenary_back_returns_it_to_the_queue(self) -> None:
        """The SetReply assigns rather than only adding, so a mercenary the client marked
        optimistically and never got stored has to come back rather than stay spent."""
        handler = self.handler()
        granted = self.roster()
        handler.try_sync_mercenaries(granted)
        spent = handler.seated()[0]

        handler.use_mercenary(spent)
        handler.try_sync_mercenaries(granted)
        self.assertTrue(handler.is_used(spent))
        self.assertNotIn(spent, handler.seated() + handler.queued())

        handler.set_used(spent, False)
        handler.try_sync_mercenaries(granted)
        self.assertFalse(handler.is_used(spent))
        self.assertIn(spent, handler.seated() + handler.queued(),
                      "a mercenary the server never recorded as spent must be offered again")

    def test_using_something_that_is_not_a_mercenary_is_refused(self) -> None:
        handler = self.handler()
        handler.use_mercenary(Age2ItemData.VICTORY)
        self.assertEqual([None] * SEAT_COUNT, handler.seated(),
                         "a non-mercenary disturbed the seats")


class TestQueueFile(MercenaryHandlerTestBase):

    def test_every_seat_gets_a_record_even_when_empty(self) -> None:
        handler = self.handler()
        handler.try_sync_mercenaries(self.roster()[:1])
        written = read_ints(Path(self.folder) / "mercenary_queue.xsdat")

        seated = handler.seated()[0]
        expected = [seated.id]
        for unit in seated.type.units:
            expected.extend([unit.unit.game_id] * unit.count)
        expected.extend([EMPTY_SEAT] * (SEAT_COUNT - 1))
        self.assertEqual(expected, written,
                         "the file must carry one record per seat, so position is the seat")

    def test_units_are_written_one_per_soldier(self) -> None:
        handler = self.handler()
        handler.try_sync_mercenaries(self.roster())
        written = read_ints(Path(self.folder) / "mercenary_queue.xsdat")
        seated = handler.seated()[0]
        total = sum(unit.count for unit in seated.type.units)
        self.assertEqual(total, len(written[1:total + 1]),
                         "each soldier needs its own id; the reader counts them, not the types")

    def test_an_emptied_seat_keeps_its_position_in_the_file(self) -> None:
        handler = self.handler()
        found = self.roster()[:SEAT_COUNT]
        handler.try_sync_mercenaries(found)
        handler.use_mercenary(handler.seated()[3])
        handler.try_sync_mercenaries(found)

        written = read_ints(Path(self.folder) / "mercenary_queue.xsdat")
        self.assertEqual(EMPTY_SEAT, written[-1],
                         "the emptied last seat must still be written, or the seats shift")


class TestUsedFile(MercenaryHandlerTestBase):

    def test_it_lists_the_ids_of_spent_mercenaries(self) -> None:
        handler = self.handler()
        granted = self.roster()
        handler.try_sync_mercenaries(granted)
        self.assertEqual([], read_ints(Path(self.folder) / "mercenaries.xsdat"),
                         "nothing is spent yet, so the file should be empty")

        spent = granted[2]
        handler.use_mercenary(spent)
        handler.try_sync_mercenaries(granted)
        self.assertEqual([spent.id], read_ints(Path(self.folder) / "mercenaries.xsdat"),
                         "the file keys by item id, so only the spent id belongs in it")

    def test_a_second_spend_is_added_not_replaced(self) -> None:
        handler = self.handler()
        granted = self.roster()
        handler.try_sync_mercenaries(granted)
        for mercenary in (granted[0], granted[5]):
            handler.use_mercenary(mercenary)
        handler.try_sync_mercenaries(granted)
        self.assertEqual({granted[0].id, granted[5].id},
                         set(read_ints(Path(self.folder) / "mercenaries.xsdat")))


if __name__ == "__main__":
    unittest.main()
