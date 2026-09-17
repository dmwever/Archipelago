# world/age2DE/__init__.py

from math import ceil
import logging
from Options import OptionError
from rule_builder.cached_world import CachedRuleBuilderWorld
import settings
from typing import Any, ClassVar, Mapping
from BaseClasses import Entrance, Item, Location, MultiWorld, Region
from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, Type, components, launch as launch_subprocess
from worlds.age2de.locations import Buildings
from worlds.age2de.locations.connections import LocationMapping
from worlds.age2de.logic.goal_logic import CAMPAIGN_TO_SCENARIOS, Age2BuildingData
from .generation import Identity, LocalStart, WorldVersion
from .Options import Goal, Age2Options, ScenarioBranching
from .items import Items
from .locations import Campaigns, Locations, Scenarios
from .locations.connections import CivilizationBuildings
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
    
    # Per slot, not per class. As class attributes these accumulated across slots and
    # kept the MultiWorld alive, which WorldTestBase reports as a leak.
    included_civs: list[Scenarios.Age2CivData]
    included_campaigns: list[Campaigns.Age2CampaignData]
    starting_campaigns: list[Campaigns.Age2CampaignData]
    shuffled_buildings: list[Buildings.Age2BuildingData]
    rules: Rules

    def __init__(self, multiworld: 'MultiWorld', player: int) -> None:
        super().__init__(multiworld, player)
        self.included_civs = []
        self.included_campaigns = []
        self.starting_campaigns = []
        self.shuffled_buildings = []

    def branching_option(self, location):
        if location.type == Locations.Age2LocationType.OBJECTIVE_BRANCHING_ALL and self.options.scenarioBranching != ScenarioBranching.option_all:
            return False
        if location.type == Locations.Age2LocationType.OBJECTIVE_BRANCHING_ANY and self.options.scenarioBranching != ScenarioBranching.option_any:
            return False
        return True

    def generate_early(self) -> None:
        self.included_campaigns = [campaign for campaign in Campaigns.Age2CampaignData
                                   if campaign.campaign_name in self.options.enabled_campaigns]
        self.starting_campaigns = [campaign for campaign in self.included_campaigns
                                   if campaign.campaign_name in self.options.starting_campaigns]
        if not self.options.enabled_campaigns.value:
            raise OptionError(f"{self.player_name}: enabled_campaigns needs at least one campaign.")
        if not self.options.starting_campaigns.value:
            raise OptionError(f"{self.player_name}: starting_campaigns needs at least one campaign.")
        if not self.starting_campaigns:
            raise OptionError(f"{self.player_name}: starting_campaigns must include at least one "
                              f"enabled campaign. Enabled: {sorted(self.options.enabled_campaigns.value)}.")
        self.check_installable_name()

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
        
        for campaign in self.included_campaigns:
            scenarios = CAMPAIGN_TO_SCENARIOS[campaign]
            if not scenarios:
                raise OptionError(f"{self.player_name}: {campaign.campaign_name} has no scenarios.")
            prev_region: Region = regions[0]
            for scenario in scenarios:
                region = self.add_scenario_region(scenario, prev_region)
                regions.append(region)
                if scenario.civ not in self.included_civs:
                    self.included_civs.append(scenario.civ)
                prev_region = region
                
        buildings = Region("Can Build", self.player, self.multiworld)
        source = regions[0]
        connection = Entrance(self.player, f"{buildings.name}", source)
        source.exits.append(connection)
        connection.connect(buildings)
        for building in Buildings.Age2BuildingData:
            if all(building in civ.excluded_buildings for civ in self.included_civs):
                continue # No included civs have this non-unique building.
            if Buildings.BuildingOption.unique in building.building_options and Buildings.BuildingOption.unique not in self.options.shuffle_buildings:
                continue # We skip unique altogether, else we sort by other building type.
            if Buildings.BuildingOption.unique in building.building_options and not any(building in civ.included_buildings for civ in self.included_civs): 
                continue # No civs with this unique building are included.
            if any(option in building.building_options for option in 
                   [options for options in self.options.shuffle_buildings if not Buildings.BuildingOption.unique in options]):
                new_location = Location(self.player, building.location_name, building.id, buildings)
                buildings.locations.append(new_location)
                self.shuffled_buildings.append(building)
        regions.append(buildings)
        
        self.multiworld.regions += regions
    
    def add_scenario_region(self, scenario: Scenarios.Age2ScenarioData, source: Region) -> Region:
        new_region = Region(scenario.scenario_name, self.player, self.multiworld)
        connection = Entrance(self.player, f"{new_region.name}", source)
        source.exits.append(connection)
        connection.connect(new_region)
        for location in Locations.REGION_TO_LOCATIONS.get(scenario.scenario_name, ()):
            if not self.branching_option(location):
                continue
            new_location = Location(self.player, location.global_name(), location.id, new_region)
            new_region.locations.append(new_location)
        return new_region
        
    
    def create_items(self) -> None:
        items: list[Item] = []
        region_names = {region.name for region in self.multiworld.get_regions(self.player)}
        for item in Items.Age2ItemData:
            if isinstance(item.type, Items.Victory):
                continue
            elif isinstance(item.type, Items.ScenarioItem):
                if item.type.vanilla_scenario.scenario_name in region_names:
                    items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.Mercenary):
                if item.type.vanilla_scenario.scenario_name in region_names:
                    items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.Campaign):
                if item.type.vanilla_campaign in self.included_campaigns:
                    ap_item = self.create_item(item.item_name)
                    if item.type.vanilla_campaign.campaign_name in self.options.starting_campaigns:
                        self.multiworld.push_precollected(ap_item)
                    else:
                        items.append(ap_item)
            elif isinstance(item.type, Items.ProgressiveScenario):
                if item.type.vanilla_campaign in self.included_campaigns:
                    for i in range(item.type.num_additional_scenarios):
                        items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.Resources):
                continue
            elif isinstance(item.type, Items.StartingResources):
                continue
            elif isinstance(item.type, Items.TCResources):
                items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.Age):
                continue
            elif isinstance(item.type, Items.Building):
                continue
            else:
                raise ValueError(f"Item {item} has unknown type {type(item.type)}")

        for building in Age2BuildingData:
            building_item: Item = self.create_item(building.item.item_name)
            if building in self.shuffled_buildings:
                items.append(building_item)
            else:
                self.multiworld.push_precollected(building_item)
                

        self.multiworld.itempool += items
        
        itempool = len(items)
        number_of_unfilled_locations = len(self.multiworld.get_unfilled_locations(self.player))
        
        needed_number_of_filler_items = number_of_unfilled_locations - itempool
        
        starting_items = self.smart_add_starting_resources(needed_number_of_filler_items)
        self.multiworld.itempool += starting_items
        
        itempool = len(items + starting_items)
        
        needed_number_of_filler_items = number_of_unfilled_locations - itempool
        
        self.multiworld.itempool += [self.create_filler() for _ in range(needed_number_of_filler_items)]
        
    
    def smart_add_starting_resources(self, locations_to_fill: int) -> list[Item]:
        items: list[Item] = []
        if locations_to_fill <= 0:
            return items

        largest = {
            Items.Resource.WOOD: Items.Age2ItemData.STARTING_WOOD_LARGE,
            Items.Resource.FOOD: Items.Age2ItemData.STARTING_FOOD_LARGE,
            Items.Resource.GOLD: Items.Age2ItemData.STARTING_GOLD_LARGE,
            Items.Resource.STONE: Items.Age2ItemData.STARTING_STONE_LARGE,
        }
        amounts = {
            Items.Resource.WOOD: 1000,
            Items.Resource.FOOD: 1000,
            Items.Resource.GOLD: 750,
            Items.Resource.STONE: 500,
        }
        starting_resource_choices = Items.CATEGORY_TO_ITEMS[Items.StartingResources]

        while locations_to_fill > 0:
            worst_case = {resource: ceil(amounts[resource] / largest[resource].type.amount)
                          for resource in amounts}
            worst_case_sum = sum(worst_case.values())

            if worst_case_sum > locations_to_fill:
                amounts = {resource: amount // 2 for resource, amount in amounts.items()}
                continue

            if worst_case_sum == locations_to_fill:
                for resource, needed in worst_case.items():
                    for _ in range(needed):
                        items.append(self.create_item(largest[resource].item_name))
                        locations_to_fill -= 1
                return items

            item_data = self.random.choice(starting_resource_choices)
            resource = item_data.type.type
            amounts[resource] = max(0, amounts[resource] - item_data.type.amount)
            items.append(self.create_item(item_data.item_name))
            locations_to_fill -= 1
        return items
    
    def create_item(self, name: str) -> Item:
        item = Items.NAME_TO_ITEM[name]
        return Item(
            item.item_name,
            Items.item_type_to_classification[item.type_data],
            item.id,
            self.player
        )
    
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
        for campaign in self.included_campaigns:
            mapping[campaign.campaign_name + "_unlocked"] = campaign.campaign_name in self.options.starting_campaigns
        return mapping


def run_client(*args: Any):
    print("Running Age of Empires II: Definitive Edition Client")
    from .client.ApClient import main  # lazy import

    launch_subprocess(main, name="Age2Client")

components.append(
    Component(
        "Age of Empires II: DE Client",
        func=run_client,
        component_type=Type.CLIENT,
    )
)