from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import True_

from ..Options import Techsanity


if TYPE_CHECKING:
    from .Rules import Rules


class TechRules:

    def __init__(self, rules: 'Rules'):
        self.rules = rules
        self.world = rules.world
        self.logic = rules.logic

    def set_rules(self):
        if self.world.options.techsanity == Techsanity.option_none:
            return
        for tech in self.world.pool.techs.shuffled:
            rule = self.logic.can_research_anywhere(tech)
            if isinstance(rule, True_):
                continue
            self.world.set_rule(self.world.get_location(tech.location_name), rule)
