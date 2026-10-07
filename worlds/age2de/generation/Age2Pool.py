from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..items import Items
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData

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


@dataclass
class ItemPlan:
    pooled: list[Age2ItemData] = field(default_factory=list)
    precollected: list[Age2ItemData] = field(default_factory=list)


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
        self.filler = FillerPool(world.options, world, self.scenarios, self.campaigns)

    def item_plan(self, unit_items: list[Age2ItemData]) -> ItemPlan:
        plan = ItemPlan()
        for item in Age2ItemData:
            if isinstance(item.type, Items.Victory):
                continue
            elif isinstance(item.type, (Items.ScenarioItem, Items.Mercenary)):
                if item.type.vanilla_scenario in self.scenarios.included:
                    plan.pooled.append(item)
            elif isinstance(item.type, Items.Campaign):
                if item.type.vanilla_campaign in self.campaigns.enabled:
                    if item.type.vanilla_campaign in self.campaigns.starting:
                        plan.precollected.append(item)
                    else:
                        plan.pooled.append(item)
            elif isinstance(item.type, Items.ProgressiveScenario):
                if item.type.vanilla_campaign in self.campaigns.enabled:
                    for _ in range(item.type.num_additional_scenarios):
                        plan.pooled.append(item)
            elif isinstance(item.type, Items.Resources):
                continue
            elif isinstance(item.type, Items.StartingResources):
                continue
            elif isinstance(item.type, Items.TCResources):
                plan.pooled.append(item)
            elif isinstance(item.type, Items.Age2AgeData):
                if item.type in self.ages.locations:
                    plan.pooled.append(item)
                else:
                    plan.precollected.append(item)
            elif isinstance(item.type, (Items.Building, Items.Tech, Items.UnitLine,
                                        Items.UnitUpgrade, Items.UnitBuilding,
                                        Items.VillagerProfession, Items.Trap)):
                continue
            else:
                raise ValueError(f"Item {item} has unknown type {type(item.type)}")

        for building in Age2BuildingData:
            if building in self.buildings.locations:
                plan.pooled.append(building.item)
            else:
                plan.precollected.append(building.item)

        for tech in self.techs.shuffled:
            plan.pooled.append(tech.item)

        plan.pooled.extend(unit_items)
        return plan
