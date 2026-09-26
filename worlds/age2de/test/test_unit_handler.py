import tempfile
import unittest
from pathlib import Path

from ..client.handlers.UnitHandler import UNIT_ITEM_TYPES, UnitHandler
from ..items.Items import Age2ItemData, UnitBuilding, UnitLine, UnitUpgrade


def read_ids(folder: str) -> list[int]:
    raw = (Path(folder) / "units.xsdat").read_bytes()
    return [int.from_bytes(raw[i:i + 4], "little") for i in range(0, len(raw), 4)]


class TestUnitHandler(unittest.TestCase):
    """units.xsdat is keyed by item, not by unit.

    Buildings and technologies can key theirs by the thing unlocked because the relation is one to
    one. A line item opens every tier of a line and a unit in upgrades mode wants up to three
    tokens, so the only thing worth writing down is which items arrived.
    """

    def sync(self, unlocked):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        handler = UnitHandler()
        handler.set_user_folder(folder.name + "/")
        handler.try_sync_units(unlocked)
        return read_ids(folder.name)

    def test_it_writes_the_unit_items_it_was_given(self):
        wanted = [Age2ItemData.UNIT_LINE_ARCHER, Age2ItemData.UPGRADE_BOW]
        self.assertEqual(sorted(self.sync(wanted)), sorted(item.id for item in wanted))

    def test_it_writes_nothing_when_nothing_has_arrived(self):
        self.assertEqual(self.sync([]), [])

    def test_it_ignores_items_that_are_not_unit_items(self):
        """A technology arriving must not end up in the unit replay file."""
        techish = [item for item in Age2ItemData if item.type_data not in UNIT_ITEM_TYPES][:4]
        self.assertEqual(self.sync(techish), [])

    def test_it_covers_all_three_item_modes(self):
        """One file serves every mode, because the installer already resolved which ids gate a
        unit - the game replays ids and never asks which mode produced them."""
        kinds = {type_data: False for type_data in UNIT_ITEM_TYPES}
        for item in Age2ItemData:
            if item.type_data in kinds:
                kinds[item.type_data] = True
        self.assertTrue(all(kinds.values()), kinds)
        every = [item for item in Age2ItemData if item.type_data in UNIT_ITEM_TYPES]
        self.assertEqual(len(self.sync(every)), len(every))

    def test_an_unknown_item_is_refused_rather_than_recorded(self):
        handler = UnitHandler()
        handler.unlock_item(Age2ItemData.WONDER)
        unlocked = [managed.item for managed in handler._items.values() if managed.unlocked]
        self.assertNotIn(Age2ItemData.WONDER, unlocked)
