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

if TYPE_CHECKING:
    from ...locations.Scenarios import Age2ScenarioData
    from ..Age2Pool import Age2Pool


class BudgetKind(enum.IntEnum):
    AGE = 0
    BUILDING = 1
    TECH = 2
    UNIT = 3
    VILLAGER = 4


VILLAGER = Age2UnitData.VILLAGER_MALE

BudgetLocation = Age2AgeData | Age2BuildingData | Age2TechData | Age2UnitData
BudgetEntry = tuple[BudgetKind, BudgetLocation]

SAMPLED_RESOURCES: tuple[Resource, ...] = (Resource.FOOD, Resource.WOOD, Resource.GOLD, Resource.STONE)

TECHS_PER_RESOURCE = 3
UNITS_PER_RESOURCE = 3
BUILDINGS_DRAWN = 4
CHEAP_BUILDING_COST_LIMIT = 100


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

        self.entries: frozenset[BudgetEntry] = frozenset(
            [(BudgetKind.AGE, age) for age in self.ages]
            + [(BudgetKind.BUILDING, building) for building in self.buildings]
            + [(BudgetKind.TECH, tech) for tech in self.techs]
            + [(BudgetKind.UNIT, unit) for unit in self.units]
            + ([(BudgetKind.VILLAGER, VILLAGER)] if self.villager else []))

        ordered = sorted(self.entries, key=lambda entry: (entry[0], int(entry[1])))
        self.rank: dict['Age2ScenarioData', dict[BudgetEntry, int]] = {
            scenario: {entry: position
                       for position, entry in enumerate(rng.sample(ordered, len(ordered)))}
            for scenario in sorted(pool.scenarios.included, key=lambda scenario: scenario.id)}

    def includes(self, kind: BudgetKind, location: BudgetLocation) -> bool:
        return (kind, location) in self.entries

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
