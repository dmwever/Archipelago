from dataclasses import dataclass
import typing

from Options import (Choice, OptionCounter, OptionList, OptionSet, PerGameCommonOptions, Range,
                     StartInventoryPool, Toggle)
from worlds.age2de.locations.Campaigns import Age2CampaignData
from .locations.Buildings import BuildingOption
from .items.Items import TRAP_NAMES

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


class LocalStart(Choice):
    """Place the items needed for a playable opening in your own world.
        No: Place nothing locally.
        Base: Place the items needed to build a town centre locally.
        Guarantee Win First Scenario: Place everything needed to beat one of your starting scenarios locally.
        Both: Place both sets locally.
    """
    internal_name = "local_start"
    display_name = "Local Start"
    option_no = 0
    option_base = 1
    option_guarantee_win_first_scenario = 2
    option_both = 3
    default = option_no


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
        Attila the Hun
        Joan of Arc
    """
    display_name = "Starting Campaigns"
    valid_keys = {campaign.campaign_name for campaign in Age2CampaignData}
    default = set((Age2CampaignData.ATTILA.campaign_name,))

class EnabledCampaigns(OptionSet):
    """
    Determines which vanilla campaigns will be unlocked for the player.
        Attila the Hun
        Joan of Arc
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
    internal_name = "shuffle_ages"
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
    Items: The technology is hidden until its item arrives.
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
    Find Items: A technology the scenario would have started with is not applied on scenario start
    until the item is found. Once found, the tech costs nothing to research for its check.
    Only Find Units: Same as Find Items, but only units are hidden.
    Start In Dark Age: Every scenario opens in the Dark Age with nothing researched at all, ages
    included, so even the age-ups have to be earned back.
    """
    internal_name = "existing_techs"
    display_name = "Existing Techs"
    option_vanilla = 0
    option_find_items = 1
    option_only_find_units = 2
    option_start_in_dark_age = 3
    default = option_vanilla


class TrapDifficulty(Choice):
    """
    How punishing traps are when they are enabled. No Traps keeps them out of the item pool entirely.
    """
    internal_name = "trap_difficulty"
    display_name = "Trap Difficulty"
    option_no_traps = 0
    option_easiest = 1
    option_standard = 2
    option_medium = 3
    option_hard = 4
    option_legendary = 5
    default = option_no_traps

    def include_traps(self) -> bool:
        return self.value > 0


class TrapPercentage(Range):
    """
    Percentage of the leftover filler slots to replace with traps. Starting resources are always
    funded first, so this only ever spends what is left over once they have what they need. A seed
    with no room to spare produces no traps whatever this is set to.
    """
    internal_name = "trap_percentage"
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 20


TRAP_DEFAULT_WEIGHT = 100


class TrapDistribution(OptionCounter):
    """
    Relative chance of each trap whenever a trap slot is rolled. Every trap defaults to 100. A trap
    on 200 is twice as likely as one on 100, a trap on 10 a tenth as likely, and 0 disables that
    trap outright. Setting every weight to 0 produces no traps at all, overriding Trap Percentage.
    """
    internal_name = "trap_distribution"
    display_name = "Trap Distribution"
    min = 0
    max = 1000
    valid_keys = frozenset(TRAP_NAMES)
    default = {_trap_name: TRAP_DEFAULT_WEIGHT for _trap_name in TRAP_NAMES}


@dataclass
class Age2Options(PerGameCommonOptions):
    """
    Every option in the Age2DE randomizer
    """

    startInventoryPool: StartInventoryPool
    scenario_branching: ScenarioBranching
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
    local_start: LocalStart
    trap_difficulty: TrapDifficulty
    trap_percentage: TrapPercentage
    trap_distribution: TrapDistribution
