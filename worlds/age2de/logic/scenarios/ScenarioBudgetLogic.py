"""The terms one scenario sets on every price: where it starts, what climbs each age, and which
buildings it could ever have."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rule_builder.rules import False_, Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ..budget.Need import CLIMBED_AGES, Need
from ..custom_logic.AgeUpRequirement import AgeUpRequirement
from ..custom_logic.ScenarioQuestions import ScenarioCostWaived

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic
    from ..budget.BudgetItem import PricedLocation

class ScenarioBudgetLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self._could_have_building: dict[Age2BuildingData, bool] = {}

    @functools.cached_property
    def start_age(self) -> Age2AgeData:
        """The age the scenario pays its way up from: the Dark Age when every scenario starts
        there."""
        ages = self.world.pool.ages
        return Age2AgeData.DARK if ages.dark_start else ages.starts_in(self.scenario.scenario)

    @functools.cached_property
    def age_up_requirements(self) -> tuple[AgeUpRequirement, ...]:
        """What leaves each age, in climbing order, less the buildings that could never stand
        here."""
        return tuple(
            self.scenario.ages.age_up_requirement(age).narrowed_by_scenario(
                self.could_have,
                self.choice_order,
            )
                for age in CLIMBED_AGES
        )

    @functools.cached_property
    def standing_buildings(self) -> dict[Age2BuildingData, Rule]:
        """The buildings that might stand at the start, and the rule that has them standing. One
        standing counts whether or not the civilisation could build it."""
        standing = self.scenario.starting_state.starts_with_building
        return {
            building: standing[building] for building in Age2BuildingData
                if not isinstance(standing[building], False_)
        }

    @functools.cached_property
    def cost_waivers(self) -> list[ScenarioCostWaived.Resolved]:
        """Every waiver the scenario has: one per distinct rule among its standing buildings and
        the rules that spare its required purchases."""
        buildings: dict[Rule.Resolved, list[Age2BuildingData]] = {}
        purchases: dict[Rule.Resolved, list[PricedLocation]] = {}

        def group(rule: Rule) -> Rule.Resolved:
            """The rule, resolved, with a place for what it waives the first time it comes up."""
            resolved = rule.resolve(self.world)
            if resolved not in buildings:
                buildings[resolved] = []
                purchases[resolved] = []
            return resolved

        for building, rule in self.standing_buildings.items():
            buildings[group(rule)].append(building)
        for location, rule in self.scenario.starting_state.required_purchases.items():
            if not isinstance(rule, False_):   # nothing spares it
                purchases[group(rule)].append(location)

        return [
            ScenarioCostWaived(
                scenario=self.scenario.scenario,
                buildings=tuple(buildings[rule]),
                purchases=tuple(purchases[rule]),
            ).resolve(self.world)
                for rule in buildings
        ]

    def choice_order(self, building: Age2BuildingData) -> int:
        """Where a building stands among choices: the seed's building order."""
        return self.world.pool.budget.building_order[building]

    def could_have(self, building: Age2BuildingData) -> bool:
        if building not in self._could_have_building:
            has_building = self.scenario.has_building(building)
            self._could_have_building[building] = not self.logic.is_impossible(has_building)
        return self._could_have_building[building]

    def settle(self, need: Need) -> Need:
        return need.by_scenario(self)
