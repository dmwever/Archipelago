from __future__ import annotations
from typing import TYPE_CHECKING

from ..locations.Ages import Age2AgeData, Age2ItemData
from ..locations.Buildings import Age2BuildingData
from rule_builder.rules import HasAll, HasFromListUnique, Rule, True_


if TYPE_CHECKING:
    from .. import Age2World
    from .Rules import Rules
    
class AgeRules:
    
    def __init__(self, rules: 'Rules', world: Age2World):
        self.rules = rules
        self.world = world
        
    two_from_dark_age: Rule = HasFromListUnique(
            Age2ItemData.MILL.item_name,
            Age2ItemData.LUMBER_CAMP.item_name,
            Age2ItemData.MINING_CAMP.item_name,
            Age2ItemData.DOCK.item_name,
            Age2ItemData.BARRACKS.item_name, count=2)

    two_from_feudal_age: Rule = HasFromListUnique(
            Age2ItemData.ARCHERY_RANGE.item_name,
            Age2ItemData.STABLE.item_name,
            Age2ItemData.MARKET.item_name,
            Age2ItemData.BLACKSMITH.item_name, count=2)

    two_from_castle_age: Rule = HasFromListUnique(
            Age2ItemData.MONASTERY.item_name,
            Age2ItemData.UNIVERSITY.item_name,
            Age2ItemData.SIEGE_WORKSHOP.item_name, count=2)

    can_build_tc = HasAll(
            Age2ItemData.TOWN_CENTER_STONE.item_name,
            Age2ItemData.TOWN_CENTER_WOOD.item_name,
            Age2ItemData.TOWN_CENTER.item_name)
        
    can_reach_feudal: Rule = two_from_dark_age & can_build_tc
        
    can_reach_castle: Rule = two_from_feudal_age & can_build_tc
        
    can_reach_imperial: Rule = two_from_castle_age & can_build_tc

    def has_age(self, age: Age2AgeData) -> Rule:
        return True_()

    def has_building_age(self, building: Age2BuildingData) -> Rule:
        if building.age is Age2AgeData.FEUDAL:
            return self.can_reach_feudal
        elif building.age is Age2AgeData.CASTLE:
            return self.can_reach_castle
        elif building.age is Age2AgeData.IMPERIAL:
            return self.can_reach_imperial
        else:
            return True_()