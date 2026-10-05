from rule_builder.rules import Has, HasAny, Rule

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan1Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_1)
    
    def set_rules(self):
        super().set_rules()
        can_cross_water = Has(Age2ItemData.AP_JOAN_1_TRANSPORT.item_name)
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_RECRUITS], can_cross_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_RIVER_BURGUNDIANS], can_cross_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_RIVER_HIGHWAYMEN], can_cross_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN1_VICTORY], can_cross_water)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN1_VICTORY.scenario.scenario_name), can_cross_water)