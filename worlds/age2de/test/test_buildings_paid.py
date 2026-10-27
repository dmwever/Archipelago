import inspect
import unittest
from unittest import mock

from BaseClasses import CollectionState
from rule_builder.rules import False_, Rule

from . import bases
from .. import Age2World
from ..Options import BuildingOption, ScenarioBranching
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Locations import Age2ScenarioLocationData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.UnitLines import Age2UnitLineData
from ..logic.ScenarioLogic import ScenarioLogic
from ..locations.Units import Age2UnitData
from ..logic.custom_logic.ScenarioQuestions import ScenarioHasEasyResource, ScenarioQuestion
from ..rules.attila_rules.attila_4 import Attila4Rules

TOWN_CENTER_ITEMS = (
    Age2ItemData.TOWN_CENTER_WOOD.item_name,
    Age2ItemData.TOWN_CENTER_STONE.item_name,
)
BLEDAS_CAMP = Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name
ADVANCED_AGES = (Age2AgeData.FEUDAL, Age2AgeData.CASTLE, Age2AgeData.IMPERIAL)


def starving(*resources: Resource) -> mock._patch:
    answer = ScenarioHasEasyResource.answer

    def starved_answer(question: ScenarioHasEasyResource, scenario: ScenarioLogic) -> Rule:
        if question.resource in resources:
            return False_()
        return answer(question, scenario)

    return mock.patch.object(ScenarioHasEasyResource, "answer", starved_answer)


def asks_easy_stone(rule: Rule.Resolved, seen: dict[int, bool]) -> bool:
    if id(rule) in seen:
        return seen[id(rule)]
    seen[id(rule)] = False
    if isinstance(rule, ScenarioQuestion.Resolved) and rule.description.endswith("can easily gather stone"):
        seen[id(rule)] = True
        return True
    parts = [*getattr(rule, "children", ())]
    for name in ("child", "answer"):
        if hasattr(rule, name):
            parts.append(getattr(rule, name))
    seen[id(rule)] = any(asks_easy_stone(part, seen) for part in parts)
    return seen[id(rule)]


class BuildingsPaidTestBase(bases.Age2RuleTestBase):
    def build_starving(self, *resources: Resource, **options) -> Age2World:
        with starving(*resources):
            return self.build(**options)

    def scenario_logic(self, scenario: Age2ScenarioData) -> ScenarioLogic:
        return self.world.rules.logic.for_scenario(scenario)

    def holds(self, rule: Rule, state: CollectionState) -> bool:
        return rule.resolve(self.world)(state)

    def easy(self, scenario: Age2ScenarioData, resource: Resource, state: CollectionState) -> bool:
        return self.holds(self.scenario_logic(scenario).economy.has_easy_source(resource), state)

    def asks_easy_stone(self, rule: Rule, seen: dict[int, bool]) -> bool:
        return asks_easy_stone(rule.resolve(self.world), seen)


class TestAttila1PaysForItsAgeUpBuildings(BuildingsPaidTestBase):
    def setUp(self):
        self.build_starving(Resource.WOOD)
        self.attila_1 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_1)
        self.state = self.state_without(BLEDAS_CAMP)

    def test_no_wood_is_no_paid_feudal_advance(self):
        self.assertFalse(self.easy(Age2ScenarioData.AP_ATTILA_1, Resource.WOOD, self.state))
        self.assertTrue(self.easy(Age2ScenarioData.AP_ATTILA_1, Resource.FOOD, self.state))
        self.assertFalse(self.holds(self.attila_1.ages.can_reach(Age2AgeData.FEUDAL), self.state))

    def test_no_wood_is_no_forging(self):
        forging = self.attila_1.techs.can_research(Age2TechData.FORGING)
        self.assertFalse(self.holds(forging, self.state))

    def test_the_structural_advance_is_unchanged(self):
        structural = self.attila_1.ages.can_research_structurally(Age2AgeData.FEUDAL)
        self.assertTrue(self.holds(structural, self.state))
        self.assertTrue(self.holds(self.attila_1.ages.can_reach_structurally(Age2AgeData.FEUDAL),
                                   self.state))


