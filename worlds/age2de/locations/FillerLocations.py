import enum

from ..items.Items import Resource


class FillerKind(enum.Enum):
    EXPLORE = enum.auto()
    OWN_UNITS = enum.auto()
    KILL_UNITS = enum.auto()
    RAZE_BUILDINGS = enum.auto()
    RESEARCH_TECHS = enum.auto()
    BUILD_BUILDINGS = enum.auto()
    CONVERT_UNITS = enum.auto()
    TRAIN_VILLAGERS = enum.auto()
    COLLECT = enum.auto()


class Age2FillerLocationData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, name: str, kind: FillerKind, threshold: int,
                 resource: Resource = None) -> None:
        self.id = id
        self.location_name = f"Milestone: {name}"
        self.kind = kind
        self.threshold = threshold
        self.resource = resource

    EXPLORE_5 =    6000, "Explore 5% of the Map",   FillerKind.EXPLORE, 5
    EXPLORE_10 =   6001, "Explore 10% of the Map",  FillerKind.EXPLORE, 10
    EXPLORE_15 =   6002, "Explore 15% of the Map",  FillerKind.EXPLORE, 15
    EXPLORE_20 =   6003, "Explore 20% of the Map",  FillerKind.EXPLORE, 20
    EXPLORE_25 =   6004, "Explore 25% of the Map",  FillerKind.EXPLORE, 25
    EXPLORE_30 =   6005, "Explore 30% of the Map",  FillerKind.EXPLORE, 30
    EXPLORE_35 =   6006, "Explore 35% of the Map",  FillerKind.EXPLORE, 35
    EXPLORE_40 =   6007, "Explore 40% of the Map",  FillerKind.EXPLORE, 40
    EXPLORE_45 =   6008, "Explore 45% of the Map",  FillerKind.EXPLORE, 45
    EXPLORE_50 =   6009, "Explore 50% of the Map",  FillerKind.EXPLORE, 50

    OWN_5 =        6100, "Own 5 Units",     FillerKind.OWN_UNITS, 5
    OWN_10 =       6101, "Own 10 Units",    FillerKind.OWN_UNITS, 10
    OWN_20 =       6102, "Own 20 Units",    FillerKind.OWN_UNITS, 20
    OWN_30 =       6103, "Own 30 Units",    FillerKind.OWN_UNITS, 30
    OWN_40 =       6104, "Own 40 Units",    FillerKind.OWN_UNITS, 40
    OWN_50 =       6105, "Own 50 Units",    FillerKind.OWN_UNITS, 50
    OWN_60 =       6106, "Own 60 Units",    FillerKind.OWN_UNITS, 60
    OWN_70 =       6107, "Own 70 Units",    FillerKind.OWN_UNITS, 70
    OWN_80 =       6108, "Own 80 Units",    FillerKind.OWN_UNITS, 80
    OWN_90 =       6109, "Own 90 Units",    FillerKind.OWN_UNITS, 90
    OWN_100 =      6110, "Own 100 Units",   FillerKind.OWN_UNITS, 100

    KILL_1 =        6200, "Kill 1 Unit",     FillerKind.KILL_UNITS, 1
    KILL_5 =        6201, "Kill 5 Units",     FillerKind.KILL_UNITS, 5
    KILL_10 =       6202, "Kill 10 Units",    FillerKind.KILL_UNITS, 10
    KILL_25 =       6203, "Kill 25 Units",    FillerKind.KILL_UNITS, 25
    KILL_50 =       6204, "Kill 50 Units",    FillerKind.KILL_UNITS, 50
    KILL_100 =      6205, "Kill 100 Units",   FillerKind.KILL_UNITS, 100
    KILL_250 =      6206, "Kill 250 Units",   FillerKind.KILL_UNITS, 250
    KILL_500 =      6207, "Kill 500 Units",   FillerKind.KILL_UNITS, 500
    KILL_1000 =     6208, "Kill 1000 Units",  FillerKind.KILL_UNITS, 1000

    RAZE_1 =        6300, "Raze 1 Building",     FillerKind.RAZE_BUILDINGS, 1
    RAZE_5 =        6301, "Raze 5 Buildings",     FillerKind.RAZE_BUILDINGS, 5
    RAZE_10 =       6302, "Raze 10 Buildings",    FillerKind.RAZE_BUILDINGS, 10
    RAZE_25 =       6303, "Raze 25 Buildings",    FillerKind.RAZE_BUILDINGS, 25
    RAZE_50 =       6304, "Raze 50 Buildings",    FillerKind.RAZE_BUILDINGS, 50
    RAZE_100 =      6305, "Raze 100 Buildings",   FillerKind.RAZE_BUILDINGS, 100
    RAZE_250 =      6306, "Raze 250 Buildings",   FillerKind.RAZE_BUILDINGS, 250

    RESEARCH_1 =   6400, "Research 1 Technology",    FillerKind.RESEARCH_TECHS, 1
    RESEARCH_2 =   6401, "Research 2 Technologies",  FillerKind.RESEARCH_TECHS, 2
    RESEARCH_5 =   6402, "Research 5 Technologies",  FillerKind.RESEARCH_TECHS, 5
    RESEARCH_10 =  6403, "Research 10 Technologies", FillerKind.RESEARCH_TECHS, 10
    RESEARCH_15 =  6404, "Research 15 Technologies", FillerKind.RESEARCH_TECHS, 15
    RESEARCH_20 =  6405, "Research 20 Technologies", FillerKind.RESEARCH_TECHS, 20
    RESEARCH_25 =  6406, "Research 25 Technologies", FillerKind.RESEARCH_TECHS, 25

    BUILD_1 =      6500, "Build 1 Building",    FillerKind.BUILD_BUILDINGS, 1
    BUILD_2 =      6501, "Build 2 Buildings",   FillerKind.BUILD_BUILDINGS, 2
    BUILD_5 =      6502, "Build 5 Buildings",   FillerKind.BUILD_BUILDINGS, 5
    BUILD_10 =     6503, "Build 10 Buildings",  FillerKind.BUILD_BUILDINGS, 10

    CONVERT_1 =    6600, "Convert 1 Unit",    FillerKind.CONVERT_UNITS, 1
    CONVERT_5 =    6601, "Convert 5 Units",   FillerKind.CONVERT_UNITS, 5
    CONVERT_10 =   6602, "Convert 10 Units",  FillerKind.CONVERT_UNITS, 10
    CONVERT_25 =   6603, "Convert 25 Units",  FillerKind.CONVERT_UNITS, 25

    VILLAGERS_1 =  6700, "Train 1 Villager",    FillerKind.TRAIN_VILLAGERS, 1
    VILLAGERS_5 =  6701, "Train 5 Villagers",   FillerKind.TRAIN_VILLAGERS, 5
    VILLAGERS_10 = 6702, "Train 10 Villagers",  FillerKind.TRAIN_VILLAGERS, 10
    VILLAGERS_25 = 6703, "Train 25 Villagers",  FillerKind.TRAIN_VILLAGERS, 25
    VILLAGERS_50 = 6704, "Train 50 Villagers",  FillerKind.TRAIN_VILLAGERS, 50

    FOOD_50 =      6800, "Collect 50 Food",    FillerKind.COLLECT, 50,   Resource.FOOD
    FOOD_100 =     6801, "Collect 100 Food",   FillerKind.COLLECT, 100,   Resource.FOOD
    FOOD_150 =     6802, "Collect 150 Food",   FillerKind.COLLECT, 150,   Resource.FOOD
    FOOD_200 =     6803, "Collect 200 Food",   FillerKind.COLLECT, 200, Resource.FOOD
    FOOD_300 =     6804, "Collect 300 Food",   FillerKind.COLLECT, 300, Resource.FOOD
    FOOD_400 =     6805, "Collect 400 Food",   FillerKind.COLLECT, 400, Resource.FOOD
    FOOD_500 =     6806, "Collect 500 Food",   FillerKind.COLLECT, 500, Resource.FOOD
    FOOD_1000 =    6807, "Collect 1000 Food",  FillerKind.COLLECT, 1000, Resource.FOOD

    WOOD_50 =      6900, "Collect 50 Wood",    FillerKind.COLLECT, 50,   Resource.WOOD
    WOOD_100 =     6901, "Collect 100 Wood",   FillerKind.COLLECT, 100,   Resource.WOOD
    WOOD_150 =     6902, "Collect 150 Wood",   FillerKind.COLLECT, 150,   Resource.WOOD
    WOOD_200 =     6903, "Collect 200 Wood",   FillerKind.COLLECT, 200, Resource.WOOD
    WOOD_300 =     6904, "Collect 300 Wood",   FillerKind.COLLECT, 300, Resource.WOOD
    WOOD_400 =     6905, "Collect 400 Wood",   FillerKind.COLLECT, 400, Resource.WOOD
    WOOD_500 =     6906, "Collect 500 Wood",   FillerKind.COLLECT, 500, Resource.WOOD
    WOOD_1000 =    6907, "Collect 1000 Wood",  FillerKind.COLLECT, 1000, Resource.WOOD

    GOLD_50 =      7000, "Collect 50 Gold",    FillerKind.COLLECT, 50,   Resource.GOLD
    GOLD_100 =     7001, "Collect 100 Gold",   FillerKind.COLLECT, 100,   Resource.GOLD
    GOLD_150 =     7002, "Collect 150 Gold",   FillerKind.COLLECT, 150,   Resource.GOLD
    GOLD_200 =     7003, "Collect 200 Gold",   FillerKind.COLLECT, 200, Resource.GOLD
    GOLD_300 =     7004, "Collect 300 Gold",   FillerKind.COLLECT, 300, Resource.GOLD
    GOLD_400 =     7005, "Collect 400 Gold",   FillerKind.COLLECT, 400, Resource.GOLD
    GOLD_500 =     7006, "Collect 500 Gold",   FillerKind.COLLECT, 500, Resource.GOLD
    GOLD_1000 =    7007, "Collect 1000 Gold",  FillerKind.COLLECT, 1000, Resource.GOLD

    STONE_50 =     7100, "Collect 50 Stone",    FillerKind.COLLECT, 50,   Resource.STONE
    STONE_100 =    7101, "Collect 100 Stone",   FillerKind.COLLECT, 100,   Resource.STONE
    STONE_150 =    7102, "Collect 150 Stone",   FillerKind.COLLECT, 150,   Resource.STONE
    STONE_200 =    7103, "Collect 200 Stone",   FillerKind.COLLECT, 200, Resource.STONE
    STONE_300 =    7104, "Collect 300 Stone",   FillerKind.COLLECT, 300, Resource.STONE
    STONE_400 =    7105, "Collect 400 Stone",   FillerKind.COLLECT, 400, Resource.STONE
    STONE_500 =    7106, "Collect 500 Stone",   FillerKind.COLLECT, 500, Resource.STONE
    STONE_1000 =   7107, "Collect 1000 Stone",  FillerKind.COLLECT, 1000, Resource.STONE


FILLER_LOCATION_COUNT = len(Age2FillerLocationData)

KIND_TO_LOCATIONS: dict[FillerKind, list[Age2FillerLocationData]] = {
    kind: [] for kind in FillerKind}
for _filler in Age2FillerLocationData:
    KIND_TO_LOCATIONS[_filler.kind].append(_filler)
