"""The per-scenario economy: who can gather what, and what that makes affordable."""

import dataclasses
import unittest
from unittest import mock

from BaseClasses import CollectionState
from rule_builder.rules import False_, True_

from . import bases
from ..Options import Caveman, PartnerTrade, Techsanity, Unitsanity, UnitsanityItems
from ..items.Items import Age2ItemData, Resource
from ..locations.Buildings import Age2BuildingData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Players import Age2PlayerData, TradeAccess
from ..locations.connections.ScenarioResources import Tier, total
from ..locations.Scenarios import Age2ScenarioData
from ..logic.scenarios import ScenarioResourceLogic as economy_module
from ..logic.custom_logic.EconomyRoutes import Strength
from ..logic.custom_logic.ScenarioQuestions import ScenarioHasEasyResource


class EconomyTestBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def economy(self, scenario: Age2ScenarioData):
        return self.world.rules.logic.for_scenario(scenario).economy

    def resolved(self, rule):
        return rule.resolve(self.world)

    def is_false(self, rule) -> bool:
        return self.resolved(rule).always_false

    def easy(self, scenario: Age2ScenarioData, resource: Resource):
        """has_easy_source less the market and the scenario's declared sources."""
        return self.world.rules.logic.for_scenario(scenario).economy.has_own_easy_source(resource)


class TestSourcesPerScenario(EconomyTestBase):
    def test_a_scenario_with_no_gold_on_the_map_has_no_mining(self):
        self.build()
        joan_1 = self.economy(Age2ScenarioData.AP_JOAN_1)
        self.assertTrue(self.is_false(
            joan_1.can_mine_some(joan_1.scenario.buildings.has_gold_dropsite())))
        self.assertEqual(total(Age2ScenarioData.AP_JOAN_1).gold_count, 0)

    def test_attila_4_cannot_live_on_fish(self):
        """A dozen fish against Attila 4's demand; Attila 3 has eleven thousand within reach
        against a smaller one. Farms are mocked away too: a farm is endless food on either map,
        which is the point of farming.

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
                                 can_farm=mock.Mock(return_value=False_()),
                                 can_work_fish_traps=mock.Mock(return_value=False_())):
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
                     lambda: economy.can_mine_some(economy.scenario.buildings.has_gold_dropsite()),
                     lambda: self.easy(scenario, Resource.GOLD)),
                    (counts.stone_count, scenario.demand.stone,
                     lambda: economy.can_quarry_some(economy.scenario.buildings.has_stone_dropsite()),
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
        self.assertEqual(with_relics, {Age2ScenarioData.AP_ATTILA_3, Age2ScenarioData.AP_GENGHIS_5})


class TestRelicsUnderCaveman(EconomyTestBase):
    """Genghis 5 has no monk of its own: the Hermit Monks mercenary is what brings one, and the
    relics ride on that. Under caveman those monks come down as Militia like any unit a scenario
    hands over, so the relics want the Monk's unit items too."""

    HERMITS = Age2ItemData.AP_GENGHIS_5_HERMITS.item_name
    MONK_LINE = Age2UnitLineData.MONK_LINE.item.item_name

    CAVEMAN = dict(caveman=Caveman.option_true, unitsanity=Unitsanity.option_all,
                   unitsanity_items=UnitsanityItems.option_unit_line)

    def can_collect(self, state) -> bool:
        rule = self.economy(Age2ScenarioData.AP_GENGHIS_5).can_collect_relics()
        return bool(rule.resolve(self.world)(state))

    def test_granted_monks_alone_do_not_collect_relics_under_caveman(self):
        self.build(**self.CAVEMAN)
        self.assertFalse(self.can_collect(self.state_without(self.MONK_LINE)))
        self.assertTrue(self.can_collect(self.state_without()))

    def test_the_training_branch_is_untouched(self):
        """Caveman only ever gates the granted half. Genghis 5 can raise a monastery, so holding
        the Monk Line collects relics there whether or not the hermits ever show up."""
        self.build(**self.CAVEMAN)
        self.assertTrue(self.can_collect(self.state_without(self.HERMITS)))

    def test_without_caveman_the_mercenary_is_enough(self):
        self.build(unitsanity=Unitsanity.option_all,
                   unitsanity_items=UnitsanityItems.option_unit_line)
        self.assertTrue(self.can_collect(self.state_without(self.MONK_LINE)))


