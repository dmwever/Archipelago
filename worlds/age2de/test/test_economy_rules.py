"""The per-scenario economy: who can gather what, and what that makes affordable."""

import dataclasses
import unittest
from unittest import mock

from BaseClasses import CollectionState
from rule_builder.rules import False_, True_

from . import bases
from ..items.Items import Age2ItemData, Resource
from ..locations.Buildings import Age2BuildingData
from ..locations.connections.ScenarioResources import Tier, total
from ..locations.Scenarios import Age2ScenarioData
from ..logic.scenarios import ScenarioResourceLogic as economy_module
from ..logic.custom_logic.ScenarioQuestions import ScenarioHasResource


class EconomyTestBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc"]

    def economy(self, scenario: Age2ScenarioData):
        return self.world.rules.logic.for_scenario(scenario).economy

    def resolved(self, rule):
        return rule.resolve(self.world)

    def is_false(self, rule) -> bool:
        return self.resolved(rule).always_false

    def easy(self, scenario: Age2ScenarioData, resource: Resource):
        """The gathering half of has_easy_source, without the scenario's declared sources."""
        question = ScenarioHasResource(scenario=scenario, resource=resource, easy=True)
        return question._GATHERED_EASILY[resource](
            question, self.world.rules.logic.for_scenario(scenario))


class TestSourcesPerScenario(EconomyTestBase):
    def test_a_scenario_with_no_gold_on_the_map_has_no_mining(self):
        self.build()
        self.assertTrue(self.is_false(self.economy(Age2ScenarioData.AP_JOAN_1).can_mine_some()))
        self.assertEqual(total(Age2ScenarioData.AP_JOAN_1).gold_count, 0)

    def test_attila_4_cannot_live_on_fish(self):
        """A dozen fish against Attila 4's demand; Attila 3 has eleven thousand within reach
        against a smaller one. Farms are mocked away too: a farm is endless food on either map,
        which is the point of endless_food.

        Attila 3 rather than Attila 1 is the map that can, which is the tiering showing through.
        Attila 1 holds the most fish of anywhere - twenty thousand - but 8700 of it lies inside
        a Persian camp and 3000 is the Scythians' to give, leaving 8725 against a demand of
        10000. Only what the tiers let you reach is weighed.
        """
        self.build()
        with mock.patch.multiple(economy_module.ScenarioResourceLogic,
                                 can_hunt=mock.Mock(return_value=False_()),
                                 can_herd=mock.Mock(return_value=False_()),
                                 can_forage=mock.Mock(return_value=False_()),
                                 endless_food=mock.Mock(return_value=False_())):
            self.assertTrue(self.is_false(
                self.easy(Age2ScenarioData.AP_ATTILA_4, Resource.FOOD)))
            self.assertTrue(self.is_false(
                self.easy(Age2ScenarioData.AP_ATTILA_1, Resource.FOOD)),
                "Attila 1's fish are mostly an enemy's, so they do not count towards living "
                "on fish alone")
            self.assertFalse(self.is_false(
                self.easy(Age2ScenarioData.AP_ATTILA_3, Resource.FOOD)))

    def test_food_is_the_sum_of_what_can_be_worked(self):
        """No single source has to carry a map: Joan 2 has 680 of hunt, 1500 of herd and 2125
        of bushes, none of them near the threshold, and together they clear it."""
        self.build()
        joan_2 = total(Age2ScenarioData.AP_JOAN_2)
        for count in (joan_2.hunt_count, joan_2.herd_count, joan_2.bush_count):
            self.assertLess(count, Age2ScenarioData.AP_JOAN_2.demand.food)
        self.assertFalse(self.is_false(
            self.easy(Age2ScenarioData.AP_JOAN_2, Resource.FOOD)))

    def test_a_map_under_the_threshold_is_workable_but_not_abundant(self):
        """Read off ABUNDANT rather than off a scenario, so retuning the thresholds does not
        make this a lie."""
        self.build()
        for scenario in Age2ScenarioData:
            counts = total(scenario)
            economy = self.economy(scenario)
            for count, threshold, some, easily in (
                    (counts.gold_count, scenario.demand.gold,
                     economy.can_mine_some,
                     lambda: self.easy(scenario, Resource.GOLD)),
                    (counts.stone_count, scenario.demand.stone,
                     economy.can_quarry_some,
                     lambda: self.easy(scenario, Resource.STONE))):
                with self.subTest(f"{scenario.name}:{count}/{threshold}"):
                    # Only the threshold direction belongs here. Whether a map that clears it is
                    # actually workable turns on villagers, which Joan 1 and Joan 5 do not have.
                    if count < threshold:
                        self.assertTrue(self.is_false(easily()))
                    if not count:
                        self.assertTrue(self.is_false(some()))

    def test_no_map_supports_oysters_or_whales(self):
        self.build()
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                self.assertTrue(self.is_false(self.economy(scenario).can_gather_oysters()))
                self.assertTrue(self.is_false(self.economy(scenario).can_hunt_whales()))

    def test_relics_only_where_the_map_has_them(self):
        self.build()
        with_relics = {scenario for scenario in Age2ScenarioData
                       if not self.is_false(self.economy(scenario).can_collect_relics())}
        self.assertEqual(with_relics, {Age2ScenarioData.AP_ATTILA_3, Age2ScenarioData.AP_ATTILA_4})


