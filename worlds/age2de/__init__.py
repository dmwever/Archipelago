# world/age2DE/__init__.py

from worlds.age2de.Generation import Generation
import logging
import settings
from typing import Any, ClassVar
from BaseClasses import Item, MultiWorld
from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, SuffixIdentifier, Type, components, launch as launch_subprocess
from worlds.age2de.Options import Age2Options
from worlds.age2de.items import Items
from worlds.age2de.locations import Locations

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
    location_names = set(location.global_name() for location in Locations.Age2Location)
    item_name_to_id = Items.item_name_to_id
    item_id_to_name = Items.item_id_to_name
    location_name_to_id = Locations.location_name_to_id
    location_id_to_name = Locations.location_id_to_name

    
    def __init__(self, multiworld: 'MultiWorld', player: int) -> None:
        super().__init__(multiworld, player)
        self.generation_info: Generation | None = None

    def generate_early(self) -> None:
        self.generation_info = Generation(self)
        self.generation_info.process_options(self)

    def create_regions(self) -> None:
        assert self.generation_info is not None
        self.generation_info.create_regions(self)
    
    def create_items(self) -> None:
        assert self.generation_info is not None
        self.generation_info.create_items(self)
    
    def create_item(self, name: str) -> Item:
        print(name)
        print(Items.NAME_TO_ITEM[name])
        item = self.generation_info.new_item(Items.NAME_TO_ITEM[name])
        print(item)
        return item
    
    def get_filler_item_name(self) -> str:
        assert self.generation_info is not None
        return self.generation_info.get_filler_name(self)
    
    # def set_rules(self) -> None:
    #     rules.set_rules(self)


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