import unittest

from test.general import setup_solo_multiworld

from .. import Age2World
from ..Options import ExistingTechs, ShuffleUniqueTechs, Techsanity
from ..generation import TechData
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData, BuildingOption
from ..locations.Techs import Age2TechData, TechOption
from ..logic.goal_logic import CAMPAIGN_TO_SCENARIOS
from ..locations.connections import LocationMapping


class TechPoolTestBase(unittest.TestCase):
    def pool(self, **options) -> list[Age2TechData]:
        # create_regions appends to class level lists, so start each case clean.
        for attr, empty in (("included_civs", []), ("included_campaigns", set()),
                            ("shuffled_buildings", []), ("shuffled_techs", [])):
            setattr(Age2World, attr, empty)
        world = setup_solo_multiworld(Age2World, steps=("generate_early",)).worlds[1]
        for name, value in options.items():
            getattr(world.options, name).value = value
        world.create_regions()
        self.world = world
        return world.tech_pool()


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
        self.assertTrue(set(pool) <= set(TechData.researchable(self.world.included_civs)))


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

    def test_no_region_is_made_for_a_building_with_no_techs(self):
        self.pool(techsanity=Techsanity.option_units)
        homes = {tech.buildings[0].item.item_name for tech in self.world.shuffled_techs}
        names = {region.name for region in self.world.multiworld.get_regions(1)}
        for building in Age2BuildingData:
            if building.item.item_name not in homes:
                self.assertNotIn(building.item.item_name, names, building.name)


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
        table = TechData.rows(pool, civs=self.world.included_civs)
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
        self.assertIn(Age2TechData.LOOM, self.joan(ExistingTechs.option_lock_technologies))

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
                  existing_techs=ExistingTechs.option_only_lock_units,
                  enabled_campaigns={"Joan of Arc"})
        self.assertTrue(self.world.is_researchable_somewhere(upgrade, above), upgrade.name)
        self.assertFalse(self.world.is_researchable_somewhere(generic, above), generic.name)