class TestBledasCampAdvancesWithoutATownCenter(BuildingsPaidTestBase):
    def test_the_paid_advance_needs_no_town_center_items_and_no_easy_stone(self):
        self.build_starving(Resource.STONE)
        attila_1 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_1)
        state = self.state_without(*TOWN_CENTER_ITEMS)
        self.assertFalse(self.easy(Age2ScenarioData.AP_ATTILA_1, Resource.STONE, state))
        self.assertTrue(self.holds(attila_1.ages.can_reach(Age2AgeData.FEUDAL), state))


class TestNoPaidAgeAsksStoneForATownCenter(BuildingsPaidTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def paid_ages(self) -> dict[tuple[Age2ScenarioData, Age2AgeData], bool]:
        state = self.state_without()
        return {
            (scenario.scenario, age): self.holds(scenario.ages.can_reach(age), state)
            for scenario in self.world.rules.logic.scenarios
            for age in ADVANCED_AGES
        }

    def test_starving_stone_moves_no_paid_age(self):
        self.build()
        fed = self.paid_ages()
        self.build_starving(Resource.STONE)
        self.assertEqual(fed, self.paid_ages())


class TestAMilitiaNeedsAPaidBarracks(BuildingsPaidTestBase):
    def test_no_wood_and_no_standing_barracks_fields_no_militia(self):
        self.build_starving(Resource.WOOD)
        attila_1 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_1)
        state = self.state_without(BLEDAS_CAMP)
        militia = Age2UnitLineData.MILITIA_LINE
        self.assertFalse(self.holds(attila_1.starting_state.starts_with_building[Age2BuildingData.BARRACKS],
                                    state))
        self.assertFalse(self.holds(attila_1.units.can_field(militia, Age2AgeData.DARK), state))
        self.assertTrue(self.holds(attila_1.units.can_field_structurally(militia, Age2AgeData.DARK),
                                   state))


