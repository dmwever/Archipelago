from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from ...locations.FillerLocations import Age2FillerLocationData, FillerKind
from ...locations.connections.ScenarioMilestones import capability

if TYPE_CHECKING:
    from ... import Age2World
    from ...Options import Age2Options
    from ...locations.Scenarios import Age2ScenarioData
    from .ScenarioPool import ScenarioPool


KIND_TO_FIELD: dict[FillerKind, str] = {
    FillerKind.EXPLORE: "explore",
    FillerKind.KILL_UNITS: "kill",
    FillerKind.RAZE_BUILDINGS: "raze",
    FillerKind.OWN_UNITS: "own",
    FillerKind.CONVERT_UNITS: "convert",
}


class FillerPool:

    def __init__(self, options: 'Age2Options', world: 'Age2World',
                 scenarios: 'ScenarioPool') -> None:
        self._minimum = options.minimum_filler_locations
        self._world = world
        self._scenarios = scenarios

    @property
    def minimum(self) -> int:
        return self._minimum.value

    def affords(self, filler: Age2FillerLocationData,
                scenario: 'Age2ScenarioData') -> bool:
        if filler.kind not in KIND_TO_FIELD:
            return False
        return getattr(capability(scenario), KIND_TO_FIELD[filler.kind]) >= filler.threshold

    def is_earnable(self, filler: Age2FillerLocationData) -> bool:
        return any(self.affords(filler, scenario)
                   for scenario in self._scenarios.included)

    @cached_property
    def earnable(self) -> list[Age2FillerLocationData]:
        return [filler for filler in Age2FillerLocationData if self.is_earnable(filler)]

    @cached_property
    def shuffled(self) -> list[Age2FillerLocationData]:
        earnable = self.earnable
        wanted = min(self.minimum, len(earnable))
        if wanted <= 0:
            return []
        chosen = self._world.random.sample(earnable, wanted)
        return [filler for filler in earnable if filler in set(chosen)]

    @property
    def locations(self) -> list[Age2FillerLocationData]:
        return self.shuffled

    def includes(self, filler: Age2FillerLocationData) -> bool:
        return filler in self.shuffled
