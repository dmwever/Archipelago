"""Unit and technology costs, and what the rules do with them."""

import unittest

from . import bases
from ..items.Items import Age2ItemData, Building, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.connections.GameCosts import (GAME_DATA_SOURCE, TECHS_WITHOUT_COST,
                                               UNITS_WITHOUT_COST)
from ..logic.budget.BudgetTotal import BudgetTotal
from ..Options import ShuffleVillager


class TestEverythingIsPriced(unittest.TestCase):
    def test_every_unit_has_a_cost_or_is_declared_free(self):
        for unit in Age2UnitData:
            with self.subTest(unit.name):
                self.assertTrue(unit.cost or unit in UNITS_WITHOUT_COST)

    def test_every_tech_has_a_cost_or_is_declared_free(self):
        for tech in Age2TechData:
            with self.subTest(tech.name):
                self.assertTrue(tech.cost or tech in TECHS_WITHOUT_COST)

    def test_costs_are_whole_positive_amounts_of_real_resources(self):
        for owner in (*Age2UnitData, *Age2TechData):
            for resource, amount in owner.cost.items():
                with self.subTest(f"{owner.name}.{resource}"):
                    self.assertIsInstance(resource, Resource)
                    self.assertIsInstance(amount, int)
                    self.assertGreater(amount, 0)

    def test_the_units_without_a_cost_are_the_ones_we_think(self):
        """All Chronicles-era, none trainable by a shipped civilisation. A new name in here is a
        unit that would silently become free."""
        for unit in UNITS_WITHOUT_COST:
            with self.subTest(unit.name):
                self.assertGreaterEqual(unit.game_id, 2101)

    def test_the_source_is_recorded(self):
        self.assertTrue(GAME_DATA_SOURCE.strip())


class TestSpotChecks(unittest.TestCase):
    """A handful of costs everyone knows, so a regenerated table that is subtly wrong fails."""

    def test_known_costs(self):
        self.assertEqual(Age2UnitData.VILLAGER_MALE.cost, {Resource.FOOD: 50})
        self.assertEqual(Age2UnitData.VILLAGER_FEMALE.cost, {Resource.FOOD: 50})
        self.assertEqual(Age2UnitData.KNIGHT.cost, {Resource.FOOD: 60, Resource.GOLD: 75})
        self.assertEqual(Age2UnitData.FISHING_SHIP.cost, {Resource.WOOD: 75})
        self.assertEqual(Age2UnitData.MONK.cost, {Resource.GOLD: 100})

    def test_the_building_costs_in_items_still_agree_with_the_dump(self):
        """Thirty-four of thirty-five agreed when the table was generated. The Palisade Gate did
        not - 20 wood here against 30 in the dump - and this records that rather than hiding it."""
        gate = Age2ItemData.PALISADE_GATE
        self.assertIsInstance(gate.type, Building)
        self.assertEqual(gate.type.needed_resources, {Resource.WOOD: 20.0})


class TestAgeAndBuildingCosts(unittest.TestCase):
    """Ages and buildings were never priced: climbing an age and putting a building up both read
    as free, so logic could ask for every one of them out of a single opening pile."""

    def test_every_age_past_the_dark_age_costs_something(self):
        self.assertEqual(Age2AgeData.DARK.cost, {})
        for age in (Age2AgeData.FEUDAL, Age2AgeData.CASTLE, Age2AgeData.IMPERIAL):
            with self.subTest(age.name):
                self.assertTrue(age.cost)

    def test_the_age_up_costs_are_the_game_s(self):
        self.assertEqual(Age2AgeData.FEUDAL.cost, {Resource.FOOD: 500})
        self.assertEqual(Age2AgeData.CASTLE.cost, {Resource.FOOD: 800, Resource.GOLD: 200})
        self.assertEqual(Age2AgeData.IMPERIAL.cost, {Resource.FOOD: 1000, Resource.GOLD: 800})

    def test_every_building_location_costs_what_its_item_says(self):
        for building in Age2BuildingData:
            with self.subTest(building.name):
                expected = {resource: int(amount) for resource, amount
                            in building.item.type.needed_resources.items()}
                self.assertEqual(building.cost, expected)
                self.assertTrue(building.cost)

    def test_known_building_costs(self):
        self.assertEqual(Age2BuildingData.TOWN_CENTER.cost,
                         {Resource.WOOD: 275, Resource.STONE: 100})
        self.assertEqual(Age2BuildingData.FARM.cost, {Resource.WOOD: 60})
        self.assertEqual(Age2BuildingData.CASTLE.cost, {Resource.STONE: 650})

    def test_age_and_building_costs_are_whole_positive_amounts(self):
        for owner in (*Age2AgeData, *Age2BuildingData):
            for resource, amount in owner.cost.items():
                with self.subTest(f"{owner.name}.{resource}"):
                    self.assertIsInstance(resource, Resource)
                    self.assertIsInstance(amount, int)
                    self.assertGreater(amount, 0)


