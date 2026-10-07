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


class FillerTier(enum.Enum):
    FREE = enum.auto()
    EARLY = enum.auto()
    REGULAR = enum.auto()


class Age2FillerLocationData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str, kind: FillerKind, threshold: int,
                 tier: FillerTier, resource: Resource = None) -> None:
        self.id = id
        self.location_name = location_name
        self.kind = kind
        self.threshold = threshold
        self.tier = tier
        self.resource = resource

    EXPLORE_5 =    6000, "Explore 5% of the Map",   FillerKind.EXPLORE, 5,  FillerTier.FREE
    EXPLORE_10 =   6001, "Explore 10% of the Map",  FillerKind.EXPLORE, 10, FillerTier.FREE
    EXPLORE_15 =   6002, "Explore 15% of the Map",  FillerKind.EXPLORE, 15, FillerTier.FREE
    EXPLORE_20 =   6003, "Explore 20% of the Map",  FillerKind.EXPLORE, 20, FillerTier.FREE
    EXPLORE_25 =   6004, "Explore 25% of the Map",  FillerKind.EXPLORE, 25, FillerTier.FREE
    EXPLORE_30 =   6005, "Explore 30% of the Map",  FillerKind.EXPLORE, 30, FillerTier.FREE
    EXPLORE_35 =   6006, "Explore 35% of the Map",  FillerKind.EXPLORE, 35, FillerTier.FREE
    EXPLORE_40 =   6007, "Explore 40% of the Map",  FillerKind.EXPLORE, 40, FillerTier.FREE
    EXPLORE_45 =   6008, "Explore 45% of the Map",  FillerKind.EXPLORE, 45, FillerTier.FREE
    EXPLORE_50 =   6009, "Explore 50% of the Map",  FillerKind.EXPLORE, 50, FillerTier.FREE

    OWN_5 =        6100, "Own 5 Units",     FillerKind.OWN_UNITS, 5,   FillerTier.FREE
    OWN_10 =       6101, "Own 10 Units",    FillerKind.OWN_UNITS, 10,  FillerTier.FREE
    OWN_20 =       6102, "Own 20 Units",    FillerKind.OWN_UNITS, 20,  FillerTier.REGULAR
    OWN_30 =       6103, "Own 30 Units",    FillerKind.OWN_UNITS, 30,  FillerTier.REGULAR
    OWN_40 =       6104, "Own 40 Units",    FillerKind.OWN_UNITS, 40,  FillerTier.REGULAR
    OWN_50 =       6105, "Own 50 Units",    FillerKind.OWN_UNITS, 50,  FillerTier.REGULAR
    OWN_60 =       6106, "Own 60 Units",    FillerKind.OWN_UNITS, 60,  FillerTier.REGULAR
    OWN_70 =       6107, "Own 70 Units",    FillerKind.OWN_UNITS, 70,  FillerTier.REGULAR
    OWN_80 =       6108, "Own 80 Units",    FillerKind.OWN_UNITS, 80,  FillerTier.REGULAR
    OWN_90 =       6109, "Own 90 Units",    FillerKind.OWN_UNITS, 90,  FillerTier.REGULAR
    OWN_100 =      6110, "Own 100 Units",   FillerKind.OWN_UNITS, 100, FillerTier.REGULAR

    KILL_5 =       6200, "Kill 5 Units",    FillerKind.KILL_UNITS, 5,   FillerTier.FREE
    KILL_10 =      6201, "Kill 10 Units",   FillerKind.KILL_UNITS, 10,  FillerTier.FREE
    KILL_25 =      6202, "Kill 25 Units",   FillerKind.KILL_UNITS, 25,  FillerTier.REGULAR
    KILL_50 =      6203, "Kill 50 Units",   FillerKind.KILL_UNITS, 50,  FillerTier.REGULAR
    KILL_100 =     6204, "Kill 100 Units",  FillerKind.KILL_UNITS, 100, FillerTier.REGULAR
    KILL_150 =     6205, "Kill 150 Units",  FillerKind.KILL_UNITS, 150, FillerTier.REGULAR
    KILL_200 =     6206, "Kill 200 Units",  FillerKind.KILL_UNITS, 200, FillerTier.REGULAR

    RAZE_1 =       6300, "Raze 1 Building",    FillerKind.RAZE_BUILDINGS, 1,  FillerTier.FREE
    RAZE_2 =       6301, "Raze 2 Buildings",   FillerKind.RAZE_BUILDINGS, 2,  FillerTier.FREE
    RAZE_5 =       6302, "Raze 5 Buildings",   FillerKind.RAZE_BUILDINGS, 5,  FillerTier.FREE
    RAZE_10 =      6303, "Raze 10 Buildings",  FillerKind.RAZE_BUILDINGS, 10, FillerTier.FREE
    RAZE_15 =      6304, "Raze 15 Buildings",  FillerKind.RAZE_BUILDINGS, 15, FillerTier.REGULAR
    RAZE_20 =      6305, "Raze 20 Buildings",  FillerKind.RAZE_BUILDINGS, 20, FillerTier.REGULAR
    RAZE_25 =      6306, "Raze 25 Buildings",  FillerKind.RAZE_BUILDINGS, 25, FillerTier.REGULAR

    RESEARCH_1 =   6400, "Research 1 Technology",    FillerKind.RESEARCH_TECHS, 1,  FillerTier.EARLY
    RESEARCH_2 =   6401, "Research 2 Technologies",  FillerKind.RESEARCH_TECHS, 2,  FillerTier.EARLY
    RESEARCH_5 =   6402, "Research 5 Technologies",  FillerKind.RESEARCH_TECHS, 5,  FillerTier.EARLY
    RESEARCH_10 =  6403, "Research 10 Technologies", FillerKind.RESEARCH_TECHS, 10, FillerTier.REGULAR
    RESEARCH_15 =  6404, "Research 15 Technologies", FillerKind.RESEARCH_TECHS, 15, FillerTier.REGULAR
    RESEARCH_20 =  6405, "Research 20 Technologies", FillerKind.RESEARCH_TECHS, 20, FillerTier.REGULAR
    RESEARCH_25 =  6406, "Research 25 Technologies", FillerKind.RESEARCH_TECHS, 25, FillerTier.REGULAR

    BUILD_1 =      6500, "Build 1 Building",    FillerKind.BUILD_BUILDINGS, 1,  FillerTier.EARLY
    BUILD_2 =      6501, "Build 2 Buildings",   FillerKind.BUILD_BUILDINGS, 2,  FillerTier.EARLY
    BUILD_5 =      6502, "Build 5 Buildings",   FillerKind.BUILD_BUILDINGS, 5,  FillerTier.EARLY
    BUILD_10 =     6503, "Build 10 Buildings",  FillerKind.BUILD_BUILDINGS, 10, FillerTier.EARLY

    CONVERT_1 =    6600, "Convert 1 Unit",    FillerKind.CONVERT_UNITS, 1,  FillerTier.REGULAR
    CONVERT_5 =    6601, "Convert 5 Units",   FillerKind.CONVERT_UNITS, 5,  FillerTier.REGULAR
    CONVERT_10 =   6602, "Convert 10 Units",  FillerKind.CONVERT_UNITS, 10, FillerTier.REGULAR
    CONVERT_25 =   6603, "Convert 25 Units",  FillerKind.CONVERT_UNITS, 25, FillerTier.REGULAR

    VILLAGERS_1 =  6700, "Train 1 Villager",    FillerKind.TRAIN_VILLAGERS, 1,  FillerTier.EARLY
    VILLAGERS_5 =  6701, "Train 5 Villagers",   FillerKind.TRAIN_VILLAGERS, 5,  FillerTier.EARLY
    VILLAGERS_10 = 6702, "Train 10 Villagers",  FillerKind.TRAIN_VILLAGERS, 10, FillerTier.EARLY
    VILLAGERS_25 = 6703, "Train 25 Villagers",  FillerKind.TRAIN_VILLAGERS, 25, FillerTier.EARLY
    VILLAGERS_50 = 6704, "Train 50 Villagers",  FillerKind.TRAIN_VILLAGERS, 50, FillerTier.EARLY

    FOOD_50 =      6800, "Collect 50 Food",    FillerKind.COLLECT, 50,   FillerTier.EARLY,   Resource.FOOD
    FOOD_100 =     6801, "Collect 100 Food",   FillerKind.COLLECT, 100,  FillerTier.EARLY,   Resource.FOOD
    FOOD_150 =     6802, "Collect 150 Food",   FillerKind.COLLECT, 150,  FillerTier.EARLY,   Resource.FOOD
    FOOD_200 =     6803, "Collect 200 Food",   FillerKind.COLLECT, 200,  FillerTier.REGULAR, Resource.FOOD
    FOOD_300 =     6804, "Collect 300 Food",   FillerKind.COLLECT, 300,  FillerTier.REGULAR, Resource.FOOD
    FOOD_400 =     6805, "Collect 400 Food",   FillerKind.COLLECT, 400,  FillerTier.REGULAR, Resource.FOOD
    FOOD_500 =     6806, "Collect 500 Food",   FillerKind.COLLECT, 500,  FillerTier.REGULAR, Resource.FOOD
    FOOD_1000 =    6807, "Collect 1000 Food",  FillerKind.COLLECT, 1000, FillerTier.REGULAR, Resource.FOOD

    WOOD_50 =      6900, "Collect 50 Wood",    FillerKind.COLLECT, 50,   FillerTier.EARLY,   Resource.WOOD
    WOOD_100 =     6901, "Collect 100 Wood",   FillerKind.COLLECT, 100,  FillerTier.EARLY,   Resource.WOOD
    WOOD_150 =     6902, "Collect 150 Wood",   FillerKind.COLLECT, 150,  FillerTier.EARLY,   Resource.WOOD
    WOOD_200 =     6903, "Collect 200 Wood",   FillerKind.COLLECT, 200,  FillerTier.REGULAR, Resource.WOOD
    WOOD_300 =     6904, "Collect 300 Wood",   FillerKind.COLLECT, 300,  FillerTier.REGULAR, Resource.WOOD
    WOOD_400 =     6905, "Collect 400 Wood",   FillerKind.COLLECT, 400,  FillerTier.REGULAR, Resource.WOOD
    WOOD_500 =     6906, "Collect 500 Wood",   FillerKind.COLLECT, 500,  FillerTier.REGULAR, Resource.WOOD
    WOOD_1000 =    6907, "Collect 1000 Wood",  FillerKind.COLLECT, 1000, FillerTier.REGULAR, Resource.WOOD

    GOLD_50 =      7000, "Collect 50 Gold",    FillerKind.COLLECT, 50,   FillerTier.EARLY,   Resource.GOLD
    GOLD_100 =     7001, "Collect 100 Gold",   FillerKind.COLLECT, 100,  FillerTier.EARLY,   Resource.GOLD
    GOLD_150 =     7002, "Collect 150 Gold",   FillerKind.COLLECT, 150,  FillerTier.EARLY,   Resource.GOLD
    GOLD_200 =     7003, "Collect 200 Gold",   FillerKind.COLLECT, 200,  FillerTier.REGULAR, Resource.GOLD
    GOLD_300 =     7004, "Collect 300 Gold",   FillerKind.COLLECT, 300,  FillerTier.REGULAR, Resource.GOLD
    GOLD_400 =     7005, "Collect 400 Gold",   FillerKind.COLLECT, 400,  FillerTier.REGULAR, Resource.GOLD
    GOLD_500 =     7006, "Collect 500 Gold",   FillerKind.COLLECT, 500,  FillerTier.REGULAR, Resource.GOLD
    GOLD_1000 =    7007, "Collect 1000 Gold",  FillerKind.COLLECT, 1000, FillerTier.REGULAR, Resource.GOLD

    STONE_50 =     7100, "Collect 50 Stone",    FillerKind.COLLECT, 50,   FillerTier.EARLY,   Resource.STONE
    STONE_100 =    7101, "Collect 100 Stone",   FillerKind.COLLECT, 100,  FillerTier.EARLY,   Resource.STONE
    STONE_150 =    7102, "Collect 150 Stone",   FillerKind.COLLECT, 150,  FillerTier.EARLY,   Resource.STONE
    STONE_200 =    7103, "Collect 200 Stone",   FillerKind.COLLECT, 200,  FillerTier.REGULAR, Resource.STONE
    STONE_300 =    7104, "Collect 300 Stone",   FillerKind.COLLECT, 300,  FillerTier.REGULAR, Resource.STONE
    STONE_400 =    7105, "Collect 400 Stone",   FillerKind.COLLECT, 400,  FillerTier.REGULAR, Resource.STONE
    STONE_500 =    7106, "Collect 500 Stone",   FillerKind.COLLECT, 500,  FillerTier.REGULAR, Resource.STONE
    STONE_1000 =   7107, "Collect 1000 Stone",  FillerKind.COLLECT, 1000, FillerTier.REGULAR, Resource.STONE


FILLER_LOCATION_COUNT = len(Age2FillerLocationData)

KIND_TO_LOCATIONS: dict[FillerKind, list[Age2FillerLocationData]] = {
    kind: [] for kind in FillerKind}
for _filler in Age2FillerLocationData:
    KIND_TO_LOCATIONS[_filler.kind].append(_filler)
