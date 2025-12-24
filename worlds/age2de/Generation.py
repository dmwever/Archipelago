import time
from typing import TYPE_CHECKING, Any, Callable, Mapping

from BaseClasses import CollectionState, Entrance, Item, ItemClassification, Location, Region
from worlds.age2de.Options import Age2Options
from worlds.age2de.locations import Campaigns, Locations, Scenarios
from worlds.age2de.items import Items


if TYPE_CHECKING:
    from . import Age2World

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
    def __init__(self, world: 'Age2World') -> None:
        self.player = world.player
        self.regions: list[Region] = []
        self.locations: list[Location] = []
        self.items: list[Item] = []
        self.included_civs: Scenarios.Age2Civ = Scenarios.Age2Civ.NONE
        self.included_campaigns: set[Campaigns.Age2CampaignData] = set()

    def process_options(self, world: 'Age2World') -> None:
        pass


    def create_regions(self, world: 'Age2World') -> None:
        self.regions.append(Region(world.origin_region_name, world.player, world.multiworld))
        # if len(world.options.included_campaigns.value) == 0:
        #     self.included_campaigns = options.IncludedCampaigns.default
        # else:
        self.included_campaigns = frozenset(
            campaign
            for campaign in Campaigns.Age2CampaignData
            # if campaign.civ in world.options.included_campaigns
        )
        for scenario in Scenarios.Age2ScenarioData:
            if scenario.campaign not in self.included_campaigns:
                continue
            new_region = Region(scenario.scenario_name, world.player, world.multiworld)
            connect_region(world, self.regions[-1], new_region)
            for location in REGION_TO_LOCATIONS.get(scenario.scenario_name, ()):
                if not self.branching_option(world, location):
                    continue
                new_location = Location(world.player, location.global_name(), location.id, new_region)
                new_region.locations.append(new_location)
                self.locations.append(new_location)
            self.regions.append(new_region)
            self.included_civs |= scenario.civ
        world.multiworld.regions += self.regions

    def branching_option(self, world, location):
        if location.type == Locations.Age2LocationType.OBJECTIVE_BRANCHING_ALL and world.options.scenarioBranching == Age2Options.ScenarioBranching.option_all:
            return True
        if location.type == Locations.Age2LocationType.OBJECTIVE_BRANCHING_ANY and world.options.scenarioBranching == Age2Options.ScenarioBranching.option_any:
            return True
        return False

    _item_type_to_classification = {
        Items.ScenarioItem: ItemClassification.progression,
        Items.TC: ItemClassification.progression,
        Items.Resources: ItemClassification.filler,
        Items.TriggerActivation: ItemClassification.progression,
    }
    
    def new_item(self, item_type: Items.Age2Item) -> Item:
        return Item(
            item_type.item_name,
            self._item_type_to_classification[item_type.type.__class__],
            item_type.id,
            self.player
        )

    def get_filler_name(self, world: 'Age2World') -> str:
        filler = []
        for item in Items.CATEGORY_TO_ITEMS[Items.Resources]:
            filler.append(Items.item_id_to_name[item.id])
        print(filler)
        filler_item_name = world.random.choice(filler)
        print(filler_item_name)
        return filler_item_name

    def create_items(self, world: 'Age2World') -> None:
        tentative_items: list[Item] = []
        for item_type in Items.Age2Item:
            if isinstance(item_type.type, Items.ScenarioItem):
                if item_type.type.vanilla_scenario.scenario_name in [region.name for region in self.regions]:
                    self.items.append(self.new_item(item_type))
            elif isinstance(item_type.type, Items.Resources):
                tentative_items.append(self.new_item(item_type))
            elif isinstance(item_type.type, Items.TC):
                self.items.append(self.new_item(item_type))
            elif isinstance(item_type.type, Items.TriggerActivation):
                self.items.append(self.new_item(item_type))
            else:
                raise ValueError(f"Item {item_type} has unknown type {type(item_type.type)}")
            
        if len(self.items) < len(self.locations):
            world.random.shuffle(tentative_items)
            print('\n'.join(map(str, tentative_items[len(self.locations) - len(self.items):])))
            self.items.extend(tentative_items[:len(self.locations) - len(self.items)])

        world.multiworld.itempool += self.items
        
        itempool = len(world.multiworld.itempool)
        number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
        
        needed_number_of_filler_items = number_of_unfilled_locations - itempool
        
        print(needed_number_of_filler_items)
        world.multiworld.itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    
    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            "version_public": VERSION_PUBLIC,
            "version_major": VERSION_MAJOR,
            "version_minor": VERSION_MINOR,
            # New ID every ~0.13s; IDs loop once every 8.9 years
            "world_id": ((time.time_ns() >> 17) + self.player) & 0x7fff_ffff,
        }