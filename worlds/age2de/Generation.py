import time
from typing import Any, Callable, Mapping

from BaseClasses import CollectionState, Entrance, Item, ItemClassification, Location, Region
from worlds.age2de.World import Age2World
from worlds.age2de.locations import Campaigns, Locations, Scenarios
from worlds.age2de.items import Items

VERSION_PUBLIC = 0
VERSION_MAJOR = 0
VERSION_MINOR = 1

REGION_TO_LOCATIONS: dict[str, list[Locations.Age2Location]] = {}
for location in Locations.Age2Location:
    REGION_TO_LOCATIONS.setdefault(location.scenario.scenario_name, []).append(location)


def connect_region(
    world: 'Age2World', source: Region, target: Region, rule: Callable[[CollectionState], bool] | None = None
) -> None:
    connection = Entrance(world.player, f"{source.name} -> {target.name}", source)
    if rule:
        connection.access_rule = rule
    source.exits.append(connection)
    connection.connect(target)
    
class Generation:
    def __init__(self) -> None:
        self.regions: list[Region] = []
        self.locations: list[Location] = []
        self.items: list[Item] = []
        self.included_civs: Scenarios.Age2Civ = Scenarios.Age2Civ.NONE
        self.included_campaigns: set[Campaigns.Age2CampaignData] = set()

    def process_options(self, world: 'Age2World') -> None:
        self._options_randomize_empty_hero_names(world)


    def create_regions(self, world: 'Age2World') -> None:
        self.regions.append(Region(world.origin_region_name, world.player, world.multiworld))
        # if len(world.options.included_campaigns.value) == 0:
        #     self.included_campaigns = options.IncludedCampaigns.default
        # else:
        self.included_campaigns = frozenset(
            campaign
            for campaign in Campaigns.Age2CampaignData
            if campaign.title_faction in world.options.included_campaigns
        )
        for scenario in Scenarios.Age2ScenarioData:
            if scenario.campaign not in self.included_campaigns:
                continue
            new_region = Region(scenario.scenario_name, world.player, world.multiworld)
            connect_region(world, self.regions[-1], new_region)
            for location in REGION_TO_LOCATIONS.get(scenario.scenario_name, ()):
                new_location = Location(world.player, location.global_name(), location.id, new_region)
                new_region.locations.append(new_location)
                self.locations.append(new_location)
            self.regions.append(new_region)
            self.included_civs |= scenario.civ
        world.multiworld.regions += self.regions

    def create_items(self, world: 'Age2World') -> None:
        for item_type in Items.Age2Item:
            if isinstance(item_type.type, Items.ScenarioItem):
                if item_type.type.vanilla_scenario.scenario_name in [region.name for region in self.regions]:
                    self.items.append(Item(item_type.item_name, ItemClassification.progression, item_type.id, world.player))
            elif isinstance(item_type.type, Items.Resources):
                self.items.append(Item(item_type.item_name, ItemClassification.filler, item_type.id, world.player))
            else:
                raise ValueError(f"Item {item_type} has unknown type {type(item_type.type)}")

        world.multiworld.itempool += self.items

    
    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            "version_public": VERSION_PUBLIC,
            "version_major": VERSION_MAJOR,
            "version_minor": VERSION_MINOR,
            # New ID every ~0.13s; IDs loop once every 8.9 years
            "world_id": ((time.time_ns() >> 17) + self.player) & 0x7fff_ffff,
        }