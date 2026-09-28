from math import ceil
from typing import TYPE_CHECKING, Mapping

from rule_builder.rules import And, HasAny, Rule, True_

from ..items.Items import Resource
from ..locations.VillagerJobs import FOOD_PROFESSIONS
from ..Options import ShuffleVillager
from ..rules.custom_rules.ResourceAmount import HasResourceAmount

if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic


class ResourceLogic:

    def __init__(self, logic: 'Logic', world: 'Age2World') -> None:
        self.logic = logic
        self.world = world

    def has_amount(self, resource: Resource, amount: float) -> Rule:
        return HasResourceAmount(resource=resource, amount=ceil(amount))

    def has_amounts(self, costs: Mapping[Resource, float]) -> Rule:
        return And(*[self.has_amount(resource, amount)
                     for resource, amount in costs.items() if amount > 0])

    def available(self, resource: Resource) -> int:
        return self.world.starting_resource_totals[resource]

    def has_any_food_profession(self) -> Rule:
        if self.world.options.shuffle_villager != ShuffleVillager.option_include_professions:
            return True_()
        return HasAny(*[profession.item_name for profession in FOOD_PROFESSIONS])
