# world/age2DE/__init__.py

from math import ceil
import logging
from Options import OptionError
from rule_builder.cached_world import CachedRuleBuilderWorld
import settings
from typing import Any, ClassVar, Mapping
from BaseClasses import Entrance, Item, ItemClassification, Location, MultiWorld, Region
from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, Type, components, icon_paths, launch as launch_subprocess
from worlds.age2de.locations import Buildings
from worlds.age2de.locations.connections import LocationMapping
from worlds.age2de.locations.Buildings import Age2BuildingData
from worlds.age2de.locations.Scenarios import CAMPAIGN_TO_SCENARIOS
from .generation import Identity, LocalStart, SlotData, WorldVersion
from .generation.Age2Pool import Age2Pool
from .regions.UnitRegions import UnitRegions
from .Options import TRAP_DEFAULT_WEIGHT, Age2Options, Goal, ScenarioBranching
from .items import Items
from .locations import (Campaigns, EscortUnits, Heroes, Locations, Scenarios,
                        UnitLines, Units, VillagerJobs)
from .locations.Techs import Age2TechData
from .locations.connections import (CivilizationBuildings, CivilizationTechs,
                                    CivilizationUnits, GameCosts, ScenarioResources,
                                    ScenarioStartupUnits,
                                    ScenarioTriggerUnits, UnitBuildings,
                                    UnitCounters,
                                    UnitLineUnits, UnitRoles, UnitTechs,
                                    UnitUpgradeTokens, UnitVariants,
                                    VillagerJobBuildings)
from .rules.Rules import Rules

logger = logging.getLogger(__name__)

AGE2_DE = "Age Of Empires II: Definitive Edition"
class Age2Settings(settings.Group):
    class UserDirectory(settings.UserFolderPath):
        """The users local age2de user folder.
        Usually located at:
            "C:/Users/<USER>/Games/Age of Empires 2 DE/<STRING_OF_NUMBERS>/"
        Select the <STRING_OF_NUMBERS> folder as the user folder."""
        description = "Age of Empires II: Definitive Edition User Directory"
    
    user_folder: UserDirectory = UserDirectory(AGE2_DE)
        
