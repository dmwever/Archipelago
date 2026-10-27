from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Or, Rule, True_

from ...locations.Techs import Age2TechData
from ..custom_logic.ScenarioQuestions import ScenarioCanResearch

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


class ScenarioTechLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world

    def can_research(self, tech: Age2TechData) -> Rule:
        return (self.scenario.obtains_tech(tech)
                | (self.can_research_structurally(tech) & self.can_pay_for(tech)))

    def can_pay_for(self, tech: Age2TechData) -> Rule:
        rule = self.scenario.economy.can_pay(tech.cost) & self.scenario.ages.can_advance(tech.age)
        if tech.buildings:
            rule = rule & Or(*[self.scenario.has_building(building)
                               for building in tech.buildings])
        return rule

    def can_research_structurally(self, tech: Age2TechData) -> Rule:
        """Everything researching it asks for except paying for it."""
        if not self.scenario.civilization.researches(tech):
            return False_()
        if tech in self.scenario.scenario.excluded_techs:
            return False_()   # the scenario forbids it
        return ScenarioCanResearch(scenario=self.scenario.scenario, tech=tech)

    def researched_at_start(self, tech: Age2TechData) -> bool:
        """The scenario researched it for itself: it belongs below the age the scenario opens in,
        and it is not withheld."""
        return (tech.age < self.scenario.scenario.vanilla_age
                and not self.world.pool.techs.locked_at_start(tech))

    def has_researched(self, tech: Age2TechData) -> Rule:
        return self._has_researched(tech, paid=True)

    def has_researched_structurally(self, tech: Age2TechData) -> Rule:
        return self._has_researched(tech, paid=False)

    def _has_researched(self, tech: Age2TechData, paid: bool) -> Rule:
        if not self.scenario.civilization.researches(tech):
            return False_()
        if tech in self.scenario.scenario.excluded_techs:
            return False_()   # the scenario forbids it
        if self.researched_at_start(tech):
            return True_()
        rule = (self.can_research(tech) if paid
                else self.scenario.obtains_tech(tech) | self.can_research_structurally(tech))
        if self.world.pool.techs.includes(tech):
            rule = rule & Has(tech.item.item_name)
        return rule

    def has_tech(self, tech: Age2TechData) -> Rule:
        return self.available(tech, self.scenario.ages.has_reached(tech.age))

    def available(self, tech: Age2TechData, age: Rule) -> Rule:
        if not self.scenario.civilization.researches(tech):
            return False_()   # not this civilisation's to research
        if tech in self.scenario.scenario.excluded_techs:
            return False_()   # the scenario forbids it
        rule = age
        if tech.buildings:
            rule = rule & Or(*[self.scenario.has_building_structurally(building)
                               for building in tech.buildings])
        return rule
