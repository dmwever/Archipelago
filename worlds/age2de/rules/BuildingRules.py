from __future__ import annotations

from dataclasses import dataclass
from typing import override, TYPE_CHECKING
from NetUtils import JSONMessagePart
from rule_builder.rules import Has, HasAll, HasFromListUnique, Rule

from BaseClasses import CollectionState

from ..items.Items import Age2ItemData

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from . import AgeRules
    from .. import Age2World

def set_rules(world: Age2World) -> None:
    for building in Age2BuildingData:
        world.set_rule(building.name, Has(building.item.item_name))

two_from_dark_age: Rule = HasFromListUnique(
        Age2ItemData.MILL.item_name,
        Age2ItemData.LUMBER_CAMP.item_name,
        Age2ItemData.MINING_CAMP.item_name,
        Age2ItemData.DOCK.item_name,
        Age2ItemData.BARRACKS.item_name, count=2)

two_from_feudal_age: Rule = HasFromListUnique(
        Age2ItemData.ARCHERY_RANGE.item_name,
        Age2ItemData.STABLE.item_name,
        Age2ItemData.MARKET.item_name,
        Age2ItemData.BLACKSMITH.item_name, count=2)

two_from_castle_age: Rule = HasFromListUnique(
        Age2ItemData.MONASTERY.item_name,
        Age2ItemData.UNIVERSITY.item_name,
        Age2ItemData.SIEGE_WORKSHOP.item_name, count=2)

can_build_tc = HasAll(
        Age2ItemData.TOWN_CENTER_STONE.item_name,
         Age2ItemData.TOWN_CENTER_WOOD.item_name,
         Age2ItemData.TOWN_CENTER.item_name)

def set_building_ages(world: Age2World) -> Rule:
    for building in Age2BuildingData:
        world.set_rule(building.item.item_name, AgeRules.building_age(building))

# @dataclass
# class AgeUpBuildingRequirement(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
#     @override
#     def _instantiate(self, world: "Age2World") -> Rule.Resolved:
#         # caching_enabled only needs to be passed in when your world inherits from CachedRuleBuilderWorld
        
#         return self.Resolved(world.required_mcguffins, player=world.player)

#     class Resolved(Rule.Resolved):
#         num_needed: int
#         required_building_list: list[Age2BuildingData] = []

#         @override
#         def _evaluate(self, state: CollectionState) -> bool:
#             return state.has_from_list_unique(self.required_building_list, self.player, count=self.num_needed)

#         @override
#         def item_dependencies(self) -> dict[str, set[int]]:
#             # this function is only required if you have caching enabled
#             return dict.fromkeys([data.item.item_name for data in self.required_building_list], id(self))

#         @override
#         def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
#             # this method can be overridden to display custom explanations
#             return [
#                 {"type": "text", "text": f"Need {self.num_needed} of"},
#                 {"type": "color", "color": "green" if state and self(state) else "salmon", "text": str(self.goal)},
#                 {"type": "text", "text": " McGuffins"},
#             ]