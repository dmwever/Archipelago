import unittest

from test.general import setup_solo_multiworld

from .. import Age2World
from ..Options import IncludeUniqueUnits, ShuffleVillager, Unitsanity, UnitsanityItems
from ..items.Items import (Age2ItemData, UnitBuilding, UnitLine, UnitUpgrade,
                           NAME_TO_ITEM)
from ..locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.Units import Age2UnitData, UnitType
from ..locations.VillagerJobs import Age2VillagerJobData, VillagerSex
from ..locations.connections.CivilizationUnits import CIV_TO_UNITS
from ..regions.UnitRegions import UnitEntranceKind, UnitRegion


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

    def build_with_rules(self, **options) -> Age2World:
        world = self.build(**options)
        world.set_rules()
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
        named = {unit.location_name for unit in Age2UnitData}             | {hero.location_name for hero in Age2HeroData}             | {escort.location_name for escort in Age2EscortUnitData}
        self.assertTrue(self.own_locations(every))
        self.assertTrue(set(self.own_locations(every)) <= named)

    def test_all_replaces_line_locations_rather_than_adding_to_them(self):
        world = self.build(unitsanity=Unitsanity.option_all)
        placed = set(self.own_locations(world))
        self.assertFalse(placed & {line.location_name for line in Age2UnitLineData})

    def test_shuffle_villager_owns_the_villager_and_unitsanity_never_touches_it(self):
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        self.assertNotIn(Age2UnitData.VILLAGER_MALE, world.unit_regions.shuffled_units)
        self.assertNotIn(Age2UnitLineData.VILLAGER_LINE.location_name,
                         self.own_locations(world))
        self.assertFalse(world.unit_regions.shuffled_villager)

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
            return {unit.unit_type for unit in world.unit_regions.shuffled_units}

        self.assertFalse(kinds(IncludeUniqueUnits.option_none)
                         & {UnitType.unique_unit, UnitType.regional_unit})
        self.assertIn(UnitType.unique_unit, kinds(IncludeUniqueUnits.option_unique))
        self.assertNotIn(UnitType.regional_unit, kinds(IncludeUniqueUnits.option_unique))
        self.assertIn(UnitType.regional_unit, kinds(IncludeUniqueUnits.option_regional))
        self.assertNotIn(UnitType.unique_unit, kinds(IncludeUniqueUnits.option_regional))
        self.assertTrue({UnitType.unique_unit, UnitType.regional_unit}
                        <= kinds(IncludeUniqueUnits.option_both))

    def test_every_unit_is_either_trainable_or_handed_over(self):
        """A unit no civilization trains earns a check only when a scenario grants one - the
        Mangudai an Attila 1 mercenary muster spawns eighteen of."""
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        self.assertTrue(world.unit_regions.shuffled_units)
        trainable = {unit for civ in world.included_civs for unit in CIV_TO_UNITS[civ]}
        granted = {grant for scenario in world.included_scenarios
                   for grant in scenario.startup_units + scenario.trigger_units}
        self.assertTrue(set(world.unit_regions.shuffled_units) <= trainable | granted)
        self.assertIn(Age2UnitData.MANGUDAI, world.unit_regions.shuffled_units)
        self.assertNotIn(Age2UnitData.MANGUDAI, trainable)

    def test_a_handed_over_unit_is_no_check_under_unit_line(self):
        world = self.build(unitsanity=Unitsanity.option_unit_line,
                           include_unique_units=IncludeUniqueUnits.option_both)
        self.assertNotIn(Age2UnitLineData.MANGUDAI_LINE.location_name,
                         self.own_locations(world))


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
    """A unit line is a region and each way of coming by one is an entrance."""

    def entrances(self, world: Age2World, kind: str) -> list[tuple]:
        """(via, target) for every entrance of one kind, across the unit regions."""
        return [(entrance.via, region.target)
                for region in world.unit_regions.regions
                for entrance in region.entrances if entrance.kind == kind]

    def test_a_unit_lives_in_its_line_region_not_its_buildings(self):
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        for unit in world.unit_regions.shuffled_units:
            region = world.multiworld.get_region(unit.line.line_name, 1)
            self.assertIn(unit.location_name,
                          [location.name for location in region.locations], unit.name)
        barracks = world.multiworld.get_region(
            Age2BuildingData.BARRACKS.item.item_name, 1)
        self.assertFalse([location for location in barracks.locations
                          if location.name.startswith("Own ")])

    def test_every_line_region_has_a_way_in_that_is_not_conversion(self):
        """A region reachable only by conversion would strand every check inside it."""
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both,
                           shuffle_villager=ShuffleVillager.option_include_professions)
        real = {region.target for region in world.unit_regions.regions
                for entrance in region.entrances if entrance.kind != UnitEntranceKind.conversion}
        for line in world.unit_pool.line_locations:
            if not world.multiworld.get_region(line.line_name, 1).locations:
                continue
            self.assertIn(line, real, line.name)

    def test_conversion_is_closed_everywhere(self):
        world = self.build_with_rules(unitsanity=Unitsanity.option_all)
        conversions = [entrance for region in world.unit_regions.regions
                       for entrance in region.entrances
                       if entrance.kind == UnitEntranceKind.conversion]
        self.assertTrue(conversions)
        state = world.multiworld.get_all_state(False)
        for entrance in conversions:
            self.assertFalse(state.can_reach_entrance(entrance.name, 1), entrance.name)

    def test_a_handed_over_line_needs_no_building_to_train_it(self):
        """Attila 2 opens with twelve Tarkans, so the line is reachable without a Stable."""
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        startup = set(self.entrances(world, UnitEntranceKind.startup))
        self.assertIn((Age2ScenarioData.AP_ATTILA_2, Age2UnitLineData.TARKAN_LINE), startup)
        self.assertIn((Age2ScenarioData.AP_ATTILA_2, Age2UnitLineData.CAVALRY_ARCHER_LINE),
                      startup)

    def test_a_handed_over_line_gets_no_training_entrance(self):
        """No Hun trains a Mangudai, however many a mercenary muster spawns."""
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        trained = {target for _via, target in self.entrances(world, UnitEntranceKind.train)}
        self.assertNotIn(Age2UnitLineData.MANGUDAI_LINE, trained)
        self.assertIn(Age2UnitLineData.TARKAN_LINE, trained)

    def test_villager_locations_live_in_the_villager_line_region(self):
        """The female villager lists no producing building, so every villager location has to
        take its placement from the male - otherwise half of them would be dropped."""
        world = self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        self.assertEqual(Age2UnitData.VILLAGER_FEMALE.buildings, [])
        region = world.multiworld.get_region(Age2UnitLineData.VILLAGER_LINE.line_name, 1)
        placed = [location.name for location in region.locations]
        self.assertEqual(len(placed), 26)
        for job in Age2VillagerJobData:
            self.assertIn(job.location_name, placed, job.name)
        self.assertIn(Age2UnitData.VILLAGER_FEMALE.location_name, placed)
        trained = {target for _via, target in self.entrances(world, UnitEntranceKind.train)}
        self.assertIn(Age2UnitLineData.VILLAGER_LINE, trained)


