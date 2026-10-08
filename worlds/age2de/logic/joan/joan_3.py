from typing import TYPE_CHECKING

from rule_builder.rules import Has, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Ages import Age2AgeData

from ...locations.Buildings import Age2BuildingData
from ...locations.Units import Age2UnitData as U
from ...items.Items import Age2ItemData
from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan3StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 2)
        self.max_age = Age2AgeData.CASTLE
        self.has_vils = True_()

        has_boats = Has(Age2ItemData.AP_JOAN_3_TRANSPORT.item_name)
        self.obtains_unit[U.TRANSPORT_SHIP] = has_boats
        self.required_purchases = {U.TRANSPORT_SHIP: has_boats}
        self.obtains_unit[U.DEMOLITION_SHIP] = has_boats
        self.meets_additional_base_requirements = has_boats | (
            logic.buildings.has_building(Age2BuildingData.DOCK)
            & logic.units.has_unit_items(U.TRANSPORT_SHIP))