class TestFixedForceNeedsNoSpecialCase(EconomyTestBase):
    """Joan 1 and Joan 5 build nothing and train nothing, so every gatherer falls away on
    has_vils alone. That is why the economy carries no fixed_force branch."""

    def test_a_fixed_force_scenario_gathers_nothing(self):
        self.build()
        for scenario in (Age2ScenarioData.AP_JOAN_1, Age2ScenarioData.AP_JOAN_5):
            self.assertTrue(scenario.fixed_force)
            for resource in Resource:
                with self.subTest(f"{scenario.name}.{resource.name}"):
                    self.assertTrue(self.is_false(self.economy(scenario).has_easy_source(resource)))


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
        return mock.patch.object(logic, "has_building_structurally", side_effect=has_building), logic.buildings

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
        so can_build_structurally answers False before any of this is reached."""
        self.build()
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                logic = self.world.rules.logic.for_scenario(scenario)
                self.assertTrue(self.is_false(
                    logic.buildings.can_build_structurally(Age2BuildingData.MULE_CART)))


class TestEndlessFood(EconomyTestBase):
    def test_endless_food_needs_wood_to_stay_endless(self):
        """A farm is 60 wood and a fish trap 100, forever."""
        self.build()
        attila_1 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1).routes
        endless = [
            route for route in attila_1.scenario_specific_routes()
            if route.name == "Farmers" or route.name.startswith("Fish Traps")
        ]
        self.assertEqual(4, len(endless))
        for route in endless:
            with self.subTest(route.name):
                self.assertEqual(Strength.AT_SCALE, route.needs[Resource.WOOD])


class TestMarketTrade(EconomyTestBase):
    """Buying and selling at P1's own market is a higher-difficulty expectation, so a yaml must
    ask for it."""

    def test_market_trade_is_off_by_default(self):
        self.assertFalse(self.build().options.market_trade)

    def test_off_market_trade_is_never_satisfiable(self):
        self.build(market_trade=False)
        for scenario in self.world.rules.logic.scenarios:
            with self.subTest(scenario.scenario.name):
                self.assertTrue(self.is_false(scenario.economy.can_trade_at_market()))

    def test_on_market_trade_asks_for_a_market(self):
        self.build(market_trade=True)
        attila_1 = self.economy(Age2ScenarioData.AP_ATTILA_1)
        dependencies = set(self.resolved(attila_1.can_trade_at_market()).item_dependencies())
        self.assertIn(Age2BuildingData.MARKET.item.item_name, dependencies)

    def test_on_market_trade_needs_something_to_sell(self):
        """Wood at scale is what the market turns into everything else."""
        self.build(market_trade=True)
        attila_1 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1).routes
        needs = [route.needs for route in attila_1.market_routes()]
        self.assertEqual([{Resource.WOOD: Strength.AT_SCALE}], needs)

    def test_on_market_trade_is_satisfiable_with_a_market(self):
        self.build(market_trade=True)
        attila_1 = self.economy(Age2ScenarioData.AP_ATTILA_1)
        self.assertFalse(self.is_false(attila_1.can_trade_at_market()))

    def test_the_market_rule_terminates_when_switched_on(self):
        """The market routes are resolved with every other route, so asking easy wood never
        asks the market asking easy wood."""
        self.build(market_trade=True)
        attila_1 = self.economy(Age2ScenarioData.AP_ATTILA_1)
        for resource in Resource:
            self.resolved(attila_1.has_easy_source(resource))
        self.assertEqual(set(), self.world.rules.logic.scenario_answers_open)


class TestPartnerTrade(EconomyTestBase):
    """Trade carts and trade cogs run to a trade partner. Which partners the logic may count on
    is the yaml's choice; which buildings they keep usable is the scenario's player records."""

    PARTNER_TRADE_SCENARIOS = {
        Age2ScenarioData.AP_ATTILA_1,   # the Scythians' market
        Age2ScenarioData.AP_ATTILA_5,   # the Ostrogoths' market
        Age2ScenarioData.AP_ATTILA_6,   # the Western Roman Empire's dock
        Age2ScenarioData.AP_JOAN_2,     # Blois' market
    }

    def test_partner_trade_is_allies_by_default(self):
        self.assertEqual(self.build().options.partner_trade, PartnerTrade.option_allies)

    def test_none_opens_no_trade_anywhere(self):
        self.build(partner_trade=PartnerTrade.option_none)
        for scenario in self.world.rules.logic.scenarios:
            with self.subTest(scenario.scenario.name):
                self.assertTrue(self.is_false(scenario.economy.can_earn_gold_by_partner_trade()))
                self.assertTrue(self.is_false(scenario.economy.can_earn_wood_by_partner_trade()))

    def test_allies_opens_trade_only_where_an_ally_has_a_usable_building(self):
        self.build(partner_trade=PartnerTrade.option_allies)
        for scenario in self.world.rules.logic.scenarios:
            with self.subTest(scenario.scenario.name):
                gold = scenario.economy.can_earn_gold_by_partner_trade()
                self.assertEqual(
                    not self.is_false(gold),
                    scenario.scenario in self.PARTNER_TRADE_SCENARIOS,
                )

    def test_allies_never_opens_an_enemy_building(self):
        """Genghis 5's only usable buildings are the Polish and German markets."""
        self.build(partner_trade=PartnerTrade.option_allies)
        genghis_5 = self.economy(Age2ScenarioData.AP_GENGHIS_5)
        self.assertTrue(self.is_false(genghis_5.can_earn_gold_by_partner_trade()))

    def test_a_cart_wants_a_market(self):
        self.build()
        attila_5 = self.economy(Age2ScenarioData.AP_ATTILA_5)
        gold = set(self.resolved(attila_5.can_earn_gold_by_partner_trade()).item_dependencies())
        self.assertIn(Age2BuildingData.MARKET.item.item_name, gold)
        # The Ostrogoths keep no dock, so no cog route is offered.
        self.assertTrue(self.is_false(attila_5.can_earn_wood_by_partner_trade()))

    def test_a_cog_wants_a_dock_and_brings_wood_home(self):
        self.build()
        attila_6 = self.economy(Age2ScenarioData.AP_ATTILA_6)
        wood = set(self.resolved(attila_6.can_earn_wood_by_partner_trade()).item_dependencies())
        self.assertIn(Age2BuildingData.DOCK.item.item_name, wood)

    def test_every_economy_question_terminates_with_partner_trade(self):
        """Trade asks the Feudal Age, which asks the economy, which asks trade."""
        for partner_trade in (PartnerTrade.option_allies, PartnerTrade.option_allies_and_enemies):
            with self.subTest(partner_trade=partner_trade):
                self.build(partner_trade=partner_trade)
                for scenario in self.world.rules.logic.scenarios:
                    for resource in Resource:
                        self.resolved(scenario.economy.has_easy_source(resource))
                self.assertEqual(set(), self.world.rules.logic.scenario_answers_open)


