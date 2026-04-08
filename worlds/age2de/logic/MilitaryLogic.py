from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, HasAll, Rule, True_
from ..locations.Ages import Age2AgeData
from ..items.Items import Age2ItemData

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

class MilitaryLogic:
    
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
    
    def has_siege(self) -> Rule:
        return self.logic.buildings.has_siege()
    
    def has_long_range_siege(self) -> Rule:
        return self.logic.buildings.has_siege() & self.logic.ages.can_reach_imperial()
    
    def has_military(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.logic.buildings.has_military() & self.logic.ages.has_age(age)
    
    def has_anti_infantry(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.logic.buildings.has_anti_infantry() & self.logic.ages.has_age(age)
    
    def has_anti_trash(self, age: Age2AgeData = Age2AgeData.FEUDAL) -> Rule:
        return self.logic.buildings.has_anti_trash() & self.logic.ages.has_age(age)
    
    def has_anti_cav(self, age: Age2AgeData = Age2AgeData.FEUDAL) -> Rule:
        return self.logic.buildings.has_anti_cav() & self.logic.ages.has_age(age)
    
    def has_anti_archers(self, age: Age2AgeData = Age2AgeData.FEUDAL) -> Rule:
        return self.logic.buildings.has_anti_archer() & self.logic.ages.has_age(age)
    
    def has_navy(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.logic.buildings.has_building(Age2BuildingData.DOCK) & self.logic.ages.has_age(age)
    
    def has_naval_bombardment(self) -> Rule:
        return self.logic.buildings.has_building(Age2BuildingData.DOCK) & self.logic.ages.can_reach_imperial()