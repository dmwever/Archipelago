from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...logic.genghis.genghis_3 import Genghis3Player
from ..ScenarioRules import ScenarioRules


class Genghis3Rules(ScenarioRules):
    """Four enemies worth fighting and a fifth that gives up on its own: the Engineers resign
    the moment the Tanguts, Xi Xia, Jin and Song are all gone, so victory is owed four defeats
    rather than five. Counters follow what each script trains, never what it merely starts with.
    """

    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_3)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.defeats

        transport: Rule = Has(Age2ItemData.AP_GENGHIS_3_TRANSPORT.item_name)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_FIND_ENGINEERS], transport)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_FIND_BOMBARDS], transport)

        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.GEN3_DEFEAT_TANGUTS],
            defeats(Genghis3Player.TANGUTS),
        )
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.GEN3_DEFEAT_XI_XIA],
            defeats(Genghis3Player.XI_XIA),
        )
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.GEN3_DEFEAT_JIN],
            defeats(Genghis3Player.JIN),
        )
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.GEN3_DEFEAT_SONG],
            defeats(Genghis3Player.SONG),
        )

        can_win_scenario: Rule = (
            defeats(Genghis3Player.TANGUTS) &
            defeats(Genghis3Player.XI_XIA) &
            defeats(Genghis3Player.JIN) &
            defeats(Genghis3Player.SONG)
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN3_VICTORY.scenario.scenario_name), can_win_scenario)