class TestFixedForceNeedsNoSpecialCase(EconomyTestBase):
    """Joan 1 and Joan 5 build nothing and train nothing, so every gatherer falls away on
    has_vils alone. That is why the economy carries no fixed_force branch."""

    def test_a_fixed_force_scenario_gathers_nothing(self):
        self.build()
        for scenario in (Age2ScenarioData.AP_JOAN_1, Age2ScenarioData.AP_JOAN_5):
            self.assertTrue(scenario.logic(self.world.rules.logic).fixed_force)
            for resource in Resource:
                with self.subTest(f"{scenario.name}.{resource.name}"):
                    self.assertTrue(self.is_false(self.economy(scenario).has_source(resource)))


class TestAttila3Gold(EconomyTestBase):
    """Six mines on the map, and 3000 gold in each lump. The lumps are the gold economy."""

    def test_the_lumps_are_an_easy_source(self):
        self.build()
        rule = self.economy(Age2ScenarioData.AP_ATTILA_3).has_easy_source(Resource.GOLD)
        wanted = {Age2ItemData.AP_ATTILA_3_RED_GOLD.item_name,
                  Age2ItemData.AP_ATTILA_3_GREEN_GOLD.item_name}
        self.assertTrue(wanted <= set(self.resolved(rule).item_dependencies()))

    def test_the_lumps_matter_when_the_map_is_short(self):
        """Whether Attila 3 needs them is a tuning question - its 4800 in the ground sits against
        whatever demand the scenario declares - so this asserts the relationship, not a verdict."""
        self.build()
        attila_3 = Age2ScenarioData.AP_ATTILA_3
        easy = self.resolved(self.economy(attila_3).has_easy_source(Resource.GOLD))
        if total(attila_3).gold_count < attila_3.demand.gold:
            self.assertTrue(self.is_false(self.easy(attila_3, Resource.GOLD)))
        self.assertFalse(easy.always_false, "the lumps should keep gold reachable either way")


class TestDropsites(EconomyTestBase):
    """A mule cart is the only dropsite that is not universal: it takes wood, gold, stone and
    meat, but no other food. Neither shipped civilisation can build one, so the rules are driven
    with a scenario that has nothing standing but a cart."""

    def only_a_mule_cart(self, scenario: Age2ScenarioData):
        logic = self.world.rules.logic.for_scenario(scenario)
        def has_building(building):
            return True_() if building is Age2BuildingData.MULE_CART else False_()
        return mock.patch.object(logic, "has_building", side_effect=has_building), logic.buildings

    def test_a_mule_cart_takes_wood_gold_stone_and_meat(self):
        self.build()
        patch, buildings = self.only_a_mule_cart(Age2ScenarioData.AP_ATTILA_4)
        with patch:
            for rule in (buildings.has_wood_dropsite(), buildings.has_gold_dropsite(),
                         buildings.has_stone_dropsite(), buildings.has_hunt_dropsite()):
                self.assertFalse(self.is_false(rule))

    def test_a_mule_cart_takes_no_other_food(self):
        self.build()
        patch, buildings = self.only_a_mule_cart(Age2ScenarioData.AP_ATTILA_4)
        with patch:
            for rule in (buildings.has_food_dropsite(), buildings.has_fisherman_dropsite(),
                         buildings.has_fishing_boat_dropsite()):
                self.assertTrue(self.is_false(rule))

    def test_no_shipped_civilisation_can_build_one(self):
        """Why the two tests above have to force it: the Huns and the Franks have no mule cart,
        so can_build_building answers False before any of this is reached."""
        self.build()
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                logic = self.world.rules.logic.for_scenario(scenario)
                self.assertTrue(self.is_false(
                    logic.buildings.can_build_building(Age2BuildingData.MULE_CART)))


