import enum

from .Units import Age2UnitData


@enum.unique
class Age2UnitLineData(enum.IntEnum):

    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str, line_name: str,
                 head: Age2UnitData) -> None:
        self.id = id
        self.location_name = location_name
        self.line_name = line_name
        self.head = head

    @property
    def units(self) -> list[Age2UnitData]:
        """Every tier in this line, lowest first."""
        from .connections.UnitLineUnits import LINE_TO_UNITS
        return LINE_TO_UNITS[self]

    # 800 - 999 = Unit lines. Ids follow the head unit's order in Age2UnitData.
    ARCHER_LINE                   = 800, "Train Archer Line", "Archer Line", Age2UnitData.ARCHER
    HAND_CANNONEER_LINE           = 801, "Train Hand Cannoneer Line", "Hand Cannoneer Line", Age2UnitData.HAND_CANNONEER
    SKIRMISHER_LINE               = 802, "Train Skirmisher Line", "Skirmisher Line", Age2UnitData.SKIRMISHER
    LONGBOWMAN_LINE               = 803, "Train Longbowman Line", "Longbowman Line", Age2UnitData.LONGBOWMAN
    MANGUDAI_LINE                 = 804, "Train Mangudai Line", "Mangudai Line", Age2UnitData.MANGUDAI
    FISHING_SHIP_LINE             = 805, "Train Fishing Ship Line", "Fishing Ship Line", Age2UnitData.FISHING_SHIP
    TRADE_COG_LINE                = 806, "Train Trade Cog Line", "Trade Cog Line", Age2UnitData.TRADE_COG
    GALLEY_LINE                   = 807, "Train Galley Line", "Galley Line", Age2UnitData.GALLEY
    TEUTONIC_KNIGHT_LINE          = 808, "Train Teutonic Knight Line", "Teutonic Knight Line", Age2UnitData.TEUTONIC_KNIGHT
    BOMBARD_CANNON_LINE           = 809, "Train Bombard Cannon Line", "Bombard Cannon Line", Age2UnitData.BOMBARD_CANNON
    KNIGHT_LINE                   = 810, "Train Knight Line", "Knight Line", Age2UnitData.KNIGHT
    CAVALRY_ARCHER_LINE           = 811, "Train Cavalry Archer Line", "Cavalry Archer Line", Age2UnitData.CAVALRY_ARCHER
    CATAPHRACT_LINE               = 812, "Train Cataphract Line", "Cataphract Line", Age2UnitData.CATAPHRACT
    HUSKARL_LINE                  = 813, "Train Huskarl Line", "Huskarl Line", Age2UnitData.HUSKARL
    JANISSARY_LINE                = 814, "Train Janissary Line", "Janissary Line", Age2UnitData.JANISSARY
    CHU_KO_NU_LINE                = 815, "Train Chu Ko Nu Line", "Chu Ko Nu Line", Age2UnitData.CHU_KO_NU
    MILITIA_LINE                  = 816, "Train Militia Line", "Militia Line", Age2UnitData.MILITIA
    VILLAGER_MALE_LINE            = 817, "Train Villager (Male) Line", "Villager (Male) Line", Age2UnitData.VILLAGER_MALE
    SPEARMAN_LINE                 = 818, "Train Spearman Line", "Spearman Line", Age2UnitData.SPEARMAN
    MONK_LINE                     = 819, "Train Monk Line", "Monk Line", Age2UnitData.MONK
    TRADE_CART_EMPTY_LINE         = 820, "Train Trade Cart Line", "Trade Cart Line", Age2UnitData.TRADE_CART_EMPTY
    SLINGER_LINE                  = 821, "Train Slinger Line", "Slinger Line", Age2UnitData.SLINGER
    CAMEL_SCOUT_LINE              = 822, "Train Camel Scout Line", "Camel Scout Line", Age2UnitData.CAMEL_SCOUT
    WOAD_RAIDER_LINE              = 823, "Train Woad Raider Line", "Woad Raider Line", Age2UnitData.WOAD_RAIDER
    WAR_ELEPHANT_LINE             = 824, "Train War Elephant Line", "War Elephant Line", Age2UnitData.WAR_ELEPHANT
    LONGBOAT_LINE                 = 825, "Train Longboat Line", "Longboat Line", Age2UnitData.LONGBOAT
    SCORPION_LINE                 = 826, "Train Scorpion Line", "Scorpion Line", Age2UnitData.SCORPION
    MANGONEL_LINE                 = 827, "Train Mangonel Line", "Mangonel Line", Age2UnitData.MANGONEL
    THROWING_AXEMAN_LINE          = 828, "Train Throwing Axeman Line", "Throwing Axeman Line", Age2UnitData.THROWING_AXEMAN
    MAMELUKE_LINE                 = 829, "Train Mameluke Line", "Mameluke Line", Age2UnitData.MAMELUKE
    SAMURAI_LINE                  = 830, "Train Samurai Line", "Samurai Line", Age2UnitData.SAMURAI
    VILLAGER_FEMALE_LINE          = 831, "Train Villager (Female) Line", "Villager (Female) Line", Age2UnitData.VILLAGER_FEMALE
    TREBUCHET_PACKED_LINE         = 832, "Train Trebuchet (Packed) Line", "Trebuchet (Packed) Line", Age2UnitData.TREBUCHET_PACKED
    CANNON_GALLEON_LINE           = 833, "Train Cannon Galleon Line", "Cannon Galleon Line", Age2UnitData.CANNON_GALLEON
    BATTERING_RAM_LINE            = 834, "Train Battering Ram Line", "Battering Ram Line", Age2UnitData.BATTERING_RAM
    PETARD_LINE                   = 835, "Train Petard Line", "Petard Line", Age2UnitData.PETARD
    SCOUT_CAVALRY_LINE            = 836, "Train Scout Cavalry Line", "Scout Cavalry Line", Age2UnitData.SCOUT_CAVALRY
    DEMOLITION_RAFT_LINE          = 837, "Train Demolition Raft Line", "Demolition Raft Line", Age2UnitData.DEMOLITION_RAFT
    FIRE_GALLEY_LINE              = 838, "Train Fire Galley Line", "Fire Galley Line", Age2UnitData.FIRE_GALLEY
    TRANSPORT_SHIP_LINE           = 839, "Train Transport Ship Line", "Transport Ship Line", Age2UnitData.TRANSPORT_SHIP
    JEAN_BUREAU_LINE              = 840, "Train Jean Bureau Line", "Jean Bureau Line", Age2UnitData.JEAN_BUREAU
    BERSERK_LINE                  = 841, "Train Berserk Line", "Berserk Line", Age2UnitData.BERSERK
    JAGUAR_WARRIOR_LINE           = 842, "Train Jaguar Warrior Line", "Jaguar Warrior Line", Age2UnitData.JAGUAR_WARRIOR
    EAGLE_SCOUT_LINE              = 843, "Train Eagle Scout Line", "Eagle Scout Line", Age2UnitData.EAGLE_SCOUT
    TARKAN_LINE                   = 844, "Train Tarkan Line", "Tarkan Line", Age2UnitData.TARKAN
    PLUMED_ARCHER_LINE            = 845, "Train Plumed Archer Line", "Plumed Archer Line", Age2UnitData.PLUMED_ARCHER
    CONQUISTADOR_LINE             = 846, "Train Conquistador Line", "Conquistador Line", Age2UnitData.CONQUISTADOR
    MISSIONARY_LINE               = 847, "Train Missionary Line", "Missionary Line", Age2UnitData.MISSIONARY
    WAR_WAGON_LINE                = 848, "Train War Wagon Line", "War Wagon Line", Age2UnitData.WAR_WAGON
    TURTLE_SHIP_LINE              = 849, "Train Turtle Ship Line", "Turtle Ship Line", Age2UnitData.TURTLE_SHIP
    GENOESE_CROSSBOWMAN_LINE      = 850, "Train Genoese Crossbowman Line", "Genoese Crossbowman Line", Age2UnitData.GENOESE_CROSSBOWMAN
    MAGYAR_HUSZAR_LINE            = 851, "Train Magyar Huszar Line", "Magyar Huszar Line", Age2UnitData.MAGYAR_HUSZAR
    ELEPHANT_ARCHER_LINE          = 852, "Train Elephant Archer Line", "Elephant Archer Line", Age2UnitData.ELEPHANT_ARCHER
    BOYAR_LINE                    = 853, "Train Boyar Line", "Boyar Line", Age2UnitData.BOYAR
    KAMAYUK_LINE                  = 854, "Train Kamayuk Line", "Kamayuk Line", Age2UnitData.KAMAYUK
    CONDOTTIERO_LINE              = 855, "Train Condottiero Line", "Condottiero Line", Age2UnitData.CONDOTTIERO
    ORGAN_GUN_LINE                = 856, "Train Organ Gun Line", "Organ Gun Line", Age2UnitData.ORGAN_GUN
    CARAVEL_LINE                  = 857, "Train Caravel Line", "Caravel Line", Age2UnitData.CARAVEL
    CAMEL_ARCHER_LINE             = 858, "Train Camel Archer Line", "Camel Archer Line", Age2UnitData.CAMEL_ARCHER
    GENITOUR_LINE                 = 859, "Train Genitour Line", "Genitour Line", Age2UnitData.GENITOUR
    GBETO_LINE                    = 860, "Train Gbeto Line", "Gbeto Line", Age2UnitData.GBETO
    SHOTEL_WARRIOR_LINE           = 861, "Train Shotel Warrior Line", "Shotel Warrior Line", Age2UnitData.SHOTEL_WARRIOR
    SIEGE_TOWER_LINE              = 862, "Train Siege Tower Line", "Siege Tower Line", Age2UnitData.SIEGE_TOWER
    BALLISTA_ELEPHANT_LINE        = 863, "Train Ballista Elephant Line", "Ballista Elephant Line", Age2UnitData.BALLISTA_ELEPHANT
    KARAMBIT_WARRIOR_LINE         = 864, "Train Karambit Warrior Line", "Karambit Warrior Line", Age2UnitData.KARAMBIT_WARRIOR
    ARAMBAI_LINE                  = 865, "Train Arambai Line", "Arambai Line", Age2UnitData.ARAMBAI
    RATTAN_ARCHER_LINE            = 866, "Train Rattan Archer Line", "Rattan Archer Line", Age2UnitData.RATTAN_ARCHER
    BATTLE_ELEPHANT_LINE          = 867, "Train Battle Elephant Line", "Battle Elephant Line", Age2UnitData.BATTLE_ELEPHANT
    KONNIK_LINE                   = 868, "Train Konnik Line", "Konnik Line", Age2UnitData.KONNIK
    KESHIK_LINE                   = 869, "Train Keshik Line", "Keshik Line", Age2UnitData.KESHIK
    KIPCHAK_LINE                  = 870, "Train Kipchak Line", "Kipchak Line", Age2UnitData.KIPCHAK
    LEITIS_LINE                   = 871, "Train Leitis Line", "Leitis Line", Age2UnitData.LEITIS
    FLAMING_CAMEL_LINE            = 872, "Train Flaming Camel Line", "Flaming Camel Line", Age2UnitData.FLAMING_CAMEL
    STEPPE_LANCER_LINE            = 873, "Train Steppe Lancer Line", "Steppe Lancer Line", Age2UnitData.STEPPE_LANCER
    COUSTILLIER_LINE              = 874, "Train Coustillier Line", "Coustillier Line", Age2UnitData.COUSTILLIER
    SERJEANT_LINE                 = 875, "Train Serjeant Line", "Serjeant Line", Age2UnitData.SERJEANT
    FLEMISH_MILITIA_LINE          = 876, "Train Flemish Militia Line", "Flemish Militia Line", Age2UnitData.FLEMISH_MILITIA
    OBUCH_LINE                    = 877, "Train Obuch Line", "Obuch Line", Age2UnitData.OBUCH
    HUSSITE_WAGON_LINE            = 878, "Train Hussite Wagon Line", "Hussite Wagon Line", Age2UnitData.HUSSITE_WAGON
    URUMI_SWORDSMAN_LINE          = 879, "Train Urumi Swordsman Line", "Urumi Swordsman Line", Age2UnitData.URUMI_SWORDSMAN
    CHAKRAM_THROWER_LINE          = 880, "Train Chakram Thrower Line", "Chakram Thrower Line", Age2UnitData.CHAKRAM_THROWER
    ARMORED_ELEPHANT_LINE         = 881, "Train Armored Elephant Line", "Armored Elephant Line", Age2UnitData.ARMORED_ELEPHANT
    GHULAM_LINE                   = 882, "Train Ghulam Line", "Ghulam Line", Age2UnitData.GHULAM
    THIRISADAI_LINE               = 883, "Train Thirisadai Line", "Thirisadai Line", Age2UnitData.THIRISADAI
    SHRIVAMSHA_RIDER_LINE         = 884, "Train Shrivamsha Rider Line", "Shrivamsha Rider Line", Age2UnitData.SHRIVAMSHA_RIDER
    RATHA_RANGED_LINE             = 885, "Train Ratha Ranged Line", "Ratha Ranged Line", Age2UnitData.RATHA_RANGED
    CENTURION_LINE                = 886, "Train Centurion Line", "Centurion Line", Age2UnitData.CENTURION
    DROMON_LINE                   = 887, "Train Dromon Line", "Dromon Line", Age2UnitData.DROMON
    COMPOSITE_BOWMAN_LINE         = 888, "Train Composite Bowman Line", "Composite Bowman Line", Age2UnitData.COMPOSITE_BOWMAN
    MONASPA_LINE                  = 889, "Train Monaspa Line", "Monaspa Line", Age2UnitData.MONASPA
    WARRIOR_PRIEST_LINE           = 890, "Train Warrior Priest Line", "Warrior Priest Line", Age2UnitData.WARRIOR_PRIEST
    FIRE_LANCER_LINE              = 891, "Train Fire Lancer Line", "Fire Lancer Line", Age2UnitData.FIRE_LANCER
    ROCKET_CART_LINE              = 892, "Train Rocket Cart Line", "Rocket Cart Line", Age2UnitData.ROCKET_CART
    IRON_PAGODA_LINE              = 893, "Train Iron Pagoda Line", "Iron Pagoda Line", Age2UnitData.IRON_PAGODA
    GRENADIER_LINE                = 894, "Train Grenadier Line", "Grenadier Line", Age2UnitData.GRENADIER
    LIAO_DAO_LINE                 = 895, "Train Liao Dao Line", "Liao Dao Line", Age2UnitData.LIAO_DAO
    MOUNTED_TREBUCHET_LINE        = 896, "Train Mounted Trebuchet Line", "Mounted Trebuchet Line", Age2UnitData.MOUNTED_TREBUCHET
    TRACTION_TREBUCHET_LINE       = 897, "Train Traction Trebuchet Line", "Traction Trebuchet Line", Age2UnitData.TRACTION_TREBUCHET
    HEI_GUANG_CAVALRY_LINE        = 898, "Train Hei Guang Cavalry Line", "Hei Guang Cavalry Line", Age2UnitData.HEI_GUANG_CAVALRY
    LOU_CHUAN_LINE                = 899, "Train Lou Chuan Line", "Lou Chuan Line", Age2UnitData.LOU_CHUAN
    TIGER_CAVALRY_LINE            = 900, "Train Tiger Cavalry Line", "Tiger Cavalry Line", Age2UnitData.TIGER_CAVALRY
    XIANBEI_RAIDER_LINE           = 901, "Train Xianbei Raider Line", "Xianbei Raider Line", Age2UnitData.XIANBEI_RAIDER
    WHITE_FEATHER_GUARD_LINE      = 902, "Train White Feather Guard Line", "White Feather Guard Line", Age2UnitData.WHITE_FEATHER_GUARD
    WAR_CHARIOT_FOCUS_FIRE_LINE   = 903, "Train War Chariot Focus Fire Line", "War Chariot Focus Fire Line", Age2UnitData.WAR_CHARIOT_FOCUS_FIRE
    FIRE_ARCHER_LINE              = 904, "Train Fire Archer Line", "Fire Archer Line", Age2UnitData.FIRE_ARCHER
    JIAN_SWORDSMAN_LINE           = 905, "Train Jian Swordsman Line", "Jian Swordsman Line", Age2UnitData.JIAN_SWORDSMAN
    WAR_CHARIOT_BARRAGE_LINE      = 906, "Train War Chariot Barrage Line", "War Chariot Barrage Line", Age2UnitData.WAR_CHARIOT_BARRAGE
    IMMORTAL_MELEE_LINE           = 907, "Train Immortal Melee Line", "Immortal Melee Line", Age2UnitData.IMMORTAL_MELEE
    STRATEGOS_LINE                = 908, "Train Strategos Line", "Strategos Line", Age2UnitData.STRATEGOS
    HIPPEUS_LINE                  = 909, "Train Hippeus Line", "Hippeus Line", Age2UnitData.HIPPEUS
    HOPLITE_LINE                  = 910, "Train Hoplite Line", "Hoplite Line", Age2UnitData.HOPLITE
    LEMBOS_LINE                   = 911, "Train Lembos Line", "Lembos Line", Age2UnitData.LEMBOS
    MONOREME_LINE                 = 912, "Train Monoreme Line", "Monoreme Line", Age2UnitData.MONOREME
    GALLEY_ANTIQUITY_LINE         = 913, "Train Galley Antiquity Line", "Galley Antiquity Line", Age2UnitData.GALLEY_ANTIQUITY
    INCENDIARY_RAFT_LINE          = 914, "Train Incendiary Raft Line", "Incendiary Raft Line", Age2UnitData.INCENDIARY_RAFT
    CATAPULT_SHIP_LINE            = 915, "Train Catapult Ship Line", "Catapult Ship Line", Age2UnitData.CATAPULT_SHIP
    LEVIATHAN_LINE                = 916, "Train Leviathan Line", "Leviathan Line", Age2UnitData.LEVIATHAN
    TRANSPORT_SHIP_ANTIQUITY_LINE = 917, "Train Transport Ship Antiquity Line", "Transport Ship Antiquity Line", Age2UnitData.TRANSPORT_SHIP_ANTIQUITY
    MERCHANT_SHIP_LINE            = 918, "Train Merchant Ship Line", "Merchant Ship Line", Age2UnitData.MERCHANT_SHIP
    WAR_CHARIOT_ANTIQUITY_LINE    = 919, "Train War Chariot Antiquity Line", "War Chariot Antiquity Line", Age2UnitData.WAR_CHARIOT_ANTIQUITY
    UNIT_2550_LINE                = 920, "Train Unit 2550 Line", "Unit 2550 Line", Age2UnitData.UNIT_2550
    UNIT_2562_LINE                = 921, "Train Unit 2562 Line", "Unit 2562 Line", Age2UnitData.UNIT_2562
    UNIT_2566_LINE                = 922, "Train Unit 2566 Line", "Unit 2566 Line", Age2UnitData.UNIT_2566
    UNIT_2569_LINE                = 923, "Train Unit 2569 Line", "Unit 2569 Line", Age2UnitData.UNIT_2569
    UNIT_2579_LINE                = 924, "Train Unit 2579 Line", "Unit 2579 Line", Age2UnitData.UNIT_2579
    UNIT_2582_LINE                = 925, "Train Unit 2582 Line", "Unit 2582 Line", Age2UnitData.UNIT_2582
    UNIT_2586_LINE                = 926, "Train Unit 2586 Line", "Unit 2586 Line", Age2UnitData.UNIT_2586


NAME_TO_LINE: dict[str, Age2UnitLineData] = {line.line_name: line
                                             for line in Age2UnitLineData}
