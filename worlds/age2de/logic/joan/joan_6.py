from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState, DARK_START, VANILLA_AGE_START


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.rules = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 5)
        self.has_base = Has(Age2ItemData.AP_JOAN_6_ARMY.item_name) & logic.can_build_base()
        self.has_vils = Has(Age2ItemData.AP_JOAN_6_ARMY.item_name)
        self.age_playable[Age2AgeData.DARK] = logic.ages.can_reach(Age2AgeData.DARK) & DARK_START
        self.age_playable[Age2AgeData.FEUDAL] = logic.ages.can_reach(Age2AgeData.FEUDAL) & DARK_START
        self.age_playable[Age2AgeData.CASTLE] = logic.ages.can_reach(Age2AgeData.CASTLE) | VANILLA_AGE_START
        self.age_playable[Age2AgeData.IMPERIAL] = (Has(Age2ItemData.AP_JOAN_6_ARMY.item_name)
                                                   & logic.ages.can_reach(Age2AgeData.IMPERIAL))