class TestPartnerTradeWithEnemies(EconomyTestBase):
    """At allies and enemies, an enemy's usable market or dock opens too: a defended one once P1
    holds the event for defeating its owner, an undefended one straight away."""

    def defeats_waited_on(self, scenario: Age2ScenarioData) -> set[Age2PlayerData]:
        """Whose defeat event partner trade asks for, by cart or by cog."""
        economy = self.economy(scenario)
        asked = (
            set(self.resolved(economy.can_earn_gold_by_partner_trade()).item_dependencies())
            | set(self.resolved(economy.can_earn_wood_by_partner_trade()).item_dependencies())
        )
        return {
            player for player in scenario.players
                if player.defeat_event(scenario.scenario_name) in asked
        }

    def defended(self, scenario: Age2ScenarioData) -> set[Age2PlayerData]:
        return {
            player for player in scenario.players
                if player.can_trade_once_defeated
        }

    def worth_waiting_on(self, scenario: Age2ScenarioData) -> set[Age2PlayerData]:
        """The defended owners of each kind of building, where no partner keeps one open: an
        open one already makes the trade."""
        scenario_logic = self.world.rules.logic.for_scenario(scenario)
        waited_on: set[Age2PlayerData] = set()
        for building in (Age2BuildingData.MARKET, Age2BuildingData.DOCK):
            accesses = {player: player.trade_access(building) for player in scenario.players}
            if TradeAccess.OPEN in accesses.values():
                continue
            if self.is_false(scenario_logic.has_seeded_building(building)):
                continue
            waited_on |= {
                player for player, access in accesses.items()
                    if access in (TradeAccess.ONCE_DEFEATED, TradeAccess.GUARDED)
            }
        return waited_on

    def test_allies_never_waits_on_a_defeat(self):
        self.build(partner_trade=PartnerTrade.option_allies)
        for scenario in self.world.rules.logic.scenarios:
            with self.subTest(scenario.scenario.name):
                self.assertEqual(set(), self.defeats_waited_on(scenario.scenario))

    def test_allies_creates_no_defeat_events(self):
        self.build(partner_trade=PartnerTrade.option_allies)
        for scenario in self.world.rules.logic.scenarios:
            scenario_name = scenario.scenario.scenario_name
            for player in scenario.scenario.players:
                with self.subTest(player=player.name):
                    with self.assertRaises(KeyError):
                        self.world.get_location(player.defeat_event(scenario_name))

    def test_allies_and_enemies_waits_on_exactly_the_defended_buildings_owners(self):
        self.build(partner_trade=PartnerTrade.option_allies_and_enemies)
        for scenario in self.world.rules.logic.scenarios:
            with self.subTest(scenario.scenario.name):
                self.assertEqual(
                    self.worth_waiting_on(scenario.scenario),
                    self.defeats_waited_on(scenario.scenario),
                )

    def test_a_defeat_event_holds_exactly_when_its_owner_can_be_defeated(self):
        self.build(partner_trade=PartnerTrade.option_allies_and_enemies)
        for scenario in self.world.rules.logic.scenarios:
            scenario_name = scenario.scenario.scenario_name
            for player in self.defended(scenario.scenario):
                with self.subTest(player=player.name):
                    event = self.world.get_location(player.defeat_event(scenario_name))
                    defeat = self.resolved(scenario.player_logic.defeats(player))
                    self.assertEqual(defeat, event.access_rule)

    def test_an_enemy_market_opens_once_its_owner_is_defeated(self):
        """Genghis 5's only usable markets are the Polish and the German ones."""
        self.build(partner_trade=PartnerTrade.option_allies_and_enemies)
        genghis_5 = Age2ScenarioData.AP_GENGHIS_5
        self.assertEqual(
            {
                Age2PlayerData.GEN5_POLISH,
                Age2PlayerData.GEN5_GERMANS,
            },
            self.defeats_waited_on(genghis_5),
        )
        self.assertFalse(self.is_false(self.economy(genghis_5).can_earn_gold_by_partner_trade()))

    def test_the_english_dock_at_joan_3_stays_closed_to_allies(self):
        self.build(partner_trade=PartnerTrade.option_allies)
        joan_3 = self.economy(Age2ScenarioData.AP_JOAN_3)
        self.assertTrue(self.is_false(joan_3.can_earn_wood_by_partner_trade()))


