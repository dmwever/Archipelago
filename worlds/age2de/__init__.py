# world/age2DE/__init__.py

import time
import logging
import settings
from typing import Any, ClassVar, Mapping
from BaseClasses import Entrance, Item, Location, MultiWorld, Region
from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, Type, components, launch as launch_subprocess
from .Options import Age2Options, ScenarioBranching
from .items import Items
from .locations import Campaigns, Locations, Scenarios
from .rules import Rules

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
        
class Age2World(World):
    """
    Age of Empires II: Definitive Edition is a Real-Time Strategy game centered around the medieval
    ages and the various battles, conquests, and wars of history.
    """
    game = AGE2_DE  # name of the game/world
    settings: ClassVar[Age2Settings]
    options_dataclass = Age2Options  # options the player can set
    options: Age2Options  # typing hints for option results
    topology_present = True  # show path to required location checks in spoiler

    item_names = set(item.item_name for item in Items.Age2Item)
    location_names = set(location.global_name() for location in Locations.Age2LocationData)
    item_name_to_id = Items.item_name_to_id
    item_id_to_name = Items.item_id_to_name
    location_name_to_id = Locations.location_name_to_id
    location_id_to_name = Locations.location_id_to_name
    
    included_civs: Scenarios.Age2Civ = Scenarios.Age2Civ.NONE
    included_campaigns: set[Campaigns.Age2CampaignData] = set()

    
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
        regions = [Region(self.origin_region_name, self.player, self.multiworld)]
        for scenario in Scenarios.Age2ScenarioData:
            if scenario.campaign not in self.included_campaigns:
                continue
            new_region = Region(scenario.scenario_name, self.player, self.multiworld)
            source = regions[-1]
            connection = Entrance(self.player, f"{new_region.name}", source)
            source.exits.append(connection)
            connection.connect(new_region)
            for location in Locations.REGION_TO_LOCATIONS.get(scenario.scenario_name, ()):
                if not self.branching_option(location):
                    continue
                new_location = Location(self.player, location.global_name(), location.id, new_region)
                new_region.locations.append(new_location)
            regions.append(new_region)
            self.included_civs |= scenario.civ
        self.multiworld.regions += regions
    
    def create_items(self) -> None:
        items: list[Item] = []
        tentative_items: list[Item] = []
        for item in Items.Age2Item:
            if isinstance(item.type, Items.ScenarioItem):
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
                tentative_items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.StartingResources):
                tentative_items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.TCResources):
                items.append(self.create_item(item.item_name))
            elif isinstance(item.type, Items.TriggerActivation):
                items.append(self.create_item(item.item_name))
            else:
                raise ValueError(f"Item {item} has unknown type {type(item.type)}")

        self.multiworld.itempool += items
        
        itempool = len(items)
        number_of_unfilled_locations = len(self.multiworld.get_unfilled_locations(self.player))
        
        needed_number_of_filler_items = number_of_unfilled_locations - itempool
        
        print(needed_number_of_filler_items)
        self.multiworld.itempool += [self.create_filler() for _ in range(needed_number_of_filler_items)]
    
    def create_item(self, name: str) -> Item:
        print(name)
        print(Items.NAME_TO_ITEM[name])
        item = Items.NAME_TO_ITEM[name]
        return Item(
            item.item_name,
            Items.item_type_to_classification[item.type.__class__],
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
        Rules.set_rules(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            "version_public": 0,
            "version_major": 0,
            "version_minor": 1,
            # New ID every ~0.13s; IDs loop once every 8.9 years
            "world_id": ((time.time_ns() >> 17) + self.player) & 0x7fff_ffff,
        }


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