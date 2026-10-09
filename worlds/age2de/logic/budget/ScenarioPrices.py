"""The terms one scenario sets on every price: where it starts, what climbs each age, and which
buildings it could ever have."""
from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ..scenarios.ScenarioAgeLogic import PREVIOUS
from .Need import CLIMBED_AGES, AgeUpBuildings, Need

if TYPE_CHECKING:
    from ... import Age2World
    from ..ScenarioLogic import ScenarioLogic

class ScenarioPrices:
    def __init__(self, scenario: 'ScenarioLogic', world: 'Age2World') -> None:
        self.scenario = scenario
        self.world = world

        ages = world.pool.ages
        self.start_age = Age2AgeData.DARK if ages.dark_start else ages.starts_in(scenario.scenario)
        self.age_up_buildings: tuple[AgeUpBuildings, ...] = tuple(
            AgeUpBuildings(age, rule.buildings, rule.single_building) for age in CLIMBED_AGES
                for rule in [scenario.ages.two_from(PREVIOUS[age])]
        )

        self._could_have_building: dict[Age2BuildingData, bool] = {}

    def choice_order(self, building: Age2BuildingData) -> int:
        """Where a building stands among choices: the seed's building order."""
        return self.world.pool.budget.building_order[building]

    def is_impossible(self, rule: Rule) -> bool:
        return rule.resolve(self.world).always_false

    def could_have(self, building: Age2BuildingData) -> bool:
        if building not in self._could_have_building:
            has_building = self.scenario.has_building(building)
            self._could_have_building[building] = not self.is_impossible(has_building)
        return self._could_have_building[building]

    def settle(self, need: Need) -> Need:
        return need.by_scenario(self)
