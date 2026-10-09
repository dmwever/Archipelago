from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Rule, True_

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...generation.pools.AgePool import DARK_START, VANILLA_AGE_START
from ..custom_logic.ScenarioQuestions import ScenarioHasReached
from ..custom_logic.AgeUpRequirement import AgeUpRequirement

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


AGE_UP_BUILDINGS: dict[Age2AgeData, tuple[Age2BuildingData, ...]] = {
    Age2AgeData.FEUDAL: (
        Age2BuildingData.MILL,
        Age2BuildingData.LUMBER_CAMP,
        Age2BuildingData.MINING_CAMP,
        Age2BuildingData.DOCK,
        Age2BuildingData.BARRACKS,
    ),
    Age2AgeData.CASTLE: (
        Age2BuildingData.ARCHERY_RANGE,
        Age2BuildingData.STABLE,
        Age2BuildingData.MARKET,
        Age2BuildingData.BLACKSMITH,
    ),
    Age2AgeData.IMPERIAL: (
        Age2BuildingData.MONASTERY,
        Age2BuildingData.UNIVERSITY,
        Age2BuildingData.SIEGE_WORKSHOP,
    ),
}
"""Two of these, from the age before, have to be standing before you can climb into that age."""


class ScenarioAgeLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self._reach: dict[Age2AgeData, Rule] = {}
        self._climb: dict[Age2AgeData, Rule] = {}

    def can_reach(self, age: Age2AgeData) -> Rule:
        """Advance to it here - an event that actually happens, which a tech location cares about."""
        if age not in self._reach:
            self._reach[age] = self._can_reach(age)
        return self._reach[age]

    def climb(self, into: Age2AgeData) -> Rule:
        if into not in self._climb:
            self._climb[into] = self._climb_rule(into)
        return self._climb[into]

    def age_up_requirement(self, into_age: Age2AgeData) -> AgeUpRequirement:
        """What climbs into this age: two of the age before's buildings, or - into the Imperial
        Age - a Castle, which counts for both on its own."""
        single = Age2BuildingData.CASTLE if into_age is Age2AgeData.IMPERIAL else None
        return AgeUpRequirement.from_buildings(
            self.scenario.has_building,
            into_age,
            list(AGE_UP_BUILDINGS[into_age]),
            single,
        )

    def has_reached(self, age: Age2AgeData) -> Rule:
        return ScenarioHasReached(scenario=self.scenario.scenario, age=age)

    def start_past(self, age: Age2AgeData) -> Rule:
        if self.scenario.starting_state.fixed_force:
            return False_()
        if self.world.pool.ages.starts_in(self.scenario.scenario) > age:
            return True_() & VANILLA_AGE_START
        return False_()

    # -- what the scenario questions resolve to, and the memo behind can_reach -----------

    def can_research(self, age: Age2AgeData) -> Rule:
        state = self.scenario.starting_state
        if state.fixed_force or age > state.max_age:
            return False_()
        rule = self.climb(age)
        if age <= self.world.pool.ages.starts_in(self.scenario.scenario):
            return rule & DARK_START
        return rule

    def _can_reach(self, age: Age2AgeData) -> Rule:
        state = self.scenario.starting_state
        if state.fixed_force or age > state.max_age:
            return False_()
        override = state.age_playable.get(age)
        if override is not None:
            return override
        opens_at = self.world.pool.ages.starts_in(self.scenario.scenario)
        rule = self.climb(age)
        if age < opens_at:
            # Below the age it opens in, so it is only ever climbed when the start is pulled back.
            return rule & DARK_START
        if age == opens_at:
            # Standing in it already, unless the start is pulled back - and this is your "the two
            # buildings can be ignored if the age is started past".
            return rule | VANILLA_AGE_START
        return rule

    def _climb_rule(self, into: Age2AgeData) -> Rule:
        if into is Age2AgeData.DARK:
            return True_()   # nowhere to advance from
        return (self.logic.ages.has_age(into)
                & self.scenario.buildings.has_tc()
                & self.age_up_requirement(into))
