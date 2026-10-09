"""The terms one scenario sets on every price: where it starts, what climbs each age, and which
buildings it could ever have."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ..budget.Need import CLIMBED_AGES, Need
from ..custom_logic.AgeUpRequirement import AgeUpRequirement

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

class ScenarioPriceLogic:
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
