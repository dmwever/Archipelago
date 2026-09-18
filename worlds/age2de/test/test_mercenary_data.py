"""MercenaryData.xs is the table the game loads at startup, and the unit count in it is what makes
mercenary_queue.xsdat parseable at all: the queue writes a seat's id then one int per soldier with no
length anywhere, so the reader finds the end of a seat by looking the count up here.

A table that disagrees with the queue does not fail loudly -- every seat after the first reads
garbage. These pin the count against the item data it came from.
"""

import unittest

from ..client.DataStorage import DataStorage
from ..client.handlers.install.MercenaryData import MercenaryData
from ..items.Items import Age2ItemData, CATEGORY_TO_ITEMS, Mercenary
from ..locations.Campaigns import Age2CampaignData

EVERY_CAMPAIGN = list(Age2CampaignData)


class TestRendering(unittest.TestCase):

    def test_a_seedless_install_still_defines_the_function(self) -> None:
        """AP.xs includes this file, so it has to exist and compile before anyone runs /install.
        The engine rejects an empty function body even though the linter accepts one."""
        rendered = MercenaryData().render()
        self.assertIn("void LoadMercenaryTable() {", rendered)
        self.assertIn("return;", rendered)
        self.assertNotIn("addMercenary", rendered)

    def test_every_mercenary_gets_a_row(self) -> None:
        roster = DataStorage(EVERY_CAMPAIGN).mercenaries
        rendered = MercenaryData(roster).render()
        self.assertEqual(len(roster), rendered.count("addMercenary("))
        for mercenary in roster:
            self.assertIn(f"addMercenary({mercenary.id},", rendered)

    def test_the_count_is_soldiers_not_kinds(self) -> None:
        loyalists = Age2ItemData.AP_JOAN_5_LOYALISTS
        rendered = MercenaryData([loyalists]).render()
        soldiers = sum(unit.count for unit in loyalists.type.units)
        self.assertEqual(4, len(loyalists.type.units), "this one has four kinds of unit")
        self.assertIn(f'"{loyalists.item_name}", {soldiers});', rendered,
                      "the queue reader counts soldiers, so kinds would end the seat too early")

    def test_only_the_seed_s_mercenaries_are_rendered(self) -> None:
        rendered = MercenaryData(DataStorage([Age2CampaignData.JOAN]).mercenaries).render()
        for mercenary in DataStorage([Age2CampaignData.ATTILA]).mercenaries:
            self.assertNotIn(f"addMercenary({mercenary.id},", rendered)

    def test_rendering_is_deterministic(self) -> None:
        """/install is run more than once and the file has to come out byte-identical."""
        roster = DataStorage(EVERY_CAMPAIGN).mercenaries
        self.assertEqual(MercenaryData(roster).render(), MercenaryData(roster).render())


class TestRefusals(unittest.TestCase):

    def test_a_name_with_a_quote_is_refused(self) -> None:
        """It would close the XS string early and shift every argument after it."""
        with self.assertRaises(ValueError):
            MercenaryData([_FakeMercenary('A "Quoted" Troop', 3)]).render()

    def test_a_mercenary_with_no_units_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            MercenaryData([_FakeMercenary("Nobody", 0)]).render()

    def test_past_the_xs_capacity_is_refused(self) -> None:
        too_many = [_FakeMercenary(f"Troop {n}", 1) for n in range(MercenaryData.MERCENARY_CAPACITY + 1)]
        with self.assertRaises(ValueError):
            MercenaryData(too_many).render()


class _FakeUnit:
    def __init__(self, count: int):
        self.count = count


class _FakeMercenaryType:
    def __init__(self, units: int):
        self.units = [_FakeUnit(units)] if units else []


class _FakeMercenary:
    def __init__(self, name: str, units: int, id: int = 9000):
        self.item_name = name
        self.id = id
        self.type = _FakeMercenaryType(units)


class TestAgainstTheRealRoster(unittest.TestCase):

    def test_no_shipped_mercenary_trips_a_refusal(self) -> None:
        MercenaryData(CATEGORY_TO_ITEMS[Mercenary]).render()


if __name__ == "__main__":
    unittest.main()
