from dataclasses import dataclass, field
from enum import IntFlag
from typing import Iterable, Dict, Protocol, Optional, List

from BaseClasses import Region, Entrance
from .options import StardewOptions


class RegionFactory(Protocol):
    def __call__(self, name: str, regions: Iterable[str]) -> Region:
        raise NotImplementedError


class RandomizationFlag(IntFlag):
    NOT_RANDOMIZED = 0b0
    PELICAN_TOWN = 0b11111
    NON_PROGRESSION = 0b11110
    BUILDINGS = 0b11100
    EVERYTHING = 0b11000
    CHAOS = 0b10000


@dataclass(frozen=True)
class RegionData:
    name: str
    exits: List[str] = field(default_factory=list)
    flag: RandomizationFlag = RandomizationFlag.NOT_RANDOMIZED


@dataclass(frozen=True)
class ConnectionData:
    name: str
    destination: str
    reverse: Optional[str] = None
    flag: RandomizationFlag = RandomizationFlag.NOT_RANDOMIZED


stardew_valley_regions = [
    RegionData("Menu", ["To Stardew Valley"]),
    RegionData("Stardew Valley", ["To Farmhouse"]),
    RegionData("Farmhouse", ["Outside To Farm", "Downstairs To Cellar"]),
    RegionData("Cellar", []),
    RegionData("Farm", ["Farm To Backwoods", "Farm To Bus Stop", "Farm To Forest", "Enter Farmcave", "Enter Greenhouse",
                        "Use Desert Obelisk", "Use Island Obelisk"]),
    RegionData("Backwoods", ["Backwoods To Mountain"]),
    RegionData("Bus Stop", ["Bus Stop To Town", "Take Bus To Desert", "Bus Stop To Tunnel Entrance"]),
    RegionData("Forest", ["Forest To Town", "Enter Secret Woods", "Enter Wizard Tower", "Enter Marnie's Ranch",
                          "Enter Leah's Cottage", "Forest To Sewers"]),
    RegionData("Farmcave", []),
    RegionData("Greenhouse", []),
    RegionData("Mountain", ["Mountain to Railroad", "Enter Tent", "Enter Carpenter Shop", "Enter The Mines",
                            "Enter Quarry", "Enter Adventurer's Guild", "Mountain To Town"]),
    RegionData("Tunnel Entrance", ["Enter Tunnel"]),
    RegionData("Tunnel", []),
    RegionData("Town", ["Enter Community Center", "Town To Beach", "Enter Hospital",
                        "Enter Pierre's General Store", "Enter Saloon", "Enter Josh's House", "Enter Mayor's Manor",
                        "Enter Sam's House", "Enter Haley's House", "Town To Sewers", "Enter Clint's Blacksmith", "Enter Museum",
                        "Enter JojaMart"]),
    RegionData("Beach", ["Enter Willy's Fish Shop", "Enter Elliott's House", "Enter Tide Pools"]),
    RegionData("Railroad", ["Enter Bathhouse Entrance", "Enter Witch Warp Cave"]),  # "Enter Perfection Cutscene Area"
    RegionData("Marnie's Ranch", []),
    RegionData("Leah's Cottage", []),
    RegionData("Sewers", ["Enter Mutant Bug Lair"]),
    RegionData("Mutant Bug Lair", []),
    RegionData("Wizard Tower", ["Enter Wizard Basement"]),
    RegionData("Wizard Basement", []),
    RegionData("Tent", []),
    RegionData("Carpenter Shop", ["Enter Sebastian's Room"]),
    RegionData("Sebastian's Room", []),
    RegionData("Adventurer's Guild", []),
    RegionData("Community Center",
               ["Access Crafts Room", "Access Pantry", "Access Fish Tank", "Access Boiler Room", "Access Bulletin Board",
                "Access Vault"]),
    RegionData("Crafts Room", []),
    RegionData("Pantry", []),
    RegionData("Fish Tank", []),
    RegionData("Boiler Room", []),
    RegionData("Bulletin Board", []),
    RegionData("Vault", []),
    RegionData("Hospital", ["Enter Harvey's Room"]),
    RegionData("Harvey's Room", []),
    RegionData("Pierre's General Store", ["Enter Sunroom"]),
    RegionData("Sunroom", []),
    RegionData("Saloon", ["Play Journey of the Prairie King", "Play Junimo Kart"]),
    RegionData("Josh's House", []),
    RegionData("Mayor's Manor", []),
    RegionData("Sam's House", []),
    RegionData("Haley's House", []),
    RegionData("Clint's Blacksmith", []),
    RegionData("Museum", []),
    RegionData("JojaMart", []),
    RegionData("Willy's Fish Shop", []),
    RegionData("Elliott's House", []),
    RegionData("Tide Pools", []),
    RegionData("Bathhouse Entrance", ["Enter Locker Room"]),
    RegionData("Locker Room", ["Enter Public Bath"]),
    RegionData("Public Bath", []),
    RegionData("Witch Warp Cave", ["Enter Witch's Swamp"]),
    RegionData("Witch's Swamp", []),
    RegionData("Quarry", ["Enter Quarry Mine Entrance"]),
    RegionData("Quarry Mine Entrance", ["Enter Quarry Mine"]),
    RegionData("Quarry Mine", []),
    RegionData("Secret Woods", []),
    RegionData("The Desert", ["Enter Skull Cavern Entrance"]),
    RegionData("Skull Cavern Entrance", ["Enter Skull Cavern"]),
    RegionData("Skull Cavern", []),
    RegionData("Ginger Island", []),
    RegionData("JotPK World 1", ["Reach JotPK World 2"]),
    RegionData("JotPK World 2", ["Reach JotPK World 3"]),
    RegionData("JotPK World 3", []),
    RegionData("Junimo Kart 1", ["Reach Junimo Kart 2"]),
    RegionData("Junimo Kart 2", ["Reach Junimo Kart 3"]),
    RegionData("Junimo Kart 3", []),
    RegionData("The Mines", ["Dig to The Mines - Floor 5", "Dig to The Mines - Floor 10", "Dig to The Mines - Floor 15",
                             "Dig to The Mines - Floor 20", "Dig to The Mines - Floor 25", "Dig to The Mines - Floor 30",
                             "Dig to The Mines - Floor 35", "Dig to The Mines - Floor 40", "Dig to The Mines - Floor 45",
                             "Dig to The Mines - Floor 50", "Dig to The Mines - Floor 55", "Dig to The Mines - Floor 60",
                             "Dig to The Mines - Floor 65", "Dig to The Mines - Floor 70", "Dig to The Mines - Floor 75",
                             "Dig to The Mines - Floor 80", "Dig to The Mines - Floor 85", "Dig to The Mines - Floor 90",
                             "Dig to The Mines - Floor 95", "Dig to The Mines - Floor 100", "Dig to The Mines - Floor 105",
                             "Dig to The Mines - Floor 110", "Dig to The Mines - Floor 115", "Dig to The Mines - Floor 120"]),
    RegionData("The Mines - Floor 5", []),
    RegionData("The Mines - Floor 10", []),
    RegionData("The Mines - Floor 15", []),
    RegionData("The Mines - Floor 20", []),
    RegionData("The Mines - Floor 25", []),
    RegionData("The Mines - Floor 30", []),
    RegionData("The Mines - Floor 35", []),
    RegionData("The Mines - Floor 40", []),
    RegionData("The Mines - Floor 45", []),
    RegionData("The Mines - Floor 50", []),
    RegionData("The Mines - Floor 55", []),
    RegionData("The Mines - Floor 60", []),
    RegionData("The Mines - Floor 65", []),
    RegionData("The Mines - Floor 70", []),
    RegionData("The Mines - Floor 75", []),
    RegionData("The Mines - Floor 80", []),
    RegionData("The Mines - Floor 85", []),
    RegionData("The Mines - Floor 90", []),
    RegionData("The Mines - Floor 95", []),
    RegionData("The Mines - Floor 100", []),
    RegionData("The Mines - Floor 105", []),
    RegionData("The Mines - Floor 110", []),
    RegionData("The Mines - Floor 115", []),
    RegionData("The Mines - Floor 120", []),
]

