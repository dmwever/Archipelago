from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, StartInventoryPool

class Goal(Choice):
    """Goal for this playthrough.
    Win Selected Campaigns: Finish each campaign selected for victory.
    """
    internal_name = "goal"
    display_name = "Goal"
    option_campaign_completion = 0
    default = option_campaign_completion
    

class ScenarioBranching(Choice):
    """What checks are added to the pool for branching scenario decisions.
    Any: Each branching objective will contain a single check.
    All: Every branching objective contains a check.
    """
    internal_name = "scenario_branching"
    display_name = "Scenario Branching"
    option_any = 0
    option_all = 1
    default = option_any

@dataclass
class Age2Options(PerGameCommonOptions):
    """
    Every option in the Age2DE randomizer
    """

    startInventoryPool: StartInventoryPool
    scenarioBranching: ScenarioBranching
    goal: Goal