from __future__ import annotations

from typing import TYPE_CHECKING

from .pools.AgePool import AgePool
from .pools.BuildingPool import BuildingPool
from .pools.CampaignPool import CampaignPool
from .pools.CivilizationPool import CivilizationPool
from .pools.ScenarioPool import ScenarioPool
from .pools.TechPool import TechPool

if TYPE_CHECKING:
    from .. import Age2World


class Age2Pool:
    def __init__(self, world: 'Age2World') -> None:
        self.world = world
        self.campaigns = CampaignPool(world.options)
        self.scenarios = ScenarioPool(world.options, self.campaigns.enabled)
        self.civs = CivilizationPool(self.scenarios.included)
        self.ages = AgePool(world.options, self.scenarios.included)
        self.buildings = BuildingPool(world.options, self.civs)
        self.techs = TechPool(world.options, self.ages.earliest, self.civs)
