from dataclasses import dataclass
import enum

from BaseClasses import ItemClassification
from ..locations.Campaigns import Age2CampaignData
from ..locations.Ages import Age2AgeData
from ..locations.Scenarios import Age2ScenarioData

class Resource(enum.Enum):
    WOOD = 1,
    FOOD = 2,
    GOLD = 3,
    STONE = 4

@dataclass
class Resources:
    type: Resource
    amount: int

@dataclass
class TCResources:
    type: Resource
    amount: int

@dataclass
class Victory:
    pass

@dataclass
class Building:
    game_id: int
    total_cost: float
    age: Age2AgeData
    needed_resources: dict[Resource, float]
    
@dataclass
class Tech:
    game_id: int
    effect_id: int
    civ: int
    age: Age2AgeData
    is_upgrade: bool
    is_unique: bool

@dataclass
class ScenarioItem:
    vanilla_scenario: Age2ScenarioData

@dataclass
class Mercenary:
    vanilla_scenario: Age2ScenarioData
    # troop_count: dict[int, int] # UnitId, Count

@dataclass
class ProgressiveScenario:
    vanilla_campaign: Age2CampaignData
    num_additional_scenarios: int

@dataclass
class Campaign:
    vanilla_campaign: Age2CampaignData

@dataclass
class StartingResources:
    type: Resource
    amount: int

type FillerItemType = (
    Resources | StartingResources
)

type ItemType = (
    ScenarioItem | StartingResources | ProgressiveScenario | Mercenary | Campaign | Resources | TCResources | Victory | Building | Tech
)

item_type_to_classification = {
    ScenarioItem: ItemClassification.progression,
    ProgressiveScenario: ItemClassification.progression,
    Campaign: ItemClassification.progression,
    TCResources: ItemClassification.progression,
    Age2AgeData: ItemClassification.progression,
    Building: ItemClassification.progression,
    Tech: ItemClassification.progression,
    Mercenary: ItemClassification.useful,
    Resources: ItemClassification.filler,
    StartingResources: ItemClassification.useful,
    Victory: ItemClassification.progression,
}

