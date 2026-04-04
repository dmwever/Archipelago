from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..locations.Buildings import Age2BuildingData

from rule_builder.rules import False_, Rule, True_

from ..locations.Ages import Age2AgeData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

@dataclass
class ScenarioStartingState:
    is_unlocked: Rule = field(default_factory=lambda: False_())
    has_vils: Rule = field(default_factory=lambda: True_())
    has_tc: Rule = field(default_factory=lambda: True_())
    has_ages: dict[Age2AgeData, Rule] = field(default_factory=lambda: { age: False_() for age in Age2AgeData })
    can_reach_age: dict[Age2AgeData, Rule] = field(default_factory=lambda: { age: False_() for age in Age2AgeData })
    starts_with_building: dict[Age2BuildingData, Rule] = field(default_factory=lambda: { building: False_() for building in Age2BuildingData })
    has_water_access: Rule = field(default_factory=lambda: True_())

class ScenarioLogic:
    starting_state: ScenarioStartingState
    
    def __init__(self, logic: 'Logic', data: ScenarioStartingState):
        self.logic = logic
        self.starting_state = data
        self.starting_state.has_ages[Age2AgeData.DARK] = True_()
        self.starting_state.can_reach_age[Age2AgeData.DARK] = True_()
    
    def has_vils(self) -> Rule:
        return self.starting_state.has_vils
    
    def has_tc(self) -> Rule:
        return self.starting_state.has_tc
    
    def can_reach_age(self, age: Age2AgeData) -> Rule:
        return self.starting_state.can_reach_age[age]
    
    def start_with_building(self, building: Age2BuildingData) -> Rule:
        return self.starting_state.starts_with_building[building]
    
    def is_unlocked(self) -> Rule:
        return self.starting_state.is_unlocked