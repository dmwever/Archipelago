"""An age location: reaching the age."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rule_builder.rules import Rule

from ...locations.Ages import Age2AgeData
from .BudgetItem import BudgetItem
from .Need import Need

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


class AgeBudgetItem(BudgetItem):
    """Its node is only the age itself: the age-ups, the Town Center and the climb buildings are
    worked out by the scenario's trim, from where the scenario starts."""

    rank = 0
    location: Age2AgeData

    @property
    def age(self) -> Age2AgeData:
        return self.location

    def structural(self, scenario: ScenarioLogic) -> Rule:
        return scenario.ages.can_research(self.location)

    @functools.cached_property
    def node(self) -> Need:
        return Need.reach(self.location)
