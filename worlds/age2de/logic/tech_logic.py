from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_

from ..Options import LockTechs
from ..locations.Ages import Age2AgeData
from ..locations.Techs import Age2TechData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic


class TechLogic:
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world

    def can_research(self, tech: Age2TechData) -> Rule:
        rule = self.has_tech_items(tech)
        locked_at_start = self.world.tech_pool.locked_at_start(tech)
        if not locked_at_start:
            rule = rule & self.logic.ages.age_to_scenarios[tech.age]
        elif tech.age > tech.buildings[0].age:
            rule = rule & self.logic.can_reach_age(tech.age)
        return rule
    
    def has_tech_items(self, tech: Age2TechData) -> Rule:
        if self.world.options.lock_techs == LockTechs.option_effects:
            return True_()
        rule: Rule = Has(tech.item.item_name)
        prerequisite = tech.prerequisite
        if prerequisite is not None and self.world.tech_pool.includes(prerequisite):
            rule = rule & self.can_research(prerequisite)
        return rule
