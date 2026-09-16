import unittest

from BaseClasses import CollectionState
from test.general import setup_solo_multiworld

from .. import Age2World
from ..Options import ExistingTechs, ShuffleUniqueTechs, Techsanity
from ..client.handlers.install.TechData import TechData
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData, BuildingOption
from ..locations.Civilizations import Age2CivData
from ..generation.TechPool import TechPool
from ..locations.Techs import Age2TechData, BUILDING_TO_TECHS, TechOption
from ..locations.connections.CivilizationTechs import CIV_TO_TECHS
from ..logic.goal_logic import CAMPAIGN_TO_SCENARIOS
from ..locations.connections import LocationMapping


class TechPoolTestBase(unittest.TestCase):
    def pool(self, **options) -> list[Age2TechData]:
        world = setup_solo_multiworld(Age2World, steps=("generate_early",)).worlds[1]
        for name, value in options.items():
            getattr(world.options, name).value = value
        world.create_regions()
        self.world = world
        return world.shuffled_techs


class TestTechPool(TechPoolTestBase):
    def test_techsanity_off_makes_no_locations(self):
        self.assertEqual(self.pool(techsanity=Techsanity.option_none), [])

    def test_units_and_generic_split_all_between_them(self):
        units = self.pool(techsanity=Techsanity.option_units)
        generic = self.pool(techsanity=Techsanity.option_generic)
        every = self.pool(techsanity=Techsanity.option_all)
        self.assertEqual(sorted(units + generic), sorted(every))
        self.assertFalse(set(units) & set(generic))

    def test_uniques_join_only_when_shuffled(self):
        unshuffled = self.pool(techsanity=Techsanity.option_all,
                               shuffle_unique_techs=ShuffleUniqueTechs.option_unshuffled)
        self.assertFalse([t for t in unshuffled if TechOption.unique in t.tech_options])
        shuffled = self.pool(techsanity=Techsanity.option_all,
                             shuffle_unique_techs=ShuffleUniqueTechs.option_shuffled)
        self.assertTrue([t for t in shuffled if TechOption.unique in t.tech_options])
        self.assertEqual(set(unshuffled) - set(shuffled), set())

    def test_no_civilization_gets_a_tech_it_cannot_research(self):
        pool = self.pool(techsanity=Techsanity.option_all,
                         shuffle_unique_techs=ShuffleUniqueTechs.option_shuffled)
        self.assertTrue(pool)
        self.assertTrue(set(pool) <= {tech for civ in self.world.included_civs
                                     for tech in CIV_TO_TECHS[civ]})


class TestResearchRegions(TechPoolTestBase):
    def test_a_tech_lives_in_the_region_of_the_building_that_researches_it(self):
        pool = self.pool(techsanity=Techsanity.option_all,
                         shuffle_unique_techs=ShuffleUniqueTechs.option_shuffled)
        for tech in pool:
            region = self.world.multiworld.get_region(tech.buildings[0].item.item_name, 1)
            self.assertIn(tech.location_name, [l.name for l in region.locations], tech.name)

    def test_every_pooled_tech_got_a_location_and_nothing_else_did(self):
        pool = self.pool(techsanity=Techsanity.option_all)
        placed = [location.name
                  for region in self.world.multiworld.get_regions(1)
                  for location in region.locations
                  if location.name.startswith("Research ")]
        self.assertEqual(sorted(placed), sorted(tech.location_name for tech in pool))

    def test_the_region_set_does_not_depend_on_the_mode(self):
        # A building that researches something gets a region whatever Techsanity
        # says, so Unitsanity can hang units off the same regions later; one that
        # researches nothing of its own gets none.
        researches = {building for building in Age2BuildingData
                      if any(tech.buildings[0] is building
                             for tech in BUILDING_TO_TECHS[building])}
        for mode in (Techsanity.option_none, Techsanity.option_units,
                     Techsanity.option_all):
            with self.subTest(mode=mode):
                self.pool(techsanity=mode)
                names = {region.name for region in self.world.multiworld.get_regions(1)}
                for building in Age2BuildingData:
                    self.assertEqual(building.item.item_name in names,
                                     building in researches, building.name)

    def test_a_tech_is_placed_only_under_the_building_it_names_first(self):
        # A tech researched at a unique replacement is listed under both buildings,
        # so placing it per building would give it two locations.
        self.pool(techsanity=Techsanity.option_all)
        placed = [location.name
                  for region in self.world.multiworld.get_regions(1)
                  for location in region.locations
                  if location.name.startswith("Research ")]
        self.assertEqual(len(placed), len(set(placed)))
        for tech in self.world.shuffled_techs:
            region = self.world.multiworld.get_region(tech.buildings[0].item.item_name, 1)
            self.assertIn(tech.location_name, [l.name for l in region.locations], tech.name)


