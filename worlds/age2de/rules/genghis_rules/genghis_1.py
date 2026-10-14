from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Genghis1Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_1)

    def set_rules(self):
        super().set_rules()
        # No objectives are authored for this chapter yet, so winning it asks only that you reach it: a fixed force has no base to build.
        # The base class sets the entrance rule and nothing else - the VICTORY location and its
        # paired "Complete ..." event have to be ruled by hand, or the next chapter unlocks free.
        can_beat_scenario = True_()
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_VICTORY],

        has_monk: Rule = Has(Age2ItemData.AP_GENGHIS_1_KEREYID_TRIBE.item_name)

        if self.world.pool.scenarios.all_scenario_branches:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RELIC_RED_MONASTERY], has_monk)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RELIC_WOLF], has_monk)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RELIC_PALISADED], has_monk)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RECRUIT_UNGIRRADS], has_monk)
        else:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_ANY_RELIC], has_monk)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_VICTORY], has_monk)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN1_VICTORY.scenario.scenario_name), has_monk)
