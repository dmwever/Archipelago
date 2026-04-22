from dataclasses import dataclass
import typing

from Options import Choice, OptionList, OptionSet, PerGameCommonOptions, StartInventoryPool
from worlds.age2de.locations.Campaigns import Age2CampaignData
from .locations.Buildings import BuildingOption

class Goal(Choice):
    """Goal for this playthrough.
    Win Selected Campaigns: Finish each campaign selected for victory.
    """
    internal_name = "goal"
    display_name = "Goal"
    option_campaign_completion = 0
    default = option_campaign_completion
    

class ScenarioBranching(Choice):
    """If a story quest has multiple routes you can take depending on your decisions;
        Any: Any decision made will send the check for that story quest.
        All: Every individual decision will send it's own check, potentially requiring you to play the same scenario multiple times.
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
    Unique: Shuffle unique buildings, if applicable civilizations are in the pool. Other options apply to these buildings, e.g. if economy isn't shuffled, neither is folwark.
    Wonder: The wonder, the wonder, the... NO!
    """
    display_name = "Shuffle Buildings"
    valid_keys = frozenset({
        BuildingOption.economy,
        BuildingOption.tech,
        BuildingOption.military,
        BuildingOption.defense,
        BuildingOption.unique,
        BuildingOption.wonder,
    })
    default = set({BuildingOption.economy, BuildingOption.tech, BuildingOption.military})
    
    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, OptionSet):
            return set(self.value) == other.value
        if isinstance(other, OptionList):
            return set(self.value) == set(other.value)
        else:
            return typing.cast(bool, self.value == other)

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
    shuffle_buildings: ShuffleBuildings
    enabled_campaigns: EnabledCampaigns
    starting_campaigns: StartingCampaigns
    goal: Goal
