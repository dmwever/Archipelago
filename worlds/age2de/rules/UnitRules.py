from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Rule, True_

from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.Units import Age2UnitData

if TYPE_CHECKING:
    from .Rules import Rules
    from .ScenarioRules import ScenarioRules


class UnitRules:
    def __init__(self, rules: 'Rules'):
        self.rules = rules
        self.world = rules.world
        self.logic = rules.logic

    def scenario_logic(self, scenario) -> 'ScenarioRules':
        for scenario_rules in self.rules.scenario_rules:
            if scenario_rules.scenario is scenario:
                return scenario_rules.scenario_logic
        raise KeyError(f"{scenario.scenario_name} has no rules in this playthrough")

    def trigger_rule(self, scenario, target) -> Rule:
        logic = self.scenario_logic(scenario)
        if isinstance(target, (Age2HeroData, Age2EscortUnitData)):
            # No line to gather tiers from - the grant is the thing itself.
            return logic.obtains_unit(target)
        rule: Rule | None = None
        for grant in scenario.trigger_units:
            if not isinstance(grant, Age2UnitData) or grant.line is not target:
                continue
            obtained = logic.obtains_unit(grant)
            rule = obtained if rule is None else rule | obtained
        return rule if rule is not None else False_()

    def set_rules(self):
        for name, kind, source, target in self.world.unit_doors:
            door = self.world.get_entrance(name)
            if kind == "train":
                self.world.set_rule(door, self.logic.can_build_building(source))
            elif kind == "startup":
                self.world.set_rule(door, True_())
            elif kind == "trigger":
                self.world.set_rule(door, self.trigger_rule(source, target))
            else:
                # Conversion is a placeholder. The entrances exist so the seam sits where it
                # belongs; they open when Monk logic and per-scenario enemy rosters are real.
                self.world.set_rule(door, False_())
