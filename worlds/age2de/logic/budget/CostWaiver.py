"""The switches that make a scenario's running totals cheaper while they hold."""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from rule_builder.rules import False_, Rule

from ...locations.Buildings import Age2BuildingData
from .BudgetItem import PricedLocation

if TYPE_CHECKING:
    from ... import Age2World
    from ..ScenarioLogic import ScenarioLogic

@dataclasses.dataclass(frozen=True, eq=False)
class CostWaiver:
    """One rule, and what holding it lets a running total off: the buildings it stands up, and the
    purchases it spares. Buildings and purchases under the same rule share one waiver, so one bit
    of a budget total's mask."""
    rule: Rule.Resolved
    buildings: list[Age2BuildingData]
    purchases: list[PricedLocation]

    @classmethod
    def for_scenario(cls, scenario: ScenarioLogic, world: Age2World) -> list[CostWaiver]:
        """Every waiver the scenario has: one per distinct rule among its standing buildings and
        the rules that spare its required purchases."""
        by_rule: dict[Rule.Resolved, CostWaiver] = {}

        def waiver(rule: Rule) -> CostWaiver:
            """The waiver for this rule, made the first time the rule comes up."""
            resolved = rule.resolve(world)
            if resolved not in by_rule:
                by_rule[resolved] = cls(resolved, [], [])
            return by_rule[resolved]

        for building, rule in scenario.budget.standing_buildings.items():
            waiver(rule).buildings.append(building)
        for location, rule in scenario.starting_state.required_purchases.items():
            if not isinstance(rule, False_):   # nothing spares it
                waiver(rule).purchases.append(location)
        return list(by_rule.values())
