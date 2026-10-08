"""What one location makes a scenario pay for, before the scenario's waivers."""
from __future__ import annotations

import dataclasses
from typing import Callable

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData


CLIMBED_AGES = (Age2AgeData.FEUDAL, Age2AgeData.CASTLE, Age2AgeData.IMPERIAL)

Climb = tuple[Age2AgeData, tuple[Age2BuildingData, ...], Age2BuildingData | None]
"""Per age: the buildings two of which leave the age before it, and the one counting for both."""



@dataclasses.dataclass(frozen=True)
class Need:
    """What one location makes a scenario pay for. Adding two is a union, so whatever both need
    is charged once."""
    own: frozenset[tuple[object, tuple[tuple[Resource, int], ...]]] = frozenset()
    """Paid for itself, once per identity: a tech, a unit line, the villager."""
    entry_buildings: frozenset[Age2BuildingData] = frozenset()
    """Buildings that are themselves locations: always charged, never waived."""
    groups: frozenset[tuple[Age2BuildingData, ...]] = frozenset()
    """Buildings it needs, each as the options any one of which will do."""
    top: Age2AgeData = Age2AgeData.DARK
    """The highest age it needs."""
    start: Age2AgeData = Age2AgeData.DARK
    """The age the scenario pays its way up from; set by in_scenario."""
    climbs: tuple[Climb, ...] = ()
    """What leaves each age in this scenario; set by in_scenario."""

    def __add__(self, other: 'Need') -> 'Need':
        return Need(self.own | other.own, self.entry_buildings | other.entry_buildings,
                    self.groups | other.groups, max(self.top, other.top))

    @staticmethod
    def pay(identity: object, cost: dict[Resource, int]) -> 'Need':
        priced = tuple(sorted(((resource, amount) for resource, amount in cost.items() if amount > 0),
                              key=lambda item: item[0].value))
        return Need(own=frozenset({(identity, priced)}))

    @staticmethod
    def build(building: Age2BuildingData) -> 'Need':
        return Need(entry_buildings=frozenset({building}))

    @staticmethod
    def one_of(options: tuple[Age2BuildingData, ...]) -> 'Need':
        return Need(groups=frozenset({options})) if options else Need()

    @staticmethod
    def reach(age: Age2AgeData) -> 'Need':
        return Need(top=age)

    def in_scenario(self, start: Age2AgeData, climbs: tuple[Climb, ...],
                    could_have: Callable[[Age2BuildingData], bool]) -> 'Need':
        """Settled for one scenario: where it starts, how it climbs, and only the building
        options it could ever have."""
        groups = frozenset(kept for group in self.groups if (kept := tuple(filter(could_have, group))))
        climbs = tuple((age, tuple(filter(could_have, options)),
                        alone if alone is not None and could_have(alone) else None)
                       for age, options, alone in climbs)
        return dataclasses.replace(self, groups=groups, top=max(start, self.top), start=start,
                                   climbs=climbs)

    def own_cost(self) -> dict[Resource, int]:
        cost: dict[Resource, int] = {}
        for _, priced in self.own:
            for resource, amount in priced:
                cost[resource] = cost.get(resource, 0) + amount
        return cost
