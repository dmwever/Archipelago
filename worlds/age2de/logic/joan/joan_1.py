from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ...locations.Units import Age2UnitData as U
from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan1StartingState(ScenarioStartingState):
    transport: Rule = Has(Age2ItemData.AP_JOAN_1_TRANSPORT.item_name)
    ram_army: Rule = Has(Age2ItemData.AP_JOAN_1_RAM.item_name)
    swordsmen: Rule = Has(Age2ItemData.AP_JOAN_1_SWORDSMEN.item_name)
    crossbowmen: Rule = Has(Age2ItemData.AP_JOAN_1_CROSSBOWMEN.item_name)
    recruits: Rule = Has(Age2ItemData.AP_JOAN_1_RECRUITS.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ItemData.JOAN_OF_ARC.item_name)
        self.has_vils = False_()

        self.can_cross_water = self.transport & logic.units.survives_caveman(U.TRANSPORT_SHIP)
        recruited = self.recruits & self.can_cross_water

        self.obtains_unit[U.TRANSPORT_SHIP] = self.transport
        self.obtains_unit[U.PIKEMAN] = self.ram_army
        self.obtains_unit[U.CAPPED_RAM] = self.ram_army
        self.obtains_unit[U.MAN_AT_ARMS] = self.swordsmen | self.ram_army
        self.obtains_unit[U.CROSSBOWMAN] = self.crossbowmen | recruited
        self.obtains_unit[U.SCORPION] = recruited
