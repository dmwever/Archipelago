from rule_builder.rules import Has, HasAny, Rule
from ...logic.joan.joan_1 import Joan1StartingState

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan1Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_1)
        self.scenario_logic = ScenarioLogic(self.logic, Joan1StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        has_soldiers = HasAny(Age2ItemData.AP_JOAN_1_SWORDSMEN.item_name, Age2ItemData.AP_JOAN_1_CROSSBOWMEN.item_name)
        can_siege_village = has_soldiers & Has(Age2ItemData.AP_JOAN_1_RAM.item_name)
        can_cross_water = can_siege_village & Has(Age2ItemData.AP_JOAN_1_TRANSPORT.item_name)
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_SOUTH_HIGHWAYMEN], has_soldiers)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_VENISON], has_soldiers)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_RAM], has_soldiers)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_EAST_HIGHWAYMEN], has_soldiers)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_BREAK_INTO_BURGUNDY], can_siege_village)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_DOCK], can_siege_village)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_RECRUITS], can_cross_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_RIVER_BURGUNDIANS], can_cross_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_RIVER_HIGHWAYMEN], can_cross_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_VICTORY], can_cross_water)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN1_VICTORY.scenario.scenario_name), can_cross_water)