"""Spent-state has to outlive a disconnect, and the server cannot be trusted to remember it.

An entry is spent when it has been paid out and must not be paid again: a trap or a filler resource
the moment it is delivered, a mercenary when the pavilion finishes spawning it. Both are facts about
the same received-item stream, so both are one bit in one mask, indexed by stream position.

The Set that records a spend can be lost -- and on disconnect every handler is rebuilt, so the
server's copy used to be the only survivor. Assigning from it handed spends back. So the local file
is authoritative for *spent* and the server for *unlocked*. These pin that rule and the file
behaviour underneath it.
"""

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


if __name__ == "__main__":
    unittest.main()