class TestEscorts(UnitPoolTestBase):
    """Joan 6's cart is class 59 - the King class, which holds escort objectives beside named
    kings and heroes. Nothing trains one, but a scenario hands it to you."""

    def test_the_cart_is_a_check_a_scenario_alone_supplies(self):
        world = self.build(unitsanity=Unitsanity.option_all)
        self.assertIn(Age2EscortUnitData.CART.location_name, self.own_locations(world))
        ways_in = {(entrance.kind, entrance.via)
                   for region in world.unit_regions.regions
                   if region.target is Age2EscortUnitData.CART
                   for entrance in region.entrances}
        self.assertEqual(ways_in, {(UnitEntranceKind.startup, Age2ScenarioData.AP_JOAN_6)})

    def test_an_escort_is_a_check_under_all_only(self):
        self.assertFalse(self.build(unitsanity=Unitsanity.option_unit_line).unit_pool.escorts)
        self.assertEqual(self.build(unitsanity=Unitsanity.option_all).unit_pool.escorts,
                         list(Age2EscortUnitData))

    def test_an_escort_is_not_a_unit_and_never_an_item(self):
        """Its own enum, so no Age2UnitData invariant has to carve an exception for it - no
        line, no upgrade token, no producing building, and nothing unlocks one."""
        self.assertNotIn("CART", Age2UnitData.__members__)
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        names = {item.name for item in world.multiworld.itempool}
        for escort in Age2EscortUnitData:
            self.assertNotIn(escort.escort_name, names, escort.name)

    def test_an_untrainable_line_gets_no_unlock_item(self):
        """The Mangudai has an item, since the Mongols train one, but no seed of these two
        civilizations should pool it - there is no building here to unlock it at."""
        world = self.build(unitsanity=Unitsanity.option_all,
                           unitsanity_items=UnitsanityItems.option_unit_line,
                           include_unique_units=IncludeUniqueUnits.option_both)
        names = {item.item_name for item in self.unit_items(world)}
        self.assertNotIn("Mangudai Line", names)
        self.assertIn("Tarkan Line", names)


