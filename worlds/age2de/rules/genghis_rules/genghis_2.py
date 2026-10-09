from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Genghis2Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_2)

    def set_rules(self):
        super().set_rules()
        # No objectives are authored for this chapter yet, so winning it asks only for a base.
        # The base class sets the entrance rule and nothing else - the VICTORY location and its
        # paired "Complete ..." event have to be ruled by hand, or the next chapter unlocks free.
        can_beat_scenario = self.scenario_logic.has_base()
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN2_VICTORY],
                            can_beat_scenario)
        self.world.set_rule(
            self.world.get_location(
                "Complete " + Age2ScenarioData.AP_GENGHIS_2.scenario_name),
            can_beat_scenario)
