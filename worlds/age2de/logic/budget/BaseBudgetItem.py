"""A base to work from."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rule_builder.rules import Rule

from ...locations.Buildings import Age2BuildingData
from .BudgetItem import Age2BaseData, BudgetItem
from .Need import Need
from .VillagerBudgetItem import villager_food

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


class BaseBudgetItem(BudgetItem):
    """Villagers fed, a Town Center and, where the civilisation builds them, a House. A Town Center
    or House standing is let off like any building; the food never is, since a base with nobody in
    front of it is none. The food is the villager entry's, so the two are charged once."""

    rank = 0
    first_in_age = True
    location: Age2BaseData

    def structural(self, scenario: ScenarioLogic) -> Rule:
        return scenario.can_have_base()

    @functools.cached_property
    def node(self) -> Need:
        # A civilisation without Houses cannot have one, so the scenario's trim drops that group.
        return (villager_food() + Need.one_of(Age2BuildingData.TOWN_CENTER)
                + Need.one_of(Age2BuildingData.HOUSE))
