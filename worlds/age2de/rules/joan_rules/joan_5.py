from rule_builder.rules import HasAll, Rule
from ...items.Items import Age2ItemData

from ...locations.Locations import Age2ScenarioLocationData


from ...locations.Scenarios import Age2ScenarioData
from ...locations.Units import Age2UnitData
from ..ScenarioRules import ScenarioRules


NEEDS_THE_SIEGE = (
    Age2ScenarioLocationData.JOAN5_REFUGEE_1,
    Age2ScenarioLocationData.JOAN5_REFUGEE_2,
    Age2ScenarioLocationData.JOAN5_REFUGEE_3,
    Age2ScenarioLocationData.JOAN5_REFUGEE_4,
    Age2ScenarioLocationData.JOAN5_REFUGEE_5,
    Age2ScenarioLocationData.JOAN5_REFUGEE_6,
    Age2ScenarioLocationData.JOAN5_REFUGEE_7,
    Age2ScenarioLocationData.JOAN5_REFUGEE_8,
    Age2ScenarioLocationData.JOAN5_REFUGEE_9,
    Age2ScenarioLocationData.JOAN5_REFUGEE_10,
    Age2ScenarioLocationData.JOAN5_LOYALISTS,
)


class Joan5Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_5)

    def set_rules(self):
        super().set_rules()
        survives = self.logic.units.survives_caveman
        keeps_its_siege: Rule = (survives(Age2UnitData.BOMBARD_CANNON)
                                 | survives(Age2UnitData.TREBUCHET_PACKED))
        for location in NEEDS_THE_SIEGE:
            self.world.set_rule(self.locations[location], keeps_its_siege)

        # can_win_scenario = Has("Refugee", 10)
        can_win_scenario = HasAll(
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
        ) & keeps_its_siege

        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN5_RENDEZVOUS], can_win_scenario)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN5_ESCORT_JOAN], can_win_scenario)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN5_ESCORT_REFUGEES], can_win_scenario)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN5_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN5_VICTORY.scenario.scenario_name), can_win_scenario)
