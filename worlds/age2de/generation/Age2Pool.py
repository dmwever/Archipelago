from __future__ import annotations

from typing import TYPE_CHECKING

from .pools.AgePool import AgePool
from .pools.BuildingPool import BuildingPool
from .pools.CampaignPool import CampaignPool
from .pools.CivilizationPool import CivilizationPool
from .pools.FillerPool import FillerPool
from .pools.ResourcePool import ResourcePool
from .pools.ScenarioPool import ScenarioPool
from .pools.TechPool import TechPool
from .pools.TrapPool import TrapPool
from .pools.UnitPool import UnitPool

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
        self.units = UnitPool(world.options, self.civs, self.scenarios.included)
        self.resources = ResourcePool(world.options, world)
        self.traps = TrapPool(world.options, world)
        self.filler = FillerPool(world.options, world, self.scenarios)
