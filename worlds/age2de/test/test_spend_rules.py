"""Two rules decide when an entry in the spent record is paid for, and an entry obeys one.

A resource or a trap is spent the moment the game takes delivery, because taking it is the payout.
A mercenary is spent when the pavilion says it has finished spawning, which is a later and separate
event -- delivery only puts it in a seat. Both write the same mask, so an item that answered to
both rules would be paid for twice, and one that answered to neither would be replayable forever.
"""

import unittest

from ..items import Items
from ..items.Items import Age2ItemData


class TestTheTwoWaysToSpend(unittest.TestCase):
    def test_no_entry_answers_to_both_rules(self) -> None:
        self.assertEqual(frozenset(), Items.ONE_SHOT_ITEMS & Items.SPENT_ON_USE_ITEMS,
                         "an item spent on delivery and again on use is paid for twice")

    def test_every_mercenary_is_spent_on_use(self) -> None:
        self.assertEqual(frozenset(Items.CATEGORY_TO_ITEMS[Items.Mercenary]),
                         Items.SPENT_ON_USE_ITEMS)

    def test_a_mercenary_is_never_spent_on_delivery(self) -> None:
        """Delivery seats one. Marking it spent there would read as Used before it was offered."""
        for mercenary in Items.CATEGORY_TO_ITEMS[Items.Mercenary]:
            self.assertNotIn(mercenary, Items.ONE_SHOT_ITEMS, mercenary.item_name)

    def test_what_is_spent_at_all_is_only_these(self) -> None:
        """Everything else is replayable: the game can be handed it again with no harm."""
        spendable = Items.ONE_SHOT_ITEMS | Items.SPENT_ON_USE_ITEMS
        replayable = [item for item in Age2ItemData if item not in spendable]
        self.assertNotIn(Age2ItemData.TRAP_WOLOLO, replayable)
        self.assertIn(Age2ItemData.FISH_TRAP, replayable)


if __name__ == "__main__":
    unittest.main()
