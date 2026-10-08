"""A purchase one scenario requires of itself."""
from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Rule

from ...locations.Ages import Age2AgeData
from .BudgetItem import BudgetItem
from .Need import Need

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic
    from .TechBudgetItem import TechBudgetItem


class ScenarioBudgetItem(BudgetItem):
    """Something the scenario has to buy to be beaten, such as Joan 3's Transport Ship: priced
    exactly as the item it wraps, but always in that scenario's order, drawn or not, and first in
    its age so the rest of the order is paid for after it."""

    first_in_age = True

    def __init__(self, item: BudgetItem) -> None:
        super().__init__(item.location)
        self.item = item

    @property
    def rank(self) -> int:
        return self.item.rank

    @property
    def age(self) -> Age2AgeData:
        return self.item.age

    def scenario_rule(self, scenario: ScenarioLogic) -> Rule:
        return self.item.scenario_rule(scenario)

    @property
    def node(self) -> Need:
        return self.item.node

    @property
    def children(self) -> list[TechBudgetItem]:
        return self.item.children

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.item!r})"
