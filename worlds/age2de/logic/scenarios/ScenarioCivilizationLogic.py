from __future__ import annotations

from typing import TYPE_CHECKING

from ...locations.Buildings import Age2BuildingData, BuildingOption
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from ...locations.connections.CivilizationTechs import CIV_TO_TECHS

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


class ScenarioCivilizationLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.world = scenario.logic.world
        self.civ = scenario.scenario.civ

    def can_build(self, building: Age2BuildingData) -> bool:
        if BuildingOption.unique in building.building_options:
            return building in self.civ.included_buildings
        return building not in self.civ.excluded_buildings

    def trains(self, unit: Age2UnitData) -> bool:
        return self.world.unit_pool.civ_trains(self.civ, unit)

    def researches(self, tech: Age2TechData) -> bool:
        return tech in CIV_TO_TECHS[self.civ]
