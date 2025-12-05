# world/age2DE/__init__.py

import logging

from .Generation import Generation
from .Options import Age2Options  # the options we defined earlier
from .items import Items  # data used below to add items to the World
from .locations import Locations  # same as above
from worlds.AutoWorld import World
from BaseClasses import MultiWorld

logger = logging.getLogger(__name__)

AGE2_DE = "Age Of Empires II: Definitive Edition"

class Age2World(World):
    """
    Age of Empires II: Definitive Edition is a Real-Time Strategy game centered around the medieval
    ages and the various battles, conquests, and wars of history.
    """
    game = AGE2_DE  # name of the game/world
    options_dataclass = Age2Options  # options the player can set
    options: Age2Options  # typing hints for option results
    topology_present = True  # show path to required location checks in spoiler

    item_names = set(item.item_name for item in Items.Age2Item)
    location_names = set(location.global_name() for location in Locations.Age2Location)
    item_name_to_id = Items.item_name_to_id
    item_id_to_name = Items.item_id_to_name
    location_name_to_id = Locations.location_name_to_id
    location_id_to_name = Locations.location_id_to_name

    
    def __init__(self, multiworld: 'MultiWorld', player: int) -> None:
        super().__init__(multiworld, player)
        self.generation_info: Generation.Generation | None = None

    # def generate_early(self) -> None:
    #     self.generation_info = generation.Generation()
    #     self.generation_info.process_options(self)

    def create_regions(self) -> None:
        assert self.generation_info is not None
        self.generation_info.create_regions(self)
    
    def create_items(self) -> None:
        assert self.generation_info is not None
        self.generation_info.create_items(self)
    
    # def set_rules(self) -> None:
    #     rules.set_rules(self)
    
    def get_filler_item_name(self) -> str:
        return self.random.choices(tuple(self.filler_items_distribution), weights=self.filler_items_distribution.values())[0]  # type: ignore
    
