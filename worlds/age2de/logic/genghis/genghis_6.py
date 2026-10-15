from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Genghis6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 5)

        # Ogedei holds the north bank in imperial already: a town centre, a castle, a stable
        # and an archery range behind seven guard towers.
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()
        self.starts_with_building[Age2BuildingData.CASTLE] = True_()
        self.starts_with_building[Age2BuildingData.STABLE] = True_()
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = True_()
