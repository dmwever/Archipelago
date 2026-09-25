from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Or, Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData

if TYPE_CHECKING:
    from ..building_logic import BuildingLogic
    from ..ScenarioLogic import ScenarioLogic


class ScenarioBuildingLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self.buildings: BuildingLogic = scenario.logic.buildings

    def can_build_building(self, building: Age2BuildingData) -> Rule:
        if not self.scenario.civilization.can_build(building):
            return False_()   # not this civilisation's to put up
        return (self.buildings.has_building(building)
                & self.buildings.has_prerequisites(building)
                & self.scenario.has_vils()
                & self.scenario.can_play_age(building.age))

    def can_build_anything(self) -> Rule:
        return Or(*[self.can_build_building(building) for building in Age2BuildingData
                    if self.scenario.civilization.can_build(building)])

    def can_build_tc(self) -> Rule:
        return self.buildings.can_build_tc() & self.scenario.has_vils()

    def can_build_base(self) -> Rule:
        if not self.scenario.civilization.can_build(Age2BuildingData.HOUSE):
            return self.can_build_tc()
        return self.can_build_tc() & self.can_build_building(Age2BuildingData.HOUSE)

    def can_build_multiple_tc(self) -> Rule:
        return self.can_build_tc() & self.scenario.can_play_age(Age2AgeData.CASTLE)

    def can_mine(self) -> Rule:
        """Gold and stone need somewhere to drop off, unless a second town centre covers it."""
        return (self.can_build_multiple_tc()
                | self.can_build_building(Age2BuildingData.MINING_CAMP))
