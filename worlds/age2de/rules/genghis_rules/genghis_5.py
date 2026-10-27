from rule_builder.rules import Rule

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
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
        defeats = self.scenario_logic.player_logic.defeats

        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.GEN5_GERMAN_FLAG],
            defeats(Age2PlayerData.GEN5_GERMANS),
        )
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.GEN5_BOHEMIAN_FLAG],
            defeats(Age2PlayerData.GEN5_BOHEMIANS),
        )

        can_raise_castles: Rule = (
            self.scenario_logic.buildings.can_build_structurally(Age2BuildingData.CASTLE) &
            self.scenario_logic.economy.has_easy_source(Resource.STONE) &
            self.scenario_logic.ages.can_pay_for(Age2AgeData.CASTLE) &
            defeats(Age2PlayerData.GEN5_GERMANS)
        )
        can_raise_castles = self.scenario_logic.named("can raise castles", can_raise_castles)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_BUILD_ONE_CASTLE], can_raise_castles)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_BUILD_TWO_CASTLES], can_raise_castles)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_BUILD_THREE_CASTLES], can_raise_castles)

        # The Polish flag is a free ride, and the hermit sits alone in the mountains.
        can_win_scenario: Rule = (
            defeats(Age2PlayerData.GEN5_GERMANS) &
            defeats(Age2PlayerData.GEN5_BOHEMIANS)
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN5_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN5_VICTORY.scenario.scenario_name), can_win_scenario)
