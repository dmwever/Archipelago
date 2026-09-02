from rule_builder.rules import Has, HasAll
from ...items.Items import Age2ItemData

from ...locations.Locations import Age2ScenarioLocationData

from ...logic.joan.joan_5 import Joan5StartingState

from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan5Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_5)
        self.scenario_logic = ScenarioLogic(self.logic, Joan5StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        # can_beat_scenario = Has("Refugee", 10)
        can_beat_scenario = HasAll(
            Age2ItemData.AP_JOAN_5_REFUGEE_1.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_2.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_3.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_4.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_5.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_6.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_7.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_8.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_9.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_10.item_name,
        )
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN5_RENDEZVOUS], can_beat_scenario)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN5_ESCORT_JOAN], can_beat_scenario)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN5_ESCORT_REFUGEES], can_beat_scenario)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN5_VICTORY], can_beat_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN5_VICTORY.scenario.scenario_name), can_beat_scenario)