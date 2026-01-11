from dataclasses import dataclass

from Options import Choice, OptionSet, PerGameCommonOptions, StartInventoryPool
from worlds.age2de.locations.Campaigns import Age2CampaignData

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

class StartingCampaigns(OptionSet):
    """
    Determines which vanilla campaigns will start unlocked for the player.
    """
    display_name = "Enabled Campaigns"
    valid_keys = {campaign.campaign_name for campaign in Age2CampaignData}
    default = set((Age2CampaignData.ATTILA.campaign_name,))

class EnabledCampaigns(OptionSet):
    """
    Determines which vanilla campaigns will be unlocked for the player.
    """
    display_name = "Enabled Campaigns"
    valid_keys = {campaign.campaign_name for campaign in Age2CampaignData}
    default = set((Age2CampaignData.ATTILA.campaign_name,))

@dataclass
class Age2Options(PerGameCommonOptions):
    """
    Every option in the Age2DE randomizer
    """

    startInventoryPool: StartInventoryPool
    scenarioBranching: ScenarioBranching
    enabled_campaigns: EnabledCampaigns
    starting_campaigns: StartingCampaigns
    goal: Goal