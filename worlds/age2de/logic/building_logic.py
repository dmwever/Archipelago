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
            
    def can_build_multiple_tc(self) -> Rule:
        return self.can_build_tc() & self.logic.ages.can_reach_castle()
    
    # Military
    
    def has_military(self) -> Rule:
        return self.contains_building_counter() | self.has_building(Age2BuildingData.ARCHERY_RANGE)
    
    def has_siege(self) -> Rule:
        return self.has_building(Age2BuildingData.CASTLE) | self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
    
    # Counters
    
    def contains_building_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.STABLE) |
            self.has_siege()
        )

    def contains_milita_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.ARCHERY_RANGE) |
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        )


    def contains_spear_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.ARCHERY_RANGE) |
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        )


    def contains_scout_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.STABLE)
        )


    def contains_knight_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.MONASTERY)
        )


    def contains_skirmisher_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP) |
            self.has_building(Age2BuildingData.ARCHERY_RANGE)
        )


    def contains_archer_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP) |
            self.has_building(Age2BuildingData.ARCHERY_RANGE)
        )


    def contains_cav_archer_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP) |
            self.has_building(Age2BuildingData.ARCHERY_RANGE)
        )


    def contains_ram_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP) |
            self.has_building(Age2BuildingData.STABLE)
        )


    def contains_scorpion_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        )


    def contains_mangonel_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        )
        

    def contains_monk_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.ARCHERY_RANGE)
        )

    def contains_trebuchet_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP) |
            self.has_building(Age2BuildingData.CASTLE)
        )
        
    # Unique Counters
    
    def contains_centurion_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.MONASTERY) |
            self.has_building(Age2BuildingData.BARRACKS)
        )


    def contains_huskarl_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.STABLE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        )


    def contains_legionary_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.ARCHERY_RANGE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        )


    def contains_longbowman_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.ARCHERY_RANGE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        )


    def contains_mangudai_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.BARRACKS) |
            self.has_building(Age2BuildingData.ARCHERY_RANGE) |
            self.has_building(Age2BuildingData.STABLE)
        )


    def contains_throwing_axeman_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.ARCHERY_RANGE) |
            self.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        )


    def contains_war_elephant_counter(self) -> Rule:
        return (
            self.has_building(Age2BuildingData.MONASTERY) |
            self.has_building(Age2BuildingData.BARRACKS)
        )
    
    # Resources
    
    def can_mine(self) -> Rule:
        return self.can_build_multiple_tc() | self.has_building(Age2BuildingData.MINING_CAMP)
    
    def can_chop(self) -> Rule:
        return self.can_build_multiple_tc() | self.has_building(Age2BuildingData.LUMBER_CAMP)
    
    def can_gather_food(self) -> Rule:
        return self.can_build_multiple_tc() | self.has_farms() | self.has_building(Age2BuildingData.MILL)
    
    def has_farms(self):
        return self.has_building(Age2BuildingData.FARM)
    
    def has_fish_traps(self) -> Rule:
        return self.has_building(Age2BuildingData.FISH_TRAP)
    
    def has_renewable_food(self) -> Rule:
        return self.has_farms() | self.has_fish_traps()