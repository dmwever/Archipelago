from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from ...locations.connections.CivilizationUnits import CIV_TO_UNITS

if TYPE_CHECKING:
    from ...locations.Buildings import Age2BuildingData
    from ...locations.Civilizations import Age2CivData
    from ...locations.Scenarios import Age2ScenarioData
    from ...locations.Units import Age2UnitData


class CivilizationPool:
    """The civilisations this seed plays, and what any of them can do.

    Nobody picks these: a scenario comes with its civilisation, so the seed's civs are whichever
    ones its scenarios bring. Deduplicated in scenario order, because building, tech and unit
    membership are all decided by walking this list.
    """

    def __init__(self, scenarios: Iterable['Age2ScenarioData']) -> None:
        self.included: list['Age2CivData'] = list(dict.fromkeys(
            scenario.civ for scenario in scenarios))

    def builds(self, building: 'Age2BuildingData') -> bool:
        """Whether anyone in this seed puts this building up. An empty seed answers False, which
        is why a campaign with no scenarios has to be refused before this is ever asked."""
        return any(civ.builds(building) for civ in self.included)

    def any_trains(self, unit: 'Age2UnitData') -> bool:
        return any(unit in CIV_TO_UNITS[civ] for civ in self.included)
