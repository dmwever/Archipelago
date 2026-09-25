from __future__ import annotations

from typing import TYPE_CHECKING

from ..Options import Goal

from .goal_logic import GoalLogic

from ..locations.Buildings import Age2BuildingData
from ..locations.connections import ScenarioDataLogic
from .ScenarioLogic import ScenarioLogic
from .age_logic import AgeLogic
from .building_logic import BuildingLogic
from .tech_logic import TechLogic
from .unit_logic import UnitLogic
from rule_builder.rules import False_, Or, Rule

from ..locations.Ages import Age2AgeData
from ..locations.Techs import Age2TechData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS


if TYPE_CHECKING:
    from .. import Age2World


class Logic:
    buildings: BuildingLogic
    ages: AgeLogic
    goal: GoalLogic
    techs: TechLogic
    units: UnitLogic
    scenarios: list[ScenarioLogic]

    def __init__(self, world: Age2World):
        self.world = world
        self.scenarios = []

        self._has_vils: Or = Or()
        self._can_build: dict[Age2BuildingData, Or] = {building: Or()
                                                       for building in Age2BuildingData}
        self._can_build_anything: Or = Or()
        self._can_research: dict[Age2TechData, Or] = {}

        self.buildings = BuildingLogic(self, world)
        self.techs = TechLogic(self, world)
        self.units = UnitLogic(self, world)
        self.ages =  AgeLogic(self, world)
        
        for campaign in world.included_campaigns:
            for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
                self.scenarios.append(ScenarioLogic(self, scenario.logic(self), scenario))
        self._has_vils.children = tuple(
            scenario.is_unlocked() & scenario.has_vils() for scenario in self.scenarios)
        for building in Age2BuildingData:
            self._can_build[building].children = tuple(
                scenario.is_unlocked() & scenario.buildings.can_build_building(building)
                for scenario in self.scenarios)
        self._can_build_anything.children = tuple(
            scenario.is_unlocked() & scenario.buildings.can_build_anything()
            for scenario in self.scenarios)
        for tech in Age2TechData:
            self._can_research[tech] = Or(*[
                scenario.is_unlocked() & scenario.techs.can_research(tech)
                for scenario in self.scenarios])
        
        self.ages.set_age_to_scenarios(self.scenarios)
        self.ages.set_can_reach_age(self.scenarios)
        
        self.goal = GoalLogic(self, world)

    def has_goal(self) -> Rule:
        if self.world.options.goal == Goal.option_campaign_completion:
            return self.goal.completed_all_campaigns()
        return False_()

    def can_build_base(self) -> Rule:
        return self.buildings.can_build_tc() & self.can_build_building(Age2BuildingData.HOUSE)


    def has_vils(self) -> Rule:
        return self._has_vils

    def can_reach_age(self, age: Age2AgeData) -> Rule:
        return self.ages.can_reach_age[age]

    def can_build_anything(self) -> Rule:
        return self._can_build_anything

    def can_research(self, tech: Age2TechData) -> Rule:
        return self._can_research[tech]

    def can_build_building(self, building: Age2BuildingData) -> Rule:
        return self._can_build[building]
