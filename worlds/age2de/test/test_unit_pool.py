import unittest

from test.general import setup_solo_multiworld

from .. import Age2World
from ..Options import IncludeUniqueUnits, ShuffleVillager, Unitsanity, UnitsanityItems
from ..items.Items import (Age2ItemData, UnitBuilding, UnitLine, UnitUpgrade,
                           NAME_TO_ITEM)
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData, UnitType
from ..locations.VillagerJobs import Age2VillagerJobData, VillagerSex
from ..locations.connections.CivilizationUnits import CIV_TO_UNITS


class UnitPoolTestBase(unittest.TestCase):
    def build(self, **options) -> Age2World:
        # generate_early reads the campaign options, so it has to run after they are set.
        world = setup_solo_multiworld(Age2World, ()).worlds[1]
        world.options.enabled_campaigns.value = {"Attila the Hun", "Joan of Arc"}
        world.options.starting_campaigns.value = {"Attila the Hun"}
        for name, value in options.items():
            getattr(world.options, name).value = value
        world.generate_early()
        world.create_regions()
        world.create_items()
        self.world = world
        return world

    def own_locations(self, world: Age2World) -> list[str]:
        return [location.name for location in world.multiworld.get_locations(1)
                if location.name.startswith("Own ")]

    def unit_items(self, world: Age2World) -> list[Age2ItemData]:
        pooled = [NAME_TO_ITEM[item.name] for item in world.multiworld.itempool
                  if item.name in NAME_TO_ITEM]
        return [item for item in pooled
                if item.type_data in (UnitLine, UnitUpgrade, UnitBuilding)]


class TestUnitPool(UnitPoolTestBase):
    def test_unitsanity_off_makes_no_unit_locations(self):
        world = self.build()
        self.assertEqual(self.own_locations(world), [])
        self.assertEqual(self.unit_items(world), [])

    def test_unit_line_checks_lines_and_all_checks_units(self):
        lines = self.build(unitsanity=Unitsanity.option_unit_line)
        line_names = {line.location_name for line in Age2UnitLineData}
        self.assertTrue(self.own_locations(lines))
        self.assertTrue(set(self.own_locations(lines)) <= line_names)

        every = self.build(unitsanity=Unitsanity.option_all)
        unit_names = {unit.location_name for unit in Age2UnitData}
        self.assertTrue(self.own_locations(every))
        self.assertTrue(set(self.own_locations(every)) <= unit_names)

    def test_all_replaces_line_locations_rather_than_adding_to_them(self):
        world = self.build(unitsanity=Unitsanity.option_all)
        placed = set(self.own_locations(world))
        self.assertFalse(placed & {line.location_name for line in Age2UnitLineData})

    def test_shuffle_villager_owns_the_villager_and_unitsanity_never_touches_it(self):
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        self.assertNotIn(Age2UnitData.VILLAGER_MALE, world.shuffled_units)
        self.assertNotIn(Age2UnitLineData.VILLAGER_LINE.location_name,
                         self.own_locations(world))
        self.assertFalse(world.shuffled_villager)

    def test_yes_checks_the_line_and_professions_split_it_by_sex(self):
        plain = self.build(shuffle_villager=ShuffleVillager.option_yes)
        self.assertEqual(self.own_locations(plain),
                         [Age2UnitLineData.VILLAGER_LINE.location_name])

        jobs = self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        placed = set(self.own_locations(jobs))
        self.assertEqual(len(placed), 26)
        self.assertNotIn(Age2UnitLineData.VILLAGER_LINE.location_name, placed)
        self.assertIn(Age2UnitData.VILLAGER_MALE.location_name, placed)
        self.assertIn(Age2UnitData.VILLAGER_FEMALE.location_name, placed)
        self.assertTrue({job.location_name for job in Age2VillagerJobData} <= placed)

    def test_professions_are_evenly_split_between_the_sexes(self):
        for sex in (VillagerSex.male, VillagerSex.female):
            self.assertEqual(len([job for job in Age2VillagerJobData if job.sex == sex]), 12, sex)
        self.assertEqual(len({job.game_id for job in Age2VillagerJobData}), 24)

    def test_restricted_units_join_only_when_their_option_admits_them(self):
        def kinds(include: int) -> set[str]:
            world = self.build(unitsanity=Unitsanity.option_all, include_unique_units=include)
            return {unit.unit_type for unit in world.shuffled_units}

        self.assertFalse(kinds(IncludeUniqueUnits.option_none)
                         & {UnitType.unique_unit, UnitType.regional_unit})
        self.assertIn(UnitType.unique_unit, kinds(IncludeUniqueUnits.option_unique))
        self.assertNotIn(UnitType.regional_unit, kinds(IncludeUniqueUnits.option_unique))
        self.assertIn(UnitType.regional_unit, kinds(IncludeUniqueUnits.option_regional))
        self.assertNotIn(UnitType.unique_unit, kinds(IncludeUniqueUnits.option_regional))
        self.assertTrue({UnitType.unique_unit, UnitType.regional_unit}
                        <= kinds(IncludeUniqueUnits.option_both))

    def test_no_civilization_gets_a_unit_it_cannot_train(self):
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        self.assertTrue(world.shuffled_units)
        trainable = {unit for civ in world.included_civs for unit in CIV_TO_UNITS[civ]}
        self.assertTrue(set(world.shuffled_units) <= trainable)


