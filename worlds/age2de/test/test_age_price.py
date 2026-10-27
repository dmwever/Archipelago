import contextlib
import unittest
from typing import Callable, Iterator
from unittest import mock

from BaseClasses import CollectionState
from rule_builder.rules import False_, Rule

from . import bases
from .. import Age2World
from ..Options import ExistingTechs, ShuffleVillager
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Locations import Age2ScenarioLocationData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from ..logic.ScenarioLogic import ScenarioLogic
from ..logic.custom_logic.ScenarioQuestions import ScenarioHasEasyResource, ScenarioHasSomeResource

ALL_RESOURCES = (Resource.FOOD, Resource.WOOD, Resource.GOLD, Resource.STONE)
BLEDAS_CAMP = Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name
ATTILAS_CAMP = Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name
START_IN_DARK_AGE = {"existing_techs": ExistingTechs.option_start_in_dark_age}
CASTLES = (
    Age2ScenarioLocationData.GEN5_BUILD_ONE_CASTLE,
    Age2ScenarioLocationData.GEN5_BUILD_TWO_CASTLES,
    Age2ScenarioLocationData.GEN5_BUILD_THREE_CASTLES,
)


def starved(question: type, resources: tuple[Resource, ...]) -> mock._patch:
    answer = question.answer

    def starved_answer(asked, scenario: ScenarioLogic) -> Rule:
        if asked.resource in resources:
            return False_()
        return answer(asked, scenario)

    return mock.patch.object(question, "answer", starved_answer)


@contextlib.contextmanager
def starving(easy: tuple[Resource, ...] = (), some: tuple[Resource, ...] = ()) -> Iterator[None]:
    with starved(ScenarioHasEasyResource, easy), starved(ScenarioHasSomeResource, some):
        yield


class AgePriceTestBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def build_starving(
        self,
        easy: tuple[Resource, ...] = (),
        some: tuple[Resource, ...] = (),
        **options,
    ) -> Age2World:
        with starving(easy, some):
            return self.build(**options)

    def scenario_logic(self, scenario: Age2ScenarioData) -> ScenarioLogic:
        return self.world.rules.logic.for_scenario(scenario)

    def holds(self, rule: Rule, state: CollectionState) -> bool:
        return rule.resolve(self.world)(state)

    def location_holds(self, location: Age2ScenarioLocationData, state: CollectionState) -> bool:
        return self.world.get_location(location.global_name()).access_rule(state)

    def has_easy(self, scenario: Age2ScenarioData, resource: Resource, state: CollectionState) -> bool:
        return self.holds(self.scenario_logic(scenario).economy.has_easy_source(resource), state)

    def has_some(self, scenario: Age2ScenarioData, resource: Resource, state: CollectionState) -> bool:
        return self.holds(self.scenario_logic(scenario).economy.has_some_source(resource), state)


class TestReachingAnAgePaysTheAgePrice(AgePriceTestBase):
    def test_feudal_is_reached_with_some_food_and_no_easy_food(self):
        self.build_starving(easy=(Resource.FOOD,))
        state = self.state_without()
        self.assertFalse(self.has_easy(Age2ScenarioData.AP_ATTILA_1, Resource.FOOD, state))
        self.assertTrue(self.has_some(Age2ScenarioData.AP_ATTILA_1, Resource.FOOD, state))
        self.assertTrue(self.can_reach(Age2AgeData.FEUDAL.location_name, state))

    def test_castle_is_reached_with_easy_food_and_some_gold_but_no_easy_gold(self):
        self.build_starving(easy=(Resource.GOLD,))
        state = self.state_without()
        self.assertFalse(self.has_easy(Age2ScenarioData.AP_ATTILA_1, Resource.GOLD, state))
        self.assertTrue(self.has_easy(Age2ScenarioData.AP_ATTILA_1, Resource.FOOD, state))
        self.assertTrue(self.has_some(Age2ScenarioData.AP_ATTILA_1, Resource.GOLD, state))
        self.assertTrue(self.can_reach(Age2AgeData.CASTLE.location_name, state))

    def test_no_food_at_all_reaches_no_feudal(self):
        self.build_starving(easy=(Resource.FOOD,), some=(Resource.FOOD,))
        self.assertFalse(self.can_reach(Age2AgeData.FEUDAL.location_name, self.state_without()))