class TestEndlessFood(EconomyTestBase):
    def test_endless_food_needs_wood_to_stay_endless(self):
        """A farm is 60 wood and a fish trap 100, forever."""
        self.build()
        attila_1 = self.economy(Age2ScenarioData.AP_ATTILA_1)
        with mock.patch.object(type(attila_1), "_can_get_wood_easily", return_value=False_()):
            self.assertTrue(self.is_false(attila_1.endless_food()))


class TestStubs(EconomyTestBase):
    def test_the_market_and_ally_trade_are_off(self):
        self.build()
        attila_1 = self.economy(Age2ScenarioData.AP_ATTILA_1)
        self.assertIsInstance(attila_1.market_trades(), False_)
        self.assertIsInstance(attila_1.ally_trade_gold(), False_)
        self.assertIsInstance(attila_1.ally_trade_wood(), False_)

    def test_trade_asks_for_the_buildings_that_train_the_traders(self):
        """A cart wants a market, a cog wants a dock - and the dock is where water access comes
        in. Both stay behind trading_ally, which no scenario declares."""
        with mock.patch.object(economy_module, "ALLY_TRADE", True):
            self.build()
            attila_1 = self.economy(Age2ScenarioData.AP_ATTILA_1)
            # No scenario declares one, and without it the rule collapses before it can name
            # anything, so the ally is granted here to see what is behind it.
            attila_1.scenario.starting_state.trading_ally = True_()
            gold = set(self.resolved(attila_1.ally_trade_gold()).item_dependencies())
            wood = set(self.resolved(attila_1.ally_trade_wood()).item_dependencies())
            self.assertIn(Age2BuildingData.MARKET.item.item_name, gold)
            self.assertIn(Age2BuildingData.DOCK.item.item_name, gold)
            # Cogs only for wood: a sea route brings wood home, a cart does not. The market can
            # still turn up in here, because the wood route is seeded with gold.
            self.assertIn(Age2BuildingData.DOCK.item.item_name, wood)

    def test_the_market_rule_is_real_and_terminates_when_switched_on(self):
        """Written against the leaf gatherers, so the wood aggregate cannot ask the market
        which asks the wood aggregate."""
        with mock.patch.object(economy_module, "MARKET_ECONOMY", True):
            self.build()
            attila_1 = self.economy(Age2ScenarioData.AP_ATTILA_1)
            self.assertNotIsInstance(attila_1.market_trades(), False_)
            for resource in Resource:
                self.resolved(attila_1.has_easy_source(resource))
            self.assertEqual(set(), self.world.rules.logic.scenario_answers_open)


class TestAffordability(EconomyTestBase):
    def test_a_cost_of_nothing_asks_for_nothing(self):
        """An empty And resolves to False_, not True_ (rule_builder.rules:452), so a unit or
        tech with no cost on file would otherwise be untrainable rather than free."""
        self.build()
        economy = self.economy(Age2ScenarioData.AP_ATTILA_1)
        state = CollectionState(self.multiworld)
        for costs in ({}, {Resource.GOLD: 0}, {Resource.GOLD: 0, Resource.FOOD: 0}):
            with self.subTest(str(costs)):
                self.assertTrue(self.resolved(economy.can_afford(costs))(state))
                self.assertTrue(self.resolved(
                    self.world.rules.logic.resources.has_amounts(costs))(state))
        # can_sustain is asked which resources to keep coming, not what they cost, so the
        # zero-cost filtering happens in can_field and nothing priced at nothing reaches here.
        self.assertTrue(self.resolved(economy.can_sustain(()))(state))

    def test_a_cost_can_be_paid_from_the_bank_or_from_the_ground(self):
        self.build()
        rule = self.economy(Age2ScenarioData.AP_ATTILA_1).can_afford({Resource.GOLD: 50})
        names = set(self.resolved(rule).item_dependencies())
        self.assertIn("+50 Starting Gold", names)
        self.assertIn(Age2BuildingData.MINING_CAMP.item.item_name, names)


class TestTheQuestionIsShared(EconomyTestBase):
    def test_asking_twice_gives_the_same_answer_object(self):
        self.build()
        scenario = Age2ScenarioData.AP_ATTILA_1
        first = self.resolved(ScenarioHasResource(scenario=scenario, resource=Resource.FOOD))
        second = self.resolved(ScenarioHasResource(scenario=scenario, resource=Resource.FOOD))
        self.assertIs(first, second)

    def test_the_question_answers_what_the_economy_would_have_built(self):
        self.build()
        for scenario in Age2ScenarioData:
            for resource in Resource:
                for easy in (False, True):
                    with self.subTest(f"{scenario.name}.{resource.name}.{easy}"):
                        question = ScenarioHasResource(scenario=scenario, resource=resource,
                                                     easy=easy)
                        answer = question.answer(
                            self.world.rules.logic.for_scenario(scenario))
                        self.assertIs(self.resolved(question).answer,
                                      self.resolved(answer))

    def test_the_answers_stay_within_budget(self):
        self.build()
        self.assertLess(len(self.world.rules.logic.scenario_answers), 1000)


