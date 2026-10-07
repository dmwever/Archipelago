from __future__ import annotations

from typing import TYPE_CHECKING

from ...locations.FillerLocations import Age2FillerLocationData

if TYPE_CHECKING:
    from ... import Age2World
    from ...Options import Age2Options


class FillerPool:
    def __init__(self, options: 'Age2Options', world: 'Age2World') -> None:
        self._minimum = options.minimum_filler_locations
        self._world = world

    @property
    def minimum(self) -> int:
        return self._minimum.value

    @property
    def shuffled(self) -> list[Age2FillerLocationData]:
        return []

    @property
    def locations(self) -> list[Age2FillerLocationData]:
        return self.shuffled

    def includes(self, filler: Age2FillerLocationData) -> bool:
        return filler in self.shuffled
