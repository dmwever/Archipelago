from typing import Iterable

from ..items.Items import Age2ItemData, CATEGORY_TO_ITEMS, Mercenary
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData


class DataStorage:
    """Built once per connection from the campaigns the seed included."""

    mercenaries: list[Age2ItemData]
    scenarios: list[Age2ScenarioData]

    def __init__(self, campaigns: Iterable[Age2CampaignData]):
        included = set(campaigns)
        self.mercenaries = sorted((item for item in CATEGORY_TO_ITEMS[Mercenary]
                                   if item.type.vanilla_scenario.campaign in included),
                                  key=lambda item: item.id)
        # Sorting by id is campaign-major, chapter-minor.
        self.scenarios = sorted((scenario for scenario in Age2ScenarioData
                                 if scenario.campaign in included),
                                key=lambda scenario: scenario.id)

    def used_mercenaries(self, storage_int: int) -> set[Age2ItemData]:
        return {mercenary for index, mercenary in enumerate(self.mercenaries) if storage_int & (1 << index) != 0}

    def completed_scenarios(self, storage_int: int) -> set[Age2ScenarioData]:
        return {scenario for index, scenario in enumerate(self.scenarios) if storage_int & (1 << index) != 0}

    def mercenary_bit(self, mercenary: Age2ItemData) -> int:
        return self.mercenaries.index(mercenary)

    def scenario_bit(self, scenario: Age2ScenarioData) -> int:
        return self.scenarios.index(scenario)

    def mercenary_field(self, mercenaries: Iterable[Age2ItemData]) -> int:
        storage_int: int = 0
        for index, mercenary in enumerate(self.mercenaries):
            if mercenary in mercenaries:
                storage_int = storage_int | (1 << index)
        return storage_int

    def scenario_field(self, scenarios: Iterable[Age2ScenarioData]) -> int:
        storage_int: int = 0
        for index, scenario in enumerate(self.scenarios):
            if scenario in scenarios:
                storage_int = storage_int | (1 << index)
        return storage_int
