from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from NetUtils import JSONMessagePart
from BaseClasses import CollectionState
from ..rules.AgeRules import TwoBuildingsRequirement

from ..locations.Ages import Age2AgeData, Age2ItemData
from ..locations.Buildings import Age2BuildingData
from rule_builder.rules import False_, HasAll, HasAny, HasFromListUnique, NestedRule, Rule, True_


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic
    
class AgeLogic:
    
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
    
    def two_from_dark_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.logic.buildings.has_building(Age2BuildingData.MILL),
            self.logic.buildings.has_building(Age2BuildingData.LUMBER_CAMP),
            self.logic.buildings.has_building(Age2BuildingData.MINING_CAMP),
            self.logic.buildings.has_building(Age2BuildingData.DOCK),
            self.logic.buildings.has_building(Age2BuildingData.BARRACKS)
        ])
    
    def two_from_fuedal_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.logic.buildings.has_building(Age2BuildingData.ARCHERY_RANGE),
            self.logic.buildings.has_building(Age2BuildingData.STABLE),
            self.logic.buildings.has_building(Age2BuildingData.MARKET),
            self.logic.buildings.has_building(Age2BuildingData.BLACKSMITH)
        ])
    
    def two_from_castle_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.logic.buildings.has_building(Age2BuildingData.MONASTERY),
            self.logic.buildings.has_building(Age2BuildingData.UNIVERSITY),
            self.logic.buildings.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        ]) | self.logic.buildings.has_building(Age2BuildingData.CASTLE)

    def can_reach_feudal(self) -> Rule:
        return self.has_age(Age2AgeData.FEUDAL) & (self.two_from_dark_age() & self.logic.buildings.can_build_tc())
        
    def can_reach_castle(self) -> Rule:
        return self.has_age(Age2AgeData.CASTLE) & self.two_from_fuedal_age() & self.logic.buildings.can_build_tc()
        
    def can_reach_imperial(self) -> Rule:
        return self.has_age(Age2AgeData.IMPERIAL) & self.two_from_castle_age() & self.logic.buildings.can_build_tc()

    def has_age(self, age: Age2AgeData) -> Rule:
        return True_()

    def has_building_age(self, building: Age2BuildingData) -> Rule:
        if building.age is Age2AgeData.FEUDAL:
            return self.can_reach_feudal()
        elif building.age is Age2AgeData.CASTLE:
            return self.can_reach_castle()
        elif building.age is Age2AgeData.IMPERIAL:
            return self.can_reach_imperial()
        else:
            return True_()