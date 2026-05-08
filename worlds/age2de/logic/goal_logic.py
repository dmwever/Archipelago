from typing import TYPE_CHECKING
from rule_builder.rules import Has, HasAll, Rule, True_
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS
from ..items.Items import Age2ItemData

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

class GoalLogic:
    
    def __init__(self, logic: 'Logic', world: 'Age2World'):
        self.logic = logic
        self.world = world
    
    def completed_all_campaigns(self) -> Rule:
        completed: Rule = True_()
        for campaign in self.world.included_campaigns:
            for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
                completed = completed & Has(scenario.scenario_name + ": Unlock Next Scenario")
        return completed