class TestAffordability(EconomyTestBase):
    def test_a_cost_of_nothing_asks_for_nothing(self):
        """An empty And resolves to False_, not True_ (rule_builder.rules:452), so a unit or
        tech with no cost on file would otherwise be untrainable rather than free."""
        self.build()
        economy = self.economy(Age2ScenarioData.AP_ATTILA_1)
        state = CollectionState(self.multiworld)
        for costs in ({}, {Resource.GOLD: 0}, {Resource.GOLD: 0, Resource.FOOD: 0}):
            with self.subTest(str(costs)):
                self.assertTrue(self.resolved(
                    economy.can_pay(costs))(state))
                self.assertTrue(self.resolved(
                    self.world.rules.logic.resources.has_amounts(costs))(state))
        # can_sustain is asked which resources to keep coming, not what they cost, so the
        # zero-cost filtering happens in can_field and nothing priced at nothing reaches here.
        self.assertTrue(self.resolved(economy.can_sustain(()))(state))


class TestTheQuestionIsShared(EconomyTestBase):
    def test_asking_twice_gives_the_same_answer_object(self):
        self.build()
        scenario = Age2ScenarioData.AP_ATTILA_1
        first = self.resolved(ScenarioHasEasyResource(scenario=scenario, resource=Resource.FOOD))
        second = self.resolved(ScenarioHasEasyResource(scenario=scenario, resource=Resource.FOOD))
        self.assertIs(first, second)

    def test_the_question_answers_what_the_economy_would_have_built(self):
        self.build()
        for scenario in Age2ScenarioData:
            for resource in Resource:
                with self.subTest(f"{scenario.name}.{resource.name}"):
                    question = ScenarioHasEasyResource(scenario=scenario, resource=resource)
                    answer = question.answer(self.world.rules.logic.for_scenario(scenario))
                    self.assertIs(self.resolved(question).answer, self.resolved(answer))

    def test_the_answers_stay_within_budget(self):
        """The cache is meant to grow with the campaigns enabled and no faster. Each one costs
        about three hundred answers - 317 for Attila alone, 594 with Joan, 918 with Genghis - so
        a per-campaign ceiling catches the shape going wrong rather than the world getting bigger.

        Techsanity and unitsanity are off because each sanity asks its own questions of every
        scenario: with their defaults a campaign costs about nine hundred and thirty, still
        linear, but the ceiling is calibrated without them."""
        self.build(techsanity=Techsanity.option_none, unitsanity=Unitsanity.option_none)
        self.assertLess(len(self.world.rules.logic.scenario_answers), 400 * len(self.campaigns))


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
        # can_fish_by_boat is the shared question now; the guard lives in the rule it answers with
        self.assertIsInstance(economy._fish_by_boat(), False_)

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
                if not scenario.fixed_force]

    def easy_answer(self, scenario: Age2ScenarioData, resource: Resource):
        """The whole easy question - gathering, the scenario's declared sources, and trade."""
        question = ScenarioHasEasyResource(scenario=scenario, resource=resource)
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
