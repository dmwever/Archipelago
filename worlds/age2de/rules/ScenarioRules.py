from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..logic.Logic import Logic

from ..locations.Buildings import Age2BuildingData

from rule_builder.rules import False_, Rule, True_

from ..locations.Ages import Age2AgeData


if TYPE_CHECKING:
    from .. import Age2World
    from .Rules import Rules


class ScenarioRules:
    
    def __init__(self, rules: 'Rules'):
        self.rules = rules
        self.logic = rules.logic
        self.world = rules.world
        
    def set_rules():
        pass