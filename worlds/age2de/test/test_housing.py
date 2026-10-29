import unittest

from BaseClasses import CollectionState
from rule_builder.rules import Rule

from . import bases
from ..generation import LocalStart
from ..items.Items import Age2ItemData, Resource, Resources, SeedResources
from ..locations.Buildings import BuildingOption
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Units import Age2UnitData
from ..logic.custom_logic.EconomyRoutes import RouteResource, Strength, Yield
from ..Options import MarketTrade, PartnerTrade

HOUSE = Age2ItemData.HOUSE.item_name
ORLEANS = Age2ItemData.AP_JOAN_2_ORLEANS.item_name
FRENCH_CAMP = Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name
SHUFFLED = {
    BuildingOption.base,
    BuildingOption.economy,
    BuildingOption.tech,
    BuildingOption.military,
}
HOUSING = RouteResource.HOUSING
ALL_CAMPAIGNS = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]


class HousingBase(bases.Age2RuleTestBase):
    campaigns = ALL_CAMPAIGNS
    starting_campaigns = ALL_CAMPAIGNS

    def build_shuffled(self, **options):
        return self.build(shuffle_buildings=SHUFFLED, **options)

    def scenario(self, scenario: Age2ScenarioData):
        return self.world.rules.logic.for_scenario(scenario)

    def holds(self, rule: Rule, state: CollectionState) -> bool:
        return bool(rule.resolve(self.world)(state))

    def housing(self, scenario: Age2ScenarioData, strength: Strength) -> Rule:
        return self.scenario(scenario).economy.has_housing(strength)

    def economy(self, scenario: Age2ScenarioData):
        return self.scenario(scenario).economy.has_economy_routes().resolve(self.world)

    def running(self, scenario: Age2ScenarioData, state: CollectionState) -> set[str]:
        economy = self.economy(scenario)
        return {economy.routes[index].name for index in economy.running(state)}

    def needs(self, scenario: Age2ScenarioData) -> dict[str, dict[Yield, Strength]]:
        return {route.name: dict(route.needs)
                for route in self.scenario(scenario).routes.economy_routes().routes}

    def housing_producers(self, scenario: Age2ScenarioData, strength: Strength) -> set[str]:
        economy = self.economy(scenario)
        return {
            economy.routes[index].name for index in economy.possible
                if economy.routes[index].is_yielding_resource_at_strength(HOUSING, strength)
        }


class TestAStandingTownCenterStillAsksTheHouse(HousingBase):

    ROUTE = "Villagers gathering gold with a Base"

    def gathering_gold(self, state: CollectionState) -> set[str]:
        return {name for name in self.running(Age2ScenarioData.AP_GENGHIS_5, state)
                if name.startswith(self.ROUTE)}

    def test_genghis_5_gathers_no_gold_at_scale_without_the_house(self):
        self.build_shuffled()
        self.assertEqual(set(), self.gathering_gold(self.state_without(HOUSE)))

    def test_and_does_with_the_house_and_some_wood(self):
        self.build_shuffled()
        state = self.state_without()
        self.assertNotEqual(set(), self.gathering_gold(state))
        self.assertTrue(self.holds(
            self.scenario(Age2ScenarioData.AP_GENGHIS_5).economy.has_some_source(Resource.WOOD),
            state,
        ))

    def test_the_route_needs_housing_at_scale(self):
        self.build_shuffled()
        needs = self.needs(Age2ScenarioData.AP_GENGHIS_5)
        gathering = {name: route for name, route in needs.items() if name.startswith(self.ROUTE)}
        self.assertGreater(len(gathering), 3)
        self.assertEqual([], [name for name, route in gathering.items()
                              if route.get(HOUSING) != Strength.AT_SCALE])


class TestTheHunsNeedNoHouse(HousingBase):

    def test_attila_3_runs_its_villagers_at_scale_with_no_house(self):
        self.build_shuffled()
        running = self.running(Age2ScenarioData.AP_ATTILA_3, self.state_without(HOUSE))
        self.assertIn("Builds no Houses", running)
        self.assertNotEqual(set(), {name for name in running if "with a Base" in name})


class TestJoan2IsGrantedHousingByOrleans(HousingBase):

    def test_orleans_houses_an_at_scale_route_with_no_house(self):
        self.build_shuffled()
        state = self.state_without(HOUSE)
        self.assertTrue(self.holds(self.housing(Age2ScenarioData.AP_JOAN_2, Strength.AT_SCALE),
                                   state))
        self.assertNotEqual(set(), {name for name in self.running(Age2ScenarioData.AP_JOAN_2, state)
                                    if "with a Base" in name})

    def test_without_orleans_only_the_houses_route_houses_it(self):
        self.build_shuffled()
        self.assertEqual({"its own housing", "Houses"},
                         self.housing_producers(Age2ScenarioData.AP_JOAN_2, Strength.AT_SCALE))
        self.assertFalse(self.holds(self.housing(Age2ScenarioData.AP_JOAN_2, Strength.AT_SCALE),
                                    self.state_without(HOUSE, ORLEANS)))


