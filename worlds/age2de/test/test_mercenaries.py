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

from ..items import Items

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
