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
                                           BudgetPool)
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

    def test_four_buildings_are_drawn(self) -> None:
        self.assertEqual(BUILDINGS_DRAWN, len(self.budget.buildings))
        self.assertLessEqual(self.budget.buildings, set(self.world.pool.buildings.locations))

    def test_the_town_center_is_never_drawn(self) -> None:
        """The base charges the Town Center, so a standing one or a starting base lets it off. A
        drawn one would be paid in full in every scenario, standing or not."""
        self.assertIn(Age2BuildingData.TOWN_CENTER, self.world.pool.buildings.locations)
        for seed in range(20):
            with self.subTest(seed=seed):
                budget = BudgetPool(self.world.pool, Random(seed))
                self.assertNotIn(Age2BuildingData.TOWN_CENTER, budget.buildings)

    def test_every_age_location_is_in(self) -> None:
        self.assertEqual(self.budget.ages, set(self.world.pool.ages.locations))
        self.assertTrue(self.budget.ages)

    def test_entries_are_the_union_of_the_kinds(self) -> None:
        kinds = [self.budget.ages, self.budget.buildings, self.budget.techs, self.budget.units,
                 {VILLAGER}]
        self.assertEqual(self.budget.entries, set().union(*kinds))
        self.assertEqual(len(self.budget.entries), sum(len(kind) for kind in kinds))

    def test_the_seed_ranks_every_entry_once(self) -> None:
        """One rank for the seed, shared by every scenario's order."""
        self.assertEqual(set(self.budget.rank), set(self.budget.entries))
        self.assertEqual(sorted(self.budget.rank.values()), list(range(len(self.budget.entries))))

    def test_the_seed_orders_every_building_once(self) -> None:
        self.assertEqual(set(self.budget.building_order), set(Age2BuildingData))
        self.assertEqual(sorted(self.budget.building_order.values()),
                         list(range(len(Age2BuildingData))))


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


class TestUnshuffledAgesAreStillPaidFor(bases.Age2TestBase):
    """With Shuffle Ages off the ages are no locations, but reaching one still costs food and gold:
    the budget prices them all the same."""

    options = {**HARD_OPTIONS, "shuffle_ages": False}

    def test_every_climbable_age_is_in(self) -> None:
        self.assertFalse(self.world.pool.ages.locations)
        self.assertTrue(self.world.pool.budget.ages)
        self.assertEqual(self.world.pool.budget.ages, set(self.world.pool.ages.shuffled))


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
        self.assertEqual(first.building_order, second.building_order)

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
