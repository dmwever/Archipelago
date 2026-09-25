from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Or, Rule, True_

from ...Options import LockTechs
from ...locations.Techs import Age2TechData
from ...locations.connections.CivilizationTechs import CIV_TO_TECHS

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


class ScenarioTechLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world

    def can_research(self, tech: Age2TechData) -> Rule:
        if self.world.tech_pool.locked_at_start(tech):
            return self.available(tech, self.scenario.can_play_age(tech.age))
        return self.available(tech, self.scenario.can_reach_age(tech.age))

    def has_tech(self, tech: Age2TechData) -> Rule:
        return self.available(tech, self.scenario.can_play_age(tech.age))

    def available(self, tech: Age2TechData, age: Rule) -> Rule:
        if tech not in CIV_TO_TECHS[self.scenario.scenario.civ]:
            return False_()   # not this civilisation's to research
        rule = self.has_tech_items(tech)
        if tech.buildings:
            rule = rule & Or(*[self.scenario.buildings.can_build_building(building)
                               for building in tech.buildings])
        return rule & age

    def has_tech_items(self, tech: Age2TechData) -> Rule:
        if self.world.options.lock_techs == LockTechs.option_effects:
            return True_()
        rule: Rule = Has(tech.item.item_name)
        prerequisite = tech.prerequisite
        if prerequisite is not None and self.world.tech_pool.includes(prerequisite):
            rule = rule & self.has_tech(prerequisite)
        return rule
