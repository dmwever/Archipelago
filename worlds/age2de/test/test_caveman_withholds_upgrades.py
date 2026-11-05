from rule_builder.rules import True_

from ..Options import Caveman, ExistingTechs, Techsanity, Unitsanity
from ..generation.pools.TechPool import TechPool
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from .. import Age2World
from ..logic.ScenarioLogic import ScenarioLogic
from .bases import Age2RuleTestBase


class TestCavemanWithholdsUpgradesInJoan(Age2RuleTestBase):
    campaigns = ["Joan of Arc"]
    starting_campaigns = ["Joan of Arc"]

    def build_joan(self, caveman: int) -> Age2World:
        return self.build(caveman=caveman,
                          techsanity=Techsanity.option_all,
                          unitsanity=Unitsanity.option_all,
                          existing_techs=ExistingTechs.option_vanilla)

    def logic_for(self, scenario: Age2ScenarioData) -> ScenarioLogic:
        return self.world.rules.logic.for_scenario(scenario)

    def can_train(self, scenario: Age2ScenarioData, unit: Age2UnitData, *without: str) -> bool:
        rule = self.logic_for(scenario).units.can_train(unit).resolve(self.world)
        return rule(self.state_without(*without))

    def test_joan_1_asks_for_the_man_at_arms_upgrade(self):
        self.build_joan(Caveman.option_true)
        upgrade = Age2TechData.MAN_AT_ARMS.item.item_name
        rule = self.logic_for(Age2ScenarioData.AP_JOAN_1).units.has_upgrade_tech(
            Age2UnitData.MAN_AT_ARMS).resolve(self.world)
        self.assertIn(upgrade, set(rule.item_dependencies()))
        self.assertFalse(self.can_train(Age2ScenarioData.AP_JOAN_1, Age2UnitData.MAN_AT_ARMS,
                                        upgrade))

    def test_joan_4_trains_man_at_arms_only_with_the_upgrade(self):
        self.build_joan(Caveman.option_true)
        upgrade = Age2TechData.MAN_AT_ARMS.item.item_name
        self.assertFalse(self.can_train(Age2ScenarioData.AP_JOAN_4, Age2UnitData.MAN_AT_ARMS,
                                        upgrade))
        self.assertTrue(self.can_train(Age2ScenarioData.AP_JOAN_4, Age2UnitData.MAN_AT_ARMS))

    def test_joan_1_keeps_its_militia(self):
        self.build_joan(Caveman.option_true)
        self.assertFalse(self.logic_for(Age2ScenarioData.AP_JOAN_1).units.upgraded_away(
            Age2UnitData.MILITIA))

    def test_without_caveman_joan_1_starts_upgraded(self):
        self.build_joan(Caveman.option_false)
        joan_1 = self.logic_for(Age2ScenarioData.AP_JOAN_1)
        self.assertTrue(joan_1.techs.researched_at_start(Age2TechData.MAN_AT_ARMS))
        self.assertTrue(joan_1.units.upgraded_away(Age2UnitData.MILITIA))


class TestCavemanWithholdsAtStart(Age2RuleTestBase):
    campaigns = ["Joan of Arc"]
    starting_campaigns = ["Joan of Arc"]

    def withheld(self, caveman: int, unitsanity: int) -> bool:
        world = self.build(techsanity=Techsanity.option_all,
                           existing_techs=ExistingTechs.option_vanilla)
        world.options.caveman.value = caveman
        world.options.unitsanity.value = unitsanity
        pool = TechPool(world.options, world.pool.ages.earliest, world.pool.civs,
                        world.pool.scenarios.included)
        return pool.withheld_at_start(Age2TechData.MAN_AT_ARMS)

    def test_caveman_withholds_the_upgrade_whatever_unitsanity_is(self):
        for unitsanity in (Unitsanity.option_none, Unitsanity.option_unit_line,
                           Unitsanity.option_all):
            with self.subTest(unitsanity=unitsanity):
                self.assertTrue(self.withheld(Caveman.option_true, unitsanity))

    def test_without_caveman_the_upgrade_is_granted(self):
        self.assertFalse(self.withheld(Caveman.option_false, Unitsanity.option_all))


class TestCavemanWithholdsDemolitionShips(Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun"]
    IMPERIAL_OPENERS = (Age2ScenarioData.AP_ATTILA_6, Age2ScenarioData.AP_JOAN_5,
                        Age2ScenarioData.AP_GENGHIS_6)

    def build_all(self, caveman: int) -> Age2World:
        return self.build(caveman=caveman,
                          techsanity=Techsanity.option_all,
                          unitsanity=Unitsanity.option_all,
                          existing_techs=ExistingTechs.option_vanilla)

    def test_caveman_asks_for_the_demolition_ship(self):
        world = self.build_all(Caveman.option_true)
        item = Age2TechData.DEMOLITION_SHIP.item.item_name
        for scenario in self.IMPERIAL_OPENERS:
            with self.subTest(scenario=scenario.name):
                units = world.rules.logic.for_scenario(scenario).units
                rule = units.has_upgrade_tech(Age2UnitData.DEMOLITION_SHIP)
                self.assertNotIsInstance(rule, True_)
                self.assertIn(item, set(rule.resolve(world).item_dependencies()))
                self.assertFalse(units.upgraded_away(Age2UnitData.DEMOLITION_RAFT))

    def test_without_caveman_the_demolition_ship_is_handed_over(self):
        world = self.build_all(Caveman.option_false)
        for scenario in self.IMPERIAL_OPENERS:
            with self.subTest(scenario=scenario.name):
                units = world.rules.logic.for_scenario(scenario).units
                self.assertIsInstance(units.has_upgrade_tech(Age2UnitData.DEMOLITION_SHIP), True_)
                self.assertTrue(units.upgraded_away(Age2UnitData.DEMOLITION_RAFT))
