import contextlib
import unittest
from typing import Iterator
from unittest import mock

from rule_builder.rules import Rule, True_

from ..Options import ShuffleVillager
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..logic.ScenarioLogic import ScenarioLogic
from ..logic.custom_logic.ScenarioQuestions import ScenarioHasEasyResource, ScenarioHasSomeResource
from .test_age_price import BLEDAS_CAMP, START_IN_DARK_AGE, AgePriceTestBase

TOWN_CENTER_ITEMS = (
    Age2ItemData.TOWN_CENTER_WOOD.item_name,
    Age2ItemData.TOWN_CENTER_STONE.item_name,
)
VILLAGERS = (
    Age2ItemData.UNIT_LINE_VILLAGER.item_name,
    Age2ItemData.STARTING_VILLAGER_FOOD.item_name,
)

def fed_with(question: type, resources: tuple[Resource, ...]) -> mock._patch:
    answer = question.answer

    def fed_answer(asked, scenario: ScenarioLogic) -> Rule:
        if asked.resource in resources:
            return True_()
        return answer(asked, scenario)

    return mock.patch.object(question, "answer", fed_answer)

@contextlib.contextmanager
def feeding(easy: tuple[Resource, ...] = (), some: tuple[Resource, ...] = ()) -> Iterator[None]:
    with fed_with(ScenarioHasEasyResource, easy), fed_with(ScenarioHasSomeResource, some):
        yield

class TestACastleStartAsksNoAdvance(AgePriceTestBase):
    def answers(self, **options) -> dict[str, bool]:
        self.build_starving(easy=(Resource.WOOD,), **options)
        attila_3 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_3)
        state = self.state_without()
        return {
            "build": self.holds(attila_3.buildings.can_build(Age2BuildingData.CASTLE), state),
            "research": self.holds(attila_3.techs.can_research(Age2TechData.HUSBANDRY), state),
            "train": self.holds(attila_3.units.can_train(Age2UnitData.CAVALRY_ARCHER), state),
        }

    def test_build_tech_and_unit_ask_no_advance_where_the_scenario_starts_in_the_castle_age(self):
        self.assertEqual({"build": True, "research": True, "train": True}, self.answers())

    def test_under_start_in_dark_age_they_ask_the_feudal_advance(self):
        self.assertEqual(
            {"build": False, "research": False, "train": False},
            self.answers(**START_IN_DARK_AGE),
        )

class TestAnAdvanceAsksNoVillagersBeyondBuilders(AgePriceTestBase):
    def advances_to_feudal_without(self, *item_names: str) -> bool:
        attila_1 = self.scenario_logic(Age2ScenarioData.AP_ATTILA_1)
        state = self.state_without(BLEDAS_CAMP, *item_names)
        return self.holds(attila_1.ages.can_research(Age2AgeData.FEUDAL), state)

    def setUp(self):
        with feeding(easy=(Resource.WOOD,), some=(Resource.FOOD,)):
            self.build(shuffle_villager=ShuffleVillager.option_yes)

    def test_the_town_center_items_advance_with_no_villager_line_and_no_villager_food(self):
        self.assertTrue(self.advances_to_feudal_without(*VILLAGERS))

    def test_without_the_town_center_items_there_is_no_advance(self):
        self.assertFalse(self.advances_to_feudal_without(*VILLAGERS, *TOWN_CENTER_ITEMS))

if __name__ == "__main__":
    unittest.main()
