"""What a settled Need costs once some buildings are standing."""
from __future__ import annotations

from typing import Iterable

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from .Need import CLIMBED_AGES, AgeUpBuildings, Need


class Requirement:
    """What a settled Need costs once the buildings in `waived` are standing for free."""
    cost: dict[Resource, int]
    buildings: list[Age2BuildingData]
    ages: list[Age2AgeData]

    def __init__(self, need: Need, waived: frozenset[Age2BuildingData]) -> None:
        self._waived: frozenset[Age2BuildingData] = waived
        self._owned_buildings: set[Age2BuildingData] = set(need.entry_buildings)
        self._resource_costs: dict[Resource, int] = dict.fromkeys(SAMPLED_RESOURCES, 0)

        self._age_up_choices: dict[Age2AgeData, AgeUpBuildings] = {
            age_up.age: age_up for age_up in need.age_up_buildings}

        building_choices: list[tuple[Age2BuildingData, ...]] = sorted(
            need.building_choices, key=lambda choices: (len(choices), tuple(map(int, choices))))
        self.buildings = []
        self.ages = [age for age in CLIMBED_AGES
                     if need.starting_age < age <= need.needed_age]

        self._pay(need.own_cost().items())
        for building in need.entry_buildings:
            self._pay(building.cost.items())
        for choices in building_choices:
            if not any(self._has(choice) for choice in choices):
                self._charge(self._prerequisite_chain(choices[0]))
        if self.ages:
            self._charge(self._prerequisite_chain(Age2BuildingData.TOWN_CENTER))   # every age-up happens there
        for age in self.ages:
            self._pay(age.cost.items())
            self._charge(self._needed_age_up_buildings(age))
        for building in self.buildings:
            self._pay(building.cost.items())
        self.cost = {resource: amount for resource, amount in self._resource_costs.items()
                     if amount > 0}

    def _has(self, building: Age2BuildingData) -> bool:
        """Owned already, or standing."""
        return building in self._owned_buildings or building in self._waived

    def _pay(self, price: Iterable[tuple[Resource, int]]) -> None:
        for resource, amount in price:
            self._resource_costs[resource] += amount

    def _prerequisite_chain(self, building: Age2BuildingData | None) -> list[Age2BuildingData]:
        """The building and its prerequisites, up to the first one already owned or standing."""
        chain: list[Age2BuildingData] = []
        while building is not None and not self._has(building) and building not in chain:
            chain.append(building)
            building = BUILDING_PREREQUISITE.get(building)
        return chain

    def _charge(self, buildings: Iterable[Age2BuildingData]) -> None:
        """Charge what is not owned yet, and own all of it from here on."""
        self.buildings.extend(building for building in buildings
                              if building not in self._owned_buildings)
        self._owned_buildings.update(buildings)

    def _needed_age_up_buildings(self, age: Age2AgeData) -> list[Age2BuildingData]:
        age_up = self._age_up_choices[age]
        if age_up.single_building is not None and self._has(age_up.single_building):
            return []
        already_held = [choice for choice in age_up.choices if self._has(choice)]
        if len(already_held) >= 2:
            return []
        missing = [choice for choice in age_up.choices
                   if not self._has(choice)][:2 - len(already_held)]
        if len(already_held) + len(missing) < 2:
            if age_up.single_building is None:
                return []
            return self._prerequisite_chain(age_up.single_building)
        bought: list[Age2BuildingData] = []
        for option in missing:
            bought += [building for building in self._prerequisite_chain(option) if building not in bought]
        return bought
