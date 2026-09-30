from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import TYPE_CHECKING

from ...items import Items
from ...items.Items import Age2ItemData, Resource
from ...Options import TRAP_DEFAULT_WEIGHT

if TYPE_CHECKING:
    from ... import Age2World
    from ...Options import Age2Options


LARGEST = {
    Resource.WOOD: Age2ItemData.STARTING_WOOD_LARGE,
    Resource.FOOD: Age2ItemData.STARTING_FOOD_LARGE,
    Resource.GOLD: Age2ItemData.STARTING_GOLD_LARGE,
    Resource.STONE: Age2ItemData.STARTING_STONE_LARGE,
}

TARGETS = {
    Resource.WOOD: 725,
    Resource.FOOD: 850,
    Resource.GOLD: 750,
    Resource.STONE: 400,
}


@dataclass
class ResourcePlan:
    items: list[Age2ItemData]
    traps: list[Age2ItemData]
    surplus: int

class ResourcePool:
    def __init__(self, options: 'Age2Options', world: 'Age2World') -> None:
        self._trap_difficulty = options.trap_difficulty
        self._trap_percentage = options.trap_percentage
        self._trap_distribution = options.trap_distribution
        self._world = world
        self.totals: dict[Resource, int] = {resource: 0 for resource in Resource}

    def plan(self, locations_to_fill: int) -> ResourcePlan:
        items, surplus = self.build(locations_to_fill)
        traps = self.roll_traps(surplus)
        if traps:
            items = items[:len(items) - len(traps)]
        self._tally(items)
        return ResourcePlan(items, traps, surplus)

    def build_items(self, locations_to_fill: int) -> list[Age2ItemData]:
        return self.build(locations_to_fill)[0]

    def build(self, locations_to_fill: int) -> tuple[list[Age2ItemData], int]:
        items: list[Age2ItemData] = []
        surplus = 0
        halved = False
        if locations_to_fill <= 0:
            return items, surplus

        amounts = dict(TARGETS)
        choices = Items.CATEGORY_TO_ITEMS[Items.StartingResources]

        while locations_to_fill > 0:
            worst_case = {resource: ceil(amounts[resource] / LARGEST[resource].type.amount)
                          for resource in amounts}
            worst_case_sum = sum(worst_case.values())

            if worst_case_sum > locations_to_fill:
                amounts = {resource: amount // 2 for resource, amount in amounts.items()}
                halved = True
                continue

            if worst_case_sum == locations_to_fill:
                for resource, needed in worst_case.items():
                    for _ in range(needed):
                        items.append(LARGEST[resource])
                        locations_to_fill -= 1
                return items, surplus

            if worst_case_sum == 0 and not halved:
                surplus += 1

            item_data = self._world.random.choice(choices)
            resource = item_data.type.type
            amounts[resource] = max(0, amounts[resource] - item_data.type.amount)
            items.append(item_data)
            locations_to_fill -= 1
        return items, surplus

    def roll_traps(self, surplus: int) -> list[Age2ItemData]:
        if surplus <= 0 or not self._trap_difficulty.include_traps():
            return []

        names: list[Age2ItemData] = []
        weights: list[int] = []
        for trap in Items.CATEGORY_TO_ITEMS[Items.Trap]:
            weight = (self._trap_distribution[trap.item_name]
                      if trap.item_name in self._trap_distribution else TRAP_DEFAULT_WEIGHT)
            if weight > 0:
                names.append(trap)
                weights.append(weight)
        if not names:
            return []

        count = int(surplus * self._trap_percentage.value / 100)
        if count <= 0:
            return []
        return self._world.random.choices(names, weights=weights, k=count)

    def _tally(self, items: list[Age2ItemData]) -> None:
        tallied = {resource: 0 for resource in Resource}
        precollected = [Items.NAME_TO_ITEM[item.name]
                        for item in self._world.multiworld.precollected_items[self._world.player]]
        pooled = items + Items.CATEGORY_TO_ITEMS[Items.TCResources]
        for item in pooled + precollected:
            payload = item.type
            if isinstance(payload, (Items.StartingResources, Items.TCResources)):
                tallied[payload.type] += payload.amount
        self.totals.clear()
        self.totals.update(tallied)
