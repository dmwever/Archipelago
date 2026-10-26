from dataclasses import dataclass
import typing

from Options import (Choice, DefaultOnToggle, OptionCounter, OptionError, OptionList, OptionSet, PerGameCommonOptions,
                     Range, StartInventoryPool, Toggle)
from worlds.age2de.locations.Campaigns import Age2CampaignData
from .locations.Buildings import NAME_TO_BUILDING, Age2BuildingData, BuildingOption
from .locations.Players import Age2PlayerData, TradeAccess
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
        Base: Shuffle the town center and houses. Local Start's Base places these in your own world.
        Economy: Shuffle the market, resource buildings and farms. Includes dock.
        Tech: Shuffle the blacksmith and university.
        Military: Shuffle the barracks, archery range, stable, siege workshop and monastery. Includes dock.
        Castle: Shuffle the castle, and with Unique the krepost, fortified church and donjon.
        Defense: Shuffle walls, gates and towers.
        Unique: Shuffle unique buildings, if applicable civilizations are in the pool. Other options apply to these buildings, e.g. if economy isn't shuffled, neither is folwark.
        Wonder: The wonder, the wonder, the... NO!
    A building's own name also works and shuffles it whatever its category, e.g. [Military, Market].
    Keys ignore case.
    """
    display_name = "Shuffle Buildings"
    valid_keys = frozenset({
        BuildingOption.base,
        BuildingOption.economy,
        BuildingOption.tech,
        BuildingOption.military,
        BuildingOption.castle,
        BuildingOption.defense,
        BuildingOption.unique,
        BuildingOption.wonder,
    })
    canonical_keys_by_casefold = {
        key.casefold(): key for key in [*valid_keys, *NAME_TO_BUILDING]
    }
    default = set({BuildingOption.economy, BuildingOption.tech, BuildingOption.military})
    
    def verify_keys(self) -> None:
        """Matches each key without case, then stores its canonical spelling. The yaml is input
        only, so the player's casing carries no meaning and nothing downstream folds case again."""
        unknown = [
            key for key in self.value
                if key.casefold() not in self.canonical_keys_by_casefold
        ]
        if unknown:
            raise OptionError(
                f"Found unexpected key {', '.join(unknown)} in {self.display_name}. "
                f"Allowed keys: {sorted(self.valid_keys)} or any building's name."
            )
        self.value = {self.canonical_keys_by_casefold[key.casefold()] for key in self.value}

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
        Genghis Khan
    Leave blank for a random start: one of your enabled campaigns is chosen for you.
    """
    display_name = "Starting Campaigns"
    valid_keys = {campaign.campaign_name for campaign in Age2CampaignData}
    default = set((Age2CampaignData.GENGHIS.campaign_name,))

class EnabledCampaigns(OptionSet):
    """
    Determines which vanilla campaigns will be unlocked for the player.
        Attila the Hun
        Joan of Arc
        Genghis Khan
    """
    display_name = "Enabled Campaigns"
    valid_keys = {campaign.campaign_name for campaign in Age2CampaignData}
    default = set((Age2CampaignData.GENGHIS.campaign_name,))

class ShuffleAges(DefaultOnToggle):
    """
    Shuffles the ability to advance to the Feudal, Castle and Imperial Ages into the item pool.
    """
    internal_name = "shuffle_ages"
    display_name = "Shuffle Ages"

class Techsanity(Choice):
    """
    Shuffles technologies. A shuffled technology stays researchable; researching it sends its
    check, and its item is what applies the effect.
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
    default = option_all

def upgrade_techs_shuffled(techsanity: int) -> bool:
    """Whether unit-line upgrade technologies are items. Generic shuffles Loom and Fletching
    and leaves the upgrades free, so it does not count."""
    return techsanity in (Techsanity.option_units, Techsanity.option_all)

class TechBehavior(Choice):
    """
    When a shuffled technology's effect is applied. Requires Techsanity.
    Must Research: You research the technology as usual, and its effect lands once the item has
    arrived.
    Instant: The item applies the effect immediately, for free.
    Unit-line upgrades always behave as Must Research, since an upgrade you did not pay for would
    rewrite an army you already have.
    """
    internal_name = "tech_behavior"
    display_name = "Tech Behavior"
    option_must_research = 0
    option_instant = 1
    default = option_must_research

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
    default = option_shuffled

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
    default = option_unit_line

class UnitsanityItems(Choice):
    """
    What a unitsanity item is. Requires Unitsanity.
    Unit Line: One item per line, e.g. Militia Line, Archer Line.
    Upgrades: Units need the equipment they are known for, so a Knight wants a Horse, a Sword and
    a Shield while an Archer only wants a Bow. A unit becomes trainable once it has all of its own.
    Adapts to techsanity.
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
    default = option_both

class Caveman(Toggle):
    """
    OOOK ONK. Need Unit.
    Not for weak heart man.
    """
    internal_name = "caveman"
    display_name = "Caveman"

class MonksCanCounter(Toggle):
    """
    Whether the logic may expect monks and missionaries to counter a unit.
    Off: Monks are only considered a counter to elephants.
    On: They can counter valuable unit-lines such as heavy cavalry and siege (with redemption).
    """
    internal_name = "monks_can_counter"
    display_name = "Monks Can Counter"

class SiegeCanCounter(Toggle):
    """
    Whether the logic may expect mangonels, bombard cannons and rocket carts to counter a unit.
    Does not affect scorpions. 
    Off: Mangonels, bombard cannons and rocket carts can only counter siege.
    On: Mangonels, bombard cannons and rocket carts can counter all units they are typically strong against.
    """
    internal_name = "siege_can_counter"
    display_name = "Siege Can Counter"

class MarketTrade(Toggle):
    """
    Whether the logic may expect you to buy and sell resources at your own market.
    Off: The market is never needed to afford anything.
    On: A market with a steady supply of wood or food to sell can stand in for any resource.
    """
    internal_name = "market_trade"
    display_name = "Market Trade"

class PartnerTrade(Choice):
    """
    Whether the logic may expect you to run trade carts and trade cogs to another player's market or dock, and to whose.
    None: Trade with other players is never needed to afford anything.
    Allies: Only an ally's market or dock, and only where the scenario's ally keeps one usable.
    Allies And Enemies: An enemy's too, once you can defeat its owner, straight away if it is undefended, or once you can guard the route to it.
    """
    internal_name = "partner_trade"
    display_name = "Partner Trade"
    option_none = 0
    option_allies = 1
    option_allies_and_enemies = 2
    default = option_allies

    def needs_defeat_event(self, player: Age2PlayerData) -> bool:
        return self.value == self.option_allies_and_enemies and player.can_trade_once_defeated

    def needs_guard_event(self, player: Age2PlayerData, building: Age2BuildingData) -> bool:
        return (self.value == self.option_allies_and_enemies
                and player.trade_access(building) is TradeAccess.GUARDED)

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
    default = option_standard

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
    shuffle_unique_techs: ShuffleUniqueTechs
    existing_techs: ExistingTechs
    unitsanity: Unitsanity
    unitsanity_items: UnitsanityItems
    shuffle_villager: ShuffleVillager
    include_unique_units: IncludeUniqueUnits
    caveman: Caveman
    monks_can_counter: MonksCanCounter
    siege_can_counter: SiegeCanCounter
    market_trade: MarketTrade
    partner_trade: PartnerTrade
    goal: Goal
    local_start: LocalStart
    trap_difficulty: TrapDifficulty
    trap_percentage: TrapPercentage
    trap_distribution: TrapDistribution
