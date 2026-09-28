from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Or, Rule

from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData
from ...locations.connections.UnitRoles import ROLE_TO_LINES, UnitRole

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


class ScenarioMilitaryLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world

    def has_military(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.can_field_role(UnitRole.military, age)

    def has_siege(self) -> Rule:
        return self.can_field_role(UnitRole.siege)

    def has_long_range_siege(self) -> Rule:
        return self.can_field_role(UnitRole.long_range_siege)

    def has_navy(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.can_field_role(UnitRole.navy, age) & self.scenario.has_water_access()

    def has_naval_bombardment(self) -> Rule:
        return self.can_field_role(UnitRole.naval_bombardment) & self.scenario.has_water_access()

    def counters(self, target: Age2UnitLineData, age: Age2AgeData) -> Rule:
        return self.scenario.units.can_counter(target, age)

    def counters_building(self) -> Rule:
        return self.can_field_role(UnitRole.building_counter)

    def can_field_role(self, role: str, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        ways = [self.scenario.units.can_field(line, age)
                for line in ROLE_TO_LINES[role]]
        return Or(*[way for way in ways if not isinstance(way, False_)])
