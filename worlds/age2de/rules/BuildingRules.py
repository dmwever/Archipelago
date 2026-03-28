from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, Rule, True_

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Rules import Rules

class BuildingRules:
    
    def __init__(self, rules: 'Rules', world: Age2World):
        self.rules = rules
        self.world = world
        
    def set_rules(self) -> None:
        for building in self.world.included_buildings:
            self.world.set_rule(self.world.get_location(building.location_name), self.has_building(building) & self.rules.age_rules.has_building_age(building))
    
    def has_building(self, building: Age2BuildingData) -> Rule:
        if building not in self.world.included_buildings:
            return True_()
        return Has(building.item.item_name)
    
    def can_build(self, building: Age2BuildingData) -> Rule:
        return self.rules.can_build(building)