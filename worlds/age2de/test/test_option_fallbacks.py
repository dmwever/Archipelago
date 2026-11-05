import logging
import unittest

from test.general import setup_solo_multiworld

from .. import Age2World
from ..Options import Caveman, ExistingTechs, Techsanity, Unitsanity

ATTILA = "Attila the Hun"

class OptionFallbackTestBase(unittest.TestCase):

    def world_with(self, **options: int) -> Age2World:
        world = setup_solo_multiworld(Age2World, ()).worlds[1]
        world.options.enabled_campaigns.value = {ATTILA}
        world.options.starting_campaigns.value = {ATTILA}
        for name, value in options.items():
            getattr(world.options, name).value = value
        return world

    def generate_and_catch_warnings(self, **options: int) -> tuple[Age2World, str]:
        world = self.world_with(**options)
        with self.assertLogs("worlds.age2de", level=logging.WARNING) as caught:
            world.generate_early()
        return world, "\n".join(caught.output)

    def generate_without_warnings(self, **options: int) -> Age2World:
        world = self.world_with(**options)
        with self.assertNoLogs("worlds.age2de", level=logging.WARNING):
            world.generate_early()
        return world

class TestCavemanFallback(OptionFallbackTestBase):

    def test_caveman_without_unitsanity_is_turned_off_with_a_warning(self) -> None:
        world, warnings = self.generate_and_catch_warnings(
            caveman=Caveman.option_true,
            unitsanity=Unitsanity.option_none,
            techsanity=Techsanity.option_units,
            existing_techs=ExistingTechs.option_vanilla,
        )
        self.assertFalse(world.options.caveman.value)
        self.assertIn(world.player_name, warnings)
        self.assertIn(Caveman.display_name, warnings)
        self.assertIn(Unitsanity.display_name, warnings)

    def test_caveman_without_upgrade_techsanity_is_turned_off_with_a_warning(self) -> None:
        for techsanity in (Techsanity.option_none, Techsanity.option_generic):
            with self.subTest(techsanity=techsanity):
                world, warnings = self.generate_and_catch_warnings(
                    caveman=Caveman.option_true,
                    unitsanity=Unitsanity.option_unit_line,
                    techsanity=techsanity,
                    existing_techs=ExistingTechs.option_vanilla,
                )
                self.assertFalse(world.options.caveman.value)
                self.assertIn(world.player_name, warnings)
                self.assertIn(Caveman.display_name, warnings)
                self.assertIn(Techsanity.display_name, warnings)

    def test_caveman_with_unitsanity_and_upgrade_techsanity_stays_on(self) -> None:
        for techsanity in (Techsanity.option_units, Techsanity.option_all):
            with self.subTest(techsanity=techsanity):
                world = self.generate_without_warnings(
                    caveman=Caveman.option_true,
                    unitsanity=Unitsanity.option_unit_line,
                    techsanity=techsanity,
                    existing_techs=ExistingTechs.option_vanilla,
                )
                self.assertTrue(world.options.caveman.value)

class TestExistingTechsFallback(OptionFallbackTestBase):

    def test_existing_techs_without_techsanity_falls_back_to_vanilla_with_a_warning(self) -> None:
        for existing_techs in (
            ExistingTechs.option_find_items,
            ExistingTechs.option_only_find_units,
            ExistingTechs.option_start_in_dark_age,
        ):
            with self.subTest(existing_techs=existing_techs):
                world, warnings = self.generate_and_catch_warnings(
                    techsanity=Techsanity.option_none,
                    existing_techs=existing_techs,
                )
                self.assertEqual(ExistingTechs.option_vanilla, world.options.existing_techs.value)
                self.assertIn(world.player_name, warnings)
                self.assertIn(ExistingTechs.display_name, warnings)
                self.assertIn(Techsanity.display_name, warnings)

    def test_only_find_units_with_generic_techsanity_falls_back_to_vanilla(self) -> None:
        world, warnings = self.generate_and_catch_warnings(
            techsanity=Techsanity.option_generic,
            existing_techs=ExistingTechs.option_only_find_units,
        )
        self.assertEqual(ExistingTechs.option_vanilla, world.options.existing_techs.value)
        self.assertIn(ExistingTechs.display_name, warnings)

    def test_only_find_units_with_units_techsanity_is_unchanged(self) -> None:
        world = self.generate_without_warnings(
            techsanity=Techsanity.option_units,
            existing_techs=ExistingTechs.option_only_find_units,
        )
        self.assertEqual(ExistingTechs.option_only_find_units, world.options.existing_techs.value)

    def test_find_items_with_generic_techsanity_is_unchanged(self) -> None:
        world = self.generate_without_warnings(
            techsanity=Techsanity.option_generic,
            existing_techs=ExistingTechs.option_find_items,
        )
        self.assertEqual(ExistingTechs.option_find_items, world.options.existing_techs.value)

class TestSlotDataAfterFallback(OptionFallbackTestBase):

    def test_slot_data_carries_the_values_after_fallback(self) -> None:
        world, _ = self.generate_and_catch_warnings(
            caveman=Caveman.option_true,
            unitsanity=Unitsanity.option_unit_line,
            techsanity=Techsanity.option_none,
            existing_techs=ExistingTechs.option_start_in_dark_age,
        )
        slot_data = world.fill_slot_data()
        self.assertEqual(0, slot_data[Caveman.internal_name])
        self.assertEqual(ExistingTechs.option_vanilla, slot_data[ExistingTechs.internal_name])
