from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan1StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.rules = logic
        self.is_unlocked = Has(Age2ItemData.JOAN_OF_ARC.item_name)
        self.has_vils = False_()
        self.has_base = False_()