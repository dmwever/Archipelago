from rule_builder.rules import Rule

from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Attila2Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_2)

    def set_rules(self):
        super().set_rules()
        can_defeat_romans: Rule = self.scenario_logic.players.defeats(Age2PlayerData.ATT2_EASTERN_ROMAN_EMPIRE)
        town_center = Age2BuildingData.TOWN_CENTER
        can_build_tc = (self.scenario_logic.buildings.can_build_tc()
                        & self.scenario_logic.has_vils()
                        & self.scenario_logic.economy.can_pay(town_center.cost))
        can_build_tc = self.scenario_logic.named("can raise a Town Center", can_build_tc)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_VICTORY], can_defeat_romans & can_build_tc)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name), can_defeat_romans & can_build_tc)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_SCYTHIAN_VILS], self.scenario_logic.has_vils())
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_BUILD_TC], can_build_tc)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT2_BEAT_THE_ROMANS], can_defeat_romans)
