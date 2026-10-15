from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Units import Age2UnitData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Genghis3StartingState(ScenarioStartingState):
    transport: Rule = Has(Age2ItemData.AP_GENGHIS_3_TRANSPORT.item_name)
    engineers: Rule = Has(Age2ItemData.AP_GENGHIS_3_ENGINEERS.item_name)
    bombards: Rule = Has(Age2ItemData.AP_GENGHIS_3_BOMBARDS.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 2)

        self.has_vils = self.engineers & self.transport
        self.obtains_unit[Age2UnitData.TRANSPORT_SHIP] = self.transport

        self.starts_with_building[Age2BuildingData.SIEGE_WORKSHOP] = (
            self.bombards | self.engineers)
