from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, HasAll, Rule, True_
from ..items.Items import Age2ItemData

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

class BuildingLogic:
    
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world

    def has_building(self, building: Age2BuildingData) -> Rule:
        has_prerequisites = self.has_prerequisites(building)
        if building not in self.world.shuffled_buildings:
            return has_prerequisites
        return has_prerequisites & Has(building.item.item_name)

    def has_prerequisites(self, building: Age2BuildingData) -> Rule:
        if building in (Age2BuildingData.ARCHERY_RANGE, Age2BuildingData.STABLE):
            return self.has_building(Age2BuildingData.BARRACKS)

        if building in (Age2BuildingData.FARM, Age2BuildingData.MARKET):
            return self.has_building(Age2BuildingData.MILL)

        if building == Age2BuildingData.SIEGE_WORKSHOP:
            return self.has_building(Age2BuildingData.BLACKSMITH)

        if building == Age2BuildingData.FISH_TRAP:
            return self.has_building(Age2BuildingData.DOCK)

        return True_()

    def can_build_tc(self) -> Rule:
        return self.has_building(Age2BuildingData.TOWN_CENTER) & \
            HasAll(Age2ItemData.TOWN_CENTER_WOOD.item_name, Age2ItemData.TOWN_CENTER_STONE.item_name)
