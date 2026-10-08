"""The budget sample decides which priced locations a scenario may pay for out of its opening pile.

Logic used to let every priced location in once a scenario could pay for it alone, which put dozens
in at once and asked for a restart per location. The sample keeps that set small, so it has to be
the size it claims, and the same for the same seed or a spoiler would describe a different seed.
"""
from random import Random
import unittest

from test.general import setup_multiworld

from . import bases
from .. import Age2World
from ..generation.pools.BudgetPool import (BUILDINGS_DRAWN, SAMPLED_RESOURCES, TECHS_PER_RESOURCE,
                                           UNITS_PER_RESOURCE, VILLAGER,
                                           BudgetPool, is_cheap_building)
from ..locations.Buildings import Age2BuildingData
from ..locations.Campaigns import Age2CampaignData
from ..locations.UnitLocations import VILLAGER_LINES

ATTILA = Age2CampaignData.ATTILA.campaign_name
JOAN = Age2CampaignData.JOAN.campaign_name

HARD_OPTIONS = {
    "enabled_campaigns": {ATTILA, JOAN},
    "starting_campaigns": {ATTILA},
    "shuffle_buildings": {"Economy", "Tech", "Military"},
    "shuffle_ages": True,
    "techsanity": "all",
    "unitsanity": "all",
    "shuffle_villager": "include_professions",
}


class TestTheSampleIsTheSizeItClaims(bases.Age2TestBase):
    options = HARD_OPTIONS

    @property
    def budget(self) -> BudgetPool:
        return self.world.pool.budget

    def test_each_resource_gets_its_own_draw_of_techs(self) -> None:
        self.assertLessEqual(len(self.budget.techs), TECHS_PER_RESOURCE * len(SAMPLED_RESOURCES))
        for resource in SAMPLED_RESOURCES:
            with self.subTest(resource.name):
                costing = [tech for tech in self.world.pool.techs.shuffled
                           if tech.cost.get(resource, 0) > 0]
                drawn = [tech for tech in self.budget.techs if tech.cost.get(resource, 0) > 0]
                self.assertGreaterEqual(len(drawn), min(TECHS_PER_RESOURCE, len(costing)))

    def test_each_resource_gets_its_own_draw_of_units(self) -> None:
        self.assertLessEqual(len(self.budget.units), UNITS_PER_RESOURCE * len(SAMPLED_RESOURCES))
        for resource in SAMPLED_RESOURCES:
            with self.subTest(resource.name):
                drawn = [unit for unit in self.budget.units if unit.cost.get(resource, 0) > 0]
                self.assertTrue(drawn or not [unit for unit in self.world.pool.units.units
                                              if unit.cost.get(resource, 0) > 0])

    def test_sampled_techs_are_tech_locations(self) -> None:
        self.assertLessEqual(self.budget.techs, set(self.world.pool.techs.shuffled))

    def test_sampled_units_are_priced_trainable_unit_locations(self) -> None:
        for unit in self.budget.units:
            with self.subTest(unit.name):
                self.assertIn(unit, self.world.pool.units.units)
                self.assertTrue(self.world.pool.units.is_trainable_unit(unit))
                self.assertNotIn(unit.line, VILLAGER_LINES)
                self.assertTrue(unit.buildings)
                self.assertTrue(any(amount > 0 for amount in unit.cost.values()))

    def test_one_villager_stands_for_every_villager_location(self) -> None:
        villagers = [entry for entry in self.budget.entries
                     if getattr(entry, "line", None) in VILLAGER_LINES]
        self.assertEqual([VILLAGER], villagers)
        self.assertFalse({unit for unit in self.budget.units if unit.line in VILLAGER_LINES})

    def test_every_cheap_dark_age_building_is_in(self) -> None:
        cheap = {building for building in self.world.pool.buildings.locations
                 if is_cheap_building(building)}
        self.assertTrue(cheap, "this seed should shuffle some cheap economy buildings")
        self.assertLessEqual(cheap, self.budget.buildings)

    def test_four_more_buildings_are_drawn_at_most(self) -> None:
        extra = {building for building in self.budget.buildings if not is_cheap_building(building)}
        self.assertLessEqual(len(extra), BUILDINGS_DRAWN)
        self.assertLessEqual(self.budget.buildings, set(self.world.pool.buildings.locations))

    def test_every_age_location_is_in(self) -> None:
        self.assertEqual(self.budget.ages, set(self.world.pool.ages.locations))
        self.assertTrue(self.budget.ages)

    def test_entries_are_the_union_of_the_kinds(self) -> None:
        kinds = [self.budget.ages, self.budget.buildings, self.budget.techs, self.budget.units,
                 {VILLAGER}]
        self.assertEqual(self.budget.entries, set().union(*kinds))
        self.assertEqual(len(self.budget.entries), sum(len(kind) for kind in kinds))

    def test_every_included_scenario_ranks_every_entry_once(self) -> None:
        self.assertEqual(set(self.budget.rank), set(self.world.pool.scenarios.included))
        for scenario, rank in self.budget.rank.items():
            with self.subTest(scenario.scenario_name):
                self.assertEqual(set(rank), set(self.budget.entries))
                self.assertEqual(sorted(rank.values()), list(range(len(self.budget.entries))))


