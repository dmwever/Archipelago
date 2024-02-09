import unittest
from typing import List

from BaseClasses import MultiWorld, ItemClassification
from ... import StardewItem


def get_all_item_names(multiworld: MultiWorld) -> List[str]:
    return [item.name for item in multiworld.itempool]


def get_all_location_names(multiworld: MultiWorld) -> List[str]:
    return [location.name for location in multiworld.get_locations() if not location.event]


def assert_victory_exists(tester: unittest.TestCase, multiworld: MultiWorld):
    tester.assertIn(StardewItem("Victory", ItemClassification.progression, None, 1), multiworld.get_items())


def can_reach_victory(multiworld: MultiWorld) -> (bool, str):
    victory = multiworld.find_item("Victory", 1)
    can_win = victory.can_reach(multiworld.state)
    return can_win, victory.access_rule.explain(multiworld.state)


def assert_can_reach_victory(tester: unittest.TestCase, multiworld: MultiWorld):
    tester.assertTrue(*can_reach_victory(multiworld))


def assert_can_win(tester: unittest.TestCase, multiworld: MultiWorld):
    assert_victory_exists(tester, multiworld)
    assert_can_reach_victory(tester, multiworld)


def assert_same_number_items_locations(tester: unittest.TestCase, multiworld: MultiWorld):
    non_event_locations = [location for location in multiworld.get_locations() if not location.event]
    tester.assertEqual(len(multiworld.itempool), len(non_event_locations))


def assert_can_reach_everything(tester: unittest.TestCase, multiworld: MultiWorld):
    for location in multiworld.get_locations():
        can_reach = location.can_reach(multiworld.state)
        if hasattr(location.access_rule, "explain"):
            tester.assertTrue(can_reach, location.access_rule.explain(multiworld.state))
        else:
            tester.assertTrue(can_reach)


def basic_checks(tester: unittest.TestCase, multiworld: MultiWorld):
    assert_same_number_items_locations(tester, multiworld)
    non_event_items = [item for item in multiworld.get_items() if item.code]
    for item in non_event_items:
        multiworld.state.collect(item)
    assert_can_win(tester, multiworld)
    assert_can_reach_everything(tester, multiworld)


def basic_checks_with_subtests(tester: unittest.TestCase, multiworld: MultiWorld):
    with tester.subTest("same_number_items_locations"):
        assert_same_number_items_locations(tester, multiworld)
    non_event_items = [item for item in multiworld.get_items() if item.code]
    for item in non_event_items:
        multiworld.state.collect(item)
    with tester.subTest("can_win"):
        assert_can_win(tester, multiworld)
    with tester.subTest("can_reach_everything"):
        assert_can_reach_everything(tester, multiworld)