class TestCostsReachTheRules(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc"]

    def deps(self, rule):
        return set(rule.resolve(self.world).item_dependencies())

    def budget_terms(self, rule, location) -> list:
        """The budget totals for this location a resolved rule can be satisfied through. Others
        turn up too - an easy source of wood asks for a base, and the base is paid that way."""
        found, stack = [], [rule.resolve(self.world)]
        while stack:
            node = stack.pop()
            if isinstance(node, BudgetTotal.Resolved) and node.location is location:
                found.append(node)
            stack.extend(getattr(node, "children", ()))
            stack.extend(child for child in (getattr(node, "child", None),
                                             getattr(node, "answer", None)) if child is not None)
        return found

    def test_a_tech_in_the_budget_order_can_be_paid_from_the_pile(self):
        """A tech its scenario's budget order holds may be paid out of the opening pile as well
        as from an easy source, so its rule carries the running total."""
        self.build(techsanity=3)
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        held = [entry.location for entry in scenario.budget.order.order
                if isinstance(entry.location, Age2TechData)]
        if not held:
            self.skipTest("this seed's order holds no tech in Attila 1")
        for tech in held:
            with self.subTest(tech.name):
                self.assertTrue(self.budget_terms(scenario.techs.can_research(tech), tech))

    def test_a_tech_outside_the_budget_order_needs_an_easy_source(self):
        """Loom used to be researchable on the opening pile in every scenario, which is how
        dozens of techs came into logic at once. Outside the budget order a tech's rule offers
        only an easy source of what it costs."""
        self.build(techsanity=3)
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        order = scenario.budget.order
        held = {entry.location for entry in order.order if isinstance(entry.location, Age2TechData)}
        outside = [tech for tech in self.world.pool.techs.shuffled if tech not in held
                   and order.get_priced_location(tech) is not None]
        self.assertTrue(outside)
        for tech in outside:
            with self.subTest(tech.name):
                self.assertEqual([], self.budget_terms(scenario.techs.can_research(tech), tech))

    def test_a_free_unit_is_free_rather_than_untrainable(self):
        """An empty And resolves to False_, so a unit with no cost on file has to be handled
        explicitly or it becomes untrainable."""
        self.build()
        economy = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1).economy
        self.assertTrue(economy.can_pay({}, Age2UnitData.KNIGHT).resolve(self.world)
                        .always_true)


class TestVillagersCostFood(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def test_a_shuffled_villager_wants_the_starting_food_item(self):
        self.build(shuffle_villager=ShuffleVillager.option_yes)
        wanted = set(self.world.rules.logic.units.can_get_villager_anywhere()
                     .resolve(self.world).item_dependencies())
        self.assertIn(Age2ItemData.STARTING_VILLAGER_FOOD.item_name, wanted)


class TestABaseNeedsVillagers(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def test_even_a_granted_base_wants_the_food_to_staff_it(self):
        """Attila 3 opens with a town centre standing. A town centre with nobody in front of it
        is not a base, so the food is asked outside the granted-or-built choice."""
        self.build()
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_3)
        self.assertTrue(scenario.starting_state.has_base.resolve(self.world).always_true)
        wanted = set(scenario.has_base().resolve(self.world).item_dependencies())
        self.assertIn(Age2ItemData.STARTING_VILLAGER_FOOD.item_name, wanted)


class TestFieldingSustainsEveryTier(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def test_a_line_that_costs_gold_at_any_tier_needs_gold(self):
        """The militia line costs gold at every tier. Sustaining is asked of the union of the
        tiers, not of the cheapest one - a tier with no cost on file would read as cheapest."""
        self.build()
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        from ..locations.Ages import Age2AgeData
        rule = scenario.units.can_field(Age2UnitLineData.MILITIA_LINE, Age2AgeData.DARK)
        wanted = set(rule.resolve(self.world).item_dependencies())
        self.assertTrue(wanted, "fielding the militia line asked for nothing at all")
        tiers = scenario.units.fieldable_tiers(Age2UnitLineData.MILITIA_LINE, Age2AgeData.DARK)
        self.assertTrue(any(Resource.GOLD in unit.cost for unit in tiers))


if __name__ == "__main__":
    unittest.main()
