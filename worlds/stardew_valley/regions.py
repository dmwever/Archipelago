from typing import Iterable, Dict, Protocol

from BaseClasses import Region, Entrance


class RegionFactory(Protocol):
    def __call__(self, name: str, regions: Iterable[str]) -> Region:
        raise NotImplementedError


stardew_valley_regions = [
    ("Menu", ["To Stardew Valley"]),
    ("Stardew Valley", ["To Farmhouse"]),
    ("Farmhouse", ["Outside To Farm", "Downstairs To Cellar"]),
    ("Cellar", []),
    ("Farm", ["Farm To Backwoods", "Farm To Bus Stop", "Farm To Forest", "Enter Farmcave", "Enter Greenhouse",
              "Use Desert Obelisk", "Use Island Obelisk"]),
    ("Backwoods", ["Backwoods To Mountain"]),
    ("Bus Stop", ["Bus Stop To Town", "Take Bus To Desert", "Bus Stop To Tunnel Entrance"]),
    ("Forest", ["Forest To Town", "Enter Secret Woods", "Enter Wizard Tower", "Enter Marnie's Ranch",
                "Enter Leah's Cottage", "Forest To Sewers"]),
    ("Farmcave", []),
    ("Greenhouse", []),
    ("Mountain", ["Mountain to Railroad", "Enter Tent", "Enter Carpenter Shop", "Enter The Mines",
                  "Enter Quarry", "Enter Adventurer's Guild", "Mountain To Town"]),
    ("Tunnel Entrance", ["Enter Tunnel"]),
    ("Tunnel", []),
    ("Town", ["Enter Community Center", "Town To Beach", "Enter Hospital",
              "Enter Pierre's General Store", "Enter Saloon", "Enter Josh's House", "Enter Mayor's Manor",
              "Enter Sam's House", "Enter Haley's House", "Town To Sewers", "Enter Clint's Blacksmith", "Enter Museum",
              "Enter JojaMart"]),
    ("Beach", ["Enter Willy's Fish Shop", "Enter Elliott's House", "Enter Tide Pools"]),
    ("Railroad", ["Enter Bathhouse Entrance", "Enter Witch Warp Cave"]),  # "Enter Perfection Cutscene Area"
    ("Marnie's Ranch", []),
    ("Leah's Cottage", []),
    ("Sewers", []),
    ("Wizard Tower", ["Enter Wizard Basement"]),
    ("Wizard Basement", []),
    ("Tent", []),
    ("Carpenter Shop", ["Enter Sebastian's Room"]),
    ("Sebastian's Room", []),
    ("Adventurer's Guild", []),
    ("Community Center",
     ["Access Crafts Room", "Access Pantry", "Access Fish Tank", "Access Boiler Room", "Access Bulletin Board",
      "Access Vault"]),
    ("Crafts Room", []),
    ("Pantry", []),
    ("Fish Tank", []),
    ("Boiler Room", []),
    ("Bulletin Board", []),
    ("Vault", []),
    ("Hospital", ["Enter Harvey's Room"]),
    ("Harvey's Room", []),
    ("Pierre's General Store", ["Enter Sunroom"]),
    ("Sunroom", []),
    ("Saloon", ["Play Journey of the Prairie King", "Play Junimo Kart"]),
    ("Josh's House", []),
    ("Mayor's Manor", []),
    ("Sam's House", []),
    ("Haley's House", []),
    ("Clint's Blacksmith", []),
    ("Museum", []),
    ("JojaMart", []),
    ("Willy's Fish Shop", []),
    ("Elliott's House", []),
    ("Tide Pools", []),
    ("Bathhouse Entrance", ["Enter Locker Room"]),
    ("Locker Room", ["Enter Public Bath"]),
    ("Public Bath", []),
    ("Witch Warp Cave", []),

    ("Quarry", ["Enter Quarry Mine Entrance"]),
    ("Quarry Mine Entrance", ["Enter Quarry Mine"]),
    ("Quarry Mine", []),
    ("Secret Woods", []),
    ("The Desert", ["Enter Skull Cavern Entrance"]),
    ("Skull Cavern Entrance", ["Enter Skull Cavern"]),
    ("Skull Cavern", []),
    ("Ginger Island", []),
    ("JotPK World 1", ["Reach JotPK World 2"]),
    ("JotPK World 2", ["Reach JotPK World 3"]),
    ("JotPK World 3", []),
    ("Junimo Kart 1", ["Reach Junimo Kart 2"]),
    ("Junimo Kart 2", ["Reach Junimo Kart 3"]),
    ("Junimo Kart 3", []),
    ("The Mines", ["Dig to The Mines - Floor 5", "Dig to The Mines - Floor 10", "Dig to The Mines - Floor 15",
                   "Dig to The Mines - Floor 20", "Dig to The Mines - Floor 25", "Dig to The Mines - Floor 30",
                   "Dig to The Mines - Floor 35", "Dig to The Mines - Floor 40", "Dig to The Mines - Floor 45",
                   "Dig to The Mines - Floor 50", "Dig to The Mines - Floor 55", "Dig to The Mines - Floor 60",
                   "Dig to The Mines - Floor 65", "Dig to The Mines - Floor 70", "Dig to The Mines - Floor 75",
                   "Dig to The Mines - Floor 80", "Dig to The Mines - Floor 85", "Dig to The Mines - Floor 90",
                   "Dig to The Mines - Floor 95", "Dig to The Mines - Floor 100", "Dig to The Mines - Floor 105",
                   "Dig to The Mines - Floor 110", "Dig to The Mines - Floor 115", "Dig to The Mines - Floor 120"]),
    ("The Mines - Floor 5", []),
    ("The Mines - Floor 10", []),
    ("The Mines - Floor 15", []),
    ("The Mines - Floor 20", []),
    ("The Mines - Floor 25", []),
    ("The Mines - Floor 30", []),
    ("The Mines - Floor 35", []),
    ("The Mines - Floor 40", []),
    ("The Mines - Floor 45", []),
    ("The Mines - Floor 50", []),
    ("The Mines - Floor 55", []),
    ("The Mines - Floor 60", []),
    ("The Mines - Floor 65", []),
    ("The Mines - Floor 70", []),
    ("The Mines - Floor 75", []),
    ("The Mines - Floor 80", []),
    ("The Mines - Floor 85", []),
    ("The Mines - Floor 90", []),
    ("The Mines - Floor 95", []),
    ("The Mines - Floor 100", []),
    ("The Mines - Floor 105", []),
    ("The Mines - Floor 110", []),
    ("The Mines - Floor 115", []),
    ("The Mines - Floor 120", []),
]

