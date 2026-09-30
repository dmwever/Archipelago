from typing import TYPE_CHECKING
from rule_builder.rules import Has, Rule, True_



if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

class GoalLogic:
    
    def __init__(self, logic: 'Logic', world: 'Age2World'):
        self.logic = logic
        self.world = world
    
    def completed_all_campaigns(self) -> Rule:
        completed: Rule = True_()
        for campaign in self.world.pool.campaigns.enabled:
            for scenario in self.world.pool.scenarios.of(campaign):
                completed = completed & Has(scenario.scenario_name + ": Unlock Next Scenario")
        return completed