from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, HasAll, Rule, True_
from ..items.Items import Age2ItemData

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .Rules import Rules

class BuildingRules:
    
    def __init__(self, rules: 'Rules'):
        self.rules = rules
        self.world = rules.world
        self.logic = rules.logic
    
    def set_rules(self):
        for building in self.world.included_buildings:
            self.world.set_rule(self.world.get_location(building.location_name), self.logic.can_build_building(building))