from rule_builder.rules import Rule

from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.UnitLines import Age2UnitLineData
from ..ScenarioRules import ScenarioRules


class Genghis4Rules(ScenarioRules):
    """Only the Kipchaks are hostile when the map opens - the Russians and Khwarazm both
    start allied, and both have to be put down anyway. Neither of their scripts advances an
    age, so each is countered where the scenario placed it: the Russians in Castle, Khwarazm
    already in Imperial with a wonder to raise.
    """

    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_4)

    def set_rules(self):
        super().set_rules()
        military = self.scenario_logic.military

        can_kill_red: Rule = (
            self.scenario_logic.has_base() &
            military.has_military(Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.BOYAR_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
            military.has_siege() &
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )

        can_kill_yellow: Rule = (
            self.scenario_logic.has_base() &
            military.has_military(Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.WAR_ELEPHANT_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.IMPERIAL) &
            military.has_long_range_siege() &
            self.scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
        )

        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN4_DEFEAT_RUSSIANS], can_kill_red)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN4_DEFEAT_KHWARAZM], can_kill_yellow)

        can_beat_scenario: Rule = can_kill_red & can_kill_yellow
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN4_VICTORY], can_beat_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN4_VICTORY.scenario.scenario_name), can_beat_scenario)