class TestASingleUnitNeedsSomeHousing(HousingBase):

    def can_train(self, scenario: Age2ScenarioData, unit: Age2UnitData) -> Rule:
        return self.scenario(scenario).units.can_train(unit)

    def test_joan_4_houses_it_with_the_camp_or_the_houses_route(self):
        self.build_shuffled()
        self.assertEqual({"a little of its own housing", "Houses"},
                         self.housing_producers(Age2ScenarioData.AP_JOAN_4, Strength.SOME))
        some = self.housing(Age2ScenarioData.AP_JOAN_4, Strength.SOME)
        self.assertTrue(self.holds(some, self.state_without(HOUSE)))
        self.assertFalse(self.holds(some, self.state_without(HOUSE, FRENCH_CAMP)))

    def test_genghis_2_trains_one_from_the_start_with_no_house(self):
        self.build_shuffled()
        self.assertTrue(self.holds(self.housing(Age2ScenarioData.AP_GENGHIS_2, Strength.SOME),
                                   self.state_with()))
        self.assertTrue(self.holds(self.can_train(Age2ScenarioData.AP_GENGHIS_2, Age2UnitData.MILITIA),
                                   self.state_without(HOUSE)))

    def test_joan_3_and_genghis_3_need_the_houses_route(self):
        self.build_shuffled()
        for scenario in (Age2ScenarioData.AP_JOAN_3, Age2ScenarioData.AP_GENGHIS_3):
            with self.subTest(scenario=scenario.name):
                self.assertEqual({"Houses"}, self.housing_producers(scenario, Strength.SOME))
                train = self.can_train(scenario, Age2UnitData.MILITIA)
                self.assertTrue(self.holds(train, self.state_without()))
                self.assertFalse(self.holds(train, self.state_without(HOUSE)))


class TestRelicsHouseOnlyATrainedMonk(HousingBase):

    def test_a_standing_monk_needs_no_housing_and_a_trained_one_some(self):
        self.build_shuffled(partner_trade=PartnerTrade.option_allies_and_enemies)
        relics = {name: needs for name, needs in self.needs(Age2ScenarioData.AP_ATTILA_3).items()
                  if name.startswith("Relics")}
        standing = {name: needs for name, needs in relics.items() if "standing Monk" in name}
        trained = {name: needs for name, needs in relics.items() if "standing Monk" not in name}
        self.assertEqual(4, len(standing))
        self.assertEqual(4, len(trained))
        self.assertEqual([], [name for name, needs in standing.items() if HOUSING in needs])
        self.assertEqual([], [name for name, needs in trained.items()
                              if needs.get(HOUSING) != Strength.SOME])


class TestNoItemYieldsHousing(HousingBase):

    def test_market_trade_yields_no_housing(self):
        self.build_shuffled(market_trade=MarketTrade.option_true)
        market = [route for route in self.scenario(Age2ScenarioData.AP_ATTILA_2).routes.market_routes()]
        self.assertEqual(3, len(market))
        self.assertEqual([], [route.name for route in market if HOUSING in route.yields])

    def test_every_route_resource_an_item_carries_is_an_item_resource(self):
        self.build_shuffled()
        carried = {item.type.type for item in Age2ItemData
                   if isinstance(item.type, (Resources, SeedResources))}
        self.assertLessEqual(carried, set(Resource))
        self.assertNotIn(HOUSING, carried)
        self.assertLessEqual(set(self.world.pool.resources.totals), set(Resource))


class TestTheBaseAsksNoHouse(HousingBase):

    def asked(self, rule: Rule) -> set[str]:
        return set(rule.resolve(self.world).item_dependencies())

    def test_can_build_base_asks_no_house(self):
        self.build_shuffled()
        for scenario in (Age2ScenarioData.AP_JOAN_3, Age2ScenarioData.AP_GENGHIS_3):
            with self.subTest(scenario=scenario.name):
                self.assertNotIn(HOUSE, self.asked(self.scenario(scenario).buildings.can_build_base()))

    def test_local_start_still_asks_the_house_where_the_civilisation_builds_one(self):
        self.build_shuffled()
        self.assertIn(HOUSE, self.asked(LocalStart.base_target(self.world, Age2ScenarioData.AP_JOAN_3)))
        self.assertNotIn(HOUSE, self.asked(LocalStart.base_target(self.world, Age2ScenarioData.AP_ATTILA_1)))


class TestTheHousingProducersAreUngated(HousingBase):

    PRODUCERS = ("Houses", "Builds no Houses", "its own housing", "a little of its own housing")

    def test_every_producer_is_in_the_ungated_layer(self):
        self.build_shuffled()
        for scenario in self.world.rules.logic.scenarios:
            with self.subTest(scenario.scenario.name):
                ungated = [route.name for route in scenario.routes.ungated_routes()]
                self.assertEqual([], [name for name in self.PRODUCERS if name not in ungated])

    def test_every_scenario_answers_housing_at_both_strengths(self):
        self.build_shuffled()
        logic = self.world.rules.logic
        state = self.state_without()
        for scenario in logic.scenarios:
            for strength in Strength:
                with self.subTest(scenario=scenario.scenario.name, strength=strength.name):
                    scenario.economy.has_housing(strength).resolve(self.world)(state)
        self.assertEqual(set(), logic.scenario_answers_open)


if __name__ == "__main__":
    unittest.main()
