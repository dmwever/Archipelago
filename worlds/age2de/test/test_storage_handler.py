"""Spent-state has to outlive a disconnect, and the server cannot be trusted to remember it.

A mercenary is spent the moment the game finishes spawning it. The Set that records that can be
lost -- and on disconnect every handler is rebuilt and `mercenaries.xsdat` deleted, so the server's
bitmask used to be the only surviving copy. Assigning from it handed spent mercenaries back.

So the local file is authoritative for *spent* and the server for *unlocked*. These pin that rule
and the file behaviour underneath it.
"""

import json
import tempfile
import unittest
from pathlib import Path

from ..client.handlers.StorageHandler import StorageHandler, reconcile_spent
from ..generation import Identity
from ..items.Items import Age2ItemData, CATEGORY_TO_ITEMS, Mercenary

TAG = "b435aa86"
PLAYER = "Dave"


class StorageHandlerTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.folder = self._folder.name
        self.addCleanup(self._folder.cleanup)

    def handler(self) -> StorageHandler:
        handler = StorageHandler(CATEGORY_TO_ITEMS[Mercenary])
        handler.set_user_folder(self.folder)
        handler.set_tag(TAG)
        handler.set_player_name(PLAYER)
        return handler


class TestTheRule(StorageHandlerTestBase):
    """reconcile_spent is the whole policy; everything else is plumbing."""

    def test_no_local_file_adopts_the_server(self) -> None:
        spent, push = reconcile_spent(None, {4000, 4008})
        self.assertEqual({4000, 4008}, spent)
        self.assertFalse(push, "a cold start has nothing to teach the server")

    def test_the_local_file_wins_over_a_server_that_is_behind(self) -> None:
        spent, push = reconcile_spent({4000, 4008}, {4000})
        self.assertEqual({4000, 4008}, spent,
                         "a spend the server never stored must not be handed back")
        self.assertTrue(push, "the server is behind and has to be told")

    def test_the_local_file_wins_even_when_it_knows_less(self) -> None:
        # Deliberate: the file is authoritative, not merely additive. A union would make this case
        # indistinguishable from the one above and would mean nothing could ever be un-spent.
        spent, push = reconcile_spent({4000}, {4000, 4008})
        self.assertEqual({4000}, spent)
        self.assertTrue(push)

    def test_agreement_needs_no_push(self) -> None:
        spent, push = reconcile_spent({4000}, {4000})
        self.assertEqual({4000}, spent)
        self.assertFalse(push)

    def test_an_empty_file_is_not_a_missing_file(self) -> None:
        """Both are falsy, and confusing them would silently restore every spent mercenary."""
        spent, push = reconcile_spent(set(), {4000})
        self.assertEqual(set(), spent, "a playthrough that has spent nothing still wins")
        self.assertTrue(push)


class TestTheFile(StorageHandlerTestBase):
    def test_no_file_reads_as_none(self) -> None:
        self.assertIsNone(self.handler().try_load(),
                          "a missing file must be distinguishable from an empty one")

    def test_a_saved_set_comes_back(self) -> None:
        handler = self.handler()
        handler.try_save({4008, 4011})
        self.assertEqual({4008, 4011}, handler.try_load())

    def test_saving_creates_the_folder(self) -> None:
        handler = self.handler()
        self.assertFalse(handler.apdata_dir().exists())
        handler.try_save(set())
        self.assertTrue(handler.apdata_dir().is_dir(),
                        "no other handler creates a directory, so this one has to")

    def test_an_empty_save_round_trips_as_empty(self) -> None:
        handler = self.handler()
        handler.try_save(set())
        self.assertEqual(set(), handler.try_load())

    def test_every_mercenary_is_written_not_only_the_spent_ones(self) -> None:
        handler = self.handler()
        handler.try_save({4008})
        records = json.loads(handler.mercenary_path().read_text(encoding="utf-8"))
        self.assertEqual(len(CATEGORY_TO_ITEMS[Mercenary]), len(records),
                         "the file should read as a record of the playthrough")
        self.assertEqual(sorted(record["id"] for record in records),
                         [record["id"] for record in records],
                         "ids are sorted so the file diffs cleanly")

    def test_a_malformed_file_falls_back_to_the_server(self) -> None:
        """Worse than no file would be a file that silently un-spends everything."""
        handler = self.handler()
        handler.try_save({4008})
        handler.mercenary_path().write_text("{ not json", encoding="utf-8")
        with self.assertLogs("Client", level="ERROR"):
            self.assertIsNone(handler.try_load())

    def test_the_name_matches_the_identity_helper(self) -> None:
        handler = self.handler()
        self.assertEqual(Path(self.folder) / "APData"
                         / Identity.storage_file_name("mercenaries", TAG, PLAYER),
                         handler.mercenary_path())

    def test_two_playthroughs_do_not_share_a_file(self) -> None:
        one = self.handler()
        two = self.handler()
        two.set_tag(Identity.seed_tag("another seed", 5))
        self.assertNotEqual(one.mercenary_path(), two.mercenary_path())

    def test_keyed_by_item_id_not_by_bit_position(self) -> None:
        """DataStorage bit indices are positions in a seed-filtered roster and move when the
        campaign set changes; item ids do not."""
        handler = self.handler()
        spent = CATEGORY_TO_ITEMS[Mercenary][0]
        handler.try_save({spent.id})
        records = json.loads(handler.mercenary_path().read_text(encoding="utf-8"))
        used = [record["id"] for record in records if record["used"]]
        self.assertEqual([spent.id], used)
        self.assertIsInstance(spent, Age2ItemData)


if __name__ == "__main__":
    unittest.main()
