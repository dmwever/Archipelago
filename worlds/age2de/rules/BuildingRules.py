from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, Rule

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Rules import Rules

class BuildingRules:
    
    def __init__(self, rules: 'Rules'):
        self.rules = rules
        
    def set_rules(self, world: Age2World) -> None:
        for building in world.included_buildings:
            has_building: Rule = Has(building.item.item_name)
            has_building_age = self.rules.age_rules.has_building_age(building)
            world.set_rule(world.get_location(building.location_name), has_building & has_building_age)

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