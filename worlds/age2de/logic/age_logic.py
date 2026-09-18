from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from NetUtils import JSONMessagePart
from BaseClasses import CollectionState
from ..rules.AgeRules import TwoBuildingsRequirement

from ..items.Items import Age2ItemData
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from rule_builder.rules import False_, Has, HasAll, HasAny, HasFromListUnique, NestedRule, Or, Rule, True_

from .ScenarioLogic import ScenarioLogic


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic
    
class AgeLogic:
    
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
        self.age_to_scenarios: dict[Age2AgeData, Rule] = {age: False_() for age in Age2AgeData }
        self.can_reach_age: dict[Age2AgeData, Rule] = {age: False_() for age in Age2AgeData}
        
    def set_can_reach_age(self, scenarios: list[ScenarioLogic]):
        for age in Age2AgeData:
            rule = self.can_reach_age[age]
            for scenario in scenarios:
                rule = rule | (scenario.is_unlocked() & scenario.start_past_age(age))
            self.can_reach_age[age] = rule
    
    def set_age_to_scenarios(self, scenarios: list[ScenarioLogic]):
        for age in Age2AgeData:
            rule = self.age_to_scenarios[age]
            for scenario in scenarios:
                rule = rule | (scenario.is_unlocked() & scenario.age_playable(age))
            self.age_to_scenarios[age] = rule
    
    def two_from_dark_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.logic.buildings.has_building(Age2BuildingData.MILL),
            self.logic.buildings.has_building(Age2BuildingData.LUMBER_CAMP),
            self.logic.buildings.has_building(Age2BuildingData.MINING_CAMP),
            self.logic.buildings.has_building(Age2BuildingData.DOCK),
            self.logic.buildings.has_building(Age2BuildingData.BARRACKS)
        ])
    
    def two_from_fuedal_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.logic.buildings.has_building(Age2BuildingData.ARCHERY_RANGE),
            self.logic.buildings.has_building(Age2BuildingData.STABLE),
            self.logic.buildings.has_building(Age2BuildingData.MARKET),
            self.logic.buildings.has_building(Age2BuildingData.BLACKSMITH)
        ])
    
    def two_from_castle_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.logic.buildings.has_building(Age2BuildingData.MONASTERY),
            self.logic.buildings.has_building(Age2BuildingData.UNIVERSITY),
            self.logic.buildings.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        ]) | self.logic.buildings.has_building(Age2BuildingData.CASTLE)

    def can_reach_feudal(self) -> Rule:
        return self.has_age(Age2AgeData.FEUDAL) & (self.two_from_dark_age() & self.logic.buildings.can_build_tc())
        
    def can_reach_castle(self) -> Rule:
        return self.has_age(Age2AgeData.CASTLE) & self.two_from_fuedal_age() & self.logic.buildings.can_build_tc()
        
    def can_reach_imperial(self) -> Rule:
        return self.has_age(Age2AgeData.IMPERIAL) & self.two_from_castle_age() & self.logic.buildings.can_build_tc()

    def can_reach(self, age: Age2AgeData) -> Rule:
        if age is Age2AgeData.FEUDAL:
            return self.can_reach_feudal()
        elif age is Age2AgeData.CASTLE:
            return self.can_reach_castle()
        elif age is Age2AgeData.IMPERIAL:
            return self.can_reach_imperial()
        else:
            return True_()

    def past_age(self, age: Age2AgeData) -> Rule:
        return Or(*(self.can_reach(a) for a in Age2AgeData if a >= age))

    def has_age(self, age: Age2AgeData) -> Rule:
        if not self.world.options.shuffle_ages or age.item is None:
            return True_()
        return Has(age.item.item_name)