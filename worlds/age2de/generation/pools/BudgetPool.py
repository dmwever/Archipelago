from __future__ import annotations

import enum
from random import Random
from typing import TYPE_CHECKING

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Techs import Age2TechData
from ...locations.UnitLocations import VILLAGER_LINES
from ...locations.Units import Age2UnitData
from ...locations.connections import ScenarioResources

if TYPE_CHECKING:
    from ...locations.Scenarios import Age2ScenarioData
    from ..Age2Pool import Age2Pool


class Age2BaseData(enum.IntEnum):
    """Not a location: the base a scenario works from, given a key so the budget can charge for it
    like one. Its value is outside every location id band."""
    BASE = 1

    @property
    def location_name(self) -> str:
        return "Base"

    @property
    def age(self) -> Age2AgeData:
        return Age2AgeData.DARK


BASE = Age2BaseData.BASE

PricedLocation = Age2AgeData | Age2BuildingData | Age2TechData | Age2UnitData | Age2BaseData
"""A location the budget can price, or the base. Location ids are unique across the game, so one is its own
key whatever its type."""

VILLAGER = Age2UnitData.VILLAGER_MALE
"""The one villager entry. Villagers are never drawn as units, so this only ever means 'a
villager', whichever villager location."""

SAMPLED_RESOURCES: tuple[Resource, ...] = (Resource.FOOD, Resource.WOOD, Resource.GOLD, Resource.STONE)

TECHS_PER_RESOURCE = 3
UNITS_PER_RESOURCE = 3
BUILDINGS_DRAWN = 4
CHEAP_BUILDING_COST_LIMIT = 100

SOURCE_ALLOWANCE = 250
"""What one early gathering source is worth to a scenario's budget."""
RELIC_ALLOWANCE = 50
"""What each relic a scenario can collect is worth, in gold."""


def is_cheap_building(building: Age2BuildingData) -> bool:
    return (building.age == Age2AgeData.DARK
            and sum(building.cost.values()) <= CHEAP_BUILDING_COST_LIMIT)


class BudgetPool:
    def __init__(self, pool: 'Age2Pool', random: Random) -> None:
        rng = Random(random.getrandbits(64))
        self.techs: frozenset[Age2TechData] = self._per_resource(
            rng, sorted(pool.techs.shuffled, key=int), TECHS_PER_RESOURCE)
        
        self.units: frozenset[Age2UnitData] = self._per_resource(
            rng, self._unit_candidates(pool), UNITS_PER_RESOURCE)

        # Always in whenever Shuffle Villager made villager locations.
        self.villager: bool = bool(pool.units.villager_locations)

        buildings = sorted(pool.buildings.locations, key=int)
        drawn = rng.sample(buildings, min(BUILDINGS_DRAWN, len(buildings)))

        # add cheap buildings too
        self.buildings: frozenset[Age2BuildingData] = frozenset(
            drawn + [building for building in buildings if is_cheap_building(building) and building not in drawn])
        
        self.ages: frozenset[Age2AgeData] = frozenset(pool.ages.locations)

        self.entries: frozenset[PricedLocation] = (
            self.ages | self.buildings | self.techs | self.units
            | (frozenset({VILLAGER}) if self.villager else frozenset()))

        ordered = sorted(self.entries, key=int)
        self.rank: dict['Age2ScenarioData', dict[PricedLocation, int]] = {
            scenario: {location: position
                       for position, location in enumerate(rng.sample(ordered, len(ordered)))}
            for scenario in sorted(pool.scenarios.included, key=lambda scenario: scenario.id)}

    @staticmethod
    def relic_allowance(scenario: 'Age2ScenarioData') -> int:
        return RELIC_ALLOWANCE * ScenarioResources.total(scenario).relic_count

    @staticmethod
    def _unit_candidates(pool: 'Age2Pool') -> list[Age2UnitData]:
        """Units a scenario could train and has to pay for, to draw from. The villager is not drawn:
        it is its own entry."""
        return [unit for unit in sorted(pool.units.units, key=int)
                if pool.units.is_trainable_unit(unit) and unit.buildings
                and unit.line not in VILLAGER_LINES
                and any(amount > 0 for amount in unit.cost.values())]

    @staticmethod
    def _per_resource(rng: Random, candidates: list, per_resource: int) -> frozenset:
        """Draw per_resource for each resource in turn from what costs it, never twice."""
        chosen: list = []
        for resource in SAMPLED_RESOURCES:
            costing = [candidate for candidate in candidates
                       if candidate.cost.get(resource, 0) > 0 and candidate not in chosen]
            chosen += rng.sample(costing, min(per_resource, len(costing)))
        return frozenset(chosen)
