"""What one location makes a scenario pay for, before the scenario's waivers."""
from __future__ import annotations

import dataclasses
from typing import Callable, Iterable, NamedTuple

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData

CLIMBED_AGES = [Age2AgeData.FEUDAL, Age2AgeData.CASTLE, Age2AgeData.IMPERIAL]

class AgeUpBuildings(NamedTuple):
    """What leaves the age before this one: two of the choices, or the single building that
    counts for both. A tuple, as a Need keeps it and hashes."""
    age: Age2AgeData
    choices: tuple[Age2BuildingData, ...]
    single_building: Age2BuildingData | None

type Cost = tuple[tuple[Resource, int], ...]
"""A price as (resource, amount) pairs: a tuple, so whatever keeps it can hash."""

def as_cost(amounts: dict[Resource, int]) -> Cost:
    """A price as sorted (resource, amount) pairs, nothing at zero: the same whichever order the
    amounts came in."""
    return tuple(
        sorted(
            ((resource, amount) for resource, amount in amounts.items() if amount > 0),
            key=lambda item: item[0].value,
        )
    )

class OwnPrice(NamedTuple):
    """What one thing costs for itself, charged once per identity: a tech, a unit line, the
    villager. A tuple, as a Need keeps it and hashes."""
    identity: object
    cost: Cost

@dataclasses.dataclass(frozen=True)
class Need:
    """What one location makes a scenario pay for. Adding two is a union, so whatever both need
    is charged once."""
    own_price: frozenset[OwnPrice] = frozenset()
    """Paid for itself, once per identity: a tech, a unit line, the villager."""
    entry_buildings: frozenset[Age2BuildingData] = frozenset()
    """Buildings that are themselves locations: always charged, never waived."""
    building_choices: frozenset[tuple[Age2BuildingData, ...]] = frozenset()
    """Buildings it needs, each as the options any one of which will do."""
    needed_age: Age2AgeData = Age2AgeData.DARK
    """The highest age it needs."""
    starting_age: Age2AgeData = Age2AgeData.DARK
    """The age the scenario pays its way up from; set by by_scenario."""
    age_up_buildings: tuple[AgeUpBuildings, ...] = ()
    """What leaves each age in this scenario; set by by_scenario."""

    def __add__(self, other: 'Need') -> 'Need':
        return Need(
            self.own_price | other.own_price,
            self.entry_buildings | other.entry_buildings,
            self.building_choices | other.building_choices,
            max(self.needed_age, other.needed_age),
        )

    @staticmethod
    def pay(identity: object, cost: dict[Resource, int]) -> 'Need':
        return Need(own_price=frozenset({OwnPrice(identity, as_cost(cost))}))

    @staticmethod
    def build(building: Age2BuildingData) -> 'Need':
        return Need(entry_buildings=frozenset({building}))

    @staticmethod
    def one_of(*options: Age2BuildingData) -> 'Need':
        return Need(building_choices=frozenset({options})) if options else Need()

    @staticmethod
    def reach(age: Age2AgeData) -> 'Need':
        return Need(needed_age=age)

    def by_scenario(
        self,
        start: Age2AgeData,
        age_up_buildings: tuple[AgeUpBuildings, ...],
        could_have: Callable[[Age2BuildingData], bool],
        choice_order: Callable[[Age2BuildingData], int],
    ) -> 'Need':

        def could_be_in_scenario(
            buildings: Iterable[Age2BuildingData],
        ) -> tuple[Age2BuildingData, ...]:
            """What the scenario could have of these, in the seed's order."""
            return tuple(sorted(filter(could_have, buildings), key=choice_order))

        possible_building_choices: set[tuple[Age2BuildingData, ...]] = set()
        for choices in self.building_choices:
            building_in_scenario = could_be_in_scenario(choices)
            if building_in_scenario:
                possible_building_choices.add(building_in_scenario)

        possible_age_up_buildings: list[AgeUpBuildings] = []
        for age_up_building in age_up_buildings:
            single_building = age_up_building.single_building
            if single_building is not None and not could_have(single_building):
                single_building = None
            possible_age_up_buildings.append(
                AgeUpBuildings(
                    age_up_building.age,
                    could_be_in_scenario(age_up_building.choices),
                    single_building,
                )
            )

        # Frozen and tupled again: a Need is kept in resolved rules, which hash.
        return dataclasses.replace(
            self,
            building_choices=frozenset(possible_building_choices),
            needed_age=max(start, self.needed_age),
            starting_age=start,
            age_up_buildings=tuple(possible_age_up_buildings),
        )

    def own_cost(self) -> dict[Resource, int]:
        cost: dict[Resource, int] = {}
        for price in self.own_price:
            for resource, amount in price.cost:
                cost[resource] = cost.get(resource, 0) + amount
        return cost
