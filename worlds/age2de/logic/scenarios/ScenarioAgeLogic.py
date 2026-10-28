from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rule_builder.rules import And, False_, Has, Rule, True_

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...generation.pools.AgePool import DARK_START, VANILLA_AGE_START
from ..custom_logic.ScenarioQuestions import ScenarioCanAdvance, ScenarioHasReached
from ..custom_logic.AgeUpRequirement import AGE_UP_BUILDINGS, AgeUpRequirement

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


class ScenarioAgeLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self._reach: dict[Age2AgeData, Rule] = {}

    def can_reach(self, age: Age2AgeData) -> Rule:
        """Advance to it here and pay for it: what a victory or an army asks of an age."""
        label = f"can reach the {age.location_name.removeprefix('Reach ')}"
        if self.scenario.scenario.fixed_force or age > self.scenario.scenario.max_age:
            return self.scenario.named(label, False_())
        ages = self.world.pool.ages
        if age < ages.starts_in(self.scenario.scenario) and not ages.dark_start:
            return self.scenario.named(label, False_())
        return self.scenario.named(label, self.can_advance(age))

    def can_reach_structurally(self, age: Age2AgeData) -> Rule:
        """Advance to it here, less paying for it."""
        if age not in self._reach:
            self._reach[age] = self._can_reach_structurally(age)
        return self._reach[age]

    @functools.cached_property
    def start_age(self) -> Age2AgeData:
        """The age the scenario starts paying its advance from: the Dark Age when every scenario
        starts there."""
        ages = self.world.pool.ages
        return Age2AgeData.DARK if ages.dark_start else ages.starts_in(self.scenario.scenario)

    def can_advance_in_economy(self, age: Age2AgeData) -> Rule:
        if age <= self.start_age:
            return True_()
        economy = self.scenario.economy
        rule = (
            economy.can_pay_some([Resource.WOOD])
            & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
        )
        for advanced in Age2AgeData:
            if not self.start_age < advanced <= age:
                continue
            if advanced is Age2AgeData.FEUDAL:
                rule = rule & (economy.can_pay_some([Resource.FOOD]) | self.has_seed_item(advanced))
            elif advanced is Age2AgeData.CASTLE:
                rule = (
                    rule
                    & economy.has_ungated_easy_source(Resource.FOOD)
                    & economy.can_pay_some([Resource.GOLD])
                )
            else:
                costs = [
                    resource for resource, amount in advanced.cost.items()
                        if amount > 0
                ]
                price = And(*[economy.has_ungated_easy_source(resource) for resource in costs])
                rule = rule & economy.can_pay_some([Resource.STONE]) & price
        return rule

    def has_started_in(self, age: Age2AgeData) -> Rule:
        if self.scenario.scenario.fixed_force or age > self.start_age:
            return False_()
        return True_()

    def has_standing_or_seeded_age_up_buildings(self, age: Age2AgeData) -> Rule:
        return AgeUpRequirement.from_buildings(
            self.scenario.buildings.has_standing_or_seeded,
            age,
            list(AGE_UP_BUILDINGS[age]),
        )

    def has_seed_item(self, age: Age2AgeData) -> Rule:
        if age.seed_item not in self.world.pool.resources.seeds:
            return False_()
        return Has(age.seed_item.item_name)

    def can_advance(self, age: Age2AgeData) -> Rule:
        if self.scenario.scenario.fixed_force:
            return False_()
        if age <= self.start_age:
            return True_()
        return ScenarioCanAdvance(scenario=self.scenario.scenario, age=age)

    def has_reached(self, age: Age2AgeData) -> Rule:
        return ScenarioHasReached(scenario=self.scenario.scenario, age=age)

    def start_past(self, age: Age2AgeData) -> Rule:
        if self.scenario.scenario.fixed_force:
            return False_()
        if self.world.pool.ages.starts_in(self.scenario.scenario) > age:
            return True_() & VANILLA_AGE_START
        return False_()

    def can_research(self, age: Age2AgeData) -> Rule:
        if self.scenario.scenario.fixed_force or age > self.scenario.scenario.max_age:
            return False_()
        ages = self.world.pool.ages
        if age <= ages.starts_in(self.scenario.scenario) and not ages.dark_start:
            return False_()
        return self.can_advance(age)

    # -- what the scenario questions resolve to, and the memo behind can_reach_structurally

    def _can_reach_structurally(self, age: Age2AgeData) -> Rule:
        if self.scenario.scenario.fixed_force or age > self.scenario.scenario.max_age:
            return False_()
        opens_at = self.world.pool.ages.starts_in(self.scenario.scenario)
        advance = self._structural_advance_rule(age)
        if age < opens_at:
            # Below the age it opens in, so it is only advanced into when the start is pulled back.
            return advance & DARK_START
        if age == opens_at:
            # Standing in it already, unless the start is pulled back - and this is your "the two
            # buildings can be ignored if the age is started past".
            return advance | VANILLA_AGE_START
        return advance

    def _structural_advance_rule(self, age: Age2AgeData) -> Rule:
        if age is Age2AgeData.DARK:
            return True_()   # nowhere to advance from
        rule = (self.logic.ages.has_age(age)
                & self.scenario.has_building_structurally(Age2BuildingData.TOWN_CENTER)
                & self._age_up_requirement_structurally(age))
        before = Age2AgeData(age.value - 1)
        if before is not Age2AgeData.DARK:
            rule = rule & self.has_reached(before)
        return rule

    def _age_up_requirement_structurally(self, age: Age2AgeData) -> AgeUpRequirement:
        single = Age2BuildingData.CASTLE if age is Age2AgeData.IMPERIAL else None
        return AgeUpRequirement.from_buildings(
            self.scenario.has_building_structurally,
            age,
            list(AGE_UP_BUILDINGS[age]),
            single,
        )
