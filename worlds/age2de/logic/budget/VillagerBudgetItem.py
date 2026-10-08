"""The one villager entry, whichever villager location."""
from __future__ import annotations

import functools

from ...items.Items import Age2ItemData
from .Need import Need
from .UnitBudgetItem import UnitBudgetItem


class VillagerBudgetItem(UnitBudgetItem):
    """Male, female and every profession are the same unit: one villager, priced at the food that
    staffs a base rather than the unit's own cost. Nothing upgrades it."""

    children = ()

    @functools.cached_property
    def node(self) -> Need:
        villager, food = self.location, Age2ItemData.STARTING_VILLAGER_FOOD.type
        return (Need.pay("villager", {food.type: food.amount}) + Need.reach(villager.age)
                + Need.one_of(tuple(villager.buildings)))
