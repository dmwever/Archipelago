from __future__ import annotations
from typing import TYPE_CHECKING


from ..locations.Ages import Age2AgeData
from rule_builder.rules import False_, Has, Or, Rule

from .ScenarioLogic import ScenarioLogic


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic
    
class AgeLogic:
    
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
        self.age_to_scenarios: dict[Age2AgeData, Rule] = {age: False_() for age in Age2AgeData }
        self.can_reach_age: dict[Age2AgeData, Or] = {age: Or() for age in Age2AgeData}
        
    def set_can_reach_age(self, scenarios: list[ScenarioLogic]):
        for age in Age2AgeData:
            self.can_reach_age[age].children = tuple(
                scenario.is_unlocked()
                & (scenario.ages.can_reach(age) | scenario.ages.start_past(age))
                for scenario in scenarios)
    
    def set_age_to_scenarios(self, scenarios: list[ScenarioLogic]):
        for age in Age2AgeData:
            rule = self.age_to_scenarios[age]
            for scenario in scenarios:
                rule = rule | (scenario.is_unlocked() & scenario.ages.can_reach(age))
            self.age_to_scenarios[age] = rule
    
    def has_age(self, age: Age2AgeData) -> Rule:
        if not self.world.options.shuffle_ages or age not in self.world.shuffled_ages:
            return True_()
        return Has(age.item.item_name)