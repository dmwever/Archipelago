from rule_builder.rules import Rule

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.UnitLines import Age2UnitLineData
from ..ScenarioRules import ScenarioRules


class Genghis5Rules(ScenarioRules):
    """A flag changes hands the moment one of your units stands on it, so the Polish flag is
    a ride and nothing more. The German and Bohemian flags sit too deep to be stolen, and the
    Bohemians are the exception to counting only what a script trains: theirs trains nothing
    at all, and the seventy units it opens with are a wall rather than a stream.
    """

    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_5)

    def set_rules(self):
        super().set_rules()
        military = self.scenario_logic.military

        can_kill_red: Rule = (
            self.scenario_logic.has_base() &
            military.has_military(Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.TEUTONIC_KNIGHT_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
            military.has_siege() &
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )
        can_kill_red = self.scenario_logic.named("can beat Red", can_kill_red)

        can_kill_green: Rule = (
            self.scenario_logic.has_base() &
            military.has_military(Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.IMPERIAL) &
            military.has_long_range_siege() &
            self.scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
        )
        can_kill_green = self.scenario_logic.named("can beat Green", can_kill_green)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_GERMAN_FLAG], can_kill_red)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_BOHEMIAN_FLAG], can_kill_green)

        can_raise_castles: Rule = (
            self.scenario_logic.buildings.can_build_building(Age2BuildingData.CASTLE) &
            self.scenario_logic.economy.has_easy_source(Resource.STONE) &
            can_kill_red
        )
        can_raise_castles = self.scenario_logic.named("can raise castles", can_raise_castles)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_BUILD_ONE_CASTLE], can_raise_castles)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_BUILD_TWO_CASTLES], can_raise_castles)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_BUILD_THREE_CASTLES], can_raise_castles)

        # The Polish flag is a free ride, and the hermit sits alone in the mountains.
        can_beat_scenario: Rule = can_kill_red & can_kill_green
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_VICTORY], can_beat_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN5_VICTORY.scenario.scenario_name), can_beat_scenario)
