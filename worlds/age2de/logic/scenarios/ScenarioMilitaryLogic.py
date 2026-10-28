from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Or, Rule

from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData
from ...locations.connections.UnitRoles import ROLE_TO_LINES, UnitRole

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


def _past_dark(age: Age2AgeData | None) -> str:
    """" in the Castle Age" - nothing for the Dark Age, which any tier will do for."""
    if age is None or age is Age2AgeData.DARK:
        return ""
    return f" in the {age.location_name.removeprefix('Reach ')}"


class ScenarioMilitaryLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world

    def has_military(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.scenario.named(f"has a military{_past_dark(age)}",
                                   self.can_field_role(UnitRole.military, age))

    def has_siege(self) -> Rule:
        return self.scenario.named("has siege", self.can_field_role(UnitRole.siege))

    def has_long_range_siege(self) -> Rule:
        return self.scenario.named("has long-range siege", self.can_field_role(UnitRole.long_range_siege))

    def has_navy(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.scenario.named(f"has a navy{_past_dark(age)}",
                                   self.can_field_role(UnitRole.navy, age) & self.scenario.has_water_access())

    def can_guard_boats(self) -> Rule:
        force = self._can_field_some(UnitRole.navy)
        if isinstance(force, False_):
            return force
        return self.scenario.named("can protect its boats",
                                   force & self.scenario.has_water_access())

    def can_hold_open_ground(self) -> Rule:
        force = self._can_field_some(UnitRole.military)
        if isinstance(force, False_):
            return force
        return self.scenario.named("can hold open ground with an army", force)

    def _can_field_some(self, role: str) -> Rule:
        rules = []
        for line in ROLE_TO_LINES[role]:
            rule = self.scenario.units.can_field_structurally(line)
            if isinstance(rule, False_):
                continue
            first_tier = self.scenario.units.starting_unit(line)[0]
            wage = self.scenario.units.resources_to_train(line)
            rules.append(
                rule
                & self.scenario.economy.can_pay_some(wage)
                & self.scenario.ages.can_advance_in_economy(first_tier.age)
                & self.scenario.units.can_pay_some_for_training_building(first_tier)
            )
        if not rules:
            return False_()
        return Or(*rules)

    def has_naval_bombardment(self) -> Rule:
        return self.scenario.named("has naval bombardment",
                                   self.can_field_role(UnitRole.naval_bombardment) & self.scenario.has_water_access())

    def counters(self, target: Age2UnitLineData, age: Age2AgeData) -> Rule:
        age_name = age.location_name.removeprefix("Reach ")
        return self.scenario.named(f"counters the {target.line_name} in the {age_name}",
                                   self.scenario.units.can_counter(target, age))

    def counters_building(self) -> Rule:
        return self.scenario.named("counters buildings", self.can_field_role(UnitRole.building_counter))

    def can_field_role(self, role: str, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        rules = [self.scenario.units.can_field(line, age)
                 for line in ROLE_TO_LINES[role]]
        return Or(*[rule for rule in rules if not isinstance(rule, False_)])