class TestReplacementEntrances(TechPoolTestBase):
    """A civilization that builds a Settlement instead of a Mill still researches
    the Mill technologies, so the Mill region earns a second entrance. The location
    itself cannot move or be duplicated -- Archipelago allows one location of a
    given name per player, in exactly one region."""

    def setUp(self):
        self.was = Age2CivData.FRANKS.included_buildings
        Age2CivData.FRANKS.included_buildings = self.was + [Age2BuildingData.SETTLEMENT]
        self.addCleanup(setattr, Age2CivData.FRANKS, "included_buildings", self.was)

    def test_the_replacement_earns_the_standard_region_an_entrance(self):
        self.pool(techsanity=Techsanity.option_all,
                  enabled_campaigns={"Attila the Hun", "Joan of Arc"})
        mill = self.world.multiworld.get_region("Mill", 1)
        self.assertIn("Settlement to Mill Techs", [e.name for e in mill.entrances])

    def test_the_technology_stays_in_the_standard_region(self):
        self.pool(techsanity=Techsanity.option_all,
                  enabled_campaigns={"Attila the Hun", "Joan of Arc"})
        mw = self.world.multiworld
        self.assertEqual(mw.get_location("Research Horse Collar", 1).parent_region.name,
                         "Mill")
        # The replacement gets its own region for logic, but holds no location --
        # no technology names it first.
        self.assertEqual(len(mw.get_region("Settlement", 1).locations), 0)

    def test_the_cross_entrance_is_free_and_the_building_entrances_carry_the_rule(self):
        # Plan 3 will gate Can Build -> Mill on the Mill and Can Build -> Settlement
        # on the Settlement; the Settlement -> Mill edge stays free, which is what
        # makes reaching the Mill technologies a disjunction.
        self.pool(techsanity=Techsanity.option_all,
                  enabled_campaigns={"Attila the Hun", "Joan of Arc"})
        mw = self.world.multiworld
        mill = mw.get_region("Mill", 1)
        cross = next(e for e in mill.entrances if e.name == "Settlement to Mill Techs")
        self.assertIs(cross.parent_region, mw.get_region("Settlement", 1))
        self.assertTrue(cross.access_rule(CollectionState(mw)))

        mill_entrance = next(e for e in mill.entrances if e.name == "Mill")
        settlement_entrance = mw.get_region("Settlement", 1).entrances[0]
        for has_mill, has_settlement in ((False, False), (True, False),
                                         (False, True), (True, True)):
            with self.subTest(mill=has_mill, settlement=has_settlement):
                mill_entrance.access_rule = lambda state, v=has_mill: v
                settlement_entrance.access_rule = lambda state, v=has_settlement: v
                state = CollectionState(mw)
                self.assertEqual(state.can_reach(mill), has_mill or has_settlement)

    def test_nothing_is_added_when_no_civilization_has_the_replacement(self):
        Age2CivData.FRANKS.included_buildings = self.was
        self.pool(techsanity=Techsanity.option_all,
                  enabled_campaigns={"Attila the Hun", "Joan of Arc"})
        extra = [e.name for e in self.world.multiworld.get_region("Can Build", 1).exits
                 if " to " in e.name]
        self.assertEqual(extra, [])