class TestACastleStartPaysNoFeudalOrCastlePrice(AgePriceTestBase):
    def attila_3_holds(
        self,
        site: Callable[[ScenarioLogic], Rule],
        easy: tuple[Resource, ...] = (),
        some: tuple[Resource, ...] = (),
        **options,
    ) -> bool:
        self.build_starving(easy, some, **options)
        attila_3 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_3)
        return self.holds(site(attila_3), self.state_without())

    def answers(self, **options) -> dict[str, bool]:
        return {
            "build": self.attila_3_holds(
                lambda attila_3: attila_3.buildings.can_build(Age2BuildingData.UNIVERSITY),
                some=(Resource.FOOD, Resource.GOLD),
                **options,
            ),
            "research": self.attila_3_holds(
                lambda attila_3: attila_3.techs.can_research(Age2TechData.HUSBANDRY),
                some=(Resource.FOOD, Resource.GOLD),
                **options,
            ),
            "train past the Feudal price": self.attila_3_holds(
                lambda attila_3: attila_3.units.can_train(Age2UnitData.ARCHER),
                some=(Resource.FOOD,),
                **options,
            ),
            "train past the Castle price": self.attila_3_holds(
                lambda attila_3: attila_3.units.can_train(Age2UnitData.CAVALRY_ARCHER),
                easy=(Resource.FOOD,),
                **options,
            ),
        }

    def test_build_tech_and_unit_ask_no_age_price_where_the_scenario_starts_past_it(self):
        self.assertEqual(
            {
                "build": True,
                "research": True,
                "train past the Feudal price": True,
                "train past the Castle price": True,
            },
            self.answers(),
        )

    def test_the_same_advanced_from_the_dark_age_pays_the_price(self):
        self.assertEqual(
            {
                "build": False,
                "research": False,
                "train past the Feudal price": False,
                "train past the Castle price": False,
            },
            self.answers(**START_IN_DARK_AGE),
        )


class TestTheCastleLocationsPayForTheCastle(AgePriceTestBase):
    campaigns = ["Attila the Hun", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Genghis Khan"]

    def test_attila_3_builds_its_castle_in_logic_when_fed(self):
        self.build(**START_IN_DARK_AGE)
        self.assertTrue(self.location_holds(Age2ScenarioLocationData.ATT3_BUILD_CASTLE,
                                            self.state_without()))

    def test_attila_3_asks_the_castles_stone(self):
        self.build_starving(easy=(Resource.STONE,))
        self.assertFalse(self.location_holds(Age2ScenarioLocationData.ATT3_BUILD_CASTLE,
                                             self.state_without()))

    def test_attila_3_asks_the_castle_price(self):
        self.build_starving(some=(Resource.GOLD,), **START_IN_DARK_AGE)
        self.assertFalse(self.location_holds(Age2ScenarioLocationData.ATT3_BUILD_CASTLE,
                                             self.state_without()))

    def test_genghis_5_raises_castles_in_logic_when_fed(self):
        self.build(**START_IN_DARK_AGE)
        state = self.state_without()
        for location in CASTLES:
            with self.subTest(location=location.location_name):
                self.assertTrue(self.location_holds(location, state))

    def test_genghis_5_asks_the_castle_price(self):
        self.build_starving(some=(Resource.GOLD,), **START_IN_DARK_AGE)
        state = self.state_without()
        for location in CASTLES:
            with self.subTest(location=location.location_name):
                self.assertFalse(self.location_holds(location, state))


class TestAUnitLocationPaysItsAgeAndItsBuilding(AgePriceTestBase):
    def can_train(self, unit: Age2UnitData, state: CollectionState) -> bool:
        return self.holds(self.world.rules.logic.units.can_train_anywhere(unit), state)

    def test_an_archer_is_trained_when_fed(self):
        self.build(**START_IN_DARK_AGE)
        self.assertTrue(self.can_train(Age2UnitData.ARCHER, self.state_without()))

    def test_an_archer_asks_the_feudal_price(self):
        self.build_starving(some=(Resource.FOOD,), **START_IN_DARK_AGE)
        self.assertFalse(self.can_train(Age2UnitData.ARCHER, self.state_without()))

    def test_a_militia_with_no_wood_and_no_standing_barracks_is_not_trained(self):
        self.build_starving(easy=(Resource.WOOD,))
        self.assertFalse(self.can_train(Age2UnitData.MILITIA, self.state_without(BLEDAS_CAMP)))

    def test_a_militia_at_a_standing_barracks_needs_no_wood(self):
        self.build_starving(easy=(Resource.WOOD,))
        self.assertTrue(self.can_train(Age2UnitData.MILITIA, self.state_without()))


class TestBuildersAndRepairersPaySomeOfABuilding(AgePriceTestBase):
    def job(self, job: Age2VillagerJobData, state: CollectionState) -> bool:
        attila_1 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_1)
        return self.holds(attila_1.units.job_requirement(job), state)

    def test_a_builder_with_something_to_build_and_some_of_every_resource(self):
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        self.assertTrue(self.job(Age2VillagerJobData.BUILDER_MALE, self.state_without()))

    def test_a_builder_with_nothing_to_pay_with_builds_nothing(self):
        self.build_starving(some=ALL_RESOURCES,
                            shuffle_villager=ShuffleVillager.option_include_professions)
        self.assertFalse(self.job(Age2VillagerJobData.BUILDER_MALE, self.state_without()))

    def test_a_repairer_with_no_building_and_nothing_to_pay_with_mends_nothing(self):
        self.build_starving(some=ALL_RESOURCES,
                            shuffle_villager=ShuffleVillager.option_include_professions)
        state = self.state_without(BLEDAS_CAMP, ATTILAS_CAMP)
        self.assertFalse(self.job(Age2VillagerJobData.REPAIRER_MALE, state))

    def test_a_repairer_with_a_standing_building_needs_nothing_paid(self):
        self.build_starving(some=ALL_RESOURCES,
                            shuffle_villager=ShuffleVillager.option_include_professions)
        self.assertTrue(self.job(Age2VillagerJobData.REPAIRER_MALE, self.state_without()))


if __name__ == "__main__":
    unittest.main()
