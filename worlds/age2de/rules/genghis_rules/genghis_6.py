from rule_builder.rules import Rule

from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.UnitLines import Age2UnitLineData
from ..ScenarioRules import ScenarioRules


class Genghis6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_6)

    def set_rules(self):
        super().set_rules()
        military = self.scenario_logic.military

        can_kill_purple: Rule = (
            self.scenario_logic.has_base() &
            military.has_military(Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.SKIRMISHER_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.MAGYAR_HUSZAR_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.IMPERIAL) &
            military.has_siege() &
            self.scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
        )
        can_kill_purple = self.scenario_logic.named("can beat Purple", can_kill_purple)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN6_VICTORY], can_kill_purple)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN6_VICTORY.scenario.scenario_name), can_kill_purple)
