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
    arrives.
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
    Shuffled: Unique technologies are shuffled.
    Shuffled Everywhere: Unique technologies are shuffled. If tech behavior is instant, techs apply cross-civilization.
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
    until the item is found. Once found, the tech is free to research in that scenario.
    Only Find Units: Same as Find Items, but only units are hidden.
    Start In Dark Age: Every scenario opens in the Dark Age with nothing researched at all.
    """
    internal_name = "existing_techs"
    display_name = "Existing Techs"
    option_vanilla = 0
    option_find_items = 1
    option_only_find_units = 2
    option_start_in_dark_age = 3
    default = option_vanilla


class Unitsanity(Choice):
    """
    Shuffles units. Owning a unit sends its check, and items are what let you train one.
    None: Units behave as vanilla.
    Unit Line: A whole upgrade line is one location and one item, e.g. the Knight line.
    All: Lines are still what you unlock, but owning any single unit is its own check.
    """
    internal_name = "unitsanity"
    display_name = "Unitsanity"
    option_none = 0
    option_unit_line = 1
    option_all = 2
    default = option_none


class UnitsanityItems(Choice):
    """
    What a unitsanity item is. Requires Unitsanity.
    Unit Line: One item per line, e.g. Militia Line, Archer Line.
    Upgrades: Units need the equipment they are known for, so a Knight wants a Horse, a Sword and
    a Shield while an Archer only wants a Bow. A unit becomes trainable once it has all of its own.
    Buildings: One item per producing building, e.g. Barracks Units, Archery Range Units.
    """
    internal_name = "unitsanity_items"
    display_name = "Unitsanity Items"
    option_unit_line = 0
    option_upgrades = 1
    option_buildings = 2
    default = option_unit_line


class ShuffleVillager(Choice):
    """
    Whether the villager is shuffled. Independent of Unitsanity.
    No: Villagers behave as vanilla.
    Yes: The villager is an item and a location.
    Include Professions: Each job a villager can do is its own location.
    """
    internal_name = "shuffle_villager"
    display_name = "Shuffle Villager"
    option_no = 0
    option_yes = 1
    option_include_professions = 2
    default = option_no


class IncludeUniqueUnits(Choice):
    """
    Which civilization-restricted units join the pool. Requires Unitsanity.
    None: Only units (almost) every civilization can train are shuffled.
    Regional: Also shuffle units a handful of civilizations share, e.g. the Eagle, Camel and
    Steppe Lancer lines.
    Unique: Also shuffle units one civilization has, e.g. the Tarkan or the Longboat.
    Both: Shuffle unique and regional units alike.
    A unit is only ever obtainable while you are playing a civilization that has it.
    """
    internal_name = "include_unique_units"
    display_name = "Include Unique Units"
    option_none = 0
    option_unique = 1
    option_regional = 2
    option_both = 3
    default = option_none


class Caveman(Toggle):
    """
    OOOK ONK. Need Unit.
    Not for weak heart man.
    """
    internal_name = "caveman"
    display_name = "Caveman"


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
    unitsanity: Unitsanity
    unitsanity_items: UnitsanityItems
    shuffle_villager: ShuffleVillager
    include_unique_units: IncludeUniqueUnits
    caveman: Caveman
    goal: Goal
    local_start: LocalStart
