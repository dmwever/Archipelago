from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..locations.Buildings import Age2BuildingData

from rule_builder.options import OptionFilter
from rule_builder.rules import False_, Or, Rule, True_

from ..Options import ExistingTechs
from ..locations.Ages import Age2AgeData


VANILLA_AGE_START = OptionFilter(ExistingTechs, ExistingTechs.option_start_in_dark_age, "ne")
DARK_START = OptionFilter(ExistingTechs, ExistingTechs.option_start_in_dark_age)

if TYPE_CHECKING:
    from .. import Age2World
    from ..locations.Scenarios import Age2ScenarioData
    from .Logic import Logic

@dataclass
class ScenarioStartingState:
    is_unlocked: Rule = field(default_factory=lambda: False_())
    has_vils: Rule = field(default_factory=lambda: True_())
    has_base: Rule = field(default_factory=lambda: True_())
    age_playable: dict[Age2AgeData, Rule] = field(default_factory=lambda: { age: False_() for age in Age2AgeData })
    starts_with_building: dict[Age2BuildingData, Rule] = field(default_factory=lambda: { building: False_() for building in Age2BuildingData })
    has_water_access: Rule = field(default_factory=lambda: True_())

    def __post_init__(self):
        self.age_playable[Age2AgeData.DARK] = True_() & DARK_START

class ScenarioLogic:
    starting_state: ScenarioStartingState

    def __init__(self, logic: 'Logic', data: ScenarioStartingState,
                 scenario: 'Age2ScenarioData'):
        self.logic = logic
        self.scenario = scenario
        self.starting_state = data
    
    def has_vils(self) -> Rule:
        return self.starting_state.has_vils
    
    def has_base(self) -> Rule:
        return self.starting_state.has_base

    def can_reach_age(self, age: Age2AgeData) -> Rule:
        return self.starting_state.age_playable[age]

    def start_past_age(self, age: Age2AgeData) -> Rule:
        if self.scenario.vanilla_age > age:
            return True_() & VANILLA_AGE_START
        return False_()
    
    def start_with_building(self, building: Age2BuildingData) -> Rule:
        return self.starting_state.starts_with_building[building] | self.logic.can_build_building(building)
    
    def is_unlocked(self) -> Rule:
        return self.starting_state.is_unlocked