from rule_builder.rules import Rule
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Attila4Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_4)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.player_logic.defeats

        starting_state = self.scenario_logic.starting_state
        can_tribute_burgundy: Rule = starting_state.can_tribute_burgundy(self.scenario_logic)
        can_ally_burgundy: Rule = starting_state.can_ally_burgundy(self.scenario_logic)

        if self.world.pool.scenarios.all_scenario_branches:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_TRIBUTE_BURGUNDY_ALL],
                                can_tribute_burgundy)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_CASTLE_BURGUNDY_ALL], can_ally_burgundy)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_BURGUNDY_ALL], defeats(Age2PlayerData.ATT4_BURGUNDY))
        else:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_OR_ALLY_BURGUNDY_ANY], defeats(Age2PlayerData.ATT4_BURGUNDY) | can_ally_burgundy)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_METZ], defeats(Age2PlayerData.ATT4_METZ))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_ORLEANS], defeats(Age2PlayerData.ATT4_ORLEANS))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_DEFEAT_ROMAN_ARMY], defeats(Age2PlayerData.ATT4_WESTERN_ROMAN_EMPIRE))

        can_win_scenario: Rule = (
            defeats(Age2PlayerData.ATT4_WESTERN_ROMAN_EMPIRE) &
            defeats(Age2PlayerData.ATT4_METZ) &
            (can_ally_burgundy | defeats(Age2PlayerData.ATT4_BURGUNDY))
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT4_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT4_VICTORY.scenario.scenario_name), can_win_scenario)
