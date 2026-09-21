"""A mercenary is progression only where a rule leans on it. That has to be declared on the item,
because an item's classification is fixed in create_items while the rules that reference it are not
built until set_rules, and four of the six references live inside methods rather than on a class.
A declared flag drifts the moment someone adds or drops a rule, so these tests derive the truth from
the rule source and fail when the two disagree.
"""

import ast
import pathlib
import unittest

from BaseClasses import ItemClassification

from ..client.DataStorage import DataStorage
from ..items import Items
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS

RULE_PACKAGES = ("rules", "logic")


def referenced_by_rules() -> set[str]:
    """Names of mercenary items any rule or logic module mentions."""
    mercenaries = {item.name for item in Items.CATEGORY_TO_ITEMS[Items.Mercenary]}
    world = pathlib.Path(__file__).parent.parent
    found: set[str] = set()
    for package in RULE_PACKAGES:
        for source in (world / package).rglob("*.py"):
            tree = ast.parse(source.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                        and node.value.id == "Age2ItemData" and node.attr in mercenaries):
                    found.add(node.attr)
    return found


class TestMercenaryLogicFlag(unittest.TestCase):

    def test_in_logic_matches_the_rules_that_exist(self) -> None:
        declared = {item.name for item in Items.CATEGORY_TO_ITEMS[Items.Mercenary]
                    if item.type.in_logic}
        self.assertEqual(referenced_by_rules(), declared,
                         "in_logic no longer matches the mercenaries the rules name; a rule was "
                         "added or dropped without moving the flag with it")

    def test_classification_follows_in_logic(self) -> None:
        for item in Items.CATEGORY_TO_ITEMS[Items.Mercenary]:
            expected = (ItemClassification.progression if item.type.in_logic
                        else ItemClassification.useful)
            self.assertEqual(expected, Items.classification_for(item),
                             f"{item.item_name} is classified against its own in_logic flag")

    def test_a_mercenary_a_rule_needs_is_never_merely_useful(self) -> None:
        for name in referenced_by_rules():
            item = Items.Age2ItemData[name]
            self.assertEqual(ItemClassification.progression, Items.classification_for(item),
                             f"a rule depends on {item.item_name}, so fill has to place it as "
                             "progression or the locations behind it are unreachable")


class TestPackedBitfields(unittest.TestCase):
    """A spent mercenary must never be offered again, across reconnect and save/load, so the used
    set lives in DataStorage as a bitfield. The bit is an index into the seed's roster rather than a
    number declared on the item, so a Joan-only seed packs into bits 0-n instead of leaving every
    Attila bit permanently zero.
    """

    def views(self, campaigns: list[Age2CampaignData] = None) -> list[tuple]:
        """(roster, decode, encode, bit) for both kinds, in a full seed and a Joan-only one."""
        shapes = ([campaigns] if campaigns is not None
                  else [list(Age2CampaignData), [Age2CampaignData.JOAN]])
        views = []
        for shape in shapes:
            storage = DataStorage(shape)
            views.append((storage.mercenaries, storage.used_mercenaries,
                          storage.mercenary_field, storage.mercenary_bit))
            views.append((storage.scenarios, storage.completed_scenarios,
                          storage.scenario_field, storage.scenario_bit))
        return views

    def test_a_single_campaign_packs_from_the_rightmost_bit(self) -> None:
        for campaign in Age2CampaignData:
            for roster, _decode, _encode, bit in self.views([campaign]):
                bits = sorted(bit(member) for member in roster)
                self.assertEqual(list(range(len(roster))), bits,
                                 f"{campaign.campaign_name} alone left gaps in the bitfield")

    def test_nothing_is_set_in_a_fresh_seed(self) -> None:
        for _roster, decode, _encode, _bit in self.views():
            self.assertEqual(set(), decode(0),
                             "a key that was never written must decode as nothing set")

    def test_the_field_round_trips(self) -> None:
        for roster, decode, encode, _bit in self.views():
            for member in roster:
                self.assertEqual({member}, decode(encode({member})),
                                 f"{member} did not survive the bitfield round trip")

    def test_setting_one_leaves_the_others_alone(self) -> None:
        for roster, decode, encode, _bit in self.views():
            every = set(roster)
            for member in roster:
                rest = every - {member}
                self.assertEqual(rest, decode(encode(rest)),
                                 f"setting everything but {member} disturbed the rest")

    def test_bits_past_the_roster_are_ignored(self) -> None:
        for roster, decode, _encode, _bit in self.views():
            self.assertEqual(set(), decode(1 << len(roster)),
                             "a bit from a newer apworld must not decode as an existing member")

    def test_asking_for_a_bit_outside_the_seed_raises(self) -> None:
        """Rather than returning something shiftable. A caller that wants to tolerate this has to
        check membership first; it cannot be caught after the shift."""
        joan_only = DataStorage([Age2CampaignData.JOAN])
        attila = DataStorage([Age2CampaignData.ATTILA])
        for item in attila.mercenaries:
            with self.assertRaises(ValueError,
                                   msg=f"{item.item_name} is not in a Joan-only seed"):
                joan_only.mercenary_bit(item)
        for scenario in attila.scenarios:
            with self.assertRaises(ValueError,
                                   msg=f"{scenario.scenario_name} is not in a Joan-only seed"):
                joan_only.scenario_bit(scenario)


