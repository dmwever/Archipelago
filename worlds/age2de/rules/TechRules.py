from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import True_

from ..Options import Techsanity
from ..locations.Buildings import NAME_TO_BUILDING


if TYPE_CHECKING:
    from .Rules import Rules


class TechRules:

    def __init__(self, rules: 'Rules'):
        self.rules = rules
        self.world = rules.world
        self.logic = rules.logic
        self.doors = list(self.world.get_region("Can Build").exits)

    def set_rules(self):
        if self.world.options.techsanity == Techsanity.option_none:
            return
        for door in self.doors:
            building = NAME_TO_BUILDING[door.connected_region.name]
            self.world.set_rule(door, self.logic.can_build_building(building))
        for tech in self.world.shuffled_techs:
            rule = self.logic.can_research(tech)
            if isinstance(rule, True_):
                continue
            self.world.set_rule(self.world.get_location(tech.location_name), rule)
