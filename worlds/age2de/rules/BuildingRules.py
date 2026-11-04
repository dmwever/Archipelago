from __future__ import annotations

from typing import TYPE_CHECKING

from ..locations.Buildings import NAME_TO_BUILDING


if TYPE_CHECKING:
    from .Rules import Rules

class BuildingRules:
    
    def __init__(self, rules: 'Rules'):
        self.rules = rules
        self.world = rules.world
        self.logic = rules.logic
    
    def set_rules(self):
        for building in self.world.pool.buildings.locations:
            self.world.set_rule(self.world.get_location(building.location_name),
                                self.logic.can_build_anywhere(building))
        for door in self.world.get_region("Can Build").exits:
            building = NAME_TO_BUILDING[door.connected_region.name]
            self.world.set_rule(door, self.logic.can_build_anywhere(building))
        for door in self.world.get_region("Starts With Building").exits:
            building = NAME_TO_BUILDING[door.connected_region.name]
            self.world.set_rule(door, self.logic.starts_with_building_anywhere(building))
