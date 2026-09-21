"""The icon and string ids each mercenary declares are indices into the Ageipelago mod.

Nothing in the game validates them. A wrong icon id draws somebody else's picture, a wrong string
id shows the wrong name or nothing at all, and neither produces an error anywhere. These ids are
also written by hand on each mercenary, so the invariants they have to satisfy are pinned here
rather than left to whoever adds the next one.
"""

import unittest

from ..items.Items import CATEGORY_TO_ITEMS, Mercenary

# 312 is the highest tech icon the base game ships.
FIRST_ICON_ID = 313
# Clear of the base game's string ranges.
FIRST_STRING_ID = 990001
# xsEffectAmount takes its value as a float, and float32 holds integers exactly only to 2**24.
FLOAT_EXACT_LIMIT = 2 ** 24


class TestMercenaryAssets(unittest.TestCase):
    def setUp(self) -> None:
        self.mercenaries = sorted(CATEGORY_TO_ITEMS[Mercenary], key=lambda item: item.id)

    def test_icon_ids_are_contiguous_from_the_first_free_index(self) -> None:
        """The game loads tech icons as a dense array, so an index resolves only if every index
        below it exists. A gap makes every icon above it render blank."""
        expected = list(range(FIRST_ICON_ID, FIRST_ICON_ID + len(self.mercenaries)))
        self.assertEqual(expected, [item.type.icon_id for item in self.mercenaries])

    def test_string_ids_are_unique(self) -> None:
        ids = [item.type.name_string_id for item in self.mercenaries]
        self.assertEqual(len(set(ids)), len(ids), "two mercenaries share a name string")

    def test_string_ids_start_clear_of_the_base_game(self) -> None:
        self.assertTrue(all(item.type.name_string_id >= FIRST_STRING_ID
                            for item in self.mercenaries))

    def test_every_id_survives_a_float(self) -> None:
        """XS receives these through xsEffectAmount, which takes a float. An id past 2**24 would
        be rounded to a different one, silently."""
        for item in self.mercenaries:
            for id_ in (item.type.icon_id, item.type.name_string_id):
                self.assertLess(id_, FLOAT_EXACT_LIMIT, item.item_name)
                self.assertEqual(id_, int(float(id_)), item.item_name)

    def test_every_mercenary_has_units(self) -> None:
        """A seat's research time is its unit count, so a mercenary with none would offer a seat
        that never finishes."""
        for item in self.mercenaries:
            self.assertGreater(item.type.unit_count, 0, item.item_name)
            self.assertEqual(item.type.unit_count, len(item.type.unit_ids), item.item_name)


if __name__ == "__main__":
    unittest.main()