class TestResearchBuildings(unittest.TestCase):
    def test_every_tech_names_one_standard_building_first(self):
        for tech in Age2TechData:
            self.assertTrue(tech.buildings, tech.name)
            primary = tech.buildings[0]
            self.assertNotIn(BuildingOption.unique, primary.building_options, tech.name)

    def test_any_further_buildings_are_unique_replacements(self):
        # Option 2: the location sits in the standard building's region, and the
        # rule will widen to these later, when such a civilization ships.
        for tech in Age2TechData:
            for alternate in tech.buildings[1:]:
                self.assertIn(BuildingOption.unique, alternate.building_options, tech.name)


class TestPoolMatchesTheInstall(TechPoolTestBase):
    def test_install_accepts_exactly_what_the_server_offers(self):
        # rows() refuses a location no civ can research, so this pins the server
        # and TechData.xs to the same idea of what a tech location is.
        pool = self.pool(techsanity=Techsanity.option_all,
                         shuffle_unique_techs=ShuffleUniqueTechs.option_shuffled)
        table = TechData(pool, civs=self.world.included_civs).rows()
        self.assertEqual([row.tech for row in table if row.is_location], sorted(pool))


class TestLocationRegistry(unittest.TestCase):
    def test_every_tech_is_a_known_location(self):
        for tech in Age2TechData:
            self.assertEqual(LocationMapping.location_name_to_id[tech.location_name], tech.id)
            self.assertEqual(LocationMapping.location_id_to_name[tech.id], tech.location_name)

    def test_no_location_name_is_claimed_twice(self):
        self.assertEqual(len(LocationMapping.location_name_list),
                         len(set(LocationMapping.location_name_list)))


class TestScenarioReachability(TechPoolTestBase):
    """A scenario auto-researches everything below the age it starts in, so such
    a technology is granted on load and never becomes a location the game can
    check. Joan has no Dark Age scenario, so a Joan-only seed must not offer a
    Dark Age technology as a location unless the scenarios are rebased."""

    def joan(self, existing) -> set:
        return set(self.pool(techsanity=Techsanity.option_all,
                             existing_techs=existing,
                             enabled_campaigns={"Joan of Arc"}))

    def test_joan_alone_cannot_reach_a_dark_age_tech(self):
        self.assertNotIn(Age2TechData.LOOM, self.joan(ExistingTechs.option_vanilla))

    def test_rebasing_puts_it_back(self):
        self.assertIn(Age2TechData.LOOM, self.joan(ExistingTechs.option_find_items))

    def test_attila_keeps_it_because_attila_1_starts_in_the_dark_age(self):
        pool = self.pool(techsanity=Techsanity.option_all,
                         enabled_campaigns={"Attila the Hun"})
        self.assertIn(Age2TechData.LOOM, pool)

    def test_every_pooled_tech_is_reachable_in_some_scenario(self):
        for campaigns in ({"Attila the Hun"}, {"Joan of Arc"},
                          {"Attila the Hun", "Joan of Arc"}):
            with self.subTest(campaigns=sorted(campaigns)):
                pool = self.pool(techsanity=Techsanity.option_all,
                                 enabled_campaigns=set(campaigns))
                starts = [scenario.vanilla_age
                          for campaign in self.world.included_campaigns
                          for scenario in CAMPAIGN_TO_SCENARIOS[campaign]]
                for tech in pool:
                    self.assertTrue(any(start <= tech.age for start in starts), tech.name)

    def test_only_lock_units_keeps_an_upgrade_below_every_start(self):
        upgrade = next(t for t in Age2TechData if TechOption.units in t.tech_options)
        generic = Age2TechData.LOOM
        above = Age2AgeData.IMPERIAL
        self.pool(techsanity=Techsanity.option_all,
                  existing_techs=ExistingTechs.option_only_find_units,
                  enabled_campaigns={"Joan of Arc"})
        pool = TechPool(self.world.options, above, self.world.included_civs)
        self.assertTrue(pool.reachable(upgrade), upgrade.name)
        self.assertFalse(pool.reachable(generic), generic.name)
