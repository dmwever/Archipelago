from rule_builder.rules import Rule

from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.UnitLines import Age2UnitLineData
from ..ScenarioRules import ScenarioRules


class Genghis2Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_2)

    def set_rules(self):
        super().set_rules()

        can_kill_red: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_military(Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.SKIRMISHER_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters_building() &
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )
        can_kill_red = self.scenario_logic.named("can beat Red", can_kill_red)

        can_kill_green: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_military(Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.MANGUDAI_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.SKIRMISHER_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters_building() &
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )
        can_kill_green = self.scenario_logic.named("can beat Green", can_kill_green)

        # Kushluk hides behind both camps, so reaching him asks for both.
        can_beat_scenario: Rule = can_kill_green & can_kill_red
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN2_VICTORY], can_beat_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN2_VICTORY.scenario.scenario_name), can_beat_scenario)
