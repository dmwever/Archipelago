from __future__ import annotations

from typing import TYPE_CHECKING

from ...locations.Buildings import Age2BuildingData, BuildingOption

if TYPE_CHECKING:
    from ...Options import Age2Options
    from .CivilizationPool import CivilizationPool


class BuildingPool:
    def __init__(self, options: 'Age2Options', civs: 'CivilizationPool') -> None:
        self._shuffle_buildings = options.shuffle_buildings
        self._civs = civs

    @property
    def shuffled(self) -> list[Age2BuildingData]:
        return [building for building in Age2BuildingData if self._is_shuffled(building)]

    @property
    def locations(self) -> list[Age2BuildingData]:
        return self.shuffled

    def _is_shuffled(self, building: Age2BuildingData) -> bool:
        if not self._civs.builds(building):
            return False   # nobody in this seed puts it up
        if (BuildingOption.unique in building.building_options
                and BuildingOption.unique not in self._shuffle_buildings):
            return False   # uniques are out altogether, whatever their other category says
        return any(option in building.building_options for option in self._categories)

    @property
    def _categories(self) -> list[str]:
        return [option for option in self._shuffle_buildings if option != BuildingOption.unique]
