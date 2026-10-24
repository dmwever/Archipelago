"""Spent-state has to outlive a disconnect, and the server cannot be trusted to remember it.

An entry is spent when it has been paid out and must not be paid again: a trap or a filler resource
the moment it is delivered, a mercenary when the pavilion finishes spawning it. Both are facts about
the same received-item stream, so both are one bit in one mask, indexed by stream position.

The Set that records a spend can be lost, and the local file can be stale, so neither copy is
authoritative for *spent*: the record is the union of both, cut to the stream the server says
exists (TestReconcilingTheSpentRecord in test_item_delivery pins that). These pin the file
behaviour underneath it.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from ..client.handlers.StorageHandler import StorageHandler
from ..generation import Identity

TAG = "b435aa86"
PLAYER = "Dave"


def mask(*indices: int) -> int:
    value = 0
    for index in indices:
        value |= 1 << index
    return value


class StorageHandlerTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.folder = self._folder.name
        self.addCleanup(self._folder.cleanup)

    def handler(self) -> StorageHandler:
        handler = StorageHandler()
        handler.set_user_folder(self.folder)
        handler.set_tag(TAG)
        handler.set_player_name(PLAYER)
        return handler


class TestTheFile(StorageHandlerTestBase):
    def test_no_file_reads_as_none(self) -> None:
        self.assertIsNone(self.handler().try_load(),
                          "a missing record must be distinguishable from an empty one")

    def test_a_saved_mask_comes_back(self) -> None:
        handler = self.handler()
        handler.try_save(mask(8, 11))
        self.assertEqual(mask(8, 11), handler.try_load())
        self.assertEqual(mask(8, 11), self.handler().try_load())

    def test_an_empty_mask_round_trips_as_empty_not_missing(self) -> None:
        handler = self.handler()
        handler.try_save(0)
        self.assertEqual(0, handler.try_load())
        self.assertEqual(0, self.handler().try_load(),
                         "0 is a record that nothing is spent, not the absence of a record")

    def test_spent_mask_reads_a_missing_record_as_nothing_spent(self) -> None:
        self.assertEqual(0, self.handler().spent_mask())

    def test_a_mask_wider_than_a_machine_word_survives(self) -> None:
        """A long playthrough indexes past 64 bits, and the stream has no fixed length."""
        wide = mask(3, 700, 1499)
        handler = self.handler()
        handler.try_save(wide)
        self.assertEqual(wide, self.handler().try_load())

    def test_saving_creates_the_folder(self) -> None:
        handler = self.handler()
        self.assertFalse(handler.apdata_dir().exists())
        handler.try_save(0)
        self.assertTrue(handler.apdata_dir().is_dir(),
                        "no other handler creates a directory, so this one has to")

    def test_a_malformed_file_falls_back_to_the_server(self) -> None:
        """Worse than no file would be a file that silently un-spends everything.

        Read through a fresh handler, because that is when a bad file is actually met: the record
        is read once and then held, and every disconnect builds a new handler.
        """
        written = self.handler()
        written.try_save(mask(8))
        written.state_path().write_text("{ not json", encoding="utf-8")

        with self.assertLogs("Client", level="ERROR"):
            self.assertIsNone(self.handler().try_load())

    def test_the_name_matches_the_identity_helper(self) -> None:
        self.assertEqual(Path(self.folder) / "APData"
                         / Identity.storage_file_name("state", TAG, PLAYER),
                         self.handler().state_path())

    def test_two_playthroughs_do_not_share_a_file(self) -> None:
        one = self.handler()
        two = self.handler()
        two.set_tag(Identity.seed_tag("another seed", 5))
        self.assertNotEqual(one.state_path(), two.state_path())


class TestSpentIndices(StorageHandlerTestBase):
    """The one decode of the mask: everyone else asks in stream positions, never in bits."""

    def test_bits_name_the_positions_they_sit_over(self) -> None:
        handler = self.handler()
        handler.mark_spent({0, 2, 5})
        self.assertEqual({0, 2, 5}, handler.spent_indices(8))

    def test_a_bit_past_the_received_stream_names_nothing(self) -> None:
        """A record outlives the apsave, so it can carry bits for a stream that is not back yet."""
        handler = self.handler()
        handler.mark_spent({1, 40})
        self.assertEqual({1}, handler.spent_indices(3))

    def test_a_missing_record_names_nothing(self) -> None:
        self.assertEqual(set(), self.handler().spent_indices(4))


class TestClearing(StorageHandlerTestBase):
    def test_clearing_forgets_the_record(self) -> None:
        """Local only. The caller does not touch the server, which holds the real spends."""
        handler = self.handler()
        handler.try_save(mask(8, 11))

        self.assertTrue(handler.try_clear())
        self.assertIsNone(handler.try_load(),
                          "a cleared playthrough defers to the server again, rather than "
                          "overruling it with an empty record")
        self.assertIsNone(self.handler().try_load())

    def test_clearing_a_playthrough_with_no_record_reports_nothing_cleared(self) -> None:
        self.assertFalse(self.handler().try_clear())

    def test_a_cleared_record_can_be_written_again(self) -> None:
        handler = self.handler()
        handler.try_save(mask(8))
        handler.try_clear()

        handler.try_save(mask(2))

        self.assertEqual(mask(2), handler.try_load())


class TestAFailedWrite(StorageHandlerTestBase):
    """The record lives in memory; the disk is written behind it and may lag.

    A save that fails must not cost a mark: delivery holds nothing back on the disk, and the
    server push persists the spend meanwhile.
    """

    def blocked(self) -> StorageHandler:
        handler = self.handler()
        self.block(handler)
        return handler

    def block(self, handler: StorageHandler) -> None:
        """A file where APData should be, so nothing can be written under it."""
        shutil.rmtree(handler.apdata_dir(), ignore_errors=True)
        handler.apdata_dir().write_text("in the way", encoding="utf-8")

    def unblock(self, handler: StorageHandler) -> None:
        handler.apdata_dir().unlink()

    def test_a_mark_lands_in_memory_when_the_disk_refuses_it(self) -> None:
        handler = self.blocked()
        with self.assertLogs("Client", level="WARNING"):
            self.assertTrue(handler.mark_spent({3}), "a mark that changed the record must say so")
        self.assertEqual(mask(3), handler.spent_mask())

    def test_the_warning_names_the_path_and_comes_once(self) -> None:
        handler = self.blocked()
        with self.assertLogs("Client", level="WARNING") as logs:
            handler.mark_spent({1})
            handler.try_flush()
            handler.mark_spent({2})
        self.assertEqual(1, len(logs.records), "a failing disk warned on every tick")
        self.assertIn(str(handler.state_path()), logs.output[0])

    def test_the_next_flush_retries_the_write(self) -> None:
        handler = self.blocked()
        with self.assertLogs("Client", level="WARNING"):
            handler.mark_spent({1, 4})
        self.unblock(handler)

        handler.try_flush()

        self.assertEqual(mask(1, 4), self.handler().try_load())

    def test_a_write_that_succeeds_clears_the_warning(self) -> None:
        """So a disk that fails again later is reported again."""
        handler = self.blocked()
        with self.assertLogs("Client", level="WARNING"):
            handler.mark_spent({1})
        self.unblock(handler)
        handler.try_flush()
        self.block(handler)

        with self.assertLogs("Client", level="WARNING"):
            handler.mark_spent({2})

    def test_resetting_the_same_identity_keeps_an_unwritten_mark(self) -> None:
        """/set_user_folder sets the tag and player again; rereading the disk would drop it."""
        handler = self.blocked()
        with self.assertLogs("Client", level="WARNING"):
            handler.mark_spent({5})

        handler.set_tag(TAG)
        handler.set_player_name(PLAYER)

        self.assertEqual(mask(5), handler.spent_mask())

    def test_a_flush_with_nothing_owed_writes_nothing(self) -> None:
        handler = self.handler()
        handler.try_flush()
        self.assertFalse(handler.apdata_dir().exists())


if __name__ == "__main__":
    unittest.main()