# Exists and where they lead
mandatory_connections = [
    ConnectionData("To Stardew Valley", "Stardew Valley"),
    ConnectionData("To Farmhouse", "Farmhouse"),
    ConnectionData("Outside To Farm", "Farm"),
    ConnectionData("Downstairs To Cellar", "Cellar"),
    ConnectionData("Farm To Backwoods", "Backwoods"),
    ConnectionData("Farm To Bus Stop", "Bus Stop"),
    ConnectionData("Farm To Forest", "Forest"),
    ConnectionData("Enter Farmcave", "Farmcave"),
    ConnectionData("Enter Greenhouse", "Greenhouse"),
    ConnectionData("Use Desert Obelisk", "The Desert"),
    ConnectionData("Use Island Obelisk", "Ginger Island"),
    ConnectionData("Backwoods To Mountain", "Mountain"),
    ConnectionData("Bus Stop To Town", "Town"),
    ConnectionData("Bus Stop To Tunnel Entrance", "Tunnel Entrance"),
    ConnectionData("Take Bus To Desert", "The Desert"),
    ConnectionData("Enter Tunnel", "Tunnel"),
    ConnectionData("Forest To Town", "Town"),
    ConnectionData("Enter Wizard Tower", "Wizard Tower"),
    ConnectionData("Enter Wizard Basement", "Wizard Basement"),
    ConnectionData("Enter Marnie's Ranch", "Marnie's Ranch"),
    ConnectionData("Enter Leah's Cottage", "Leah's Cottage"),
    ConnectionData("Enter Secret Woods", "Secret Woods"),
    ConnectionData("Forest To Sewers", "Sewers"),
    ConnectionData("Town To Sewers", "Sewers"),
    ConnectionData("Enter Mutant Bug Lair", "Mutant Bug Lair"),
    ConnectionData("Mountain to Railroad", "Railroad"),
    ConnectionData("Enter Tent", "Tent"),
    ConnectionData("Enter Carpenter Shop", "Carpenter Shop"),
    ConnectionData("Enter Sebastian's Room", "Sebastian's Room"),
    ConnectionData("Enter Adventurer's Guild", "Adventurer's Guild"),
    ConnectionData("Enter Quarry", "Quarry"),
    ConnectionData("Enter Quarry Mine Entrance", "Quarry Mine Entrance"),
    ConnectionData("Enter Quarry Mine", "Quarry Mine"),
    ConnectionData("Mountain To Town", "Town"),
    ConnectionData("Enter Community Center", "Community Center"),
    # ConnectionData("Exit Community Center", "Town", reverse="Enter Community Center", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Access Crafts Room", "Crafts Room"),
    ConnectionData("Access Pantry", "Pantry"),
    ConnectionData("Access Fish Tank", "Fish Tank"),
    ConnectionData("Access Boiler Room", "Boiler Room"),
    ConnectionData("Access Bulletin Board", "Bulletin Board"),
    ConnectionData("Access Vault", "Vault"),
    ConnectionData("Enter Hospital", "Hospital"),
    # ConnectionData("Exit Hospital", "Town", reverse="Enter Hospital", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Enter Harvey's Room", "Harvey's Room"),
    ConnectionData("Enter Pierre's General Store", "Pierre's General Store"),
    # ConnectionData("Exit Pierre's General Store", "Town", reverse="Enter Pierre's General Story", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Enter Sunroom", "Sunroom"),
    ConnectionData("Enter Clint's Blacksmith", "Clint's Blacksmith"),
    # ConnectionData("Exit Clint's Blacksmith", "Town", reverse="Enter Clint's Blacksmith", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Enter Saloon", "Saloon"),
    # ConnectionData("Exit Saloon", "Town", reverse="Enter Saloon", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Play Journey of the Prairie King", "JotPK World 1"),
    ConnectionData("Reach JotPK World 2", "JotPK World 2"),
    ConnectionData("Reach JotPK World 3", "JotPK World 3"),
    ConnectionData("Play Junimo Kart", "Junimo Kart 1"),
    ConnectionData("Reach Junimo Kart 2", "Junimo Kart 2"),
    ConnectionData("Reach Junimo Kart 3", "Junimo Kart 3"),
    ConnectionData("Enter Sam's House", "Sam's House"),
    # ConnectionData("Exit Sam's House", "Town", reverse="Enter Sam's House", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Enter Haley's House", "Haley's House"),
    # ConnectionData("Exit Haley's House", "Town", reverse="Enter Haley's House", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Enter Mayor's Manor", "Mayor's Manor"),
    # ConnectionData("Exit Mayor's Manor", "Town", reverse="Enter Mayor's Manor", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Enter Josh's House", "Josh's House"),
    # ConnectionData("Exit Josh's House", "Town", reverse="Enter Josh's House", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Enter Museum", "Museum"),
    # ConnectionData("Exit Museum", "Town", reverse="Enter Museum", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Enter JojaMart", "JojaMart"),
    # ConnectionData("Exit JojaMart", "Town", reverse="Enter JojaMart", flag=RandomizationFlag.PELICAN_TOWN),
    ConnectionData("Town To Beach", "Beach"),
    ConnectionData("Enter Elliott's House", "Elliott's House"),
    ConnectionData("Enter Willy's Fish Shop", "Willy's Fish Shop"),
    ConnectionData("Enter Tide Pools", "Tide Pools"),
    ConnectionData("Enter The Mines", "The Mines"),
    ConnectionData("Dig to The Mines - Floor 5", "The Mines - Floor 5"),
    ConnectionData("Dig to The Mines - Floor 10", "The Mines - Floor 10"),
    ConnectionData("Dig to The Mines - Floor 15", "The Mines - Floor 15"),
    ConnectionData("Dig to The Mines - Floor 20", "The Mines - Floor 20"),
    ConnectionData("Dig to The Mines - Floor 25", "The Mines - Floor 25"),
    ConnectionData("Dig to The Mines - Floor 30", "The Mines - Floor 30"),
    ConnectionData("Dig to The Mines - Floor 35", "The Mines - Floor 35"),
    ConnectionData("Dig to The Mines - Floor 40", "The Mines - Floor 40"),
    ConnectionData("Dig to The Mines - Floor 45", "The Mines - Floor 45"),
    ConnectionData("Dig to The Mines - Floor 50", "The Mines - Floor 50"),
    ConnectionData("Dig to The Mines - Floor 55", "The Mines - Floor 55"),
    ConnectionData("Dig to The Mines - Floor 60", "The Mines - Floor 60"),
    ConnectionData("Dig to The Mines - Floor 65", "The Mines - Floor 65"),
    ConnectionData("Dig to The Mines - Floor 70", "The Mines - Floor 70"),
    ConnectionData("Dig to The Mines - Floor 75", "The Mines - Floor 75"),
    ConnectionData("Dig to The Mines - Floor 80", "The Mines - Floor 80"),
    ConnectionData("Dig to The Mines - Floor 85", "The Mines - Floor 85"),
    ConnectionData("Dig to The Mines - Floor 90", "The Mines - Floor 90"),
    ConnectionData("Dig to The Mines - Floor 95", "The Mines - Floor 95"),
    ConnectionData("Dig to The Mines - Floor 100", "The Mines - Floor 100"),
    ConnectionData("Dig to The Mines - Floor 105", "The Mines - Floor 105"),
    ConnectionData("Dig to The Mines - Floor 110", "The Mines - Floor 110"),
    ConnectionData("Dig to The Mines - Floor 115", "The Mines - Floor 115"),
    ConnectionData("Dig to The Mines - Floor 120", "The Mines - Floor 120"),
    ConnectionData("Enter Skull Cavern Entrance", "Skull Cavern Entrance"),
    ConnectionData("Enter Skull Cavern", "Skull Cavern"),
    ConnectionData("Enter Witch Warp Cave", "Witch Warp Cave"),
    ConnectionData("Enter Witch's Swamp", "Witch's Swamp"),
    ConnectionData("Enter Bathhouse Entrance", "Bathhouse Entrance"),
    ConnectionData("Enter Locker Room", "Locker Room"),
    ConnectionData("Enter Public Bath", "Public Bath"),
]


def create_regions(region_factory: RegionFactory, options: StardewOptions) -> Iterable[Region]:
    regions: Dict[str: Region] = {region.name: region_factory(region.name, region.exits) for region in stardew_valley_regions}
    entrances: Dict[str: Entrance] = {entrance.name: entrance
                                      for region in regions.values()
                                      for entrance in region.exits}

    for connection in mandatory_connections:
        if connection.name not in entrances:
            continue
        entrances[connection.name].connect(regions[connection.destination])

    return regions.values()