class TestVillagerLinesStillMeanOneVillager(bases.Age2TestBase):
    """Male and female villagers are the same unit to the game: one entry, whatever the
    granularity Shuffle Villager used."""

    options = {**HARD_OPTIONS, "shuffle_villager": "yes"}

    def test_the_villager_is_in_once(self) -> None:
        budget = self.world.pool.budget
        self.assertTrue(budget.villager)
        self.assertEqual(1, len([entry for entry in budget.entries
                                 if getattr(entry, "line", None) in VILLAGER_LINES]))


class TestNoVillagerLocationsNoVillager(bases.Age2TestBase):
    options = {**HARD_OPTIONS, "shuffle_villager": "no"}

    def test_the_villager_is_out(self) -> None:
        self.assertFalse(self.world.pool.budget.villager)
        self.assertNotIn(VILLAGER, self.world.pool.budget.entries)


class TestTheCheapRule(unittest.TestCase):
    """The always-in buildings are every Dark Age building costing 100 or less in total."""

    def test_the_rule_picks_the_economy_basics(self) -> None:
        for building in (Age2BuildingData.HOUSE, Age2BuildingData.FARM, Age2BuildingData.MILL,
                         Age2BuildingData.MINING_CAMP, Age2BuildingData.LUMBER_CAMP,
                         Age2BuildingData.OUTPOST, Age2BuildingData.PALISADE_WALL,
                         Age2BuildingData.PALISADE_GATE):
            with self.subTest(building.name):
                self.assertTrue(is_cheap_building(building))

    def test_the_rule_leaves_out_the_dear_and_the_late(self) -> None:
        for building in (Age2BuildingData.TOWN_CENTER, Age2BuildingData.DOCK,
                         Age2BuildingData.FISH_TRAP, Age2BuildingData.DONJON,
                         Age2BuildingData.BARRACKS):
            with self.subTest(building.name):
                self.assertFalse(is_cheap_building(building))


class TestTheSampleIsDeterministic(unittest.TestCase):
    """Two generations of one seed have to agree, or the spoiler describes some other seed."""

    @staticmethod
    def world_for(seed: int) -> Age2World:
        multiworld = setup_multiworld(Age2World, ("generate_early",), seed=seed,
                                      options=HARD_OPTIONS)
        return multiworld.worlds[1]

    def test_the_same_seed_draws_the_same_sample_and_ranks(self) -> None:
        first, second = self.world_for(7).pool.budget, self.world_for(7).pool.budget
        self.assertEqual(first.entries, second.entries)
        self.assertEqual(first.rank, second.rank)

    def test_different_seeds_draw_different_samples(self) -> None:
        samples = {self.world_for(seed).pool.budget.entries for seed in range(6)}
        self.assertGreater(len(samples), 1)

    def test_the_sample_spends_one_value_of_the_world_random(self) -> None:
        """A private Random keeps the rest of the seed's choices where they were."""
        world = self.world_for(3)
        state = world.random.getstate()
        BudgetPool(world.pool, world.random)
        after = world.random.getstate()
        probe = Random()
        probe.setstate(state)
        probe.getrandbits(64)
        self.assertEqual(probe.getstate(), after)
