from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ...locations.Units import Age2UnitData
from ..ScenarioRules import ScenarioRules


class Joan2Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_2)

    def set_rules(self):
        super().set_rules()
        by_sea: Rule = (Has(Age2ItemData.AP_JOAN_2_DOCK.item_name)
                        & self.logic.units.survives_caveman(Age2UnitData.TRANSPORT_SHIP))
        can_cross: Rule = Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name) | by_sea
        can_conquer_bridge: Rule = (
            Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name)
            | (by_sea & self.scenario_logic.military.has_military())
        )
        can_conquer_bridge = self.scenario_logic.named("can take the bridge", can_conquer_bridge)
        can_defeat_northern_english: Rule = self.scenario_logic.player_logic.defeats(Age2PlayerData.JOAN2_NORTHERN_ENGLISH)
        can_defeat_southern_english: Rule = self.scenario_logic.player_logic.defeats(Age2PlayerData.JOAN2_SOUTHERN_ENGLISH)
        victory: Rule = can_defeat_northern_english | can_defeat_southern_english

        if self.world.pool.scenarios.all_scenario_branches:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_NORTHEAST_CASTLE], can_defeat_northern_english)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_NORTHWEST_CASTLE], can_defeat_northern_english)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_SOUTHWEST_CASTLE], can_defeat_southern_english)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_SOUTHEAST_CASTLE], can_defeat_southern_english)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_BRING_CARTS_TO_ORLEANS], Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_CONQUER_BRIDGE], can_conquer_bridge)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_BRING_JOAN_TO_ORLEANS], can_cross)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_FIND_FARMING_VILLAGE], can_cross)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_VICTORY], victory)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN2_VICTORY.scenario.scenario_name), victory)
