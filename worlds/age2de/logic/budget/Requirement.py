"""What a settled Need costs: the cheapest way to cover it once some buildings are standing."""
from __future__ import annotations

import dataclasses
import itertools
from typing import Iterable

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from .Need import CLIMBED_AGES, Need


@dataclasses.dataclass(frozen=True)
class Requirement:
    cost: dict[Resource, int]
    buildings: list[Age2BuildingData]
    ages: list[Age2AgeData]


def required(need: Need, waived: frozenset[Age2BuildingData]) -> Requirement:
    cost: dict[Resource, int] = dict.fromkeys(SAMPLED_RESOURCES, 0)
    have: set[Age2BuildingData] = set(need.entry_buildings)
    charged: list[Age2BuildingData] = []
    groups: list[tuple[Age2BuildingData, ...]] = sorted(
        need.groups, key=lambda group: (len(group), tuple(map(int, group))))
    ages: list[Age2AgeData] = [age for age in CLIMBED_AGES if need.start < age <= need.top]
    climbs: dict[Age2AgeData, tuple[tuple[Age2BuildingData, ...], Age2BuildingData | None]] = {
        age: (options, alone) for age, options, alone in need.climbs}

    def pay(price: Iterable[tuple[Resource, int]]) -> None:
        for resource, amount in price:
            cost[resource] += amount

    def chain(building: Age2BuildingData | None) -> list[Age2BuildingData]:
        """The building and its prerequisites, up to the first one already paid or standing."""
        out: list[Age2BuildingData] = []
        while building is not None and building not in waived | have and building not in out:
            out.append(building)
            building = BUILDING_PREREQUISITE.get(building)
        return out

    def take(buildings: Iterable[Age2BuildingData]) -> None:
        charged.extend(building for building in buildings if building not in have)
        have.update(buildings)

    def worth(buildings: Iterable[Age2BuildingData]) -> int:
        return sum(sum(building.cost.values()) for building in buildings)

    def cheapest_climb(age: Age2AgeData) -> list[Age2BuildingData] | None:
        """The cheapest two buildings that leave the age before this one, or the one that
        counts for both, with what they stand on; None if the scenario can have none."""
        options, alone = climbs[age]
        candidates: list[tuple[int, list[int], list[Age2BuildingData]]] = []
        for first, second in itertools.combinations(options, 2):
            both = chain(first)
            both += [building for building in chain(second) if building not in both]
            candidates.append((worth(both), [int(first), int(second)], both))
        if alone is not None:
            candidates.append((worth(chain(alone)), [int(alone)], chain(alone)))
        if not candidates:
            return None
        return min(candidates, key=lambda candidate: candidate[:2])[2]

    pay(need.own_cost().items())
    for building in need.entry_buildings:
        pay(building.cost.items())
    for options in groups:
        take(chain(min(options, key=lambda option: (worth(chain(option)), int(option)))))
    if ages:
        take(chain(Age2BuildingData.TOWN_CENTER))   # every age is researched at a Town Center
    for age in ages:
        pay(age.cost.items())
        climb = cheapest_climb(age)
        if climb is not None:
            take(climb)
    for building in charged:
        pay(building.cost.items())
    return Requirement({resource: amount for resource, amount in cost.items() if amount > 0},
                       charged, ages)