if __name__ == "__main__":
    unittest.main()


class TestDeepFishIsWhatABoatNeeds(EconomyTestBase):
    """A fishing ship can only reach the fish a villager on the shore cannot, so the guard that
    switches the boat rule off has to read deep_fish_count - the same number the abundance weighing
    pairs it with. Every shipped map has deep fish, so the two spellings agree on all of them and
    only a map whose fish are all inshore can tell them apart."""

    def counts_with(self, scenario, **fields):
        """economy.counts is the tiers added together, so doctoring it is still a flat
        dataclass - the tier table itself is left alone."""
        return dataclasses.replace(total(scenario), **fields)

    def test_a_map_whose_fish_are_all_inshore_cannot_be_fished_by_boat(self):
        self.build()
        economy = self.economy(Age2ScenarioData.AP_ATTILA_1)
        economy.counts = self.counts_with(Age2ScenarioData.AP_ATTILA_1,
                                          shore_fish_count=4000, deep_fish_count=0)
        self.assertEqual(0, economy.counts.deep_fish_count)
        self.assertTrue(economy.counts.shore_fish_count, "shore fish must stay non-zero to tell "
                                                         "the two guards apart")
        self.assertIsInstance(economy.can_fish_by_boat(), False_)

    def test_deep_fish_alone_can_be(self):
        self.build()
        economy = self.economy(Age2ScenarioData.AP_ATTILA_1)
        economy.counts = self.counts_with(Age2ScenarioData.AP_ATTILA_1,
                                          shore_fish_count=0, deep_fish_count=4000)
        self.assertNotIsInstance(economy.can_fish_by_boat(), False_)


class TestEveryScenarioCanLive(EconomyTestBase):
    """The tiers gate, so a scenario can be shut out of a resource by the data alone - a map
    whose only gold sits in a camp the scenario never asks you to take would read as abundant
    and be unwinnable. This is the test that says which, rather than leaving it to a seed.

    A fixed force is excluded on purpose: no villagers, so nothing is gatherable by design.
    """

    def playable(self):
        return [scenario for scenario in Age2ScenarioData
                if not self.world.rules.logic.for_scenario(scenario).starting_state.fixed_force]

    def easy_answer(self, scenario: Age2ScenarioData, resource: Resource):
        """The whole easy question - gathering, the scenario's declared sources, and trade."""
        question = ScenarioHasResource(scenario=scenario, resource=resource, easy=True)
        return question.answer(self.world.rules.logic.for_scenario(scenario))

    def test_every_scenario_can_qualify_for_every_resource(self):
        self.build()
        barren = [f"{scenario.name}:{resource.name}"
                  for scenario in self.playable()
                  for resource in Resource
                  if self.is_false(self.easy_answer(scenario, resource))]
        self.assertEqual([], barren,
                         "a scenario cannot reach one of its resources by any route; either the "
                         "tier split is wrong or the gate is too tight")

    def test_a_fixed_force_is_shut_out_on_purpose(self):
        """The counterpart: if these ever start qualifying, a fixed force has gained an economy
        and the exclusion above has stopped meaning anything."""
        self.build()
        for scenario in (Age2ScenarioData.AP_JOAN_1, Age2ScenarioData.AP_JOAN_5):
            for resource in (Resource.FOOD, Resource.GOLD, Resource.STONE):
                with self.subTest(f"{scenario.name}.{resource.name}"):
                    self.assertTrue(self.is_false(self.easy_answer(scenario, resource)))

    def test_the_tiers_actually_gate(self):
        """Half of the scenarios lose a resource when only the base tier counts. If this ever
        comes back empty the gates have stopped gating and every tier is being summed again."""
        self.build()
        before = {(scenario, resource)
                  for scenario in self.playable() for resource in Resource
                  if not self.is_false(self.easy_answer(scenario, resource))}

        base_only = {tier: (True_() if tier is Tier.BASE else False_()) for tier in Tier}
        with mock.patch.object(economy_module.ScenarioResourceLogic, "tier_gates",
                               lambda self, kind="land": base_only):
            self.world.rules.logic.scenario_answers.clear()
            after = {(scenario, resource)
                     for scenario in self.playable() for resource in Resource
                     if not self.is_false(self.easy_answer(scenario, resource))}
        self.world.rules.logic.scenario_answers.clear()

        self.assertTrue(after < before,
                        "gating every tier but the base should cost somebody something")
