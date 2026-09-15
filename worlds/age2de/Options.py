from dataclasses import dataclass
import typing

from Options import Choice, OptionList, OptionSet, PerGameCommonOptions, StartInventoryPool, Toggle
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

class ShuffleAges(Toggle):
    """
    Shuffles the ability to advance to the Feudal, Castle and Imperial Ages into the item pool.
    Reaching each age is its own check. Advancing still costs resources and still requires the
    usual buildings; the item only permits it. A scenario that starts above the Dark Age keeps
    the ages it starts with.
    """
    display_name = "Shuffle Ages"


class Techsanity(Choice):
    """
    Shuffles technologies. Researching a shuffled technology sends its check, and its item is what
    makes the technology available.
    None: Technologies behave as vanilla.
    Units: Only unit-line upgrades are shuffled, e.g. Man-At-Arms, Crossbowman, Elite Skirmisher.
    Generic: Every other technology is shuffled, e.g. Loom, Fletching, Wheelbarrow.
    All: Both.
    """
    internal_name = "techsanity"
    display_name = "Techsanity"
    option_none = 0
    option_units = 1
    option_generic = 2
    option_all = 3
    default = option_none


class TechBehavior(Choice):
    """
    When a shuffled technology's effect is applied. Requires Techsanity.
    Must Research: The item makes the technology available; you still pay for it and research it.
    Instant: The item applies the effect immediately, for free.
    Unit-line upgrades always behave as Must Research, since an upgrade you did not pay for would
    rewrite an army you already have.
    """
    internal_name = "tech_behavior"
    display_name = "Tech Behavior"
    option_must_research = 0
    option_instant = 1
    default = option_must_research


class LockTechs(Choice):
    """
    What a shuffled technology's item unlocks. Requires Techsanity.
    Items: The technology is greyed out until its item arrives.
    Effects: The technology is always researchable, but researching it does nothing until its item
    arrives. Researching still sends the check, so no check is ever locked behind its own item.
    """
    internal_name = "lock_techs"
    display_name = "Lock Techs"
    option_items = 0
    option_effects = 1
    default = option_items


class ShuffleUniqueTechs(Choice):
    """
    Whether civilization unique technologies join the pool. Requires Techsanity.
    Unshuffled: Unique technologies behave as vanilla.
    Shuffled: Unique technologies are shuffled. A unique technology's effect only applies while you
    are playing a civilization that has it.
    Shuffled Everywhere: As above, but the effect applies to whichever civilization you are playing.
    No setting ever lets a civilization research another civilization's unique technology.
    """
    internal_name = "shuffle_unique_techs"
    display_name = "Shuffle Unique Techs"
    option_unshuffled = 0
    option_shuffled = 1
    option_shuffled_everywhere = 2
    default = option_unshuffled


class ExistingTechs(Choice):
    """
    What happens to the technologies a scenario would normally start with. Requires Techsanity.
    Vanilla: A scenario starting in the Castle Age keeps every Dark and Feudal Age technology.
    Lock Technologies: Nothing is granted; every shuffled technology must be found.
    Only Lock Units: Economy and blacksmith technologies are granted as vanilla, but unit-line
    upgrades below the scenario's age must be found.
    Under Only Lock Units, Techsanity: Generic behaves as Vanilla and Techsanity: Units behaves as
    Lock Technologies.
    """
    internal_name = "existing_techs"
    display_name = "Existing Techs"
    option_vanilla = 0
    option_lock_technologies = 1
    option_only_lock_units = 2
    default = option_vanilla

    @classmethod
    def rebases(cls, value: int) -> bool:
        """Whether the installed scenario has to start in the Dark Age, so that
        the engine auto-researches nothing and XS can grant the right state."""
        return value != cls.option_vanilla

    @classmethod
    def locks(cls, value: int, is_upgrade: bool) -> bool:
        """Whether this mode withholds a technology the scenario would grant."""
        if value == cls.option_lock_technologies:
            return True
        return value == cls.option_only_lock_units and is_upgrade


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
    shuffle_ages: ShuffleAges
    techsanity: Techsanity
    tech_behavior: TechBehavior
    lock_techs: LockTechs
    shuffle_unique_techs: ShuffleUniqueTechs
    existing_techs: ExistingTechs
    goal: Goal
