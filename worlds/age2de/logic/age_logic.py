from __future__ import annotations
from typing import TYPE_CHECKING


from ..locations.Ages import Age2AgeData
from rule_builder.rules import Has, Or, Rule, True_

from .ScenarioLogic import ScenarioLogic


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic
    
class AgeLogic:
    
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
        self.can_reach_age: dict[Age2AgeData, Or] = {age: Or() for age in Age2AgeData}

    def set_can_reach_age(self, scenarios: list[ScenarioLogic]):
        """What the age advancement events ask: somewhere you climb into this age.

        Not can_reach, which counts a scenario that opens at or above the age. Neither researches
        the age, and the location can only be sent by researching it, so counting them let a seed
        put progression behind an age it never had to reach.
        """
        for age in Age2AgeData:
            self.can_reach_age[age].children = tuple(
                scenario.is_unlocked() & scenario.ages.can_research(age)
                for scenario in scenarios)
    
    def has_age(self, age: Age2AgeData) -> Rule:
        if age not in self.world.pool.ages.shuffled:
            return True_()
        return Has(age.item.item_name)