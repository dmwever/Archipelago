from __future__ import annotations
from typing import TYPE_CHECKING




if TYPE_CHECKING:
    from .. import Age2World
    from .Rules import Rules
    
class AgeRules:
    
    def __init__(self, rules: 'Rules', world: Age2World):
        self.rules = rules
        self.world = world
        self.logic = rules.logic

    def set_rules(self):
        if not self.world.options.shuffle_ages:
            return  # create_regions built no age locations to rule on
        for age in self.world.shuffled_ages:
            self.world.set_rule(self.world.get_location(age.location_name),
                                self.logic.can_reach_age_anywhere(age))
