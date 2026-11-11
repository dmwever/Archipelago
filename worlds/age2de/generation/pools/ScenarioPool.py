from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from ...locations.Locations import Age2LocationType
from ...locations.Scenarios import CAMPAIGN_TO_SCENARIOS, Age2ScenarioData
from ...Options import ScenarioBranching

if TYPE_CHECKING:
    from ...locations.Campaigns import Age2CampaignData
    from ...Options import Age2Options


class ScenarioPool:
    def __init__(self, options: 'Age2Options', campaigns: Iterable['Age2CampaignData']) -> None:
        self._mode = options.scenario_branching
        self._by_campaign = {campaign: CAMPAIGN_TO_SCENARIOS[campaign] for campaign in campaigns}
        self.included: list[Age2ScenarioData] = [scenario
                                                 for scenarios in self._by_campaign.values()
                                                 for scenario in scenarios]

    @property
    def all_scenario_branches(self) -> bool:
        return self._mode == ScenarioBranching.option_all

    def in_campaign(self, campaign: 'Age2CampaignData') -> list[Age2ScenarioData]:
        return self._by_campaign[campaign]

    def first_scenario(self, campaign: 'Age2CampaignData') -> Age2ScenarioData:
        return self._by_campaign[campaign][0]

    def includes_location(self, location) -> bool:
        if location.type == Age2LocationType.OBJECTIVE_BRANCHING_ALL:
            return self._mode == ScenarioBranching.option_all
        if location.type == Age2LocationType.OBJECTIVE_BRANCHING_ANY:
            return self._mode == ScenarioBranching.option_any
        return True
