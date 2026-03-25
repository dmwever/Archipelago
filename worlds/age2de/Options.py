from dataclasses import dataclass

from Options import Choice, OptionSet, PerGameCommonOptions, StartInventoryPool
from worlds.age2de.locations.Campaigns import Age2CampaignData
from .items.Items import BuildingOption

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


class ShuffleBuildings(OptionSet):
    """
    Determines which buildings to shuffle.
    Economy: Shuffle houses, TC, market, resource buildings, farms. Includes dock.
    Tech: Shuffle blacksmith, university, monastery.
    Military: Shuffle military buildings. Includes dock and castle.
    Defense: Shuffle defensive buildings. Includes castle.
    Unique: Shuffle unique buildings, if applicable civilizations are in the pool. Other options apply to these buildings, 
    e.g. if economy isn't shuffled, neither is folwark.
    """
    display_name = "Shuffle Buildings"
    valid_keys = frozenset({
        BuildingOption.ECONOMY,
        BuildingOption.TECH,
        BuildingOption.MILITARY,
        BuildingOption.DEFENSE,
        BuildingOption.UNIQUE,
        BuildingOption.WONDER,
    })
    default = set((BuildingOption.ECONOMY, BuildingOption.TECH, BuildingOption.MILITARY))

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