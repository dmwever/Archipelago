from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from ...items.Items import Age2ItemData
from ..unit_logic import NOT_CAVEMAN

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Genghis1StartingState(ScenarioStartingState):
    kereyid: Rule = Has(Age2ItemData.AP_GENGHIS_1_KEREYID_TRIBE.item_name)
    ungirrad: Rule = Has(Age2ItemData.AP_GENGHIS_1_UNGIRRAD_TRIBE.item_name)
    uighur: Rule = Has(Age2ItemData.AP_GENGHIS_1_UIGHUR_TRIBE.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ItemData.GENGHIS_KHAN.item_name)
        # No villagers: the map holds no gold or stone either, so there is nothing to gather.
        self.has_vils = False_()

        self.has_monk = self.kereyid & logic.units.survives_caveman(Age2UnitData.MONK)
        self.can_slay_ornlu = NOT_CAVEMAN | self.kereyid

        self.obtains_unit[Age2UnitData.CAVALRY_ARCHER] = True_()
        self.obtains_unit[Age2UnitData.LIGHT_CAVALRY] = True_()
        self.obtains_unit[Age2UnitData.MONK] = self.kereyid
        self.obtains_unit[Age2UnitData.MANGUDAI] = self.ungirrad & self.has_monk
        self.obtains_unit[Age2UnitData.CAMEL_RIDER] = self.uighur & self.can_slay_ornlu

        self.obtains_tech[Age2TechData.CHEMISTRY] = True_()
