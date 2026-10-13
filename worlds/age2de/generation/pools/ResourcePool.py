from __future__ import annotations

from collections import Counter
from math import ceil
from typing import TYPE_CHECKING

from ...items import Items
from ...items.Items import Age2ItemData, Resource

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
    Resource.WOOD: 725,   # 1000, less the Starting Town Center Wood every pool has
    Resource.FOOD: 850,
    Resource.GOLD: 750,
    Resource.STONE: 400,
}


MAX_ITEM_POOL_PERCENT = 0.5


class ResourcePool:
    def __init__(self, options: 'Age2Options', world: 'Age2World') -> None:
        self._world = world
        self.totals: dict[Resource, int] = {resource: 0 for resource in Resource}
        self.pile: Counter[Age2ItemData] = Counter()
        """Every item that adds to the starting pile, pooled or precollected, and how many."""

    def plan(self, locations_to_fill: int) -> list[Age2ItemData]:
        """The starting resources for this seed, out of at most its share of the open locations,
        tallied into totals."""
        items = self.build(int(locations_to_fill * MAX_ITEM_POOL_PERCENT))
        self._tally(items)
        return items

    def build(self, locations_to_fill: int) -> list[Age2ItemData]:
        """Random starting resources until every target is met, then stop: what is left of the
        locations is spare. A budget too small for the targets halves them and spends it all."""
        items: list[Age2ItemData] = []
        halved = False
        if locations_to_fill <= 0:
            return items

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
                return items

            if worst_case_sum == 0 and not halved:
                return items   # every target met

            item_data = self._world.random.choice(choices)
            resource = item_data.type.type
            amounts[resource] = max(0, amounts[resource] - item_data.type.amount)
            items.append(item_data)
            locations_to_fill -= 1
        return items

    def _tally(self, items: list[Age2ItemData]) -> None:
        tallied = {resource: 0 for resource in Resource}
        precollected = [Items.NAME_TO_ITEM[item.name]
                        for item in self._world.multiworld.precollected_items[self._world.player]]
        pooled = items + Items.CATEGORY_TO_ITEMS[Items.TCResources]
        self.pile.clear()
        for item in pooled + precollected:
            payload = item.type
            if isinstance(payload, (Items.StartingResources, Items.TCResources)):
                tallied[payload.type] += payload.amount
                self.pile[item] += 1
        self.totals.clear()
        self.totals.update(tallied)

    # -- the spoiler --------------------------------------------------------------------------

    def spoiler_lines(self) -> list[str]:
        """Every starting resource item the seed has, by resource, largest first after the town
        centre's own, with the running total each one brings the pile to."""
        def place(item: Age2ItemData) -> tuple[bool, int]:
            return not isinstance(item.type, Items.TCResources), -item.type.amount

        width = max((len(item.item_name) for item in self.pile), default=0)
        lines: list[str] = []
        for resource in (Resource.FOOD, Resource.WOOD, Resource.GOLD, Resource.STONE):
            held = sorted(
                (item for item in self.pile if item.type.type is resource),
                key=place,
            )
            if not held:
                continue
            lines.append(f"    {resource.name.title()}:")
            running = 0
            for item in held:
                count, each = self.pile[item], item.type.amount
                running += count * each
                lines.append(
                    f"        {item.item_name:<{width}}  {count:>2} x {each:>3} = {count * each:>4}"
                    f"   running {running:>5}"
                )
        return lines