class TestHeroes(UnitPoolTestBase):
    def test_heroes_are_checks_under_all_only(self):
        self.assertFalse(self.build(unitsanity=Unitsanity.option_unit_line).unit_pool.heroes)
        self.assertFalse(self.build(shuffle_villager=ShuffleVillager.option_yes)
                         .unit_pool.heroes)
        world = self.build(unitsanity=Unitsanity.option_all)
        self.assertEqual(len(world.unit_pool.heroes), len(list(Age2HeroData)))

    def test_a_hero_has_one_region_and_an_entrance_per_granting_scenario(self):
        world = self.build(unitsanity=Unitsanity.option_all)
        for hero in world.unit_pool.heroes:
            region = world.multiworld.get_region(hero.hero_name, 1)
            self.assertEqual([location.name for location in region.locations],
                             [hero.location_name])
            granting = {scenario for scenario in world.included_scenarios
                        if hero in scenario.startup_units + scenario.trigger_units}
            ways_in = {entrance.via for entrance in
                       world.multiworld.get_region(hero.hero_name, 1).entrances}
            self.assertEqual(ways_in, granting, hero.name)

    def test_attila_arrives_by_trigger_in_one_scenario_and_on_the_map_in_another(self):
        world = self.build(unitsanity=Unitsanity.option_all)
        kinds = {(entrance.kind, entrance.via) for region in world.unit_regions.regions
                 if region.target is Age2HeroData.ATTILA_THE_HUN
                 for entrance in region.entrances}
        self.assertIn((UnitEntranceKind.trigger, Age2ScenarioData.AP_ATTILA_1), kinds)
        self.assertIn((UnitEntranceKind.startup, Age2ScenarioData.AP_ATTILA_6), kinds)

    def test_no_hero_is_an_item(self):
        world = self.build(unitsanity=Unitsanity.option_all,
                           include_unique_units=IncludeUniqueUnits.option_both)
        names = {item.name for item in world.multiworld.itempool}
        for hero in Age2HeroData:
            self.assertNotIn(hero.hero_name, names, hero.name)

    def test_every_hero_location_is_reachable(self):
        """Bleda and Constable Richemont arrive only through a grant with no mercenary item
        behind it, so an unauthored grant has to be open rather than shut."""
        world = self.build_with_rules(unitsanity=Unitsanity.option_all)
        state = world.multiworld.get_all_state(False)
        for hero in world.unit_pool.heroes:
            self.assertTrue(state.can_reach_location(hero.location_name, 1), hero.name)
