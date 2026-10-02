from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, Rule, True_
from ..items.Items import Age2ItemData

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

BUILDING_PREREQUISITE: dict[Age2BuildingData, Age2BuildingData] = {
    Age2BuildingData.ARCHERY_RANGE: Age2BuildingData.BARRACKS,
    Age2BuildingData.STABLE: Age2BuildingData.BARRACKS,
    Age2BuildingData.FARM: Age2BuildingData.MILL,
    Age2BuildingData.MARKET: Age2BuildingData.MILL,
    Age2BuildingData.SIEGE_WORKSHOP: Age2BuildingData.BLACKSMITH,
    Age2BuildingData.FISH_TRAP: Age2BuildingData.DOCK,
}


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
        villager_food = Age2ItemData.STARTING_VILLAGER_FOOD.type
        resources = self.logic.resources
        return (self.has_building(Age2BuildingData.TOWN_CENTER)
                & resources.has_amounts(Age2ItemData.TOWN_CENTER.type.needed_resources)
                & resources.has_amount(villager_food.type, villager_food.amount))