class TestUnitItems(UnitPoolTestBase):
    def test_each_mode_hands_out_its_own_kind_of_item(self):
        for mode, payload in ((UnitsanityItems.option_unit_line, UnitLine),
                              (UnitsanityItems.option_upgrades, UnitUpgrade),
                              (UnitsanityItems.option_buildings, UnitBuilding)):
            world = self.build(unitsanity=Unitsanity.option_all, unitsanity_items=mode)
            items = self.unit_items(world)
            self.assertTrue(items, mode)
            self.assertEqual({item.type_data for item in items}, {payload}, mode)

    def test_the_villager_is_a_line_item_in_every_mode(self):
        for mode in (UnitsanityItems.option_unit_line, UnitsanityItems.option_upgrades,
                     UnitsanityItems.option_buildings):
            for villager in (ShuffleVillager.option_yes,
                             ShuffleVillager.option_include_professions):
                world = self.build(shuffle_villager=villager, unitsanity_items=mode)
                self.assertEqual([item.item_name for item in self.unit_items(world)],
                                 [Age2UnitLineData.VILLAGER_LINE.item.item_name],
                                 (mode, villager))

    def test_no_item_for_a_building_no_civilization_can_put_up(self):
        # The Donjon trains spearmen, but neither Huns nor Franks build one.
        world = self.build(unitsanity=Unitsanity.option_all,
                           unitsanity_items=UnitsanityItems.option_buildings,
                           include_unique_units=IncludeUniqueUnits.option_both)
        names = {item.item_name for item in self.unit_items(world)}
        self.assertIn("Barracks Units", names)
        self.assertNotIn("Donjon Units", names)
        self.assertNotIn("Krepost Units", names)

    def test_every_unit_item_is_paid_for_by_a_location(self):
        for options in (dict(unitsanity=Unitsanity.option_unit_line),
                        dict(unitsanity=Unitsanity.option_all),
                        dict(unitsanity=Unitsanity.option_all,
                             unitsanity_items=UnitsanityItems.option_upgrades),
                        dict(unitsanity=Unitsanity.option_all,
                             shuffle_villager=ShuffleVillager.option_include_professions)):
            world = self.build(**options)
            self.assertLessEqual(len(self.unit_items(world)),
                                 len(self.own_locations(world)), options)


class TestUnitRegions(UnitPoolTestBase):
    def test_a_unit_lives_in_the_region_of_the_building_that_trains_it(self):
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        for unit in world.shuffled_units:
            home = next(building for building in unit.buildings
                        if world.civ_can_build(building))
            region = world.multiworld.get_region(home.item.item_name, 1)
            self.assertIn(unit.location_name,
                          [location.name for location in region.locations], unit.name)

    def test_villager_jobs_live_where_villagers_are_trained(self):
        """The female villager lists no producing building, so every villager location has to
        take its placement from the male - otherwise half of them would be dropped."""
        world = self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        self.assertEqual(Age2UnitData.VILLAGER_FEMALE.buildings, [])
        region = world.multiworld.get_region(
            Age2UnitData.VILLAGER_MALE.buildings[0].item.item_name, 1)
        placed = [location.name for location in region.locations]
        for job in Age2VillagerJobData:
            self.assertIn(job.location_name, placed, job.name)
        self.assertIn(Age2UnitData.VILLAGER_FEMALE.location_name, placed)
