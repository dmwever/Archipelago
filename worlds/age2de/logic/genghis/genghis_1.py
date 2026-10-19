from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState
from ..ScenarioPlayer import ScenarioPlayer


if TYPE_CHECKING:
    from ..Logic import Logic

class Genghis1Player(ScenarioPlayer):
    """No one to defeat: victory is the Kereyid monk, and every other slot is an ally or
    neutral."""

class Genghis1StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ItemData.GENGHIS_KHAN.item_name)
        # No villagers: the map holds no gold or stone either, so there is nothing to gather.
        self.has_vils = False_()

        self.obtains_unit[Age2UnitData.CAVALRY_ARCHER] = True_()
        self.obtains_unit[Age2UnitData.LIGHT_CAVALRY] = True_()

        self.obtains_tech[Age2TechData.CHEMISTRY] = True_()
