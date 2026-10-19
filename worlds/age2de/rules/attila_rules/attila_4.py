from rule_builder.rules import Has, Rule
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...logic.attila.attila_4 import Attila4Player
from ..ScenarioRules import ScenarioRules


class Attila4Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_4)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.defeats

        can_ally_burgundy: Rule = (
            self.scenario_logic.has_base() &
            self.logic.buildings.has_building(Age2BuildingData.MARKET) &
            self.logic.buildings.has_building(Age2BuildingData.CASTLE) &
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )
        can_ally_burgundy = self.scenario_logic.named("can ally with Burgundy", can_ally_burgundy)

        if self.world.pool.scenarios.all_scenario_branches:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_TRIBUTE_BURGUNDY_ALL], Has(Age2ItemData.MARKET.item_name))
            self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_CASTLE_BURGUNDY_ALL], can_ally_burgundy)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_BURGUNDY_ALL], defeats(Attila4Player.BURGUNDY))
        else:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_OR_ALLY_BURGUNDY_ANY], defeats(Attila4Player.BURGUNDY) | can_ally_burgundy)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_METZ], defeats(Attila4Player.METZ))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_ORLEANS], defeats(Attila4Player.ORLEANS))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_ROMAN_ARMY], defeats(Attila4Player.WESTERN_ROMAN_EMPIRE))

        can_win_scenario: Rule = (
            defeats(Attila4Player.WESTERN_ROMAN_EMPIRE) &
            defeats(Attila4Player.METZ) &
            (can_ally_burgundy | defeats(Attila4Player.BURGUNDY))
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT4_VICTORY.scenario.scenario_name), can_win_scenario)
