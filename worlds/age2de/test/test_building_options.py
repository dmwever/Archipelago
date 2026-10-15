"""shuffle_buildings keys: categories and building names, matched without case."""

import unittest

from Options import OptionError

from ..Options import ShuffleBuildings
from ..locations.Buildings import Age2BuildingData
from .bases import Age2TestBase


class TestShuffleBuildingsKeys(unittest.TestCase):

    def test_categories_and_building_names_both_validate(self) -> None:
        ShuffleBuildings.from_any(["Base", "Castle", "Market", "Watch Tower"]).verify_keys()

    def test_keys_validate_in_any_case(self) -> None:
        ShuffleBuildings.from_any(["economy", "ARCHERY RANGE", "fOlWaRk"]).verify_keys()

    def test_keys_are_stored_in_their_canonical_spelling(self) -> None:
        """The yaml is input only: the player's casing carries no meaning, so the value keeps the
        intent and nothing downstream has to fold case again."""
        option = ShuffleBuildings.from_any(["economy", "ARCHERY RANGE", "castle"])
        option.verify_keys()
        self.assertEqual({"Economy", "Archery Range", "Castle"}, option.value)

    def test_a_misspelled_building_is_rejected(self) -> None:
        with self.assertRaises(OptionError):
            ShuffleBuildings.from_any(["Fulwark"]).verify_keys()

    def test_only_the_categories_are_listed(self) -> None:
        """valid_keys is what the options page draws as checkboxes; building names stay off it."""
        self.assertEqual(
            {"Base", "Economy", "Tech", "Military", "Castle", "Defense", "Unique", "Wonder"},
            set(ShuffleBuildings.valid_keys),
        )

    def test_the_default_leaves_base_and_castle_unshuffled(self) -> None:
        self.assertEqual({"Economy", "Tech", "Military"}, ShuffleBuildings.default)


class TestCategoriesMixedWithNames(Age2TestBase):
    """A full generation with categories and names side by side."""

    options = {
        "enabled_campaigns": {"Attila the Hun", "Joan of Arc"},
        "starting_campaigns": {"Attila the Hun"},
        "shuffle_buildings": {"Base", "Castle", "Stable"},
    }

    def test_the_union_of_categories_and_names_is_shuffled(self) -> None:
        self.assertEqual(
            [
                Age2BuildingData.TOWN_CENTER,
                Age2BuildingData.HOUSE,
                Age2BuildingData.STABLE,
                Age2BuildingData.CASTLE,
            ],
            self.world.pool.buildings.shuffled,
        )
