from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, HasAll, Rule, True_
from ..items.Items import Age2ItemData

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

class CounterLogic:
    
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
    
    def has_anti_cav(self) -> Rule:
        return self.logic.buildings.has_anti_cav_building()
    
    def has_anti_archers(self) -> Rule:
        return self.logic.buildings.has_anti_archer_building()