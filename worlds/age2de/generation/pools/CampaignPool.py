from __future__ import annotations

from typing import TYPE_CHECKING

from ...locations.Campaigns import Age2CampaignData

if TYPE_CHECKING:
    from ...Options import Age2Options


class CampaignPool:
    def __init__(self, options: 'Age2Options') -> None:
        self.enabled = [campaign for campaign in Age2CampaignData
                        if campaign.campaign_name in options.enabled_campaigns]
        self.starting = [campaign for campaign in self.enabled
                         if campaign.campaign_name in options.starting_campaigns]
