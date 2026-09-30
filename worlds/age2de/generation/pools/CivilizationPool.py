from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from ...locations.connections.CivilizationTechs import CIV_TO_TECHS
from ...locations.connections.CivilizationUnits import CIV_TO_UNITS

if TYPE_CHECKING:
    from ...locations.Buildings import Age2BuildingData
    from ...locations.Civilizations import Age2CivData
    from ...locations.Scenarios import Age2ScenarioData
    from ...locations.Techs import Age2TechData
    from ...locations.Units import Age2UnitData


class CivilizationPool:
    def __init__(self, scenarios: Iterable['Age2ScenarioData']) -> None:
        self.included: list['Age2CivData'] = list(dict.fromkeys(
            scenario.civ for scenario in scenarios))

    def builds(self, building: 'Age2BuildingData') -> bool:
        return any(civ.builds(building) for civ in self.included)

    def any_trains(self, unit: 'Age2UnitData') -> bool:
        return any(unit in CIV_TO_UNITS[civ] for civ in self.included)

    def any_researches(self, tech: 'Age2TechData') -> bool:
        return any(tech in CIV_TO_TECHS[civ] for civ in self.included)