class TestRosterStability(unittest.TestCase):
    """The rosters are sorted by id, so a stored bitfield only keeps its meaning while ids do.
    Mercenary ids must be append-only. Scenario ids are computed as campaign.value * 100 + chapter,
    so campaign values must be append-only and a shipped campaign's chapter count must never change:
    inserting a chapter shifts every later campaign's index and silently re-points stored bits.
    """

    def test_a_higher_id_mercenary_appends_and_shifts_nothing(self) -> None:
        storage = DataStorage(list(Age2CampaignData))
        roster = storage.mercenaries
        highest = max(item.id for item in roster)
        for index, item in enumerate(roster):
            self.assertLess(item.id, highest + 1)
            self.assertEqual(index, storage.mercenary_bit(item))
        self.assertEqual(sorted(roster, key=lambda item: item.id), roster,
                         "the roster is not in id order, so append-only ids would not protect it")

    def test_scenario_ids_stay_campaign_major(self) -> None:
        roster = DataStorage(list(Age2CampaignData)).scenarios
        for earlier, later in zip(roster, roster[1:]):
            if earlier.campaign == later.campaign:
                self.assertLess(earlier.chapter, later.chapter,
                                "chapters within a campaign are out of order")
            else:
                self.assertLess(earlier.campaign.value, later.campaign.value,
                                "campaigns are out of order, so campaign values are not append-only")

    def test_shipped_campaigns_have_the_chapter_counts_the_bits_assume(self) -> None:
        expected = {Age2CampaignData.ATTILA: 6, Age2CampaignData.JOAN: 6}
        for campaign, chapters in expected.items():
            self.assertEqual(chapters, len(CAMPAIGN_TO_SCENARIOS[campaign]),
                             f"{campaign.campaign_name} changed chapter count; every later "
                             "campaign's bit has shifted and stored completions now decode wrong")


class TestMercenaryUnits(unittest.TestCase):

    def test_every_mercenary_delivers_at_least_one_unit(self) -> None:
        for item in Items.CATEGORY_TO_ITEMS[Items.Mercenary]:
            self.assertTrue(item.type.units,
                            f"{item.item_name} has no units, so researching its seat would spawn "
                            "nothing and the seat would never clear")

    def test_unit_counts_are_positive(self) -> None:
        for item in Items.CATEGORY_TO_ITEMS[Items.Mercenary]:
            for unit in item.type.units:
                self.assertGreater(unit.count, 0,
                                   f"{item.item_name} asks for {unit.count} {unit.unit.unit_name}; "
                                   "the count is also the seat's research time in seconds")


if __name__ == "__main__":
    unittest.main()
