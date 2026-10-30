from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ...locations.Units import Age2UnitData
from ..ScenarioRules import ScenarioRules


class Attila2Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_2)

    def set_rules(self):
        super().set_rules()
        can_defeat_romans: Rule = self.scenario_logic.player_logic.defeats(Age2PlayerData.ATT2_EASTERN_ROMAN_EMPIRE)
        can_build_tc = (self.scenario_logic.buildings.can_build_tc()
                        & Has(Age2ItemData.TOWN_CENTER_WOOD.item_name)
                        & Has(Age2ItemData.TOWN_CENTER_STONE.item_name))
        can_build_tc = self.scenario_logic.named("can raise a Town Center", can_build_tc)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_VICTORY], can_defeat_romans & can_build_tc)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name), can_defeat_romans & can_build_tc)
        can_raze_red_tc: Rule = (self.logic.units.survives_caveman(Age2UnitData.TARKAN)
                                 | self.has_military)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_RED_TC], can_raze_red_tc)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_SCYTHIAN_VILS], self.scenario_logic.has_vils())
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_BUILD_TC], can_build_tc)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_BEAT_THE_ROMANS], can_defeat_romans)
