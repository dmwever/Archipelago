# world/age2DE/__init__.py

from math import ceil
import time
import logging
from Options import OptionError
from rule_builder.cached_world import CachedRuleBuilderWorld
import settings
from typing import Any, ClassVar, Mapping
from BaseClasses import Entrance, Item, Location, MultiWorld, Region
from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, Type, components, launch as launch_subprocess
from worlds.age2de.locations import Buildings
from worlds.age2de.logic.goal_logic import CAMPAIGN_TO_SCENARIOS, Age2BuildingData
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
    location_names = set(location.global_name() for location in Locations.Age2ScenarioLocationData)
    item_name_to_id = Items.item_name_to_id
    item_id_to_name = Items.item_id_to_name
    location_name_to_id = Locations.location_name_to_id
    location_id_to_name = Locations.location_id_to_name
    item_mapping = Items.item_mapping
    
    included_civs: list[Scenarios.Age2CivData] = []
    included_campaigns: set[Campaigns.Age2CampaignData] = set()
    shuffled_buildings: list[Buildings.Age2BuildingData] = []
    rules: Rules
    
    def __init__(self, multiworld: 'MultiWorld', player: int) -> None:
        super().__init__(multiworld, player)
        
    def branching_option(self, location):
        if location.type == Locations.Age2LocationType.OBJECTIVE_BRANCHING_ALL and self.options.scenarioBranching != ScenarioBranching.option_all:
            return False
        if location.type == Locations.Age2LocationType.OBJECTIVE_BRANCHING_ANY and self.options.scenarioBranching != ScenarioBranching.option_any:
            return False
        return True

    def create_regions(self) -> None:
        if len(self.options.enabled_campaigns.value) == 0:
            self.included_campaigns = self.options.enabled_campaigns.default
        else:
            campaign_names = self.options.enabled_campaigns
            self.included_campaigns = {campaign for campaign in Campaigns.Age2CampaignData if campaign.campaign_name in campaign_names}
        
        regions: list[Region] = [Region(self.origin_region_name, self.player, self.multiworld)]
        
        for campaign in self.included_campaigns:
            scenarios = iter(CAMPAIGN_TO_SCENARIOS[campaign])
            prev_region: Region = None
            try:
                first_scn = next(scenarios)
                region = self.add_scenario_region(first_scn, regions[0])
                regions.append(region)
                prev_region = region
            except StopIteration:
                raise OptionError(f"Could not iterate {first_scn.scenario_name} region from {campaign.campaign_name}")
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
                continue # No included civs have this building
            if Buildings.BuildingOption.unique in building.building_options and Buildings.BuildingOption.unique not in self.options.shuffle_buildings:
                continue # We skip unique altogether, else we sort by other building type.
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
        for item in Items.Age2ItemData:
            if isinstance(item.type, Items.Victory):
                continue
            elif isinstance(item.type, Items.ScenarioItem):
                if item.type.vanilla_scenario.scenario_name in [region.name for region in self.multiworld.regions]:
                    items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.Mercenary):
                if item.type.vanilla_scenario.scenario_name in [region.name for region in self.multiworld.regions]:
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
        
        print(needed_number_of_filler_items)
        self.multiworld.itempool += [self.create_filler() for _ in range(needed_number_of_filler_items)]
        
        for campaign in Campaigns.Age2CampaignData:
            if campaign.campaign_name in self.options.starting_campaigns:
                self.add_early_campaign_items(campaign)
        
    
    def add_early_campaign_items(self, campaign: Campaigns.Age2CampaignData):
        if campaign == Campaigns.Age2CampaignData.JOAN:
            choice: str = self.random.choice([Items.Age2ItemData.AP_JOAN_1_CROSSBOWMEN.item_name, Items.Age2ItemData.AP_JOAN_1_SWORDSMEN.item_name])
            self.multiworld.early_items[self.player][choice] = 1
            self.multiworld.early_items[self.player][Items.Age2ItemData.AP_JOAN_1_RAM.item_name] = 1
    
    def smart_add_starting_resources(self, locations_to_fill: int):
        items: list[Item] = []
        if locations_to_fill == 0:
            return []
        wood_amount: int = 1000
        food_amount: int = 1000
        gold_amount: int = 750
        stone_amount: int = 500
        starting_resource_choices = Items.CATEGORY_TO_ITEMS[Items.StartingResources]
        while locations_to_fill > 0:
            worst_case_wood_needed: int = ceil(wood_amount / Items.Age2ItemData.STARTING_WOOD_LARGE.type.amount)
            worst_case_food_needed: int = ceil(food_amount / Items.Age2ItemData.STARTING_FOOD_LARGE.type.amount)
            worst_case_gold_needed: int = ceil(gold_amount / Items.Age2ItemData.STARTING_GOLD_LARGE.type.amount)
            worst_case_stone_needed: int = ceil(stone_amount / Items.Age2ItemData.STARTING_STONE_LARGE.type.amount)
            worst_case_sum = worst_case_wood_needed + worst_case_food_needed + worst_case_gold_needed + worst_case_stone_needed
            if worst_case_sum > locations_to_fill:
                wood_amount = wood_amount / 2
                food_amount = food_amount / 2
                gold_amount= gold_amount / 2
                stone_amount = stone_amount / 2
                continue
            if worst_case_sum == locations_to_fill:
                for _ in range(worst_case_wood_needed):
                    self.create_item(Items.Age2ItemData.STARTING_WOOD_LARGE.item_name)
                for _ in range(worst_case_food_needed):
                    self.create_item(Items.Age2ItemData.STARTING_FOOD_LARGE.item_name)
                for _ in range(worst_case_gold_needed):
                    self.create_item(Items.Age2ItemData.STARTING_GOLD_LARGE.item_name)
                for _ in range(worst_case_stone_needed):
                    self.create_item(Items.Age2ItemData.STARTING_STONE_LARGE.item_name)
                return items
            item_data = self.random.choice(starting_resource_choices)
            if item_data.type.type == Items.Resource.WOOD:
                wood_amount -= item_data.type.amount
                if wood_amount < 0:
                    wood_amount = 0
            if item_data.type.type == Items.Resource.GOLD:
                gold_amount -= item_data.type.amount
                if gold_amount < 0:
                    gold_amount = 0
            if item_data.type.type == Items.Resource.FOOD:
                food_amount -= item_data.type.amount
                if food_amount < 0:
                    food_amount = 0
            if item_data.type.type == Items.Resource.STONE:
                stone_amount -= item_data.type.amount
                if stone_amount < 0:
                    stone_amount = 0
                
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

    def fill_slot_data(self) -> Mapping[str, Any]:
        mapping: Mapping[str, Any] = {
            "version_public": 0,
            "version_major": 2,
            "version_minor": 0,
            "world_id": ((time.time_ns() >> 17) + self.player) & 0x7fff_ffff,
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