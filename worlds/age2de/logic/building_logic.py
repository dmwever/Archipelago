from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, Rule, True_

from ..locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic


class BuildingLogic:

    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world

    def has_building(self, building: Age2BuildingData) -> Rule:
        return self.has_prerequisites(building) & self.has_building_item(building)

    def has_building_item(self, building: Age2BuildingData) -> Rule:
        if building not in self.world.pool.buildings.shuffled:
            return True_()
        return Has(building.item.item_name)

    def prerequisite(self, building: Age2BuildingData) -> Age2BuildingData | None:
        if building not in BUILDING_PREREQUISITE:
            return None
        return BUILDING_PREREQUISITE[building]

    def has_prerequisites(self, building: Age2BuildingData) -> Rule:
        prerequisite = self.prerequisite(building)
        if prerequisite is None:
            return True_()
        return self.has_building(prerequisite)

    def can_build_tc(self) -> Rule:
        """Putting one up, less paying for it: ages, dropsites and second Town Centers ask this
        structurally, and the budget charges a Town Center wherever one is needed."""
        return self.has_building(Age2BuildingData.TOWN_CENTER)