# Exists and where they lead
mandatory_connections = [
    ("To Stardew Valley", "Stardew Valley"),
    ("To Farmhouse", "Farmhouse"),
    ("Outside To Farm", "Farm"),
    ("Downstairs To Cellar", "Cellar"),
    ("Farm To Backwoods", "Backwoods"),
    ("Farm To Bus Stop", "Bus Stop"),
    ("Farm To Forest", "Forest"),
    ("Enter Farmcave", "Farmcave"),
    ("Enter Greenhouse", "Greenhouse"),
    ("Use Desert Obelisk", "The Desert"),
    ("Use Island Obelisk", "Ginger Island"),
    ("Backwoods To Mountain", "Mountain"),
    ("Bus Stop To Town", "Town"),
    ("Bus Stop To Tunnel Entrance", "Tunnel Entrance"),
    ("Take Bus To Desert", "The Desert"),
    ("Enter Tunnel", "Tunnel"),
    ("Forest To Town", "Town"),
    ("Enter Wizard Tower", "Wizard Tower"),
    ("Enter Wizard Basement", "Wizard Basement"),
    ("Enter Marnie's Ranch", "Marnie's Ranch"),
    ("Enter Leah's Cottage", "Leah's Cottage"),
    ("Enter Secret Woods", "Secret Woods"),
    ("Forest To Sewers", "Sewers"),
    ("Town To Sewers", "Sewers"),
    ("Mountain to Railroad", "Railroad"),
    ("Enter Tent", "Tent"),
    ("Enter Carpenter Shop", "Carpenter Shop"),
    ("Enter Sebastian's Room", "Sebastian's Room"),
    ("Enter Adventurer's Guild", "Adventurer's Guild"),
    ("Enter Quarry", "Quarry"),
    ("Enter Quarry Mine Entrance", "Quarry Mine Entrance"),
    ("Enter Quarry Mine", "Quarry Mine"),
    ("Mountain To Town", "Town"),
    ("Enter Community Center", "Community Center"),
    ("Access Crafts Room", "Crafts Room"),
    ("Access Pantry", "Pantry"),
    ("Access Fish Tank", "Fish Tank"),
    ("Access Boiler Room", "Boiler Room"),
    ("Access Bulletin Board", "Bulletin Board"),
    ("Access Vault", "Vault"),
    ("Enter Hospital", "Hospital"),
    ("Enter Harvey's Room", "Harvey's Room"),
    ("Enter Pierre's General Store", "Pierre's General Store"),
    ("Enter Sunroom", "Sunroom"),
    ("Enter Clint's Blacksmith", "Clint's Blacksmith"),
    ("Enter Saloon", "Saloon"),
    ("Play Journey of the Prairie King", "JotPK World 1"),
    ("Reach JotPK World 2", "JotPK World 2"),
    ("Reach JotPK World 3", "JotPK World 3"),
    ("Play Junimo Kart", "Junimo Kart 1"),
    ("Reach Junimo Kart 2", "Junimo Kart 2"),
    ("Reach Junimo Kart 3", "Junimo Kart 3"),
    ("Enter Sam's House", "Sam's House"),
    ("Enter Haley's House", "Haley's House"),
    ("Enter Mayor's Manor", "Mayor's Manor"),
    ("Enter Josh's House", "Josh's House"),
    ("Enter Museum", "Museum"),
    ("Enter JojaMart", "JojaMart"),
    ("Town To Beach", "Beach"),
    ("Enter Elliott's House", "Elliott's House"),
    ("Enter Willy's Fish Shop", "Willy's Fish Shop"),
    ("Enter Tide Pools", "Tide Pools"),
    ("Enter The Mines", "The Mines"),
    ("Dig to The Mines - Floor 5", "The Mines - Floor 5"),
    ("Dig to The Mines - Floor 10", "The Mines - Floor 10"),
    ("Dig to The Mines - Floor 15", "The Mines - Floor 15"),
    ("Dig to The Mines - Floor 20", "The Mines - Floor 20"),
    ("Dig to The Mines - Floor 25", "The Mines - Floor 25"),
    ("Dig to The Mines - Floor 30", "The Mines - Floor 30"),
    ("Dig to The Mines - Floor 35", "The Mines - Floor 35"),
    ("Dig to The Mines - Floor 40", "The Mines - Floor 40"),
    ("Dig to The Mines - Floor 45", "The Mines - Floor 45"),
    ("Dig to The Mines - Floor 50", "The Mines - Floor 50"),
    ("Dig to The Mines - Floor 55", "The Mines - Floor 55"),
    ("Dig to The Mines - Floor 60", "The Mines - Floor 60"),
    ("Dig to The Mines - Floor 65", "The Mines - Floor 65"),
    ("Dig to The Mines - Floor 70", "The Mines - Floor 70"),
    ("Dig to The Mines - Floor 75", "The Mines - Floor 75"),
    ("Dig to The Mines - Floor 80", "The Mines - Floor 80"),
    ("Dig to The Mines - Floor 85", "The Mines - Floor 85"),
    ("Dig to The Mines - Floor 90", "The Mines - Floor 90"),
    ("Dig to The Mines - Floor 95", "The Mines - Floor 95"),
    ("Dig to The Mines - Floor 100", "The Mines - Floor 100"),
    ("Dig to The Mines - Floor 105", "The Mines - Floor 105"),
    ("Dig to The Mines - Floor 110", "The Mines - Floor 110"),
    ("Dig to The Mines - Floor 115", "The Mines - Floor 115"),
    ("Dig to The Mines - Floor 120", "The Mines - Floor 120"),
    ("Enter Skull Cavern Entrance", "Skull Cavern Entrance"),
    ("Enter Skull Cavern", "Skull Cavern"),
    ("Enter Witch Warp Cave", "Witch Warp Cave"),
    ("Enter Bathhouse Entrance", "Bathhouse Entrance"),
    ("Enter Locker Room", "Locker Room"),
    ("Enter Public Bath", "Public Bath"),
]


def create_regions(region_factory: RegionFactory) -> Iterable[Region]:
    regions: Dict[str: Region] = {region[0]: region_factory(*region) for region in stardew_valley_regions}
    entrances: Dict[str: Entrance] = {entrance.name: entrance
                                      for region in regions.values()
                                      for entrance in region.exits}

    for connection in mandatory_connections:
        entrances[connection[0]].connect(regions[connection[1]])

    return regions.values()
