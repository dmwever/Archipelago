from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification, Location
from ..locations.Buildings import Age2BuildingData
from ..locations.Ages import Age2AgeData
from .attila.Attila1StartingState import Attila1StartingState
from .ScenarioLogic import ScenarioLogic
from .AgeLogic import AgeLogic
from .BuildingLogic import BuildingLogic
from rule_builder.rules import CanReachRegion, False_, Has, HasAll, Rule, True_

from ..locations.Scenarios import Age2ScenarioData

from ..items.Items import Age2ItemData
from ..locations.Locations import VICTORY_LOCATIONS, Age2ScenarioLocationData, Age2LocationType

if TYPE_CHECKING:
    from .. import Age2World


class Logic:
    buildings: BuildingLogic
    ages: AgeLogic
    scenarios: list[ScenarioLogic]
    
    def __init__(self, world: Age2World):
        self.buildings = BuildingLogic(self, world)
        self.ages =  AgeLogic(self, world)
        self.scenarios = []
        self.world = world