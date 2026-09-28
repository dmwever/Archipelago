from rule_builder.rules import Has, Rule
from ...Options import ScenarioBranching
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...items.Items import Age2ItemData

from ...logic.joan.joan_3 import Joan3StartingState

from ...logic.ScenarioLogic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan3Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_3)
        self.scenario_logic = ScenarioLogic(self.logic, Joan3StartingState(self.logic), self.scenario)
    
    def set_rules(self):
        super().set_rules()
        can_cross_ocean = Has(Age2ItemData.AP_JOAN_3_TRANSPORT.item_name) | (self.logic.buildings.has_building(Age2BuildingData.DOCK) & Has(Age2ItemData.TOWN_CENTER_WOOD.item_name))
        can_destroy_castle: Rule = (
            self.scenario_logic.has_base() &
            can_cross_ocean & 
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE)
        )
        can_beat_purple: Rule = (
            self.scenario_logic.has_base() &
            can_cross_ocean &
            self.scenario_logic.military.counters_building() &
            self.scenario_logic.military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.CASTLE)
        )
        can_beat_fastolf: Rule = (
            self.scenario_logic.has_base() &
            can_cross_ocean &
            self.scenario_logic.military.counters_building() &
            self.scenario_logic.military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.FEUDAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE)
        )
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_SLAY_FASTOLF], can_beat_fastolf)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_VICTORY], can_destroy_castle & can_beat_fastolf)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN3_VICTORY.scenario.scenario_name), can_destroy_castle & can_beat_fastolf)
        
        if self.world.options.scenario_branching == ScenarioBranching.option_all:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_CENTRAL_CASTLE], can_destroy_castle)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_REAR_CASTLE], can_destroy_castle)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_LEFT_CASTLE], can_destroy_castle)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_RIGHT_CASTLE], can_destroy_castle)
        else:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_ONE_CASTLE], can_destroy_castle)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_TWO_CASTLES], can_destroy_castle & can_beat_fastolf)