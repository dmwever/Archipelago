from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ...locations.Units import Age2UnitData as U
from ..ScenarioLogic import ScenarioStartingState, DARK_START, VANILLA_AGE_START


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan4StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 3)
        self.has_vils = Has(Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name)

        camp = Has(Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name)
        self.obtains_unit[U.CROSSBOWMAN] = camp
        self.obtains_unit[U.VILLAGER_MALE] = camp
        self.obtains_unit[U.VILLAGER_FEMALE] = camp
