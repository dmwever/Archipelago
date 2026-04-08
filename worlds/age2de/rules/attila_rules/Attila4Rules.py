from rule_builder.rules import Has, Rule, True_
from ...logic.attila.Attila3StartingState import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...logic.attila.Attila4StartingState import Attila4StartingState

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila4Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_4)
        self.scenario_logic = ScenarioLogic(self.logic, Attila4StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        can_beat_red: Rule = self.logic.military.has_anti_infantry(Age2AgeData.IMPERIAL) & \
            self.logic.military.has_anti_cav(Age2AgeData.IMPERIAL) & self.logic.military.has_siege() & self.logic.ages.has_age(Age2AgeData.IMPERIAL)
        can_beat_purple: Rule = self.logic.military.has_anti_archers(Age2AgeData.CASTLE) & self.logic.military.has_anti_infantry(Age2AgeData.CASTLE)
        can_ally_purple: Rule = self.logic.buildings.has_building(Age2BuildingData.MARKET) & \
            self.logic.buildings.has_building(Age2BuildingData.CASTLE) & self.logic.ages.has_age(Age2AgeData.CASTLE)
        can_beat_cyan: Rule = self.logic.military.has_anti_cav(Age2AgeData.IMPERIAL) & self.logic.military.has_anti_trash(Age2AgeData.IMPERIAL) & \
            self.logic.military.has_long_range_siege() & self.logic.ages.has_age(Age2AgeData.IMPERIAL)
        can_beat_blue: Rule = can_beat_cyan
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_TRIBUTE_BURGUNDY_ALL], Has(Age2BuildingData.MARKET))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_CASTLE_BURGUNDY_ALL], can_ally_purple)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_BURGUNDY_ALL], can_beat_purple)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_OR_ALLY_BURGUNDY_ANY], can_beat_purple | can_ally_purple)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_METZ], can_beat_red)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_ORLEANS], can_beat_cyan)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_ROMAN_ARMY], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_VICTORY], can_beat_blue & can_beat_red & (can_ally_purple | can_beat_purple))