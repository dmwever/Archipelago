from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Or, Rule

from ...locations.Techs import Age2TechData

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


class ScenarioTechLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world

    def can_research(self, tech: Age2TechData) -> Rule:
        return self.can_research_structurally(tech) & self.scenario.economy.can_pay(tech.cost, tech)

    def can_research_structurally(self, tech: Age2TechData) -> Rule:
        """Everything researching it asks for except paying for it."""
        if self.world.pool.techs.locked_at_start(tech):
            age = self.scenario.ages.has_reached(tech.age)
        else:
            age = self.scenario.ages.can_reach(tech.age)
        return self.available(tech, age)

    def researched_at_start(self, tech: Age2TechData) -> bool:
        """The scenario researched it for itself: it belongs below the age the scenario opens in,
        and it is not withheld."""
        return (tech.age < self.scenario.scenario.vanilla_age
                and not self.world.pool.techs.locked_at_start(tech))

    def has_tech(self, tech: Age2TechData) -> Rule:
        return self.available(tech, self.scenario.ages.has_reached(tech.age))

    def available(self, tech: Age2TechData, age: Rule) -> Rule:
        if not self.scenario.civilization.researches(tech):
            return False_()   # not this civilisation's to research
        rule = age
        if tech.buildings:
            rule = rule & Or(*[self.scenario.has_building(building)
                               for building in tech.buildings])
        return rule
