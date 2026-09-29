"""The banked-resource primitive.

HasResourceAmount is the one rule in the world that adds item payloads together, and the one that
decides at resolve time whether a seed can pay a price at all. Both halves are worth pinning: the
summation, and the degrade to False_ when the pool falls short.
"""

import unittest

from BaseClasses import CollectionState
from rule_builder.rules import False_, True_

from . import bases
from ..items.Items import Age2ItemData, Resource, StartingResources
from ..locations.VillagerJobs import Age2VillagerJobData, FOOD_PROFESSIONS
from ..Options import ShuffleVillager
from ..logic.custom_logic.ResourceAmount import HasResourceAmount, contributors


class TestContributors(unittest.TestCase):
    def test_both_resource_bands_contribute(self):
        """The three town-centre items are the guaranteed floor, so they count toward the same
        totals as the random padding does."""
        names = {name for resource in Resource for name, _ in contributors(resource)}
        self.assertIn(Age2ItemData.TOWN_CENTER_WOOD.item_name, names)
        self.assertIn(Age2ItemData.TOWN_CENTER_STONE.item_name, names)
        self.assertIn(Age2ItemData.STARTING_VILLAGER_FOOD.item_name, names)

    def test_the_trio_alone_pays_for_an_opening(self):
        """What keeps a base reachable in every seed: one of each is always pooled, and together
        they come to exactly a town centre plus three villagers."""
        cost = dict(Age2ItemData.TOWN_CENTER.type.needed_resources)
        for resource, amount in cost.items():
            with self.subTest(resource.name):
                trio = dict(contributors(resource))
                from_tc = sum(value for name, value in trio.items()
                              if name.startswith("Starting Town Center"))
                self.assertGreaterEqual(from_tc, amount)
        food = dict(contributors(Resource.FOOD))
        self.assertGreaterEqual(food[Age2ItemData.STARTING_VILLAGER_FOOD.item_name], 150)

    def test_every_starting_resource_item_is_claimed_by_its_resource(self):
        for item in Age2ItemData:
            if not isinstance(item.type, StartingResources):
                continue
            with self.subTest(item.item_name):
                self.assertIn((item.item_name, item.type.amount),
                              contributors(item.type.type))

    def test_the_food_row_is_what_we_think(self):
        self.assertEqual(
            dict(contributors(Resource.FOOD)),
            {"+50 Starting Food": 50, "+100 Starting Food": 100, "+250 Starting Food": 250,
             "Starting Villager Food": 150})


class TestSummation(bases.Age2RuleTestBase):
    """The arithmetic, driven through a real world so the resolve path is the real one."""

    def resolved(self, resource: Resource, amount: int):
        return HasResourceAmount(resource=resource, amount=amount).resolve(self.world)

    def state_with(self, **items: int) -> CollectionState:
        state = CollectionState(self.multiworld)
        for name, count in items.items():
            for _ in range(count):
                state.collect(self.world.create_item(name), prevent_sweep=True)
        return state

    def test_denominations_add_up(self):
        self.build()
        self.world.starting_resource_totals[Resource.FOOD] = 10000
        rule = self.resolved(Resource.FOOD, 400)
        state = self.state_with(**{"+50 Starting Food": 1, "+100 Starting Food": 1,
                                   "+250 Starting Food": 1})
        self.assertTrue(rule(state), "50 + 100 + 250 should cover 400")

    def test_one_short_is_short(self):
        self.build()
        self.world.starting_resource_totals[Resource.FOOD] = 10000
        rule = self.resolved(Resource.FOOD, 401)
        state = self.state_with(**{"+50 Starting Food": 1, "+100 Starting Food": 1,
                                   "+250 Starting Food": 1})
        self.assertFalse(rule(state), "400 banked should not pay 401")

    def test_copies_of_one_denomination_stack(self):
        self.build()
        self.world.starting_resource_totals[Resource.WOOD] = 10000
        rule = self.resolved(Resource.WOOD, 200)
        self.assertTrue(rule(self.state_with(**{"+50 Starting Wood": 4})))
        self.assertFalse(rule(self.state_with(**{"+50 Starting Wood": 3})))

    def test_one_resource_does_not_pay_for_another(self):
        self.build()
        self.world.starting_resource_totals[Resource.GOLD] = 10000
        rule = self.resolved(Resource.GOLD, 50)
        self.assertFalse(rule(self.state_with(**{"+250 Starting Food": 1})))


class TestResolveTimeDegrade(bases.Age2RuleTestBase):
    def test_nothing_asked_is_always_true(self):
        self.build()
        self.assertIsInstance(HasResourceAmount(resource=Resource.FOOD, amount=0)
                              .resolve(self.world), True_.Resolved)

    def test_more_than_the_seed_holds_is_false(self):
        """Not an unsatisfiable rule - an honest False, so the Or in can_afford drops this
        branch and the gathering branch carries the cost alone."""
        self.build()
        self.world.starting_resource_totals[Resource.STONE] = 100
        self.assertIsInstance(HasResourceAmount(resource=Resource.STONE, amount=101)
                              .resolve(self.world), False_.Resolved)

    def test_exactly_what_the_seed_holds_is_a_real_rule(self):
        self.build()
        self.world.starting_resource_totals[Resource.STONE] = 100
        resolved = HasResourceAmount(resource=Resource.STONE, amount=100).resolve(self.world)
        self.assertIsInstance(resolved, HasResourceAmount.Resolved)


class TestDependencies(bases.Age2RuleTestBase):
    def test_every_contributing_name_is_declared(self):
        """LocalStart.solve narrows its candidates by this set, so a missing name means local
        start quietly stops finding that resource."""
        self.build()
        self.world.starting_resource_totals[Resource.FOOD] = 10000
        resolved = HasResourceAmount(resource=Resource.FOOD, amount=100).resolve(self.world)
        self.assertEqual(set(resolved.item_dependencies()),
                         {name for name, _ in contributors(Resource.FOOD)})

    def test_collecting_a_contributor_flips_a_rule_that_cached_false(self):
        """The ScenarioQuestion.mine failure mode, written down: a cached False that never
        clears is how this becomes hundreds of FillErrors instead of one wrong answer."""
        self.build()
        self.world.starting_resource_totals[Resource.FOOD] = 10000
        rule = HasResourceAmount(resource=Resource.FOOD, amount=250).resolve(self.world)
        state = CollectionState(self.multiworld)
        self.assertFalse(rule(state))
        state.collect(self.world.create_item("+250 Starting Food"), prevent_sweep=True)
        self.assertTrue(rule(state), "the rule did not notice the item it depends on")


class TestFoodProfessions(bases.Age2RuleTestBase):
    def test_food_is_free_when_professions_are_not_shuffled(self):
        self.build(shuffle_villager=ShuffleVillager.option_no)
        rule = self.world.rules.logic.resources.has_any_food_profession()
        self.assertIsInstance(rule, True_)

    def test_any_food_profession_names_all_six(self):
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        rule = self.world.rules.logic.resources.has_any_food_profession()
        self.assertEqual(set(rule.resolve(self.world).item_dependencies()),
                         {profession.item_name for profession in FOOD_PROFESSIONS})

    def test_every_food_profession_is_a_real_job(self):
        jobs = {job.item for job in Age2VillagerJobData}
        for profession in FOOD_PROFESSIONS:
            with self.subTest(profession.item_name):
                self.assertIn(profession, jobs)
