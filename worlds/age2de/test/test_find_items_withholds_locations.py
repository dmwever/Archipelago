from ..Options import ExistingTechs, ShuffleUniqueTechs, Techsanity, Unitsanity
from ..locations.Ages import Age2AgeData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..logic.ScenarioLogic import ScenarioLogic
from .bases import Age2RuleTestBase


class TestFindItemsWithholdsOnlyLocations(Age2RuleTestBase):

    def researching(self, tech: Age2TechData, above: Age2AgeData) -> list[ScenarioLogic]:
        scenarios = [scenario for scenario in self.world.rules.logic.scenarios
                     if scenario.scenario.vanilla_age > above
                     and scenario.civilization.researches(tech)
                     and tech not in scenario.scenario.excluded_techs]
        self.assertTrue(scenarios, f"no scenario opens above {above.name} with {tech.name}")
        return scenarios

    def test_loom_is_granted_when_it_is_not_a_location(self):
        world = self.build(existing_techs=ExistingTechs.option_find_items,
                           techsanity=Techsanity.option_units)
        self.assertFalse(world.pool.techs.includes(Age2TechData.LOOM))
        for scenario in self.researching(Age2TechData.LOOM, Age2AgeData.DARK):
            with self.subTest(scenario=scenario.scenario.name):
                self.assertTrue(scenario.techs.researched_at_start(Age2TechData.LOOM))

    def test_man_at_arms_is_granted_when_it_is_not_a_location(self):
        world = self.build(existing_techs=ExistingTechs.option_find_items,
                           techsanity=Techsanity.option_generic,
                           unitsanity=Unitsanity.option_all)
        self.assertFalse(world.pool.techs.includes(Age2TechData.MAN_AT_ARMS))
        for scenario in self.researching(Age2TechData.MAN_AT_ARMS, Age2AgeData.FEUDAL):
            with self.subTest(scenario=scenario.scenario.name):
                self.assertTrue(scenario.techs.researched_at_start(Age2TechData.MAN_AT_ARMS))
                self.assertTrue(scenario.units.upgraded_away(Age2UnitData.MILITIA))

    def test_unshuffled_marauders_is_granted_in_attila_6(self):
        world = self.build(existing_techs=ExistingTechs.option_find_items,
                           techsanity=Techsanity.option_all,
                           shuffle_unique_techs=ShuffleUniqueTechs.option_unshuffled)
        attila_6 = world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_6)
        self.assertTrue(attila_6.techs.researched_at_start(Age2TechData.MARAUDERS_HUNS))

    def test_a_location_is_still_withheld(self):
        world = self.build(existing_techs=ExistingTechs.option_find_items,
                           techsanity=Techsanity.option_all)
        self.assertTrue(world.pool.techs.includes(Age2TechData.LOOM))
        for scenario in world.rules.logic.scenarios:
            with self.subTest(scenario=scenario.scenario.name):
                self.assertFalse(scenario.techs.researched_at_start(Age2TechData.LOOM))
                self.assertFalse(scenario.units.upgraded_away(Age2UnitData.MILITIA))

    def test_start_in_dark_age_withholds_loom_that_is_not_a_location(self):
        world = self.build(existing_techs=ExistingTechs.option_start_in_dark_age,
                           techsanity=Techsanity.option_units)
        self.assertFalse(world.pool.techs.includes(Age2TechData.LOOM))
        for scenario in world.rules.logic.scenarios:
            with self.subTest(scenario=scenario.scenario.name):
                self.assertFalse(scenario.techs.researched_at_start(Age2TechData.LOOM))
