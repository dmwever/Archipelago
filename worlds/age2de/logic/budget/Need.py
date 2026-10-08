"""What one location makes a scenario pay for, before the scenario's waivers."""
from __future__ import annotations

import dataclasses
from typing import Callable, Iterable

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData


CLIMBED_AGES = [Age2AgeData.FEUDAL, Age2AgeData.CASTLE, Age2AgeData.IMPERIAL]

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
    building_choices: frozenset[tuple[Age2BuildingData, ...]] = frozenset()
    """Buildings it needs, each as the options any one of which will do."""
    needed_age: Age2AgeData = Age2AgeData.DARK
    """The highest age it needs."""
    starting_age: Age2AgeData = Age2AgeData.DARK
    """The age the scenario pays its way up from; set by in_scenario."""
    age_up_buildings: tuple[Climb, ...] = ()
    """What leaves each age in this scenario; set by in_scenario."""

    def __add__(self, other: 'Need') -> 'Need':
        return Need(self.own | other.own, self.entry_buildings | other.entry_buildings,
                    self.building_choices | other.building_choices, max(self.needed_age, other.needed_age))

    @staticmethod
    def pay(identity: object, cost: dict[Resource, int]) -> 'Need':
        priced = tuple(sorted(((resource, amount) for resource, amount in cost.items() if amount > 0),
                              key=lambda item: item[0].value))
        return Need(own=frozenset({(identity, priced)}))

    @staticmethod
    def build(building: Age2BuildingData) -> 'Need':
        return Need(entry_buildings=frozenset({building}))

    @staticmethod
    def one_of(*options: Age2BuildingData) -> 'Need':
        return Need(building_choices=frozenset({options})) if options else Need()

    @staticmethod
    def reach(age: Age2AgeData) -> 'Need':
        return Need(needed_age=age)

    def in_scenario(self,
                    start: Age2AgeData,
                    age_up_buildings: tuple[Climb, ...],
                    could_have: Callable[[Age2BuildingData], bool],
                    choice_order: Callable[[Age2BuildingData], int]) -> 'Need':
        """Settled for one scenario: the age it starts in, what leaves each age there, and only
        the buildings it could ever have, each set of choices in the seed's order. A set of
        choices left empty is dropped; so is a single building the scenario can never have."""

        def settled(buildings: Iterable[Age2BuildingData]) -> tuple[Age2BuildingData, ...]:
            """What the scenario could have of these, in the seed's order."""
            return tuple(sorted(filter(could_have, buildings), key=choice_order))

        building_choices: set[tuple[Age2BuildingData, ...]] = set()
        for choices in self.building_choices:
            kept = settled(choices)
            if kept:
                building_choices.add(kept)

        settled_age_ups: list[Climb] = []
        for age, options, single_building in age_up_buildings:
            if single_building is not None and not could_have(single_building):
                single_building = None
            settled_age_ups.append((age, settled(options), single_building))

        # Frozen and tupled again: a Need is kept in resolved rules, which hash.
        return dataclasses.replace(self,
                                   building_choices=frozenset(building_choices),
                                   needed_age=max(start, self.needed_age),
                                   starting_age=start,
                                   age_up_buildings=tuple(settled_age_ups))

    def own_cost(self) -> dict[Resource, int]:
        cost: dict[Resource, int] = {}
        for _, priced in self.own:
            for resource, amount in priced:
                cost[resource] = cost.get(resource, 0) + amount
        return cost
