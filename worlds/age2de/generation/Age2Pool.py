from __future__ import annotations

from typing import TYPE_CHECKING

from .pools.CampaignPool import CampaignPool
from .pools.ScenarioPool import ScenarioPool

if TYPE_CHECKING:
    from .. import Age2World


class Age2Pool:
    def __init__(self, world: 'Age2World') -> None:
        self.world = world
        self.campaigns = CampaignPool(world.options)
        self.scenarios = ScenarioPool(world.options, self.campaigns.enabled)
