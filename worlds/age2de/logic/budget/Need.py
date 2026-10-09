"""What one location makes a scenario pay for, before the scenario's waivers."""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Iterable

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData

if TYPE_CHECKING:
    from ..custom_logic.AgeUpRequirement import AgeUpRequirement
    from ..scenarios.ScenarioPriceLogic import ScenarioPriceLogic

CLIMBED_AGES = [Age2AgeData.FEUDAL, Age2AgeData.CASTLE, Age2AgeData.IMPERIAL]

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

@dataclasses.dataclass(frozen=True)
class OwnPrice:
    """What one thing costs for itself, charged once per identity: a tech, a unit line, the
    villager. Compared by value, not identity: the villager entry and the base each build their
    own, and a Need's union has to see them as one to charge the food once."""
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
    age_up_requirements: tuple[AgeUpRequirement, ...] = ()
    """What leaves each age in this scenario, narrowed to what could stand; set by
    by_scenario."""

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

    def by_scenario(self, price_logic: ScenarioPriceLogic) -> 'Need':
        def could_be_in_scenario(
            buildings: Iterable[Age2BuildingData],
        ) -> tuple[Age2BuildingData, ...]:
            
            available_buildings = filter(price_logic.could_have, buildings)
            return tuple(sorted(available_buildings, key=price_logic.choice_order))

        possible_building_choices: set[tuple[Age2BuildingData, ...]] = set()
        for choices in self.building_choices:
            building_in_scenario = could_be_in_scenario(choices)
            if building_in_scenario:
                possible_building_choices.add(building_in_scenario)

        # Frozen and tupled again: a Need is kept in resolved rules, which hash.
        return dataclasses.replace(
            self,
            building_choices=frozenset(possible_building_choices),
            needed_age=max(price_logic.start_age, self.needed_age),
            starting_age=price_logic.start_age,
            age_up_requirements=price_logic.age_up_requirements,
        )

    def own_cost(self) -> dict[Resource, int]:
        cost: dict[Resource, int] = {}
        for price in self.own_price:
            for resource, amount in price.cost:
                cost[resource] = cost.get(resource, 0) + amount
        return cost
