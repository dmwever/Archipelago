from __future__ import annotations

from functools import cached_property
from math import ceil
from typing import TYPE_CHECKING

from BaseClasses import ItemClassification

from ...items.Items import Age2ItemData
from ...locations.FillerLocations import Age2FillerLocationData, FillerKind
from ...locations.connections.ScenarioMilestones import capability

if TYPE_CHECKING:
    from ... import Age2World
    from ...Options import Age2Options
    from ...locations.Scenarios import Age2ScenarioData
    from .CampaignPool import CampaignPool
    from .ScenarioPool import ScenarioPool


KIND_TO_FIELD: dict[FillerKind, str] = {
    FillerKind.EXPLORE: "explore",
    FillerKind.KILL_UNITS: "kill",
    FillerKind.RAZE_BUILDINGS: "raze",
    FillerKind.OWN_UNITS: "own",
    FillerKind.CONVERT_UNITS: "convert",
}

EARLY_FLOOR = 10

DENSITY_TARGET = 0.85

RESOURCE_SHARE = 0.5


class FillerPool:

    def __init__(self, options: 'Age2Options', world: 'Age2World',
                 scenarios: 'ScenarioPool', campaigns: 'CampaignPool') -> None:
        self._minimum = options.minimum_filler_locations
        self._world = world
        self._scenarios = scenarios
        self._campaigns = campaigns
        self._chosen: list[Age2FillerLocationData] | None = None

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
    def opening_scenarios(self) -> list['Age2ScenarioData']:
        return [self._scenarios.of(campaign)[0]
                for campaign in self._campaigns.starting
                if self._scenarios.of(campaign)]

    @cached_property
    def opening_locations(self) -> int:
        from ...locations import Locations
        total = 0
        for scenario in self.opening_scenarios:
            for location in Locations.REGION_TO_LOCATIONS.get(scenario.scenario_name, ()):
                if self._scenarios.includes_location(location):
                    total += 1
        return total

    @cached_property
    def earnable_at_once(self) -> list[Age2FillerLocationData]:
        return [filler for filler in self.earnable
                if any(self.affords(filler, scenario)
                       for scenario in self.opening_scenarios)]

    def progression_in(self, locations: int, unit_items: list[Age2ItemData]) -> int:
        plan = self._world.pool.item_plan(unit_items)
        structural = sum(1 for data in plan.pooled
                         if self._world.classification_for(data)
                         & ItemClassification.progression)
        budget = max(0, int((locations - len(plan.pooled)) * RESOURCE_SHARE))
        return structural + budget

    def needed_for_density(self, locations: int, progression: int) -> int:
        if locations <= 0 or progression <= 0:
            return 0
        if progression <= DENSITY_TARGET * locations:
            return 0
        return max(0, ceil(progression / DENSITY_TARGET) - locations)

    def early_shortfall(self) -> int:
        return max(0, EARLY_FLOOR - self.opening_locations)

    def choose(self, locations: int,
               unit_items: list[Age2ItemData]) -> list[Age2FillerLocationData]:
        picked: list[Age2FillerLocationData] = []
        picked += self._take(self.earnable_at_once, self.early_shortfall(), picked)

        wanted = self.needed_for_density(locations,
                                         self.progression_in(locations, unit_items))
        picked += self._take(self.earnable, wanted, picked)
        picked += self._take(self.earnable, self.minimum, picked)

        chosen = set(picked)
        self._chosen = [filler for filler in self.earnable if filler in chosen]
        return self._chosen

    def _take(self, source: list[Age2FillerLocationData], target: int,
              already: list[Age2FillerLocationData]) -> list[Age2FillerLocationData]:
        held = set(already)
        pool = [filler for filler in source if filler not in held]
        wanted = min(target - len(already), len(pool))
        if wanted <= 0:
            return []
        return self._world.random.sample(pool, wanted)

    @property
    def shuffled(self) -> list[Age2FillerLocationData]:
        return [] if self._chosen is None else self._chosen

    @property
    def locations(self) -> list[Age2FillerLocationData]:
        return self.shuffled

    def includes(self, filler: Age2FillerLocationData) -> bool:
        return filler in self.shuffled
