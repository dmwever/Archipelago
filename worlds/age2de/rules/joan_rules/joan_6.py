
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ...items.Items import Age2ItemData

from rule_builder.rules import Has, HasAll

from ...locations.Locations import Age2ScenarioLocationData

from ...logic.joan.joan_6 import Joan6StartingState

from ...logic.ScenarioLogic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_6)
        self.scenario_logic = ScenarioLogic(self.logic, Joan6StartingState(self.logic), self.scenario)
    
    def set_rules(self):
        super().set_rules()
        
        can_defeat_purple = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE)
        )
        
        can_siege_town = (
            HasAll(
                Age2ItemData.AP_JOAN_6_ARMY.item_name, 
                Age2ItemData.AP_JOAN_6_ARTILLERY.item_name
            ) |
            can_defeat_purple
        )
        can_defeat_orange = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL)
        )
        can_defeat_red = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL)
        )
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN6_BURGUNDIAN_TOWN], can_siege_town)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN6_VICTORY], can_siege_town & can_defeat_red)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN6_VICTORY.scenario.scenario_name), can_siege_town & can_defeat_red)