class Age2World(CachedRuleBuilderWorld):
    """
    Age of Empires II: Definitive Edition is a Real-Time Strategy game centered around the medieval
    ages and the various battles, conquests, and wars of history.
    """
    game = AGE2_DE  # name of the game/world
    settings: ClassVar[Age2Settings]
    options_dataclass = Age2Options  # options the player can set
    options: Age2Options  # typing hints for option results
    topology_present = True  # show path to required location checks in spoiler

    item_names = set(item.item_name for item in Items.Age2ItemData)
    location_names = set(LocationMapping.location_name_list)
    item_name_to_id = Items.item_name_to_id
    item_id_to_name = Items.item_id_to_name
    location_name_to_id = LocationMapping.location_name_to_id
    location_id_to_name = LocationMapping.location_id_to_name
    item_mapping = Items.item_mapping
    item_name_groups = {"Traps": set(Items.TRAP_NAMES)}
    
    pool: Age2Pool
    unit_regions: UnitRegions
    rules: Rules

    def __init__(self, multiworld: 'MultiWorld', player: int) -> None:
        super().__init__(multiworld, player)

    @classmethod
    def create_group(cls, multiworld: 'MultiWorld', new_player_id: int, players: set[int]) -> World:
        group = super().create_group(multiworld, new_player_id, players)
        group.pool = Age2Pool(group)
        return group

    def inspect_options(self, options: Age2Options, player_name: str) -> None:
        if not options.enabled_campaigns.value:
            raise OptionError(f"{player_name}: enabled_campaigns needs at least one campaign.")
        enabled = {campaign.campaign_name for campaign in Campaigns.Age2CampaignData
                   if campaign.campaign_name in options.enabled_campaigns}
        if not options.starting_campaigns.value:
            drawn = self.random.choice(sorted(enabled))
            options.starting_campaigns.value = {drawn}
            logger.info("%s left starting_campaigns blank; starting them in %s.",
                        player_name, drawn)
        elif not enabled & set(options.starting_campaigns.value):
            raise OptionError(f"{player_name}: starting_campaigns must include at least one "
                              f"enabled campaign. Enabled: {sorted(options.enabled_campaigns.value)}.")
        for campaign in Campaigns.Age2CampaignData:
            if campaign.campaign_name in enabled and not CAMPAIGN_TO_SCENARIOS[campaign]:
                raise OptionError(f"{player_name}: {campaign.campaign_name} has no scenarios.")

    def generate_early(self) -> None:
        self.inspect_options(self.options, self.player_name)
        self.check_installable_name()
        self.pool = Age2Pool(self)

    def check_installable_name(self) -> None:
        """/install names each campaign file after the slot, so the name has to survive a file
        name. Refuse a name that leaves nothing behind, and announce one that merely changes."""
        safe_name = Identity.sanitize_player(self.player_name)
        if not safe_name:
            raise OptionError(
                f"{self.player_name}: this name has no characters that can be used in a file name. "
                f"Age2 installs campaign files named after your slot, so pick a name that is not "
                r'made up entirely of <>:"/\|?* and dots.')
        if safe_name != self.player_name:
            logger.warning(
                "%s's name contains characters that cannot be used in a file name. Their campaigns "
                "will be installed as \"%s\".", self.player_name, safe_name)

    def create_regions(self) -> None:
        
        
        regions: list[Region] = [Region(self.origin_region_name, self.player, self.multiworld)]
        scenario_regions: dict[Scenarios.Age2ScenarioData, Region] = {}
        
        for campaign in self.pool.campaigns.enabled:
            scenarios = self.pool.scenarios.of(campaign)
            prev_region: Region = regions[0]
            for scenario in scenarios:
                region = self.add_scenario_region(scenario, prev_region)
                regions.append(region)
                scenario_regions[scenario] = region
                prev_region = region
                
        buildings = Region("Can Build", self.player, self.multiworld)
        source = regions[0]
        connection = Entrance(self.player, f"{buildings.name}", source)
        source.exits.append(connection)
        connection.connect(buildings)
        for building in self.pool.buildings.locations:
            buildings.locations.append(
                Location(self.player, building.location_name, building.id, buildings))
        for age in self.pool.ages.locations:
            buildings.locations.append(
                Location(self.player, age.location_name, age.id, buildings))
        regions.append(buildings)
        
        
        building_regions: dict[Buildings.Age2BuildingData, Region] = {}
        for building in Age2BuildingData:
            if not self.pool.buildings.hosts_locations(building):
                continue
            region = Region(building.item.item_name, self.player, self.multiworld)
            connection = Entrance(self.player, f"{region.name}", buildings)
            buildings.exits.append(connection)
            connection.connect(region)
            regions.append(region)
            building_regions[building] = region
            linked_buildings: set[Region] = set()
            for tech in self.pool.techs.by_building(building):
                host = self.pool.techs.host_building(tech)
                if host is building:
                    region.locations.append(
                        Location(self.player, tech.location_name, tech.id, region))
                    continue

                # Its location is in the host's region already; reach it by a ruleless entrance.
                existing_building = building_regions[host]
                if existing_building in linked_buildings:
                    continue
                linked_buildings.add(existing_building)
                alternate = Entrance(
                    self.player,
                    f"{region.name} to {existing_building.name} Techs", region)
                region.exits.append(alternate)
                alternate.connect(existing_building)

        self.unit_regions = UnitRegions(self, building_regions, scenario_regions)
        regions += self.unit_regions.create()

        regions[0].add_event("Victory", Items.Age2ItemData.VICTORY.item_name)

        self.multiworld.regions += regions

    def add_scenario_region(self, scenario: Scenarios.Age2ScenarioData, source: Region) -> Region:
        new_region = Region(scenario.scenario_name, self.player, self.multiworld)
        connection = Entrance(self.player, f"{new_region.name}", source)
        source.exits.append(connection)
        connection.connect(new_region)
        for location in Locations.REGION_TO_LOCATIONS.get(scenario.scenario_name, ()):
            if not self.pool.scenarios.includes_location(location):
                continue
            new_location = Location(self.player, location.global_name(), location.id, new_region)
            new_region.locations.append(new_location)
        if scenario.scenario_name in Locations.VICTORY_SCENARIO_LOCATIONS:
            new_region.add_event("Complete " + scenario.scenario_name,
                                 scenario.scenario_name + ": Unlock Next Scenario",
                                 show_in_spoiler=False)
        return new_region
        
    
    def create_items(self) -> None:
        items: list[Item] = []
        for item in Items.Age2ItemData:
            if isinstance(item.type, Items.Victory):
                continue
            elif isinstance(item.type, (Items.ScenarioItem, Items.Mercenary)):
                if item.type.vanilla_scenario in self.pool.scenarios.included:
                    items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.Campaign):
                if item.type.vanilla_campaign in self.pool.campaigns.enabled:
                    ap_item = self.create_item(item.item_name)
                    if item.type.vanilla_campaign in self.pool.campaigns.starting:
                        self.multiworld.push_precollected(ap_item)
                    else:
                        items.append(ap_item)
            elif isinstance(item.type, Items.ProgressiveScenario):
                if item.type.vanilla_campaign in self.pool.campaigns.enabled:
                    for i in range(item.type.num_additional_scenarios):
                        items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.Resources):
                continue
            elif isinstance(item.type, Items.StartingResources):
                continue
            elif isinstance(item.type, Items.TCResources):
                items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.Age2AgeData):
                age_item = self.create_item(item.item_name)
                if item.type in self.pool.ages.locations:
                    items.append(age_item)
                else:
                    self.multiworld.push_precollected(age_item)
            elif isinstance(item.type, Items.Building):
                continue
            elif isinstance(item.type, Items.Tech):
                continue
            elif isinstance(item.type, Items.UnitLine):
                continue
            elif isinstance(item.type, Items.UnitUpgrade):
                continue
            elif isinstance(item.type, Items.UnitBuilding):
                continue
            elif isinstance(item.type, Items.VillagerProfession):
                continue
            elif isinstance(item.type, Items.Trap):
                continue
            else:
                raise ValueError(f"Item {item} has unknown type {type(item.type)}")

        for building in Age2BuildingData:
            building_item: Item = self.create_item(building.item.item_name)
            if building in self.pool.buildings.locations:
                items.append(building_item)
            else:
                self.multiworld.push_precollected(building_item)

        for tech in self.pool.techs.shuffled:
            items.append(self.create_item(tech.item.item_name))

        for item in self.unit_regions.items():
            items.append(self.create_item(item.item_name))
                

        self.multiworld.itempool += items
        
        itempool = len(items)
        number_of_unfilled_locations = len(self.multiworld.get_unfilled_locations(self.player))
        
        needed_number_of_filler_items = number_of_unfilled_locations - itempool
        
        # Starting resources come first. Traps only ever spend the padding appended once
        # every resource target is already met, so they never cost the player economy.
        plan = self.pool.resources.plan(needed_number_of_filler_items)
        starting_items = [self.create_item(data.item_name) for data in plan.items]
        traps = [self.create_item(data.item_name) for data in plan.traps]

        self.multiworld.itempool += starting_items
        self.multiworld.itempool += traps
        
        itempool = len(items + starting_items + traps)
        
        needed_number_of_filler_items = number_of_unfilled_locations - itempool
        
        self.multiworld.itempool += [self.create_filler() for _ in range(needed_number_of_filler_items)]

    def create_item(self, name: str) -> Item:
        item = Items.NAME_TO_ITEM[name]
        return Item(
            item.item_name,
            self.classification_for(item),
            item.id,
            self.player
        )

    def classification_for(self, item: Items.Age2ItemData) -> ItemClassification:
        if isinstance(item.type, Items.Mercenary) and self.needs_mercenary(item):
            return ItemClassification.progression
        return Items.classification_for(item)

    def needs_mercenary(self, item: Items.Age2ItemData) -> bool:
        if item.type.in_logic:
            return True
        return any(self.pool.units.mercenary_exclusive_location(soldier.unit)
                   for soldier in item.type.units
                   if isinstance(soldier.unit, Units.Age2UnitData))
    
    def get_filler_item_name(self) -> str:
        filler = []
        for item in Items.filler_items:
            filler.append(Items.item_id_to_name[item.id])
        filler_item_name = self.random.choice(filler)
        return filler_item_name
    
    def set_rules(self) -> None:
        self.rules = Rules(self)
        self.rules.set_rules()

    def pre_fill(self) -> None:
        LocalStart.apply(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        mapping: Mapping[str, Any] = {
            WorldVersion.SLOT_DATA_KEY: self.world_version.as_simple_string(),
        }
        for campaign in self.pool.campaigns.enabled:
            mapping[campaign.campaign_name + "_unlocked"] = campaign in self.pool.campaigns.starting
        for option_name in SlotData.OPTIONS.values():
            mapping[option_name] = int(getattr(self.options, option_name).value)
        mapping[ScenarioBranching.internal_name] = int(self.options.scenario_branching.value)
        return mapping


def run_client(*args: Any):
    print("Running Age of Empires II: Definitive Edition Client")
    from .client.ApClient import main  # lazy import

    launch_subprocess(main, name="Age2Client")

icon_paths["age2de_client"] = f"ap:{__name__}/icons/age2de_client.png"

components.append(
    Component(
        "Age of Empires II: DE Client",
        func=run_client,
        component_type=Type.CLIENT,
        icon="age2de_client",
    )
)