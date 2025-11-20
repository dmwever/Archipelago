# world/age2DE/__init__.py

import logging
import settings
from typing import Any
from .Options import Age2Options  # the options we defined earlier
from .Items import age2_items  # data used below to add items to the World
from .Locations import age2_locations  # same as above
from worlds.AutoWorld import World
from Launcher import launch
from worlds.LauncherComponents import Component, SuffixIdentifier, Type, components, launch as launch_component, launch_subprocess
from BaseClasses import Region, Location, Item

logger = logging.getLogger(__name__)

AGE2_DE = "Age Of Empires II: Definitive Edition"

class Age2Item(Item):  # or from Items import MyGameItem
    game = AGE2_DE  # name of the game/world this item is from


class Age2Location(Location):  # or from Locations import MyGameLocation
    game = AGE2_DE  # name of the game/world this location is in

class Age2World(World):
    """
    Age of Empires II: Definitive Edition is a Real-Time Strategy game centered around the medieval
    ages and the various battles, conquests, and wars of history.
    """
    game = AGE2_DE  # name of the game/world
    options_dataclass = Age2Options  # options the player can set
    options: Age2Options  # typing hints for option results
    topology_present = True  # show path to required location checks in spoiler

    # ID of first item and location, could be hard-coded but code may be easier
    # to read with this as a property.
    base_id = 1234
    # instead of dynamic numbering, IDs could be part of data

    # The following two dicts are required for the generation to know which
    # items exist. They could be generated from json or something else. They can
    # include events, but don't have to since events will be placed manually.
    item_name_to_id = {name: id for
                       id, name in enumerate(age2_items, base_id)}
    location_name_to_id = {name: id for
                           id, name in enumerate(age2_locations, base_id)}

    # Items can be grouped using their names to allow easy checking if any item
    # from that group has been collected. Group names can also be used for !hint
    item_name_groups = {
        "weapons": {"sword", "lance"},
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
        file_identifier=SuffixIdentifier(".apcivvi"),
    )
)