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
from rule_builder.rules import False_, Rule

from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS


if TYPE_CHECKING:
    from .. import Age2World


class Logic:
    buildings: BuildingLogic
    ages: AgeLogic
    military: MilitaryLogic
    goal: GoalLogic
    scenarios: list[ScenarioLogic] = []
    
    def __init__(self, world: Age2World):
        self.buildings = BuildingLogic(self, world)
        self.ages =  AgeLogic(self, world)
        for campaign in world.included_campaigns:
            for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
                self.scenarios.append(ScenarioLogic(self, scenario.logic(self)))
        self.military = MilitaryLogic(self, world)
        self.world = world
        self.goal = GoalLogic(self, world)

    def has_goal(self) -> Rule:
        if self.world.options.goal == Goal.option_campaign_completion:
            return self.goal.completed_all_campaigns()
        return False_()

    def has_military(self) -> Rule:
        return self.buildings.has_military()
    
    def has_siege(self) -> Rule:
        return self.buildings.has_siege()
    
    def can_build_building(self, building: Age2BuildingData) -> Rule:
        can_build: Rule = self.buildings.has_building(building) & self.ages.has_building_age(building) & self.buildings.has_prerequisites(building)
        has_vils: Rule = False_()
        can_reach_age: Rule = False_()
        for scenario in self.scenarios:
            has_vils = has_vils | (scenario.is_unlocked() & scenario.has_vils())
            can_reach_age = can_reach_age | (scenario.is_unlocked() & scenario.can_reach_age(building.age))
        return can_build & has_vils & can_reach_age