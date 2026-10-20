from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Units import Age2UnitData as U
from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Attila2StartingState(ScenarioStartingState):
    purple_vils: Rule = Has(Age2ItemData.AP_ATTILA_2_VILLAGERS.item_name)
    scythian_troop: Rule = Has(Age2ItemData.AP_ATTILA_2_SCYTHIAN_TROOP.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario")
        self.has_vils = self.purple_vils

        self.obtains_unit[U.VILLAGER_MALE] = self.purple_vils
        self.obtains_unit[U.VILLAGER_FEMALE] = self.purple_vils

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            # Neither city offers any resistance.
            Age2PlayerData.ATT2_DYRRHACHIUM: True_(),
            Age2PlayerData.ATT2_THESSALONICA: True_(),
            Age2PlayerData.ATT2_EASTERN_ROMAN_EMPIRE: (
                self.scythian_troop |
                (
                    scenario_logic.has_base() &
                    military.has_siege() &
                    military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
                    military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                    military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.CASTLE)
                )
            ),
        }
