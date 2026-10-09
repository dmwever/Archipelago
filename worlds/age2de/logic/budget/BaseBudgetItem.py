"""A base to work from."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rule_builder.rules import Rule

from ...locations.Buildings import Age2BuildingData
from .BudgetItem import Age2BaseData, BudgetItem
from .Need import Need
from .VillagerBudgetItem import VillagerBudgetItem

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

class BaseBudgetItem(BudgetItem):
    rank = 0
    first_in_age = True
    location: Age2BaseData

    def scenario_rule(self, scenario: ScenarioLogic) -> Rule:
        return scenario.can_have_base()

    @functools.cached_property
    def node(self) -> Need:
        # A civilisation without Houses cannot have one, so the scenario's trim drops that group.
        return (
            VillagerBudgetItem.villager_food()
            + Need.one_of(Age2BuildingData.TOWN_CENTER)
            + Need.one_of(Age2BuildingData.HOUSE)
        )
