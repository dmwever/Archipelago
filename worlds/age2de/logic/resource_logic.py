from math import ceil
from typing import TYPE_CHECKING, Mapping

from rule_builder.rules import And, Rule, True_

from ..items.Items import Resource
from .custom_logic.ResourceAmount import HasResourceAmount

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
        priced = [resource for resource, amount in costs.items() if amount > 0]
        if not priced:
            return True_()
        return And(*[self.has_amount(resource, costs[resource]) for resource in priced])

