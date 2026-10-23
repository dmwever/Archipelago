import unittest
from unittest import mock

from BaseClasses import CollectionState
from rule_builder.rules import True_

from . import bases
from ..Options import BuildingOption, ExistingTechs, ShuffleVillager, Unitsanity
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Locations import Age2ScenarioLocationData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.VillagerJobs import Age2VillagerJobData
from ..logic.scenarios import ScenarioResourceLogic as economy_module

TOWN_CENTER_ITEMS = (
    Age2ItemData.TOWN_CENTER_WOOD.item_name,
    Age2ItemData.TOWN_CENTER_STONE.item_name,
)
VILLAGER_LINE = Age2ItemData.UNIT_LINE_VILLAGER.item_name


class BaseThroughPriceTestBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    def scenario_logic(self, scenario: Age2ScenarioData):
        return self.world.rules.logic.for_scenario(scenario)

    def holds(self, rule, state: CollectionState) -> bool:
        return rule.resolve(self.world)(state)

    def paid_climb(self, scenario: Age2ScenarioData, age: Age2AgeData):
        scenario_logic = self.scenario_logic(scenario)
        return scenario_logic.ages.can_research(age) & scenario_logic.economy.can_pay(age.cost)


class TestAttila1PaysForItsTownCenter(BaseThroughPriceTestBase):
    def setUp(self):
        self.build()
        self.attila_1 = Age2ScenarioData.AP_ATTILA_1
        self.bledas_camp = Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name

    def test_no_feudal_climb_without_the_town_center_items(self):
        state = self.state_without(self.bledas_camp, *TOWN_CENTER_ITEMS)
        self.assertFalse(self.holds(self.paid_climb(self.attila_1, Age2AgeData.FEUDAL), state))

    def test_no_forging_without_the_town_center_items(self):
        state = self.state_without(self.bledas_camp, *TOWN_CENTER_ITEMS)
        forging = self.scenario_logic(self.attila_1).techs.can_research(Age2TechData.FORGING)
        self.assertFalse(self.holds(forging, state))

    def test_the_town_center_items_pay_for_the_climb_and_forging(self):
        state = self.state_without(self.bledas_camp)
        forging = self.scenario_logic(self.attila_1).techs.can_research(Age2TechData.FORGING)
        self.assertTrue(self.holds(self.paid_climb(self.attila_1, Age2AgeData.FEUDAL), state))
        self.assertTrue(self.holds(forging, state))


class TestABaseNeedsTheVillagerLine(BaseThroughPriceTestBase):
    def test_attila_3_has_no_base_before_the_villager_line(self):
        for option in (ShuffleVillager.option_yes, ShuffleVillager.option_include_professions):
            with self.subTest(shuffle_villager=option):
                self.build(shuffle_villager=option)
                has_base = self.scenario_logic(Age2ScenarioData.AP_ATTILA_3).has_base()
                self.assertFalse(self.holds(has_base, self.state_without(VILLAGER_LINE)))
                self.assertTrue(self.holds(has_base, self.state_without()))


class TestAStandingTownCenterIsABase(BaseThroughPriceTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def test_genghis_needs_nothing_to_build_a_base_it_starts_with(self):
        self.build(
            shuffle_villager=ShuffleVillager.option_include_professions,
            shuffle_buildings={BuildingOption.base},
        )
        building_items = (
            Age2VillagerJobData.BUILDER_MALE.item.item_name,
            Age2BuildingData.TOWN_CENTER.item.item_name,
            Age2BuildingData.HOUSE.item.item_name,
        )
        state = self.state_without(*building_items)
        for scenario in (
            Age2ScenarioData.AP_GENGHIS_4,
            Age2ScenarioData.AP_GENGHIS_5,
            Age2ScenarioData.AP_GENGHIS_6,
        ):
            with self.subTest(scenario.name):
                self.assertTrue(self.holds(self.scenario_logic(scenario).has_base(), state))


class TestEasyFoodNeedsABase(BaseThroughPriceTestBase):
    def raw_or_endless_food(self, scenario: Age2ScenarioData):
        return self.scenario_logic(scenario).economy.has_own_easy_source(Resource.FOOD)

    def test_no_raw_food_without_the_villager_line(self):
        self.build(shuffle_villager=ShuffleVillager.option_yes)
        food = self.raw_or_endless_food(Age2ScenarioData.AP_ATTILA_3)
        self.assertFalse(self.holds(food, self.state_without(VILLAGER_LINE)))
        self.assertTrue(self.holds(food, self.state_without()))

    def test_endless_food_asks_no_base_of_its_own(self):
        self.build(shuffle_villager=ShuffleVillager.option_yes)
        with mock.patch.object(economy_module.ScenarioResourceLogic, "endless_food",
                               return_value=True_()):
            food = self.raw_or_endless_food(Age2ScenarioData.AP_ATTILA_3)
        self.assertTrue(self.holds(food, self.state_without(VILLAGER_LINE)))


class TestJoan3ClimbsOnlyAcrossTheWater(BaseThroughPriceTestBase):
    def test_no_feudal_climb_without_boats(self):
        self.build(
            existing_techs=ExistingTechs.option_start_in_dark_age,
            unitsanity=Unitsanity.option_all,
        )
        state = self.state_without(
            Age2ItemData.AP_JOAN_3_TRANSPORT.item_name,
            Age2ItemData.UNIT_LINE_TRANSPORT_SHIP.item_name,
        )
        feudal_climb = self.paid_climb(Age2ScenarioData.AP_JOAN_3, Age2AgeData.FEUDAL)
        self.assertFalse(self.holds(feudal_climb, state))
        self.assertTrue(self.holds(feudal_climb, self.state_without()))


class TestAttila2RaisesATownCenterWithItsItems(BaseThroughPriceTestBase):
    def location_holds(self, location: Age2ScenarioLocationData, *item_names: str) -> bool:
        state = CollectionState(self.multiworld)
        for item_name in item_names:
            state.collect(self.world.create_item(item_name), prevent_sweep=True)
        return self.world.get_location(location.global_name()).access_rule(state)

    def test_the_builder_and_the_town_center_items_are_all_it_takes(self):
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        builder = Age2VillagerJobData.BUILDER_MALE.item.item_name
        build_tc = Age2ScenarioLocationData.ATT2_BUILD_TC
        purple_vils = self.scenario_logic(Age2ScenarioData.AP_ATTILA_2).starting_state.has_vils
        vils = sorted(purple_vils.resolve(self.world).item_dependencies())
        self.assertTrue(self.location_holds(build_tc, builder, *TOWN_CENTER_ITEMS, *vils))
        self.assertFalse(self.location_holds(build_tc, *TOWN_CENTER_ITEMS, *vils))
        for withheld in TOWN_CENTER_ITEMS:
            with self.subTest(withheld=withheld):
                kept = [item for item in TOWN_CENTER_ITEMS if item != withheld]
                self.assertFalse(self.location_holds(build_tc, builder, *kept, *vils))


if __name__ == "__main__":
    unittest.main()
