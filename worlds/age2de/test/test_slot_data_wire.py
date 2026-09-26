import dataclasses
import struct
import tempfile
import unittest
from pathlib import Path

from test.general import setup_solo_multiworld

from .. import Age2World
from ..Options import Age2Options
from ..client.handlers.TechHandler import TechHandler
from ..generation import Identity, SlotData
from ..locations.Techs import Age2TechData

SEED = "0123456789abcdef"


class TestOptionsReachTheGame(unittest.TestCase):
    def test_every_wired_option_is_a_real_option(self):
        fields = {field.name for field in dataclasses.fields(Age2Options)}
        for xs_name, option_name in SlotData.OPTIONS.items():
            self.assertIn(option_name, fields, xs_name)


class TestSlotDataRoundTrip(unittest.TestCase):
    CHOSEN = {"techsanity": 3, "tech_behavior": 1, "lock_techs": 1, "shuffle_ages": 1,
              "shuffle_unique_techs": 1, "existing_techs": 1,
              "unitsanity": 2, "unitsanity_items": 1, "shuffle_villager": 2,
              "include_unique_units": 3, "caveman": 1}

    def slot_data(self, **options):
        world = setup_solo_multiworld(Age2World).worlds[1]
        for name, value in options.items():
            getattr(world.options, name).value = value
        return world.fill_slot_data()

    def test_the_options_survive_the_wire(self):
        slot_data = self.slot_data(**self.CHOSEN)
        for option_name in SlotData.OPTIONS.values():
            self.assertIn(option_name, slot_data)

        values = SlotData.slot_fields(3, Identity.seed_tag(SEED, 3), slot_data)
        for xs_name, option_name in SlotData.OPTIONS.items():
            self.assertEqual(values[xs_name], self.CHOSEN[option_name], xs_name)

    def test_nothing_falls_back_to_a_default(self):
        # A missing key silently reads as Techsanity off, which is the failure
        # the wire is here to prevent.
        values = SlotData.slot_fields(3, Identity.seed_tag(SEED, 3),
                                      self.slot_data(**self.CHOSEN))
        for name in SlotData.OPTIONS:
            self.assertNotEqual(values[name], SlotData.UNSET, name)


class TestTechHandler(unittest.TestCase):
    def sync(self, techs, unlocked):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        handler = TechHandler(techs)
        handler.set_user_folder(folder.name + "/")
        handler.try_sync_techs(unlocked)
        written = Path(folder.name, "techs.xsdat").read_bytes()
        return [struct.unpack("<i", written[i:i + 4])[0] for i in range(0, len(written), 4)]

    def test_only_unlocked_techs_are_written(self):
        marauders = Age2TechData.MARAUDERS_HUNS
        atheism = Age2TechData.ATHEISM_HUNS
        self.assertEqual(self.sync([marauders, atheism], [marauders.item]), [marauders.item.id])

    def test_nothing_unlocked_writes_an_empty_file(self):
        self.assertEqual(self.sync([Age2TechData.MARAUDERS_HUNS], []), [])

    def test_it_writes_item_ids(self):
        tech = Age2TechData.ELITE_TARKAN_HUNS
        self.assertEqual(self.sync([tech], [tech.item]), [tech.item.id])

    def test_an_unlock_sticks_across_syncs(self):
        tech = Age2TechData.MARAUDERS_HUNS
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        handler = TechHandler([tech])
        handler.set_user_folder(folder.name + "/")
        handler.try_sync_techs([tech.item])
        handler.try_sync_techs([])
        written = Path(folder.name, "techs.xsdat").read_bytes()
        self.assertEqual(len(written), 4)