class Age2ItemData(enum.IntEnum):
    def __new__(cls, id: int, name: str, type: ItemType) -> 'Age2ItemData':
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, name: str, type: ItemType) -> None:
        self.id = id
        self.item_name = name
        self.type = type
        self.type_data = self.type.__class__
    
    VICTORY =                       0, "Victory", Victory()
    
    #1 - 999 = Resources (25), Ages (25), Civs (150), Buildings (100), Units (350), Techs (350) 
    
    # Filler Resources
    FILLER_WOOD_SMALL =             1, "+100 Wood",   Resources(Resource.WOOD, 100)
    FILLER_FOOD_SMALL =             2, "+100 Food",   Resources(Resource.FOOD, 100)
    FILLER_GOLD_SMALL =             3, "+100 Gold",   Resources(Resource.GOLD, 100)
    FILLER_STONE_SMALL =            4, "+50 Stone",   Resources(Resource.STONE, 50)
    FILLER_WOOD_MEDIUM =            5, "+250 Wood",   Resources(Resource.WOOD, 250)
    FILLER_FOOD_MEDIUM =            6, "+250 Food",   Resources(Resource.FOOD, 250)
    FILLER_GOLD_MEDIUM =            7, "+250 Gold",   Resources(Resource.GOLD, 250)
    FILLER_STONE_MEDIUM =           8, "+125 Stone",  Resources(Resource.STONE, 125)
    FILLER_WOOD_LARGE =             9, "+1000 Wood",  Resources(Resource.WOOD, 1000)
    FILLER_FOOD_LARGE =            10, "+1000 Food",  Resources(Resource.FOOD, 1000)
    FILLER_GOLD_LARGE =            11, "+1000 Gold",  Resources(Resource.GOLD, 1000)
    FILLER_STONE_LARGE =           12, "+500 Stone",  Resources(Resource.STONE, 500)
    
    #Starting Resources
    STARTING_WOOD_SMALL =             13, "+50 Starting Wood",      StartingResources(Resource.WOOD, 50)
    STARTING_FOOD_SMALL =             14, "+50 Starting Food",      StartingResources(Resource.FOOD, 50)
    STARTING_GOLD_SMALL =             15, "+50 Starting Gold",      StartingResources(Resource.GOLD, 50)
    STARTING_STONE_SMALL =            16, "+25 Starting Stone",     StartingResources(Resource.STONE, 25)
    STARTING_WOOD_MEDIUM =            17, "+100 Starting Wood",     StartingResources(Resource.WOOD, 100)
    STARTING_FOOD_MEDIUM =            18, "+100 Starting Food",     StartingResources(Resource.FOOD, 100)
    STARTING_GOLD_MEDIUM =            19, "+100 Starting Gold",     StartingResources(Resource.GOLD, 100)
    STARTING_STONE_MEDIUM =           20, "+50 Starting Stone",     StartingResources(Resource.STONE, 50)
    STARTING_WOOD_LARGE =             21, "+250 Starting Wood",     StartingResources(Resource.WOOD, 250)
    STARTING_FOOD_LARGE =             22, "+250 Starting Food",     StartingResources(Resource.FOOD, 250)
    STARTING_GOLD_LARGE =             23, "+250 Starting Gold",     StartingResources(Resource.GOLD, 250)
    STARTING_STONE_LARGE =            24, "+125 Starting Stone",    StartingResources(Resource.STONE, 125)
    
    #Ages
    FEUDAL_AGE =        26, "Feudal Age", Age2AgeData.FEUDAL
    CASTLE_AGE =        27, "Castle Age", Age2AgeData.CASTLE
    IMPERIAL_AGE =      28, "Imperial Age", Age2AgeData.IMPERIAL
    
    #200 - 300 = Buildings
    WONDER =                        200, "Wonder",              Building(276, 3000.0,   Age2AgeData.IMPERIAL,   { Resource.WOOD: 1000.0, Resource.GOLD: 1000.0, Resource.STONE: 1000.0 })
    OUTPOST =                       201, "Outpost",             Building(598, 30.0,     Age2AgeData.DARK,       { Resource.WOOD: 25.0, Resource.STONE: 5.0 })
    TOWN_CENTER =                   202, "Town Center",         Building(621, 375.0,    Age2AgeData.DARK,       { Resource.WOOD: 275.0, Resource.STONE: 100.0 })
    HOUSE =                         203, "House",               Building(70, 25.0,      Age2AgeData.DARK,       { Resource.WOOD: 25.0 })
    MILL =                          204, "Mill",                Building(68, 100.0,     Age2AgeData.DARK,       { Resource.WOOD: 100.0 })
    MINING_CAMP =                   205, "Mining Camp",         Building(584, 100.0,    Age2AgeData.DARK,       { Resource.WOOD: 100.0 })
    LUMBER_CAMP =                   206, "Lumber Camp",         Building(562, 100.0,    Age2AgeData.DARK,       { Resource.WOOD: 100.0 })
    FARM =                          207, "Farm",                Building(50, 60.0,      Age2AgeData.DARK,       { Resource.WOOD: 60.0 })
    FISH_TRAP =                     208, "Fish Trap",           Building(199, 100.0,    Age2AgeData.FEUDAL,     { Resource.WOOD: 100.0 })
    DOCK =                          209, "Dock",                Building(45, 150.0,     Age2AgeData.DARK,       { Resource.WOOD: 150.0 })
    MARKET =                        210, "Market",              Building(84, 175.0,     Age2AgeData.FEUDAL,     { Resource.WOOD: 175.0 })
    UNIVERSITY =                    211, "University",          Building(209, 200.0,    Age2AgeData.CASTLE,     { Resource.WOOD: 200.0 })
    BLACKSMITH =                    212, "Blacksmith",          Building(103, 150.0,    Age2AgeData.FEUDAL,     { Resource.WOOD: 150.0 })
    MONASTERY =                     213, "Monastery",           Building(104, 175.0,    Age2AgeData.CASTLE,     { Resource.WOOD: 175.0 })
    BARRACKS =                      214, "Barracks",            Building(12, 175.0,     Age2AgeData.DARK,       { Resource.WOOD: 175.0 })
    ARCHERY_RANGE =                 215, "Archery Range",       Building(87, 175.0,     Age2AgeData.FEUDAL,     { Resource.WOOD: 175.0 })
    STABLE =                        216, "Stable",              Building(101, 175.0,    Age2AgeData.FEUDAL,     { Resource.WOOD: 175.0 })
    SIEGE_WORKSHOP =                217, "Siege Workshop",      Building(49, 200.0,     Age2AgeData.CASTLE,     { Resource.WOOD: 200.0 })
    CASTLE =                        218, "Castle",              Building(82, 650.0,     Age2AgeData.CASTLE,     { Resource.STONE: 650.0 })
    PALISADE_GATE =                 219, "Palisade Gate",       Building(792, 20.0,     Age2AgeData.DARK,       { Resource.WOOD: 20.0 })
    GATE =                          220, "Stone Gate",          Building(487, 30.0,     Age2AgeData.FEUDAL,     { Resource.STONE: 30.0 })
    PALISADE_WALL =                 221, "Palisade Wall",       Building(72, 3.0,       Age2AgeData.DARK,       { Resource.WOOD: 3.0 })
    STONE_WALL =                    222, "Stone Wall",          Building(117, 5.0,      Age2AgeData.FEUDAL,     { Resource.STONE: 5.0 })
    WATCH_TOWER =                   223, "Watch Tower",         Building(79, 160.0,     Age2AgeData.FEUDAL,     { Resource.WOOD: 35.0, Resource.STONE: 125.0 })
    BOMBARD_TOWER =                 224, "Bombard Tower",       Building(236, 225.0,    Age2AgeData.IMPERIAL,   { Resource.STONE: 125.0, Resource.GOLD: 100.0 })
    FOLWARK =                       225, "Folwark",             Building(1734, 100.0,   Age2AgeData.DARK,       { Resource.WOOD: 100.0 })
    MULE_CART =                     226, "Mule Cart",           Building(1808, 100.0,   Age2AgeData.DARK,       { Resource.FOOD: 20.0, Resource.WOOD: 80.0 })
    PASTURE =                       227, "Pasture",             Building(1889, 110.0,   Age2AgeData.DARK,       { Resource.WOOD: 110.0 })
    HARBOR =                        228, "Harbor",              Building(1189, 150.0,   Age2AgeData.CASTLE,     { Resource.WOOD: 150.0 })
    CARAVANSERAI =                  229, "Caravanserai",        Building(1754, 225.0,   Age2AgeData.IMPERIAL,   { Resource.WOOD: 175.0, Resource.STONE: 50.0 })
    FEITORIA =                      230, "Feitoria",            Building(1021, 650.0,   Age2AgeData.IMPERIAL,   { Resource.STONE: 300.0, Resource.GOLD: 350.0 })
    SETTLEMENT =                    231, "Settlement",          Building(2556, 125.0,   Age2AgeData.DARK,       { Resource.WOOD: 125.0 })
    FORTIFIED_CHURCH =              232, "Fortified Church",    Building(1806, 200.0,   Age2AgeData.CASTLE,     { Resource.WOOD: 200.0 })
    KREPOST =                       233, "Krepost",             Building(1251, 350.0,   Age2AgeData.CASTLE,     { Resource.STONE: 350.0 })
    DONJON =                        234, "Donjon",              Building(1665, 225.0,   Age2AgeData.DARK,       { Resource.WOOD: 50.0, Resource.STONE: 175 })
    
    #1000 - 2999 = Progression Items
    TOWN_CENTER_WOOD =                  1000, "Starting Town Center Wood",          TCResources(Resource.WOOD, 275)
    TOWN_CENTER_STONE =                 1001, "Starting Town Center Stone",         TCResources(Resource.FOOD, 100)
    
    # Scenario Progression Items
    AP_ATTILA_1_BLEDAS_CAMP =   1002, "Attila, The Scourge of God: Bleda's Camp",           ScenarioItem(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_1_ATTILAS_CAMP =  1003, "Attila, The Scourge of God: Attila's Camp",          ScenarioItem(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_2_VILLAGERS =     1004, "Attila, The Great Ride: Villagers",                  ScenarioItem(Age2ScenarioData.AP_ATTILA_2)
    AP_ATTILA_3_RED_GOLD =      1005, "Attila, The Walls of Constantinople: Red Gold",      ScenarioItem(Age2ScenarioData.AP_ATTILA_3)
    AP_ATTILA_3_GREEN_GOLD =    1006, "Attila, The Walls of Constantinople: Green Gold",    ScenarioItem(Age2ScenarioData.AP_ATTILA_3)
    
    # Joan of Arc
    AP_JOAN_1_TRANSPORT =       1007, "Joan of Arc, An Unlikely Messiah: Transport Ships",          ScenarioItem(Age2ScenarioData.AP_JOAN_1)
    AP_JOAN_2_ORLEANS =         1008, "Joan of Arc, The Maid of Orleans: Orleans",                  ScenarioItem(Age2ScenarioData.AP_JOAN_2)
    AP_JOAN_2_TRADE_CARTS =     1009, "Joan of Arc, The Maid of Orleans: Trade Carts",              ScenarioItem(Age2ScenarioData.AP_JOAN_2)
    AP_JOAN_2_DOCK =            1010, "Joan of Arc, The Maid of Orleans: Dock",                     ScenarioItem(Age2ScenarioData.AP_JOAN_2)
    AP_JOAN_3_TRANSPORT =       1011, "Joan of Arc, The Cleansing of the Loire: Transport Ships",   ScenarioItem(Age2ScenarioData.AP_JOAN_3)
    AP_JOAN_4_FRENCH_CAMP =     1012, "Joan of Arc, The Rising: French Camp",                       ScenarioItem(Age2ScenarioData.AP_JOAN_4)
    AP_JOAN_5_REFUGEE_1 =       1013, "Joan of Arc, The Siege of Paris: Refugee 1",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_2 =       1014, "Joan of Arc, The Siege of Paris: Refugee 2",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_3 =       1015, "Joan of Arc, The Siege of Paris: Refugee 3",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_4 =       1016, "Joan of Arc, The Siege of Paris: Refugee 4",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_5 =       1017, "Joan of Arc, The Siege of Paris: Refugee 5",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_6 =       1018, "Joan of Arc, The Siege of Paris: Refugee 6",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_7 =       1019, "Joan of Arc, The Siege of Paris: Refugee 7",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_8 =       1020, "Joan of Arc, The Siege of Paris: Refugee 8",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_9 =       1021, "Joan of Arc, The Siege of Paris: Refugee 9",                 ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_REFUGEE_10 =      1022, "Joan of Arc, The Siege of Paris: Refugee 10",                ScenarioItem(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_6_ARMY =            1023, "Joan of Arc, A Perfect Martyr: French Army",                 ScenarioItem(Age2ScenarioData.AP_JOAN_6)
    
    #3000 - 3999 = Scenarios (500), Campaigns (100)
    
    # Progressive Scenarios (Campaign Count - 1)
    PROGRESSIVE_ATTILA_SCENARIO = 3000, "Progressive Attila Scenario", ProgressiveScenario(Age2CampaignData.ATTILA, 5)
    PROGRESSIVE_JOAN_SCENARIO = 3001, "Progressive Joan of Arc Scenario", ProgressiveScenario(Age2CampaignData.JOAN, 5)
    
    # Campaign Unlocks (Unlocks first level)
    ATTILA_THE_HUN = 3500, "Attila the Hun Campaign", Campaign(Age2CampaignData.ATTILA)
    JOAN_OF_ARC = 3501, "Joan of Arc Campaign", Campaign(Age2CampaignData.JOAN)
    
    #3600 - 3999 = Techs

    TECH_ELITE_TARKAN_HUNS                  = 3600, "Elite Tarkan (Huns)",                  Tech(2, 454, 17, Age2AgeData.IMPERIAL, True, True)
    TECH_YEOMEN_BRITONS                     = 3601, "Yeomen (Britons)",                     Tech(3, 455, 1, Age2AgeData.CASTLE, False, True)
    TECH_COTTON_ARMORS_MAYANS               = 3602, "Cotton Armors (Mayans)",               Tech(4, 456, 16, Age2AgeData.IMPERIAL, False, True)
    TECH_FUROR_CELTICA_CELTS                = 3603, "Furor Celtica (Celts)",                Tech(5, 239, 13, Age2AgeData.IMPERIAL, False, True)
    TECH_DRILL_MONGOLS                      = 3604, "Drill (Mongols)",                      Tech(6, 457, 12, Age2AgeData.IMPERIAL, False, True)
    TECH_CITADELS_PERSIANS                  = 3605, "Citadels (Persians)",                  Tech(7, 458, 8, Age2AgeData.IMPERIAL, False, True)
    TECH_TOWN_WATCH                         = 3606, "Town Watch",                           Tech(8, 8, -1, Age2AgeData.FEUDAL, False, False)
    TECH_ARTILLERY_TURKS                    = 3607, "Artillery (Turks)",                    Tech(10, 460, 10, Age2AgeData.IMPERIAL, False, True)
    TECH_CRENELLATIONS_TEUTONS              = 3608, "Crenellations (Teutons)",              Tech(11, 461, 4, Age2AgeData.IMPERIAL, False, True)
    TECH_CROP_ROTATION                      = 3609, "Crop Rotation",                        Tech(12, 12, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_HEAVY_PLOW                         = 3610, "Heavy Plow",                           Tech(13, 13, -1, Age2AgeData.CASTLE, False, False)
    TECH_HORSE_COLLAR                       = 3611, "Horse Collar",                         Tech(14, 14, -1, Age2AgeData.FEUDAL, False, False)
    TECH_GUILDS                             = 3612, "Guilds",                               Tech(15, 15, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_ANARCHY_GOTHS                      = 3613, "Anarchy (Goths)",                      Tech(16, 462, 3, Age2AgeData.CASTLE, False, True)
    TECH_BANKING                            = 3614, "Banking",                              Tech(17, 17, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_ATHEISM_HUNS                       = 3615, "Atheism (Huns)",                       Tech(21, 464, 17, Age2AgeData.IMPERIAL, False, True)
    TECH_LOOM                               = 3616, "Loom",                                 Tech(22, 22, -1, Age2AgeData.DARK, False, False)
    TECH_COINAGE                            = 3617, "Coinage",                              Tech(23, 23, -1, Age2AgeData.CASTLE, False, False)
    TECH_GARLAND_WARS_AZTECS                = 3618, "Garland Wars (Aztecs)",                Tech(24, 465, 15, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_PLUMED_ARCHER_MAYANS         = 3619, "Elite Plumed Archer (Mayans)",         Tech(27, 469, 16, Age2AgeData.IMPERIAL, True, True)
    TECH_BIMARISTAN_SARACENS                = 3620, "Bimaristan (Saracens)",                Tech(28, 28, 9, Age2AgeData.CASTLE, False, True)
    TECH_WARSHIPS                           = 3621, "Warships",                             Tech(34, 155, -1, Age2AgeData.CASTLE, True, False)
    TECH_HEAVY_WARSHIPS                     = 3622, "Heavy Warships",                       Tech(35, -1, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_HUSBANDRY                          = 3623, "Husbandry",                            Tech(39, 39, -1, Age2AgeData.CASTLE, False, False)
    TECH_EXORCISM                           = 3624, "Exorcism",                             Tech(45, 45, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_DEVOTION                           = 3625, "Devotion",                             Tech(46, 46, -1, Age2AgeData.CASTLE, False, False)
    TECH_FLAMING_ARROWS                     = 3626, "Flaming Arrows",                       Tech(47, 47, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_CARAVAN                            = 3627, "Caravan",                              Tech(48, 482, -1, Age2AgeData.CASTLE, False, False)
    TECH_BOGSVEIGAR_VIKINGS                 = 3628, "Bogsveigar (Vikings)",                 Tech(49, 467, 11, Age2AgeData.IMPERIAL, False, True)
    TECH_MASONRY                            = 3629, "Masonry",                              Tech(50, 50, -1, Age2AgeData.CASTLE, False, False)
    TECH_ARCHITECTURE                       = 3630, "Architecture",                         Tech(51, 51, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_ROCKETRY_CHINESE                   = 3631, "Rocketry (Chinese)",                   Tech(52, 483, 6, Age2AgeData.IMPERIAL, False, True)
    TECH_TREADMILL_CRANE                    = 3632, "Treadmill Crane",                      Tech(54, 54, -1, Age2AgeData.CASTLE, False, False)
    TECH_GOLD_MINING                        = 3633, "Gold Mining",                          Tech(55, 55, -1, Age2AgeData.FEUDAL, False, False)
    TECH_KATAPARUTO_JAPANESE                = 3634, "Kataparuto (Japanese)",                Tech(59, 59, 5, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_CONQUISTADOR_SPANISH         = 3635, "Elite Conquistador (Spanish)",         Tech(60, 492, 14, Age2AgeData.IMPERIAL, True, True)
    TECH_LOGISTICA_BYZANTINES               = 3636, "Logistica (Byzantines)",               Tech(61, 493, 7, Age2AgeData.IMPERIAL, False, True)
    TECH_BASTION                            = 3637, "Bastion",                              Tech(63, 63, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_BOMBARD_TOWER_TECH                 = 3638, "Bombard Tower (Tech)",                 Tech(64, 64, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_GILLNETS                           = 3639, "Gillnets",                             Tech(65, 24, -1, Age2AgeData.CASTLE, False, False)
    TECH_FORGING                            = 3640, "Forging",                              Tech(67, 67, -1, Age2AgeData.FEUDAL, False, False)
    TECH_IRON_CASTING                       = 3641, "Iron Casting",                         Tech(68, 68, -1, Age2AgeData.CASTLE, False, False)
    TECH_SCALE_MAIL_ARMOR                   = 3642, "Scale Mail Armor",                     Tech(74, 74, -1, Age2AgeData.FEUDAL, False, False)
    TECH_BLAST_FURNACE                      = 3643, "Blast Furnace",                        Tech(75, 75, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_CHAIN_MAIL_ARMOR                   = 3644, "Chain Mail Armor",                     Tech(76, 76, -1, Age2AgeData.CASTLE, False, False)
    TECH_PLATE_MAIL_ARMOR                   = 3645, "Plate Mail Armor",                     Tech(77, 77, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_PLATE_BARDING_ARMOR                = 3646, "Plate Barding Armor",                  Tech(80, 80, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_SCALE_BARDING_ARMOR                = 3647, "Scale Barding Armor",                  Tech(81, 81, -1, Age2AgeData.FEUDAL, False, False)
    TECH_CHAIN_BARDING_ARMOR                = 3648, "Chain Barding Armor",                  Tech(82, 82, -1, Age2AgeData.CASTLE, False, False)
    TECH_BEARDED_AXE_FRANKS                 = 3649, "Bearded Axe (Franks)",                 Tech(83, 291, 2, Age2AgeData.CASTLE, False, True)
    TECH_TARGET_PRACTICE                    = 3650, "Target Practice",                      Tech(93, 93, -1, Age2AgeData.CASTLE, False, False)
    TECH_CAPPED_RAM                         = 3651, "Capped Ram",                           Tech(96, 96, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_SKIRMISHER                   = 3652, "Elite Skirmisher",                     Tech(98, 164, -1, Age2AgeData.CASTLE, True, False)
    TECH_CROSSBOWMAN                        = 3653, "Crossbowman",                          Tech(100, 163, -1, Age2AgeData.CASTLE, True, False)
    TECH_GUARD_TOWER                        = 3654, "Guard Tower",                          Tech(140, 139, -1, Age2AgeData.CASTLE, False, False)
    TECH_GOLD_SHAFT_MINING                  = 3655, "Gold Shaft Mining",                    Tech(182, 178, -1, Age2AgeData.CASTLE, False, False)
    TECH_FORTIFIED_WALL                     = 3656, "Fortified Wall",                       Tech(194, 187, -1, Age2AgeData.CASTLE, False, False)
    TECH_PIKEMAN                            = 3657, "Pikeman",                              Tech(197, 190, -1, Age2AgeData.CASTLE, True, False)
    TECH_FLETCHING                          = 3658, "Fletching",                            Tech(199, 192, -1, Age2AgeData.FEUDAL, False, False)
    TECH_BODKIN_ARROW                       = 3659, "Bodkin Arrow",                         Tech(200, 193, -1, Age2AgeData.CASTLE, False, False)
    TECH_BRACER                             = 3660, "Bracer",                               Tech(201, 194, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_DOUBLE_BIT_AXE                     = 3661, "Double-Bit Axe",                       Tech(202, 195, -1, Age2AgeData.FEUDAL, False, False)
    TECH_BOW_SAW                            = 3662, "Bow Saw",                              Tech(203, 196, -1, Age2AgeData.CASTLE, False, False)
    TECH_LONG_SWORDSMAN                     = 3663, "Long Swordsman",                       Tech(207, 182, -1, Age2AgeData.CASTLE, True, False)
    TECH_CAVALIER                           = 3664, "Cavalier",                             Tech(209, 175, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_PADDED_ARCHER_ARMOR                = 3665, "Padded Archer Armor",                  Tech(211, 202, -1, Age2AgeData.FEUDAL, False, False)
    TECH_LEATHER_ARCHER_ARMOR               = 3666, "Leather Archer Armor",                 Tech(212, 203, -1, Age2AgeData.CASTLE, False, False)
    TECH_WHEELBARROW                        = 3667, "Wheelbarrow",                          Tech(213, 200, -1, Age2AgeData.FEUDAL, False, False)
    TECH_SQUIRES                            = 3668, "Squires",                              Tech(215, 204, -1, Age2AgeData.CASTLE, False, False)
    TECH_TWO_HANDED_SWORDSMAN               = 3669, "Two-Handed Swordsman",                 Tech(217, 206, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_HEAVY_CAVALRY_ARCHER               = 3670, "Heavy Cavalry Archer",                 Tech(218, 207, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_RING_ARCHER_ARMOR                  = 3671, "Ring Archer Armor",                    Tech(219, 208, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_TWO_MAN_SAW                        = 3672, "Two-Man Saw",                          Tech(221, 210, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_MAN_AT_ARMS                        = 3673, "Man-at-Arms",                          Tech(222, 211, -1, Age2AgeData.FEUDAL, True, False)
    TECH_HARUSPICY                          = 3674, "Haruspicy",                            Tech(230, 220, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_AMULET_PROTECTION                  = 3675, "Amulet Protection",                    Tech(231, 221, -1, Age2AgeData.CASTLE, False, False)
    TECH_PURIFICATION                       = 3676, "Purification",                         Tech(233, 219, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_HEAVY_CAMEL_RIDER                  = 3677, "Heavy Camel Rider",                    Tech(236, 225, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ARBALESTER                         = 3678, "Arbalester",                           Tech(237, 226, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_HEAVY_SCORPION                     = 3679, "Heavy Scorpion",                       Tech(239, 228, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_HEAVY_DEMOLITION_SHIP              = 3680, "Heavy Demolition Ship",                Tech(244, 233, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_HAND_CART                          = 3681, "Hand Cart",                            Tech(249, 238, -1, Age2AgeData.CASTLE, False, False)
    TECH_FERVOR                             = 3682, "Fervor",                               Tech(252, 241, -1, Age2AgeData.CASTLE, False, False)
    TECH_LIGHT_CAVALRY                      = 3683, "Light Cavalry",                        Tech(254, 245, -1, Age2AgeData.CASTLE, True, False)
    TECH_SIEGE_RAM                          = 3684, "Siege Ram",                            Tech(255, 246, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ONAGER                             = 3685, "Onager",                               Tech(257, 247, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_CHAMPION                           = 3686, "Champion",                             Tech(264, 252, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_PALADIN                            = 3687, "Paladin",                              Tech(265, 253, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_STONE_MINING                       = 3688, "Stone Mining",                         Tech(278, 278, -1, Age2AgeData.FEUDAL, False, False)
    TECH_STONE_SHAFT_MINING                 = 3689, "Stone Shaft Mining",                   Tech(279, 279, -1, Age2AgeData.CASTLE, False, False)
    TECH_TOWN_PATROL                        = 3690, "Town Patrol",                          Tech(280, 280, -1, Age2AgeData.CASTLE, False, False)
    TECH_CONSCRIPTION                       = 3691, "Conscription",                         Tech(315, 315, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_SACRIFICIAL_DEDICATION             = 3692, "Sacrificial Dedication",               Tech(316, 316, -1, Age2AgeData.CASTLE, False, False)
    TECH_SYNCRETISM                         = 3693, "Syncretism",                           Tech(319, 319, -1, Age2AgeData.CASTLE, False, False)
    TECH_SIEGE_ONAGER                       = 3694, "Siege Onager",                         Tech(320, 320, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_SAPPERS                            = 3695, "Sappers",                              Tech(321, 321, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_MURDER_HOLES                       = 3696, "Murder Holes",                         Tech(322, 236, -1, Age2AgeData.CASTLE, False, False)
    TECH_ELITE_LONGBOWMAN_BRITONS           = 3697, "Elite Longbowman (Britons)",           Tech(360, 358, 1, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_CATAPHRACT_BYZANTINES        = 3698, "Elite Cataphract (Byzantines)",        Tech(361, 359, 7, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_CHU_KO_NU_CHINESE            = 3699, "Elite Chu Ko Nu (Chinese)",            Tech(362, 360, 6, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_THROWING_AXEMAN_FRANKS       = 3700, "Elite Throwing Axeman (Franks)",       Tech(363, 361, 2, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_TEUTONIC_KNIGHT_TEUTONS      = 3701, "Elite Teutonic Knight (Teutons)",      Tech(364, 362, 4, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_HUSKARL_GOTHS                = 3702, "Elite Huskarl (Goths)",                Tech(365, 363, 3, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_SAMURAI_JAPANESE             = 3703, "Elite Samurai (Japanese)",             Tech(366, 364, 5, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_WAR_ELEPHANT_PERSIANS        = 3704, "Elite War Elephant (Persians)",        Tech(367, 365, 8, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_MAMELUKE_SARACENS            = 3705, "Elite Mameluke (Saracens)",            Tech(368, 366, 9, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_JANISSARY_TURKS              = 3706, "Elite Janissary (Turks)",              Tech(369, 367, 10, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_WOAD_RAIDER_CELTS            = 3707, "Elite Woad Raider (Celts)",            Tech(370, 368, 13, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_MANGUDAI_MONGOLS             = 3708, "Elite Mangudai (Mongols)",             Tech(371, 369, 12, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_LONGBOAT_VIKINGS             = 3709, "Elite Longboat (Vikings)",             Tech(372, 370, 11, Age2AgeData.IMPERIAL, True, True)
    TECH_SHIPWRIGHT                         = 3710, "Shipwright",                           Tech(373, 371, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_CAREENING                          = 3711, "Careening",                            Tech(374, 372, -1, Age2AgeData.CASTLE, False, False)
    TECH_DRY_DOCK                           = 3712, "Dry Dock",                             Tech(375, 373, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_ELITE_CANNON_GALLEON               = 3713, "Elite Cannon Galleon",                 Tech(376, 374, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_SIEGE_ENGINEERS                    = 3714, "Siege Engineers",                      Tech(377, 375, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_HOARDINGS                          = 3715, "Hoardings",                            Tech(379, 377, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_LIGHTHOUSE                         = 3716, "Lighthouse",                           Tech(380, 378, -1, Age2AgeData.CASTLE, False, False)
    TECH_EAGLE_WARRIOR                      = 3717, "Eagle Warrior",                        Tech(384, 558, -1, Age2AgeData.CASTLE, True, False)
    TECH_ELITE_BERSERK_VIKINGS              = 3718, "Elite Berserk (Vikings)",              Tech(398, 397, 11, Age2AgeData.IMPERIAL, True, True)
    TECH_SPIES_TREASON                      = 3719, "Spies/Treason",                        Tech(408, 420, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_HUSSAR                             = 3720, "Hussar",                               Tech(428, 439, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_HALBERDIER                         = 3721, "Halberdier",                           Tech(429, 189, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_JAGUAR_WARRIOR_AZTECS        = 3722, "Elite Jaguar Warrior (Aztecs)",        Tech(432, 444, 15, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_EAGLE_WARRIOR                = 3723, "Elite Eagle Warrior",                  Tech(434, 445, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_BLOODLINES                         = 3724, "Bloodlines",                           Tech(435, 450, -1, Age2AgeData.FEUDAL, False, False)
    TECH_PARTHIAN_TACTICS                   = 3725, "Parthian Tactics",                     Tech(436, 452, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_THUMB_RING                         = 3726, "Thumb Ring",                           Tech(437, 451, -1, Age2AgeData.CASTLE, False, False)
    TECH_MYSTERY_CULTS                      = 3727, "Mystery Cults",                        Tech(438, 494, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_HEMLOCK                            = 3728, "Hemlock",                              Tech(439, 188, -1, Age2AgeData.CASTLE, False, False)
    TECH_SUPREMACY_SPANISH                  = 3729, "Supremacy (Spanish)",                  Tech(440, 495, 14, Age2AgeData.IMPERIAL, False, True)
    TECH_HERBAL_MEDICINE                    = 3730, "Herbal Medicine",                      Tech(441, 41, -1, Age2AgeData.CASTLE, False, False)
    TECH_SHINKICHON_KOREANS                 = 3731, "Shinkichon (Koreans)",                 Tech(445, 506, 18, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_TURTLE_SHIP_KOREANS          = 3732, "Elite Turtle Ship (Koreans)",          Tech(448, 501, 18, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_WAR_WAGON_KOREANS            = 3733, "Elite War Wagon (Koreans)",            Tech(450, 503, 18, Age2AgeData.IMPERIAL, True, True)
    TECH_COUNTERWEIGHTS_SARACENS            = 3734, "Counterweights (Saracens)",            Tech(454, 480, 9, Age2AgeData.IMPERIAL, False, True)
    TECH_DETINETS_SLAVS                     = 3735, "Detinets (Slavs)",                     Tech(455, 481, 23, Age2AgeData.CASTLE, False, True)
    TECH_PERFUSION_GOTHS                    = 3736, "Perfusion (Goths)",                    Tech(457, 513, 3, Age2AgeData.IMPERIAL, False, True)
    TECH_ATLATL_AZTECS                      = 3737, "Atlatl (Aztecs)",                      Tech(460, 514, 15, Age2AgeData.CASTLE, False, True)
    TECH_WARWOLF_BRITONS                    = 3738, "Warwolf (Britons)",                    Tech(461, 540, 1, Age2AgeData.IMPERIAL, False, True)
    TECH_GREAT_WALL_CHINESE                 = 3739, "Great Wall (Chinese)",                 Tech(462, 516, 6, Age2AgeData.CASTLE, False, True)
    TECH_CHIEFTAINS_VIKINGS                 = 3740, "Chieftains (Vikings)",                 Tech(463, 517, 11, Age2AgeData.CASTLE, False, True)
    TECH_GREEK_FIRE_BYZANTINES              = 3741, "Greek Fire (Byzantines)",              Tech(464, 518, 7, Age2AgeData.CASTLE, False, True)
    TECH_ELITE_GENOESE_CROSSBOWMAN_ITALIANS = 3742, "Elite Genoese Crossbowman (Italians)", Tech(468, 520, 19, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_MAGYAR_HUSZAR_MAGYAR         = 3743, "Elite Magyar Huszar (Magyar)",         Tech(472, 526, 22, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_ELEPHANT_ARCHER              = 3744, "Elite Elephant Archer",                Tech(481, 536, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_STRONGHOLD_CELTS                   = 3745, "Stronghold (Celts)",                   Tech(482, 537, 13, Age2AgeData.CASTLE, False, True)
    TECH_MARAUDERS_HUNS                     = 3746, "Marauders (Huns)",                     Tech(483, 538, 17, Age2AgeData.CASTLE, False, True)
    TECH_YASAMA_JAPANESE                    = 3747, "Yasama (Japanese)",                    Tech(484, 539, 5, Age2AgeData.CASTLE, False, True)
    TECH_OBSIDIAN_ARROWS_MAYANS             = 3748, "Obsidian Arrows (Mayans)",             Tech(485, 515, 16, Age2AgeData.CASTLE, False, True)
    TECH_EUPSEONG_KOREANS                   = 3749, "Eupseong (Koreans)",                   Tech(486, 541, 18, Age2AgeData.CASTLE, False, True)
    TECH_NOMADS_MONGOLS                     = 3750, "Nomads (Mongols)",                     Tech(487, 542, 12, Age2AgeData.CASTLE, False, True)
    TECH_KAMANDARAN_PERSIANS                = 3751, "Kamandaran (Persians)",                Tech(488, 543, 8, Age2AgeData.CASTLE, False, True)
    TECH_IRONCLAD_TEUTONS                   = 3752, "Ironclad (Teutons)",                   Tech(489, 544, 4, Age2AgeData.CASTLE, False, True)
    TECH_SIPAHI_TURKS                       = 3753, "Sipahi (Turks)",                       Tech(491, 546, 10, Age2AgeData.CASTLE, False, True)
    TECH_INQUISITION_SPANISH                = 3754, "Inquisition (Spanish)",                Tech(492, 547, 14, Age2AgeData.CASTLE, False, True)
    TECH_CHIVALRY_FRANKS                    = 3755, "Chivalry (Franks)",                    Tech(493, 548, 2, Age2AgeData.IMPERIAL, False, True)
    TECH_SILK_ROAD_ITALIANS                 = 3756, "Silk Road (Italians)",                 Tech(499, 554, 19, Age2AgeData.CASTLE, False, True)
    TECH_ELITE_BOYAR_SLAVS                  = 3757, "Elite Boyar (Slavs)",                  Tech(504, 557, 23, Age2AgeData.IMPERIAL, True, True)
    TECH_GRAND_TRUNK_ROAD_INDIANS           = 3758, "Grand Trunk Road (Indians)",           Tech(506, 562, 20, Age2AgeData.CASTLE, False, True)
    TECH_SHATAGNI_INDIANS                   = 3759, "Shatagni (Indians)",                   Tech(507, 563, 20, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_KAMAYUK_INCAS                = 3760, "Elite Kamayuk (Incas)",                Tech(509, 565, 21, Age2AgeData.IMPERIAL, True, True)
    TECH_DRUZHINA_SLAVS                     = 3761, "Druzhina (Slavs)",                     Tech(513, 569, 23, Age2AgeData.IMPERIAL, False, True)
    TECH_CORVINIAN_ARMY_MAGYAR              = 3762, "Corvinian Army (Magyar)",              Tech(514, 571, 22, Age2AgeData.CASTLE, False, True)
    TECH_RECURVE_BOW_MAGYAR                 = 3763, "Recurve Bow (Magyar)",                 Tech(515, 570, 22, Age2AgeData.IMPERIAL, False, True)
    TECH_ANDEAN_SLING_INCAS                 = 3764, "Andean Sling (Incas)",                 Tech(516, 572, 21, Age2AgeData.CASTLE, False, True)
    TECH_FABRIC_SHIELDS_INCAS               = 3765, "Fabric Shields (Incas)",               Tech(517, 573, 21, Age2AgeData.IMPERIAL, False, True)
    TECH_IMPERIAL_CAMEL_RIDER_INDIANS       = 3766, "Imperial Camel Rider (Indians)",       Tech(521, 577, 20, Age2AgeData.IMPERIAL, True, True)
    TECH_SAVAR_PERSIANS                     = 3767, "Savar (Persians)",                     Tech(526, 581, 8, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_ORGAN_GUN_PORTUGUESE         = 3768, "Elite Organ Gun (Portuguese)",         Tech(563, 592, 24, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_CAMEL_ARCHER_BERBERS         = 3769, "Elite Camel Archer (Berbers)",         Tech(565, 595, 27, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_GBETO_MALIANS                = 3770, "Elite Gbeto (Malians)",                Tech(567, 597, 26, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_SHOTEL_WARRIOR_ETHIOPIANS    = 3771, "Elite Shotel Warrior (Ethiopians)",    Tech(569, 599, 25, Age2AgeData.IMPERIAL, True, True)
    TECH_ARQUEBUS_PORTUGUESE                = 3772, "Arquebus (Portuguese)",                Tech(573, 602, 24, Age2AgeData.IMPERIAL, False, True)
    TECH_ROYAL_HEIRS_ETHIOPIANS             = 3773, "Royal Heirs (Ethiopians)",             Tech(574, 603, 25, Age2AgeData.CASTLE, False, True)
    TECH_TORSION_ENGINES_ETHIOPIANS         = 3774, "Torsion Engines (Ethiopians)",         Tech(575, 604, 25, Age2AgeData.IMPERIAL, False, True)
    TECH_TIGUI_MALIANS                      = 3775, "Tigui (Malians)",                      Tech(576, 605, 26, Age2AgeData.CASTLE, False, True)
    TECH_FARIMBA_MALIANS                    = 3776, "Farimba (Malians)",                    Tech(577, 606, 26, Age2AgeData.IMPERIAL, False, True)
    TECH_KASBAH_BERBERS                     = 3777, "Kasbah (Berbers)",                     Tech(578, 607, 27, Age2AgeData.CASTLE, False, True)
    TECH_MAGHREBI_CAMELS_BERBERS            = 3778, "Maghrebi Camels (Berbers)",            Tech(579, 608, 27, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_CARAVEL_PORTUGUESE           = 3779, "Elite Caravel (Portuguese)",           Tech(597, 623, 24, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_GENITOUR                     = 3780, "Elite Genitour",                       Tech(599, 625, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ARSON                              = 3781, "Arson",                                Tech(602, 628, -1, Age2AgeData.FEUDAL, False, False)
    TECH_ARROWSLITS                         = 3782, "Arrowslits",                           Tech(608, 633, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_ELITE_BALLISTA_ELEPHANT_KHMER      = 3783, "Elite Ballista Elephant (Khmer)",      Tech(615, 655, 28, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_KARAMBIT_WARRIOR_MALAY       = 3784, "Elite Karambit Warrior (Malay)",       Tech(617, 657, 29, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_ARAMBAI_BURMESE              = 3785, "Elite Arambai (Burmese)",              Tech(619, 659, 30, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_RATTAN_ARCHER_VIETNAMESE     = 3786, "Elite Rattan Archer (Vietnamese)",     Tech(621, 661, 31, Age2AgeData.IMPERIAL, True, True)
    TECH_TUSK_SWORDS_KHMER                  = 3787, "Tusk Swords (Khmer)",                  Tech(622, 662, 28, Age2AgeData.CASTLE, False, True)
    TECH_DOUBLE_CROSSBOW_KHMER              = 3788, "Double Crossbow (Khmer)",              Tech(623, 663, 28, Age2AgeData.IMPERIAL, False, True)
    TECH_THALASSOCRACY_MALAY                = 3789, "Thalassocracy (Malay)",                Tech(624, 664, 29, Age2AgeData.CASTLE, False, True)
    TECH_FORCED_LEVY_MALAY                  = 3790, "Forced Levy (Malay)",                  Tech(625, 665, 29, Age2AgeData.IMPERIAL, False, True)
    TECH_HOWDAH_BURMESE                     = 3791, "Howdah (Burmese)",                     Tech(626, 666, 30, Age2AgeData.IMPERIAL, False, True)
    TECH_MANIPUR_CAVALRY_BURMESE            = 3792, "Manipur Cavalry (Burmese)",            Tech(627, 667, 30, Age2AgeData.CASTLE, False, True)
    TECH_CHATRAS_VIETNAMESE                 = 3793, "Chatras (Vietnamese)",                 Tech(628, 668, 31, Age2AgeData.CASTLE, False, True)
    TECH_PAPER_MONEY_VIETNAMESE             = 3794, "Paper Money (Vietnamese)",             Tech(629, 669, 31, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_BATTLE_ELEPHANT              = 3795, "Elite Battle Elephant",                Tech(631, 671, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_IMPERIAL_SKIRMISHER                = 3796, "Imperial Skirmisher",                  Tech(655, 691, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_KONNIK_BULGARIANS            = 3797, "Elite Konnik (Bulgarians)",            Tech(678, 715, 32, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_KESHIK_TATARS                = 3798, "Elite Keshik (Tatars)",                Tech(680, 717, 33, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_KIPCHAK_CUMANS               = 3799, "Elite Kipchak (Cumans)",               Tech(682, 719, 34, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_LEITIS_LITHUANIANS           = 3800, "Elite Leitis (Lithuanians)",           Tech(684, 721, 35, Age2AgeData.IMPERIAL, True, True)
    TECH_STIRRUPS_BULGARIANS                = 3801, "Stirrups (Bulgarians)",                Tech(685, 722, 32, Age2AgeData.CASTLE, False, True)
    TECH_BAGAINS_BULGARIANS                 = 3802, "Bagains (Bulgarians)",                 Tech(686, 723, 32, Age2AgeData.IMPERIAL, False, True)
    TECH_SILK_ARMOR_TATARS                  = 3803, "Silk Armor (Tatars)",                  Tech(687, 724, 33, Age2AgeData.CASTLE, False, True)
    TECH_TIMURID_SIEGECRAFT_TATARS          = 3804, "Timurid Siegecraft (Tatars)",          Tech(688, 725, 33, Age2AgeData.IMPERIAL, False, True)
    TECH_STEPPE_HUSBANDRY_CUMANS            = 3805, "Steppe Husbandry (Cumans)",            Tech(689, 726, 34, Age2AgeData.CASTLE, False, True)
    TECH_CUMAN_MERCENARIES_CUMANS           = 3806, "Cuman Mercenaries (Cumans)",           Tech(690, 727, 34, Age2AgeData.IMPERIAL, False, True)
    TECH_HILL_FORTS_LITHUANIANS             = 3807, "Hill Forts (Lithuanians)",             Tech(691, 728, 35, Age2AgeData.CASTLE, False, True)
    TECH_TOWER_SHIELDS_LITHUANIANS          = 3808, "Tower Shields (Lithuanians)",          Tech(692, 729, 35, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_STEPPE_LANCER                = 3809, "Elite Steppe Lancer",                  Tech(715, 752, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_COUSTILLIER_BURGUNDIANS      = 3810, "Elite Coustillier (Burgundians)",      Tech(751, 787, 36, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_SERJEANT_SICILIANS           = 3811, "Elite Serjeant (Sicilians)",           Tech(753, 789, 37, Age2AgeData.IMPERIAL, True, True)
    TECH_BURGUNDIAN_VINEYARDS_BURGUNDIANS   = 3812, "Burgundian Vineyards (Burgundians)",   Tech(754, 790, 36, Age2AgeData.CASTLE, False, True)
    TECH_FLEMISH_REVOLUTION_BURGUNDIANS     = 3813, "Flemish Revolution (Burgundians)",     Tech(755, 791, 36, Age2AgeData.IMPERIAL, False, True)
    TECH_FIRST_CRUSADE_SICILIANS            = 3814, "First Crusade (Sicilians)",            Tech(756, 792, 37, Age2AgeData.CASTLE, False, True)
    TECH_HAUBERK_SICILIANS                  = 3815, "Hauberk (Sicilians)",                  Tech(757, 793, 37, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_OBUCH_POLES                  = 3816, "Elite Obuch (Poles)",                  Tech(779, 806, 38, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_HUSSITE_WAGON_BOHEMIANS      = 3817, "Elite Hussite Wagon (Bohemians)",      Tech(781, 808, 39, Age2AgeData.IMPERIAL, True, True)
    TECH_SZLACHTA_PRIVILEGES_POLES          = 3818, "Szlachta Privileges (Poles)",          Tech(782, 809, 38, Age2AgeData.CASTLE, False, True)
    TECH_LECHITIC_LEGACY_POLES              = 3819, "Lechitic Legacy (Poles)",              Tech(783, 810, 38, Age2AgeData.IMPERIAL, False, True)
    TECH_EASTERN_SETTLEMENT_BOHEMIANS       = 3820, "Eastern Settlement (Bohemians)",       Tech(784, 811, 39, Age2AgeData.CASTLE, False, True)
    TECH_HUSSITE_REFORMS_BOHEMIANS          = 3821, "Hussite Reforms (Bohemians)",          Tech(785, 812, 39, Age2AgeData.IMPERIAL, False, True)
    TECH_WINGED_HUSSAR                      = 3822, "Winged Hussar",                        Tech(786, 813, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_HOUFNICE_BOHEMIANS                 = 3823, "Houfnice (Bohemians)",                 Tech(787, 814, 39, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_URUMI_SWORDSMAN_DRAVIDIANS   = 3824, "Elite Urumi Swordsman (Dravidians)",   Tech(826, 845, 40, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_RATHA_BENGALIS               = 3825, "Elite Ratha (Bengalis)",               Tech(828, 847, 41, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_CHAKRAM_THROWER_GURJARAS     = 3826, "Elite Chakram Thrower (Gurjaras)",     Tech(830, 849, 42, Age2AgeData.IMPERIAL, True, True)
    TECH_MEDICAL_CORPS_DRAVIDIANS           = 3827, "Medical Corps (Dravidians)",           Tech(831, 850, 40, Age2AgeData.CASTLE, False, True)
    TECH_WOOTZ_STEEL_DRAVIDIANS             = 3828, "Wootz Steel (Dravidians)",             Tech(832, 851, 40, Age2AgeData.IMPERIAL, False, True)
    TECH_PAIKS_BENGALIS                     = 3829, "Paiks (Bengalis)",                     Tech(833, 852, 41, Age2AgeData.CASTLE, False, True)
    TECH_MAHAYANA_BENGALIS                  = 3830, "Mahayana (Bengalis)",                  Tech(834, 853, 41, Age2AgeData.IMPERIAL, False, True)
    TECH_KSHATRIYAS_GURJARAS                = 3831, "Kshatriyas (Gurjaras)",                Tech(835, 854, 42, Age2AgeData.CASTLE, False, True)
    TECH_FRONTIER_GUARDS_GURJARAS           = 3832, "Frontier Guards (Gurjaras)",           Tech(836, 855, 42, Age2AgeData.IMPERIAL, False, True)
    TECH_SIEGE_ELEPHANT                     = 3833, "Siege Elephant",                       Tech(838, 857, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_GHULAM_INDIANS               = 3834, "Elite Ghulam (Indians)",               Tech(840, 859, 20, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_SHRIVAMSHA_RIDER_GURJARAS    = 3835, "Elite Shrivamsha Rider (Gurjaras)",    Tech(843, 862, 42, Age2AgeData.IMPERIAL, True, True)
    TECH_GAMBESONS                          = 3836, "Gambesons",                            Tech(875, 886, -1, Age2AgeData.CASTLE, False, False)
    TECH_ELITE_CENTURION_ROMANS             = 3837, "Elite Centurion (Romans)",             Tech(882, 893, 43, Age2AgeData.IMPERIAL, True, True)
    TECH_BALLISTAS_ROMANS                   = 3838, "Ballistas (Romans)",                   Tech(883, 894, 43, Age2AgeData.CASTLE, False, True)
    TECH_COMITATENSES_ROMANS                = 3839, "Comitatenses (Romans)",                Tech(884, 895, 43, Age2AgeData.IMPERIAL, False, True)
    TECH_LEGIONARY_ROMANS                   = 3840, "Legionary (Romans)",                   Tech(885, 896, 43, Age2AgeData.IMPERIAL, True, True)
    TECH_PIROTECHNIA_ITALIANS               = 3841, "Pirotechnia (Italians)",               Tech(902, 904, 19, Age2AgeData.IMPERIAL, False, True)
    TECH_DEMOLITION_SHIP                    = 3842, "Demolition Ship",                      Tech(905, 912, -1, Age2AgeData.CASTLE, True, False)
    TECH_FISHING_LINES                      = 3843, "Fishing Lines",                        Tech(906, 913, -1, Age2AgeData.FEUDAL, False, False)
    TECH_CARVEL_HULL                        = 3844, "Carvel Hull",                          Tech(907, 909, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_CLINKER_CONSTRUCTION               = 3845, "Clinker Construction",                 Tech(908, 908, -1, Age2AgeData.CASTLE, False, False)
    TECH_SIPHONS                            = 3846, "Siphons",                              Tech(909, 915, -1, Age2AgeData.CASTLE, False, False)
    TECH_INCENDIARIES                       = 3847, "Incendiaries",                         Tech(910, 916, -1, Age2AgeData.IMPERIAL, False, False)
    TECH_ELITE_COMPOSITE_BOWMAN_ARMENIANS   = 3848, "Elite Composite Bowman (Armenians)",   Tech(918, 930, 44, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_MONASPA_GEORGIANS            = 3849, "Elite Monaspa (Georgians)",            Tech(920, 932, 45, Age2AgeData.IMPERIAL, True, True)
    TECH_FERETERS_ARMENIANS                 = 3850, "Fereters (Armenians)",                 Tech(921, 933, 44, Age2AgeData.IMPERIAL, False, True)
    TECH_CILICIAN_FLEET_ARMENIANS           = 3851, "Cilician Fleet (Armenians)",           Tech(922, 934, 44, Age2AgeData.CASTLE, False, True)
    TECH_SVAN_TOWERS_GEORGIANS              = 3852, "Svan Towers (Georgians)",              Tech(923, 935, 45, Age2AgeData.CASTLE, False, True)
    TECH_AZNAURI_CAVALRY_GEORGIANS          = 3853, "Aznauri Cavalry (Georgians)",          Tech(924, 936, 45, Age2AgeData.IMPERIAL, False, True)
    TECH_HEAVY_ROCKET_CART                  = 3854, "Heavy Rocket Cart",                    Tech(980, 980, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_FIRE_LANCER                  = 3855, "Elite Fire Lancer",                    Tech(982, 982, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_IRON_PAGODA_JURCHENS         = 3856, "Elite Iron Pagoda (Jurchens)",         Tech(991, 991, 52, Age2AgeData.IMPERIAL, True, True)
    TECH_FORTIFIED_BASTIONS_JURCHENS        = 3857, "Fortified Bastions (Jurchens)",        Tech(996, 996, 52, Age2AgeData.CASTLE, False, True)
    TECH_THUNDERCLAP_BOMBS_JURCHENS         = 3858, "Thunderclap Bombs (Jurchens)",         Tech(997, 997, 52, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_LIAO_DAO_KHITANS             = 3859, "Elite Liao Dao (Khitans)",             Tech(1002, 1002, 53, Age2AgeData.IMPERIAL, True, True)
    TECH_LAMELLAR_ARMOR_KHITANS             = 3860, "Lamellar Armor (Khitans)",             Tech(1006, 1006, 53, Age2AgeData.CASTLE, False, True)
    TECH_ORDO_CAVALRY_KHITANS               = 3861, "Ordo Cavalry (Khitans)",               Tech(1007, 1007, 53, Age2AgeData.IMPERIAL, False, True)
    TECH_DRAGON_SHIP_CHINESE                = 3862, "Dragon Ship (Chinese)",                Tech(1010, 1010, 6, Age2AgeData.IMPERIAL, True, True)
    TECH_TRANSHUMANCE_KHITANS               = 3863, "Transhumance (Khitans)",               Tech(1012, 1012, 53, Age2AgeData.IMPERIAL, False, True)
    TECH_PASTORALISM_KHITANS                = 3864, "Pastoralism (Khitans)",                Tech(1013, 1013, 53, Age2AgeData.CASTLE, False, True)
    TECH_DOMESTICATION_KHITANS              = 3865, "Domestication (Khitans)",              Tech(1014, 1014, 53, Age2AgeData.FEUDAL, False, True)
    TECH_HEAVY_HEI_GUANG_CAVALRY            = 3866, "Heavy Hei Guang Cavalry",              Tech(1033, 1033, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_TIGER_CAVALRY_WEI            = 3867, "Elite Tiger Cavalry (Wei)",            Tech(1036, 1036, 51, Age2AgeData.IMPERIAL, True, True)
    TECH_TUNTIAN_WEI                        = 3868, "Tuntian (Wei)",                        Tech(1061, 1061, 51, Age2AgeData.CASTLE, False, True)
    TECH_MING_KUANG_ARMOR_WEI               = 3869, "Ming-Kuang Armor (Wei)",               Tech(1062, 1062, 51, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_WHITE_FEATHER_GUARD_SHU      = 3870, "Elite White Feather Guard (Shu)",      Tech(1064, 1064, 49, Age2AgeData.IMPERIAL, True, True)
    TECH_BOLT_MAGAZINE_SHU                  = 3871, "Bolt Magazine (Shu)",                  Tech(1069, 1069, 49, Age2AgeData.IMPERIAL, False, True)
    TECH_COILED_SERPENT_ARRAY_SHU           = 3872, "Coiled Serpent Array (Shu)",           Tech(1070, 1070, 49, Age2AgeData.CASTLE, False, True)
    TECH_ELITE_FIRE_ARCHER_WU               = 3873, "Elite Fire Archer (Wu)",               Tech(1074, 1074, 50, Age2AgeData.IMPERIAL, True, True)
    TECH_RED_CLIFF_TACTICS_WU               = 3874, "Red Cliff Tactics (Wu)",               Tech(1080, 1080, 50, Age2AgeData.CASTLE, False, True)
    TECH_SITTING_TIGER_WU                   = 3875, "Sitting Tiger (Wu)",                   Tech(1081, 1081, 50, Age2AgeData.IMPERIAL, False, True)
    TECH_CHAMPI_SCOUT                       = 3876, "Champi Scout",                         Tech(1350, 1350, -1, Age2AgeData.DARK, True, False)
    TECH_CHAMPI_WARRIOR                     = 3877, "Champi Warrior",                       Tech(1351, 1351, -1, Age2AgeData.CASTLE, True, False)
    TECH_ELITE_CHAMPI_WARRIOR               = 3878, "Elite Champi Warrior",                 Tech(1352, 1352, -1, Age2AgeData.IMPERIAL, True, False)
    TECH_ELITE_GUECHA_WARRIOR_MUISCA        = 3879, "Elite Guecha Warrior (Muisca)",        Tech(1364, 1364, 57, Age2AgeData.IMPERIAL, True, True)
    TECH_HERBALISM_MUISCA                   = 3880, "Herbalism (Muisca)",                   Tech(1365, 1365, 57, Age2AgeData.CASTLE, False, True)
    TECH_FABRIC_SHIELDS_MUISCA              = 3881, "Fabric Shields (Muisca)",              Tech(1366, 1366, 57, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_KONA_MAPUCHE                 = 3882, "Elite Kona (Mapuche)",                 Tech(1376, 1376, 58, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_BOLAS_RIDER_MAPUCHE          = 3883, "Elite Bolas Rider (Mapuche)",          Tech(1378, 1378, 58, Age2AgeData.IMPERIAL, True, True)
    TECH_MALON_MAPUCHE                      = 3884, "Malon (Mapuche)",                      Tech(1379, 1379, 58, Age2AgeData.CASTLE, False, True)
    TECH_BUTALMAPU_MAPUCHE                  = 3885, "Butalmapu (Mapuche)",                  Tech(1380, 1380, 58, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_BLACKWOOD_ARCHER_TUPI        = 3886, "Elite Blackwood Archer (Tupi)",        Tech(1389, 1389, 59, Age2AgeData.IMPERIAL, True, True)
    TECH_ELITE_IBIRAPEMA_WARRIOR_TUPI       = 3887, "Elite Ibirapema Warrior (Tupi)",       Tech(1391, 1391, 59, Age2AgeData.IMPERIAL, True, True)
    TECH_CACIQUES_TUPI                      = 3888, "Caciques (Tupi)",                      Tech(1392, 1392, 59, Age2AgeData.CASTLE, False, True)
    TECH_CURARE_TUPI                        = 3889, "Curare (Tupi)",                        Tech(1393, 1393, 59, Age2AgeData.IMPERIAL, False, True)
    TECH_ELITE_TEMPLE_GUARD_MUISCA          = 3890, "Elite Temple Guard (Muisca)",          Tech(1401, 1401, 57, Age2AgeData.IMPERIAL, True, True)
    TECH_CHAMPI_RUNNER                      = 3891, "Champi Runner",                        Tech(1402, 1402, -1, Age2AgeData.FEUDAL, True, False)
    TECH_CIRCUMNAVIGATION_PORTUGUESE        = 3892, "Circumnavigation (Portuguese)",        Tech(1404, 1404, 24, Age2AgeData.CASTLE, False, True)

    #4000 - 4999 = Troops, Future Use
    
    #Troop Items
    AP_ATTILA_1_MANGUDAI =                  4000, "Attila, The Scourge of God: Scythian Mangudai",      Mercenary(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_1_ROMAN_VILLAGERS =           4001, "Attila, The Scourge of God: Roman Villagers",        Mercenary(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_2_DYRRHACHIUMS_PRISONERS =    4002, "Attila, The Great Ride: Dyrrhachium's Prisoners",    Mercenary(Age2ScenarioData.AP_ATTILA_2)
    AP_ATTILA_2_SCYTHIAN_TROOP =            4003, "Attila, The Great Ride: Scythian Troops",            Mercenary(Age2ScenarioData.AP_ATTILA_2)
    
    # Joan of Arc
    AP_JOAN_1_RAM =                     4004, "Joan of Arc, An Unlikely Messiah: Battering Ram Army",           ScenarioItem(Age2ScenarioData.AP_JOAN_1)
    AP_JOAN_1_SWORDSMEN =               4005, "Joan of Arc, An Unlikely Messiah: Starting Swordsmen",           ScenarioItem(Age2ScenarioData.AP_JOAN_1)
    AP_JOAN_1_CROSSBOWMEN =             4006, "Joan of Arc, An Unlikely Messiah: Starting Crossbowmen",         ScenarioItem(Age2ScenarioData.AP_JOAN_1)
    AP_JOAN_1_RECRUITS =                4007, "Joan of Arc, An Unlikely Messiah: Recruits Across the River",    Mercenary(Age2ScenarioData.AP_JOAN_1)
    AP_JOAN_5_LOYALISTS =               4008, "Joan of Arc, The Siege of Paris: Loyalist Troop",                Mercenary(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_5_KINGS_REINFORCEMENTS =    4009, "Joan of Arc, The Siege of Paris: King's Reinforcements",         Mercenary(Age2ScenarioData.AP_JOAN_5)
    AP_JOAN_6_LA_HIRE =                 4010, "Joan of Arc, A Perfect Martyr: A Single Longswordsman",          Mercenary(Age2ScenarioData.AP_JOAN_6)
    AP_JOAN_6_ARTILLERY =               4011, "Joan of Arc, A Perfect Martyr: French Artillery",                ScenarioItem(Age2ScenarioData.AP_JOAN_6)
    

        
NAME_TO_ITEM: dict[str, Age2ItemData] = {}
ID_TO_ITEM: dict[int, Age2ItemData] = {}
CATEGORY_TO_ITEMS: dict[type, list[Age2ItemData]] = {}
SCENARIO_TO_ITEMS: dict[Age2ScenarioData, list[Age2ItemData]] = {_scenario: [] for _scenario in Age2ScenarioData}
filler_items: list[Age2ItemData] = []
item_id_to_name: dict[int, str] = {}
item_name_to_id: dict[str, int] = {}
for item in Age2ItemData:
    assert item.item_name not in item_name_to_id, f"Duplicate item name: {item.item_name}"
    assert item.id not in item_id_to_name, f"Duplicate item ID: {item.id}"
    NAME_TO_ITEM[item.item_name] = item
    ID_TO_ITEM[item.id] = item
    if item_type_to_classification[item.type_data] == ItemClassification.filler:
        filler_items.append(item)
    item_id_to_name[item.id] = item.item_name
    item_name_to_id[item.item_name] = item.id
    CATEGORY_TO_ITEMS.setdefault(item.type_data, []).append(item)
    if item.type_data == ScenarioItem or item.type_data == Mercenary:
        SCENARIO_TO_ITEMS[item.type.vanilla_scenario].append(item)

item_mapping: dict[str, str] = {
    Age2ItemData.AP_JOAN_5_REFUGEE_1.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_2.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_3.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_4.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_5.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_6.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_7.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_8.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_9.item_name: "Refugee",
    Age2ItemData.AP_JOAN_5_REFUGEE_10.item_name: "Refugee",
}