class TestAttila4AlliesWithBurgundyAtAPaidCastle(BuildingsPaidTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def ally(self, state: CollectionState) -> bool:
        location = Age2ScenarioLocationData.ATT4_CASTLE_BURGUNDY_ALL
        return self.world.get_location(location.global_name()).access_rule(state)

    def tribute(self, state: CollectionState) -> bool:
        location = Age2ScenarioLocationData.ATT4_TRIBUTE_BURGUNDY_ALL
        return self.world.get_location(location.global_name()).access_rule(state)

    def test_burgundy_is_allied_with_everything(self):
        self.build(scenario_branching=ScenarioBranching.option_all)
        self.assertTrue(self.ally(self.state_without()))
        self.assertTrue(self.tribute(self.state_without()))

    def test_no_easy_gold_is_no_alliance(self):
        self.build_starving(Resource.GOLD, scenario_branching=ScenarioBranching.option_all)
        self.assertFalse(self.ally(self.state_without()))

    def test_no_easy_gold_is_no_tribute(self):
        self.build_starving(Resource.GOLD, scenario_branching=ScenarioBranching.option_all)
        self.assertFalse(self.tribute(self.state_without()))

    def test_no_easy_wood_is_no_alliance(self):
        self.build_starving(Resource.WOOD, scenario_branching=ScenarioBranching.option_all)
        self.assertFalse(self.ally(self.state_without()))

    def test_no_easy_stone_is_no_alliance(self):
        self.build_starving(Resource.STONE, scenario_branching=ScenarioBranching.option_all)
        self.assertFalse(self.ally(self.state_without()))

    def test_no_castle_in_attila_4_is_no_alliance(self):
        attila_4 = Age2ScenarioData.AP_ATTILA_4
        excluded = [*attila_4.excluded_buildings, Age2BuildingData.CASTLE]
        with mock.patch.object(attila_4, "excluded_buildings", excluded):
            self.build(scenario_branching=ScenarioBranching.option_all)
            self.assertFalse(self.ally(self.state_without()))

    def test_the_tribute_needs_no_castle_and_no_easy_stone(self):
        attila_4 = Age2ScenarioData.AP_ATTILA_4
        excluded = [*attila_4.excluded_buildings, Age2BuildingData.CASTLE]
        with mock.patch.object(attila_4, "excluded_buildings", excluded):
            self.build_starving(Resource.STONE, scenario_branching=ScenarioBranching.option_all)
            self.assertFalse(self.ally(self.state_without()))
            self.assertTrue(self.tribute(self.state_without()))

    def test_the_alliance_asks_no_base_directly(self):
        self.assertNotIn("has_base", inspect.getsource(Attila4Rules.set_rules))


class TestATownCenterIsPaidByItsItems(BuildingsPaidTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def setUp(self):
        self.build(shuffle_buildings={BuildingOption.base})

    def build_town_center(self, state: CollectionState) -> bool:
        location = Age2BuildingData.TOWN_CENTER.location_name
        return self.world.get_location(location).access_rule(state)

    def test_building_a_town_center_needs_both_town_center_items(self):
        self.assertTrue(self.build_town_center(self.state_without()))
        for withheld in TOWN_CENTER_ITEMS:
            with self.subTest(withheld=withheld):
                self.assertFalse(self.build_town_center(self.state_without(withheld)))

    def test_a_standing_town_center_still_needs_the_items_for_another(self):
        attila_3 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_3)
        build = attila_3.buildings.can_build(Age2BuildingData.TOWN_CENTER)
        self.assertTrue(self.holds(build, self.state_without()))
        for withheld in TOWN_CENTER_ITEMS:
            with self.subTest(withheld=withheld):
                self.assertFalse(self.holds(build, self.state_without(withheld)))

    def test_a_base_without_a_standing_town_center_needs_both_town_center_items(self):
        for withheld in TOWN_CENTER_ITEMS:
            state = self.state_without(withheld)
            for scenario in self.world.rules.logic.scenarios:
                standing = scenario.starting_state.starts_with_building[Age2BuildingData.TOWN_CENTER]
                if self.holds(standing, state):
                    continue
                with self.subTest(scenario=scenario.scenario.name, withheld=withheld):
                    self.assertFalse(self.holds(scenario.has_base(), state))

    def test_a_town_center_never_asks_easy_stone(self):
        seen: dict[int, bool] = {}
        location = self.world.get_location(Age2BuildingData.TOWN_CENTER.location_name)
        self.assertFalse(asks_easy_stone(location.access_rule, seen))
        town_center = Age2BuildingData.TOWN_CENTER
        for scenario in self.world.rules.logic.scenarios:
            rules = {
                "has_building": scenario.has_building(town_center),
                "has_building_structurally": scenario.has_building_structurally(town_center),
                "can_build": scenario.buildings.can_build(town_center),
                "can_build_structurally": scenario.buildings.can_build_structurally(town_center),
            }
            for name, rule in rules.items():
                with self.subTest(scenario=scenario.scenario.name, rule=name):
                    self.assertFalse(self.asks_easy_stone(rule, seen))


class TestNothingUnpaidAsksEasyStone(BuildingsPaidTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def structural_rules(self, scenario: ScenarioLogic) -> dict[str, Rule]:
        rules: dict[str, Rule] = {
            "has_base": scenario.has_base(),
            "can_have_base": scenario.can_have_base(),
        }
        for age in Age2AgeData:
            rules[f"can_research_structurally {age.name}"] = (
                scenario.ages.can_research_structurally(age))
            rules[f"can_reach_structurally {age.name}"] = scenario.ages.can_reach_structurally(age)
        for building in Age2BuildingData:
            rules[f"can_build_structurally {building.name}"] = scenario.buildings.can_build_structurally(building)
            rules[f"has_building_structurally {building.name}"] = scenario.has_building_structurally(building)
        for tech in Age2TechData:
            rules[f"can_research_structurally {tech.name}"] = scenario.techs.can_research_structurally(tech)
        for unit in Age2UnitData:
            rules[f"can_train_structurally {unit.name}"] = scenario.units.can_train_structurally(unit)
        for line in Age2UnitLineData:
            rules[f"can_field_structurally {line.name}"] = scenario.units.can_field_structurally(line)
            for age in Age2AgeData:
                rules[f"can_field_structurally {line.name} {age.name}"] = (
                    scenario.units.can_field_structurally(line, age))
        return rules

    def test_no_base_or_structural_form_asks_easy_stone(self):
        self.build()
        seen: dict[int, bool] = {}
        stone = self.scenario_logic(Age2ScenarioData.AP_ATTILA_1).economy.has_easy_source(Resource.STONE)
        self.assertTrue(self.asks_easy_stone(stone, seen))
        for scenario in self.world.rules.logic.scenarios:
            stony = [name for name, rule in self.structural_rules(scenario).items()
                     if self.asks_easy_stone(rule, seen)]
            with self.subTest(scenario=scenario.scenario.name):
                self.assertEqual([], stony)


if __name__ == "__main__":
    unittest.main()
