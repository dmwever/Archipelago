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
        if building not in self.world.included_buildings:
            return has_prerequisites
        return has_prerequisites & Has(building.item.item_name)
    
    def has_prerequisites(self, building: Age2BuildingData) -> Rule:
        if building == (Age2BuildingData.ARCHERY_RANGE or Age2BuildingData.STABLE):
            return self.has_building(Age2BuildingData.BARRACKS)
        
        if building == (Age2BuildingData.FARM or Age2BuildingData.MARKET):
            return self.has_building(Age2BuildingData.MILL)
        
        if building == Age2BuildingData.SIEGE_WORKSHOP:
            return self.has_building(Age2BuildingData.BLACKSMITH)
        
        if building == Age2BuildingData.FISH_TRAP:
            return self.has_building(Age2BuildingData.DOCK)
        
        return True_()
    
    def can_build_tc(self) -> Rule:
        return self.has_building(Age2BuildingData.TOWN_CENTER) & \
            HasAll(Age2ItemData.TOWN_CENTER_WOOD.item_name, Age2ItemData.TOWN_CENTER_STONE.item_name)
    
    def has_siege_building(self) -> Rule:
        return self.has_building(Age2BuildingData.CASTLE) | self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
    
    def has_anti_building_building(self) -> Rule:
        return self.has_building(Age2BuildingData.BARRACKS) | self.has_building(Age2BuildingData.STABLE) | self.has_siege_building()
    
    def has_anti_cav_building(self) -> Rule:
        return self.has_building(Age2BuildingData.BARRACKS) | self.has_building(Age2BuildingData.STABLE)
    
    def has_anti_archer_building(self) -> Rule:
        return self.has_building(Age2BuildingData.STABLE) | self.has_building(Age2BuildingData.SIEGE_WORKSHOP) | self.has_building(Age2BuildingData.ARCHERY_RANGE)
    
    def has_anti_siege_building(self) -> Rule:
        return self.has_building(Age2BuildingData.STABLE) | self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
    
    def has_anti_inf_building(self) -> Rule:
        return self.has_building(Age2BuildingData.STABLE) | self.has_building(Age2BuildingData.SIEGE_WORKSHOP) | self.has_building(Age2BuildingData.ARCHERY_RANGE)
    
    def has_military_building(self) -> Rule:
        return self.has_anti_building_building() | self.has_building(Age2BuildingData.ARCHERY_RANGE)
    
    def has_farms(self):
        return self.has_building(Age2BuildingData.FARM) & self.has_prerequisites(Age2BuildingData.FARM)