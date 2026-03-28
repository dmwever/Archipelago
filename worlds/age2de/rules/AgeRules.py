from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from NetUtils import JSONMessagePart
from BaseClasses import CollectionState

from ..locations.Ages import Age2AgeData, Age2ItemData
from ..locations.Buildings import Age2BuildingData
from rule_builder.rules import False_, HasAll, HasAny, HasFromListUnique, NestedRule, Rule, True_


if TYPE_CHECKING:
    from .. import Age2World
    from .Rules import Rules
    
class AgeRules:
    
    def __init__(self, rules: 'Rules', world: Age2World):
        self.rules = rules
        self.world = world
    
    def two_from_dark_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.rules.building_rules.has_building(Age2BuildingData.MILL),
            self.rules.building_rules.has_building(Age2BuildingData.LUMBER_CAMP),
            self.rules.building_rules.has_building(Age2BuildingData.MINING_CAMP),
            self.rules.building_rules.has_building(Age2BuildingData.DOCK),
            self.rules.building_rules.has_building(Age2BuildingData.BARRACKS)
        ])
    
    def two_from_fuedal_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.rules.building_rules.has_building(Age2BuildingData.ARCHERY_RANGE),
            self.rules.building_rules.has_building(Age2BuildingData.STABLE),
            self.rules.building_rules.has_building(Age2BuildingData.MARKET),
            self.rules.building_rules.has_building(Age2BuildingData.BLACKSMITH)
        ])
    
    def two_from_castle_age(self) -> Rule:
        return TwoBuildingsRequirement([
            self.rules.building_rules.has_building(Age2BuildingData.MONASTERY),
            self.rules.building_rules.has_building(Age2BuildingData.UNIVERSITY),
            self.rules.building_rules.has_building(Age2BuildingData.SIEGE_WORKSHOP)
        ]) | self.rules.building_rules.has_building(Age2BuildingData.CASTLE)

    def can_build_tc(self) -> Rule:
        return self.rules.building_rules.has_building(Age2BuildingData.TOWN_CENTER) & \
            HasAll(Age2ItemData.TOWN_CENTER_WOOD.item_name, Age2ItemData.TOWN_CENTER_STONE.item_name)

    def can_reach_feudal(self) -> Rule:
        return self.has_age(Age2AgeData.FEUDAL) & (self.two_from_dark_age() & self.can_build_tc())
        
    def can_reach_castle(self) -> Rule:
        return self.has_age(Age2AgeData.CASTLE) & self.two_from_fuedal_age() & self.can_build_tc()
        
    def can_reach_imperial(self) -> Rule:
        return self.has_age(Age2AgeData.IMPERIAL) & self.two_from_castle_age() & self.can_build_tc()

    def has_age(self, age: Age2AgeData) -> Rule:
        return True_()

    def has_building_age(self, building: Age2BuildingData) -> Rule:
        if building.age is Age2AgeData.FEUDAL:
            return self.can_reach_feudal()
        elif building.age is Age2AgeData.CASTLE:
            return self.can_reach_castle()
        elif building.age is Age2AgeData.IMPERIAL:
            return self.can_reach_imperial()
        else:
            return True_()
    
@dataclass
class TwoBuildingsRequirement(NestedRule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """A rule that checks that a player has at least two of the needed buildings to age up"""

    class Resolved(NestedRule.Resolved):
        num_needed: int = 2

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            count_reached: int = 0
            
            for rule in self.children:
                if rule(state):
                    count_reached += 1
            return count_reached >= self.num_needed


        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            # this method can be overridden to display custom explanations
            messages: list[JSONMessagePart] = [{"type": "text", "text": f"Need {self.num_needed} of"}]
            for i, child in enumerate(self.children):
                if i > 0:
                    messages.append({"type": "color", "color": "green" if state and self(state) else "salmon", "type": "text", "text": " | "})
                messages.extend(child.explain_json(state))
            messages.append({"type": "text", "text": " Buildings"})
            
            return messages