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
    buildings: tuple[Age2BuildingData, ...]
    ages: tuple[Age2AgeData, ...]


def required(need: Need, waived: frozenset[Age2BuildingData]) -> Requirement:
    """What a settled Need costs once the buildings in `waived` are standing for free."""
    cost = dict.fromkeys(SAMPLED_RESOURCES, 0)
    for resource, amount in tuple(need.own_cost().items()) + tuple(
            item for building in need.entry_buildings for item in building.cost.items()):
        cost[resource] += amount
    have, charged = set(need.entry_buildings), []

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

    for options in sorted(need.groups, key=lambda group: (len(group), tuple(map(int, group)))):
        take(chain(min(options, key=lambda option: (worth(chain(option)), int(option)))))
    ages = tuple(age for age in CLIMBED_AGES if need.start < age <= need.top)
    if ages:
        take(chain(Age2BuildingData.TOWN_CENTER))   # every age is researched at a Town Center
    climbs = {age: (options, alone) for age, options, alone in need.climbs}
    for age in ages:
        for resource, amount in age.cost.items():
            cost[resource] += amount
        options, alone = climbs[age]
        candidates = []
        for first, second in itertools.combinations(options, 2):
            both = chain(first)
            both += [building for building in chain(second) if building not in both]
            candidates.append((worth(both), (int(first), int(second)), both))
        if alone is not None:
            candidates.append((worth(chain(alone)), (int(alone),), chain(alone)))
        if candidates:
            take(min(candidates, key=lambda candidate: candidate[:2])[2])
    for resource, amount in (item for building in charged for item in building.cost.items()):
        cost[resource] += amount
    return Requirement({resource: amount for resource, amount in cost.items() if amount > 0},
                       tuple(charged), ages)
