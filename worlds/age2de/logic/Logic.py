from __future__ import annotations

from typing import TYPE_CHECKING

from ..Options import Goal

from .goal_logic import GoalLogic

from .MilitaryLogic import MilitaryLogic
from ..locations.Buildings import Age2BuildingData
from ..locations.connections import ScenarioDataLogic
from .ScenarioLogic import ScenarioLogic
from .age_logic import AgeLogic
from .building_logic import BuildingLogic
from rule_builder.rules import False_, Or, Rule

from ..locations.Ages import Age2AgeData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS


if TYPE_CHECKING:
    from .. import Age2World


class Logic:
    buildings: BuildingLogic
    ages: AgeLogic
    military: MilitaryLogic
    goal: GoalLogic
    scenarios: list[ScenarioLogic]

    def __init__(self, world: Age2World):
        self.world = world
        self.scenarios = []

        self._has_vils: Or = Or()
        self._can_reach_age: dict[Age2AgeData, Or] = {age: Or() for age in Age2AgeData}

        self.buildings = BuildingLogic(self, world)
        self.ages =  AgeLogic(self, world)
        for campaign in world.included_campaigns:
            for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
                self.scenarios.append(ScenarioLogic(self, scenario.logic(self), scenario))
        self._has_vils.children = tuple(
            scenario.is_unlocked() & scenario.has_vils() for scenario in self.scenarios)
        for age in Age2AgeData:
            self._can_reach_age[age].children = tuple(
                scenario.is_unlocked() & scenario.can_reach_age(age)
                for scenario in self.scenarios)
        self.military = MilitaryLogic(self, world)
        self.goal = GoalLogic(self, world)

    def has_goal(self) -> Rule:
        if self.world.options.goal == Goal.option_campaign_completion:
            return self.goal.completed_all_campaigns()
        return False_()

    def can_build_base(self) -> Rule:
        return self.buildings.can_build_tc() & self.can_build_building(Age2BuildingData.HOUSE)

    def has_military(self) -> Rule:
        return self.buildings.has_military()
    
    def has_siege(self) -> Rule:
        return self.buildings.has_siege()
    
    def has_vils(self) -> Rule:
        return self._has_vils

    def can_reach_age(self, age: Age2AgeData) -> Rule:
        return self._can_reach_age[age]

    def can_build_building(self, building: Age2BuildingData) -> Rule:
        can_build: Rule = (self.buildings.has_building(building)
                           & self.ages.can_reach(building.age)
                           & self.buildings.has_prerequisites(building))
        return can_build & self.has_vils() & self.can_reach_age(building.age)