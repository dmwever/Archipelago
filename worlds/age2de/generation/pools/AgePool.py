from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from rule_builder.options import OptionFilter

from ...locations.Ages import SHUFFLED_AGES, Age2AgeData
from ...Options import ExistingTechs

if TYPE_CHECKING:
    from ...locations.Scenarios import Age2ScenarioData
    from ...Options import Age2Options


VANILLA_AGE_START = OptionFilter(ExistingTechs, ExistingTechs.option_start_in_dark_age, "ne")

DARK_START = OptionFilter(ExistingTechs, ExistingTechs.option_start_in_dark_age)

class AgePool:
    def __init__(self, options: 'Age2Options', scenarios: Iterable['Age2ScenarioData']) -> None:
        self._shuffle_ages = options.shuffle_ages
        self._existing_techs = options.existing_techs
        self.earliest: Age2AgeData = min(scenario.vanilla_age for scenario in scenarios)
        self.shuffled: list[Age2AgeData] = [age for age in SHUFFLED_AGES
                                            if self.dark_start or age > self.earliest]

    @property
    def dark_start(self) -> bool:
        return self._existing_techs == ExistingTechs.option_start_in_dark_age

    @property
    def locations(self) -> list[Age2AgeData]:
        return self.shuffled if self._shuffle_ages else []

    def starts_in(self, scenario: 'Age2ScenarioData') -> Age2AgeData:
        return scenario.vanilla_age
