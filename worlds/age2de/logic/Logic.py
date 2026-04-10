from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification, Location
from .attila.Attila6StartingState import Attila6StartingState
from .attila.Attila5StartingState import Attila5StartingState
from .attila.Attila4StartingState import Attila4StartingState
from .attila.Attila3StartingState import Attila3StartingState
from .MilitaryLogic import MilitaryLogic
from ..locations.Buildings import Age2BuildingData
from ..locations.Ages import Age2AgeData
from .attila.Attila1StartingState import Attila1StartingState
from .attila.Attila2StartingState import Attila2StartingState
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
    military: MilitaryLogic
    scenarios: list[ScenarioLogic]
    
    def __init__(self, world: Age2World):
        self.buildings = BuildingLogic(self, world)
        self.ages =  AgeLogic(self, world)
        self.scenarios = [
            ScenarioLogic(self, Attila1StartingState(self)),
            ScenarioLogic(self, Attila2StartingState(self)),
            ScenarioLogic(self, Attila3StartingState(self)),
            ScenarioLogic(self, Attila4StartingState(self)),
            ScenarioLogic(self, Attila5StartingState(self)),
            ScenarioLogic(self, Attila6StartingState(self)),
        ]
        self.military = MilitaryLogic(self, world)
        self.world = world

    def has_military(self) -> Rule:
        return self.buildings.has_military()
    
    def has_siege(self) -> Rule:
        return self.buildings.has_siege()
    
    def can_build_building(self, building: Age2BuildingData) -> Rule:
        can_build: Rule = self.buildings.has_building(building) & self.ages.has_building_age(building) & self.buildings.has_prerequisites(building)
        has_vils: Rule = False_()
        can_reach_age: Rule = False_()
        for scenario in self.scenarios:
            has_vils = has_vils | (scenario.is_unlocked() & scenario.has_vils())
            can_reach_age = can_reach_age | (scenario.is_unlocked() & scenario.can_reach_age(building.age))
        return can_build & has_vils & can_reach_age