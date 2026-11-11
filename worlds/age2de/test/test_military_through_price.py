import inspect
import unittest
from unittest import mock

from BaseClasses import CollectionState
from rule_builder.rules import False_, Rule

from . import bases
from ..Options import MarketTrade, PartnerTrade, ShuffleVillager
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from ..locations.connections.ScenarioPlayers import SCENARIO_TO_PLAYERS
from ..logic.ScenarioLogic import ScenarioLogic, ScenarioStartingState
from ..logic.scenarios.ScenarioUnitLogic import ScenarioUnitLogic

VILLAGER_ITEMS = (
    Age2ItemData.UNIT_LINE_VILLAGER.item_name,
    *(job.item.item_name for job in Age2VillagerJobData),
)
SHUFFLED_VILLAGERS = (ShuffleVillager.option_yes, ShuffleVillager.option_include_professions)
ALL_CAMPAIGNS = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]


def starting_states(cls: type) -> list[type]:
    return [state for subclass in cls.__subclasses__() for state in (subclass, *starting_states(subclass))]


class MilitaryThroughPriceTestBase(bases.Age2RuleTestBase):
    def scenario_logic(self, scenario: Age2ScenarioData) -> ScenarioLogic:
        return self.world.rules.logic.for_scenario(scenario)

    def holds(self, rule: Rule, state: CollectionState) -> bool:
        return rule.resolve(self.world)(state)


class TestNoMilitaryQuestionAsksABaseDirectly(unittest.TestCase):
    def test_fielding_asks_no_base_in_either_form(self):
        self.assertNotIn("has_base", inspect.getsource(ScenarioUnitLogic._field))

    def test_no_defeat_rules_asks_a_base(self):
        overrides = [state for state in starting_states(ScenarioStartingState)
                     if "defeat_rules" in vars(state)]
        self.assertGreaterEqual(len(overrides), 14)
        for state in overrides:
            with self.subTest(state.__name__):
                self.assertNotIn("has_base", inspect.getsource(state.defeat_rules))


class TestAttila3MonkWithoutVillagers(MilitaryThroughPriceTestBase):
    def test_the_monk_is_not_fielded_in_the_castle_age(self):
        for option in SHUFFLED_VILLAGERS:
            with self.subTest(shuffle_villager=option):
                self.build(shuffle_villager=option)
                attila_3 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_3)
                state = self.state_without(*VILLAGER_ITEMS)
                self.assertFalse(self.holds(attila_3.has_base(), state))
                self.assertTrue(self.holds(attila_3.economy.has_easy_source(Resource.GOLD), state))
                self.assertFalse(self.holds(attila_3.economy.has_easy_source(Resource.WOOD), state))
                self.assertFalse(self.holds(attila_3.units.can_pay_for_training_building(Age2UnitData.MONK),
                                            state))
                monk = attila_3.units.can_field(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE)
                self.assertFalse(self.holds(monk, state))


class TestAFoodUnitBringsTheBase(MilitaryThroughPriceTestBase):
    def test_no_base_fields_no_scout_cavalry(self):
        for option in SHUFFLED_VILLAGERS:
            with self.subTest(shuffle_villager=option):
                self.build(shuffle_villager=option)
                attila_3 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_3)
                state = self.state_without(*VILLAGER_ITEMS)
                self.assertFalse(self.holds(attila_3.has_base(), state))
                self.assertFalse(self.holds(attila_3.economy.has_easy_source(Resource.FOOD), state))
                scouts = Age2UnitLineData.SCOUT_CAVALRY_LINE
                tiers = attila_3.units.fieldable_tiers(scouts, Age2AgeData.CASTLE)
                self.assertTrue(any(self.holds(attila_3.units.can_train_structurally(tier), state)
                                    for tier in tiers))
                self.assertFalse(self.holds(attila_3.units.can_field(scouts, Age2AgeData.CASTLE), state))


def no_base(scenario: ScenarioLogic) -> Rule:
    return False_()


def no_fielding(units: ScenarioUnitLogic, line: Age2UnitLineData, age: Age2AgeData | None, paid: bool) -> Rule:
    return False_()


class TestNoMilitaryDefeatWithoutABase(MilitaryThroughPriceTestBase):
    campaigns = ALL_CAMPAIGNS
    starting_campaigns = ALL_CAMPAIGNS

    def defeats(self, **options) -> dict[str, bool]:
        self.build(**options)
        state = self.state_without()
        defeats = {}
        for scenario in SCENARIO_TO_PLAYERS:
            scenario_logic = self.scenario_logic(scenario)
            for player in scenario_logic.starting_state.defeat_rules(scenario_logic):
                defeat = scenario_logic.player_logic.defeats(player)
                defeats[f"{scenario.name} {player.name}"] = self.holds(defeat, state)
        return defeats

    def test_with_partner_trade_off_every_military_defeat_needs_a_base(self):
        for market_trade in (MarketTrade.option_false, MarketTrade.option_true):
            options = {"partner_trade": PartnerTrade.option_none, "market_trade": market_trade}
            with self.subTest(market_trade=market_trade):
                with mock.patch.object(ScenarioUnitLogic, "_field", no_fielding):
                    without_military = self.defeats(**options)
                with mock.patch.object(ScenarioLogic, "has_base", no_base):
                    without_base = self.defeats(**options)
                needing_military = [name for name, holds in without_military.items() if not holds]
                self.assertGreater(len(needing_military), 30)
                for name in needing_military:
                    with self.subTest(name):
                        self.assertFalse(without_base[name])


if __name__ == "__main__":
    unittest.main()
