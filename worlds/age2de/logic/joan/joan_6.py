from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ...locations.Units import Age2UnitData as U
from ...locations.Heroes import Age2HeroData as H
from ..ScenarioLogic import ScenarioStartingState, DARK_START, VANILLA_AGE_START


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 5)
        self.has_vils = Has(Age2ItemData.AP_JOAN_6_ARMY.item_name)

        army = Has(Age2ItemData.AP_JOAN_6_ARMY.item_name)
        self.obtains_unit[U.ARCHER] = army
        self.obtains_unit[U.MILITIA] = army
        self.obtains_unit[U.SCOUT_CAVALRY] = army
        self.obtains_unit[U.KNIGHT] = army
        self.obtains_unit[U.TREBUCHET_PACKED] = army
        self.obtains_unit[U.VILLAGER_MALE] = army
        self.obtains_unit[U.VILLAGER_FEMALE] = army
        self.obtains_unit[H.LA_HIRE] = army
        self.obtains_unit[H.CONSTABLE_RICHEMONT] = army
