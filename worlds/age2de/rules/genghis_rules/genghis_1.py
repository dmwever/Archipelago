from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Units import Age2UnitData
from ...logic.unit_logic import NOT_CAVEMAN
from ..ScenarioRules import ScenarioRules


class Genghis1Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_1)

    def set_rules(self):
        super().set_rules()

        has_monk: Rule = (Has(Age2ItemData.AP_GENGHIS_1_KEREYID_TRIBE.item_name)
                          & self.logic.units.survives_caveman(Age2UnitData.MONK))

        can_slay_ornlu: Rule = NOT_CAVEMAN | Has(Age2ItemData.AP_GENGHIS_1_KEREYID_TRIBE.item_name)
        can_slay_ornlu = self.scenario_logic.named("can slay Ornlu", can_slay_ornlu)

        if self.world.pool.scenarios.all_scenario_branches:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RELIC_RED_MONASTERY], has_monk)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RELIC_WOLF], has_monk)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RELIC_PALISADED], has_monk)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RECRUIT_UNGIRRADS], has_monk)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_RECRUIT_UIGHURS],
                                can_slay_ornlu)
        else:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_ANY_RELIC], has_monk)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN1_VICTORY], has_monk)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN1_VICTORY.scenario.scenario_name), has_monk)
