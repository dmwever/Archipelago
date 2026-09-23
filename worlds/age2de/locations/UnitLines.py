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

    # 800 - 999 = Unit lines. Names come from the game's own unitlines.json.
    ARCHER_LINE                   = 800, "Own Archer Line", "Archer Line", Age2UnitData.ARCHER
    HAND_CANNONEER_LINE           = 801, "Own Hand Cannoneer Line", "Hand Cannoneer Line", Age2UnitData.HAND_CANNONEER
    SKIRMISHER_LINE               = 802, "Own Skirmisher Line", "Skirmisher Line", Age2UnitData.SKIRMISHER
    LONGBOWMAN_LINE               = 803, "Own Longbowman Line", "Longbowman Line", Age2UnitData.LONGBOWMAN
    MANGUDAI_LINE                 = 804, "Own Mangudai Line", "Mangudai Line", Age2UnitData.MANGUDAI
    FISHING_SHIP_LINE             = 805, "Own Fishing Ship Line", "Fishing Ship Line", Age2UnitData.FISHING_SHIP
    TRADE_COG_LINE                = 806, "Own Trade Cog Line", "Trade Cog Line", Age2UnitData.TRADE_COG
    TEUTONIC_KNIGHT_LINE          = 807, "Own Teutonic Knight Line", "Teutonic Knight Line", Age2UnitData.TEUTONIC_KNIGHT
    BOMBARD_CANNON_LINE           = 808, "Own Bombard Cannon Line", "Bombard Cannon Line", Age2UnitData.BOMBARD_CANNON
    KNIGHT_LINE                   = 809, "Own Knight Line", "Knight Line", Age2UnitData.KNIGHT
    CAVALRY_ARCHER_LINE           = 810, "Own Cavalry Archer Line", "Cavalry Archer Line", Age2UnitData.CAVALRY_ARCHER
    CATAPHRACT_LINE               = 811, "Own Cataphract Line", "Cataphract Line", Age2UnitData.CATAPHRACT
    HUSKARL_LINE                  = 812, "Own Huskarl Line", "Huskarl Line", Age2UnitData.HUSKARL
    JANISSARY_LINE                = 813, "Own Janissary Line", "Janissary Line", Age2UnitData.JANISSARY
    CHU_KO_NU_LINE                = 814, "Own Chu Ko Nu Line", "Chu Ko Nu Line", Age2UnitData.CHU_KO_NU
    MILITIA_LINE                  = 815, "Own Militia Line", "Militia Line", Age2UnitData.MILITIA
    VILLAGER_MALE_LINE            = 816, "Own Villager (Male) Line", "Villager (Male) Line", Age2UnitData.VILLAGER_MALE
    SPEARMAN_LINE                 = 817, "Own Spearman Line", "Spearman Line", Age2UnitData.SPEARMAN
    MONK_LINE                     = 818, "Own Monk Line", "Monk Line", Age2UnitData.MONK
    TRADE_CART_EMPTY_LINE         = 819, "Own Trade Cart Line", "Trade Cart Line", Age2UnitData.TRADE_CART_EMPTY
    SLINGER_LINE                  = 820, "Own Slinger Line", "Slinger Line", Age2UnitData.SLINGER
    WOAD_RAIDER_LINE              = 821, "Own Woad Raider Line", "Woad Raider Line", Age2UnitData.WOAD_RAIDER
    WAR_ELEPHANT_LINE             = 822, "Own War Elephant Line", "War Elephant Line", Age2UnitData.WAR_ELEPHANT
    LONGBOAT_LINE                 = 823, "Own Longboat Line", "Longboat Line", Age2UnitData.LONGBOAT
    SCORPION_LINE                 = 824, "Own Scorpion Line", "Scorpion Line", Age2UnitData.SCORPION
    MANGONEL_LINE                 = 825, "Own Mangonel Line", "Mangonel Line", Age2UnitData.MANGONEL
    THROWING_AXEMAN_LINE          = 826, "Own Throwing Axeman Line", "Throwing Axeman Line", Age2UnitData.THROWING_AXEMAN
    MAMELUKE_LINE                 = 827, "Own Mameluke Line", "Mameluke Line", Age2UnitData.MAMELUKE
    SAMURAI_LINE                  = 828, "Own Samurai Line", "Samurai Line", Age2UnitData.SAMURAI
    VILLAGER_FEMALE_LINE          = 829, "Own Villager (Female) Line", "Villager (Female) Line", Age2UnitData.VILLAGER_FEMALE
    TREBUCHET_PACKED_LINE         = 830, "Own Trebuchet (Packed) Line", "Trebuchet (Packed) Line", Age2UnitData.TREBUCHET_PACKED
    CANNON_GALLEON_LINE           = 831, "Own Cannon Galleon Line", "Cannon Galleon Line", Age2UnitData.CANNON_GALLEON
    PETARD_LINE                   = 832, "Own Petard Line", "Petard Line", Age2UnitData.PETARD
    SCOUT_CAVALRY_LINE            = 833, "Own Scout Cavalry Line", "Scout Cavalry Line", Age2UnitData.SCOUT_CAVALRY
    GALLEY_LINE                   = 834, "Own War Galley Line", "War Galley Line", Age2UnitData.GALLEY
    TRANSPORT_SHIP_LINE           = 835, "Own Transport Ship Line", "Transport Ship Line", Age2UnitData.TRANSPORT_SHIP
    JEAN_BUREAU_LINE              = 836, "Own Jean Bureau Line", "Jean Bureau Line", Age2UnitData.JEAN_BUREAU
    BERSERK_LINE                  = 837, "Own Berserk Line", "Berserk Line", Age2UnitData.BERSERK
    JAGUAR_WARRIOR_LINE           = 838, "Own Jaguar Warrior Line", "Jaguar Warrior Line", Age2UnitData.JAGUAR_WARRIOR
    EAGLE_SCOUT_LINE              = 839, "Own Eagle Warrior Line", "Eagle Warrior Line", Age2UnitData.EAGLE_SCOUT
    TARKAN_LINE                   = 840, "Own Tarkan Line", "Tarkan Line", Age2UnitData.TARKAN
    PLUMED_ARCHER_LINE            = 841, "Own Plumed Archer Line", "Plumed Archer Line", Age2UnitData.PLUMED_ARCHER
    CONQUISTADOR_LINE             = 842, "Own Conquistador Line", "Conquistador Line", Age2UnitData.CONQUISTADOR
    MISSIONARY_LINE               = 843, "Own Missionary Line", "Missionary Line", Age2UnitData.MISSIONARY
    WAR_WAGON_LINE                = 844, "Own War Wagon Line", "War Wagon Line", Age2UnitData.WAR_WAGON
    TURTLE_SHIP_LINE              = 845, "Own Turtle Ship Line", "Turtle Ship Line", Age2UnitData.TURTLE_SHIP
    GENOESE_CROSSBOWMAN_LINE      = 846, "Own Genoese Crossbowman Line", "Genoese Crossbowman Line", Age2UnitData.GENOESE_CROSSBOWMAN
    MAGYAR_HUSZAR_LINE            = 847, "Own Magyar Huszar Line", "Magyar Huszar Line", Age2UnitData.MAGYAR_HUSZAR
    ELEPHANT_ARCHER_LINE          = 848, "Own Elephant Archer Line", "Elephant Archer Line", Age2UnitData.ELEPHANT_ARCHER
    BOYAR_LINE                    = 849, "Own Boyar Line", "Boyar Line", Age2UnitData.BOYAR
    KAMAYUK_LINE                  = 850, "Own Kamayuk Line", "Kamayuk Line", Age2UnitData.KAMAYUK
    CONDOTTIERO_LINE              = 851, "Own Condottiero Line", "Condottiero Line", Age2UnitData.CONDOTTIERO
    ORGAN_GUN_LINE                = 852, "Own Organ Gun Line", "Organ Gun Line", Age2UnitData.ORGAN_GUN
    CARAVEL_LINE                  = 853, "Own Caravel Line", "Caravel Line", Age2UnitData.CARAVEL
    CAMEL_ARCHER_LINE             = 854, "Own Camel Archer Line", "Camel Archer Line", Age2UnitData.CAMEL_ARCHER
    GENITOUR_LINE                 = 855, "Own Genitour Line", "Genitour Line", Age2UnitData.GENITOUR
    GBETO_LINE                    = 856, "Own Gbeto Line", "Gbeto Line", Age2UnitData.GBETO
    SHOTEL_WARRIOR_LINE           = 857, "Own Shotel Warrior Line", "Shotel Warrior Line", Age2UnitData.SHOTEL_WARRIOR
    FIRE_GALLEY_LINE              = 858, "Own Fire Ship Line", "Fire Ship Line", Age2UnitData.FIRE_GALLEY
    DEMOLITION_RAFT_LINE          = 859, "Own Demolition Ship Line", "Demolition Ship Line", Age2UnitData.DEMOLITION_RAFT
    SIEGE_TOWER_LINE              = 860, "Own Siege Tower Line", "Siege Tower Line", Age2UnitData.SIEGE_TOWER
    BALLISTA_ELEPHANT_LINE        = 861, "Own Ballista Elephant Line", "Ballista Elephant Line", Age2UnitData.BALLISTA_ELEPHANT
    KARAMBIT_WARRIOR_LINE         = 862, "Own Karambit Warrior Line", "Karambit Warrior Line", Age2UnitData.KARAMBIT_WARRIOR
    ARAMBAI_LINE                  = 863, "Own Arambai Line", "Arambai Line", Age2UnitData.ARAMBAI
    RATTAN_ARCHER_LINE            = 864, "Own Rattan Archer Line", "Rattan Archer Line", Age2UnitData.RATTAN_ARCHER
    BATTLE_ELEPHANT_LINE          = 865, "Own Battle Elephant Line", "Battle Elephant Line", Age2UnitData.BATTLE_ELEPHANT
    KONNIK_LINE                   = 866, "Own Konnik Line", "Konnik Line", Age2UnitData.KONNIK
    KESHIK_LINE                   = 867, "Own Keshik Line", "Keshik Line", Age2UnitData.KESHIK
    KIPCHAK_LINE                  = 868, "Own Kipchak Line", "Kipchak Line", Age2UnitData.KIPCHAK
    LEITIS_LINE                   = 869, "Own Leitis Line", "Leitis Line", Age2UnitData.LEITIS
    BATTERING_RAM_LINE            = 870, "Own Battering Ram Line", "Battering Ram Line", Age2UnitData.BATTERING_RAM
    FLAMING_CAMEL_LINE            = 871, "Own Flaming Camel Line", "Flaming Camel Line", Age2UnitData.FLAMING_CAMEL
    DRAGON_SHIP_LINE              = 872, "Own Dragon Ship Line", "Dragon Ship Line", Age2UnitData.DRAGON_SHIP
    STEPPE_LANCER_LINE            = 873, "Own Steppe Lancer Line", "Steppe Lancer Line", Age2UnitData.STEPPE_LANCER
    COUSTILLIER_LINE              = 874, "Own Coustillier Line", "Coustillier Line", Age2UnitData.COUSTILLIER
    SERJEANT_LINE                 = 875, "Own Serjeant Line", "Serjeant Line", Age2UnitData.SERJEANT
    FLEMISH_MILITIA_LINE          = 876, "Own Flemish Militia Line", "Flemish Militia Line", Age2UnitData.FLEMISH_MILITIA
    OBUCH_LINE                    = 877, "Own Obuch Line", "Obuch Line", Age2UnitData.OBUCH
    HUSSITE_WAGON_LINE            = 878, "Own Hussite Wagon Line", "Hussite Wagon Line", Age2UnitData.HUSSITE_WAGON
    URUMI_SWORDSMAN_LINE          = 879, "Own Urumi Swordsman Line", "Urumi Swordsman Line", Age2UnitData.URUMI_SWORDSMAN
    CHAKRAM_THROWER_LINE          = 880, "Own Chakram Thrower Line", "Chakram Thrower Line", Age2UnitData.CHAKRAM_THROWER
    ARMORED_ELEPHANT_LINE         = 881, "Own Armored Elephant Line", "Armored Elephant Line", Age2UnitData.ARMORED_ELEPHANT
    GHULAM_LINE                   = 882, "Own Ghulam Line", "Ghulam Line", Age2UnitData.GHULAM
    THIRISADAI_LINE               = 883, "Own Thirisadai Line", "Thirisadai Line", Age2UnitData.THIRISADAI
    SHRIVAMSHA_RIDER_LINE         = 884, "Own Shrivamsha Rider Line", "Shrivamsha Rider Line", Age2UnitData.SHRIVAMSHA_RIDER
    CAMEL_SCOUT_LINE              = 885, "Own Camel Line", "Camel Line", Age2UnitData.CAMEL_SCOUT
    RATHA_RANGED_LINE             = 886, "Own Ratha Ranged Line", "Ratha Ranged Line", Age2UnitData.RATHA_RANGED
    CENTURION_LINE                = 887, "Own Centurion Line", "Centurion Line", Age2UnitData.CENTURION
    DROMON_LINE                   = 888, "Own Dromon Line", "Dromon Line", Age2UnitData.DROMON
    COMPOSITE_BOWMAN_LINE         = 889, "Own Composite Bowman Line", "Composite Bowman Line", Age2UnitData.COMPOSITE_BOWMAN
    MONASPA_LINE                  = 890, "Own Monaspa Line", "Monaspa Line", Age2UnitData.MONASPA
    WARRIOR_PRIEST_LINE           = 891, "Own Warrior Priest Line", "Warrior Priest Line", Age2UnitData.WARRIOR_PRIEST
    FIRE_LANCER_LINE              = 892, "Own Fire Lancer Line", "Fire Lancer Line", Age2UnitData.FIRE_LANCER
    ROCKET_CART_LINE              = 893, "Own Rocket Cart Line", "Rocket Cart Line", Age2UnitData.ROCKET_CART
    HEAVY_ROCKET_CART_LINE        = 894, "Own Heavy Rocket Cart Line", "Heavy Rocket Cart Line", Age2UnitData.HEAVY_ROCKET_CART
    IRON_PAGODA_LINE              = 895, "Own Iron Pagoda Line", "Iron Pagoda Line", Age2UnitData.IRON_PAGODA
    GRENADIER_LINE                = 896, "Own Grenadier Line", "Grenadier Line", Age2UnitData.GRENADIER
    LIAO_DAO_LINE                 = 897, "Own Liao Dao Line", "Liao Dao Line", Age2UnitData.LIAO_DAO
    MOUNTED_TREBUCHET_LINE        = 898, "Own Mounted Trebuchet Line", "Mounted Trebuchet Line", Age2UnitData.MOUNTED_TREBUCHET
    TRACTION_TREBUCHET_LINE       = 899, "Own Traction Trebuchet Line", "Traction Trebuchet Line", Age2UnitData.TRACTION_TREBUCHET
    HEI_GUANG_CAVALRY_LINE        = 900, "Own Hei Guang Cavalry Line", "Hei Guang Cavalry Line", Age2UnitData.HEI_GUANG_CAVALRY
    LOU_CHUAN_LINE                = 901, "Own Lou Chuan Line", "Lou Chuan Line", Age2UnitData.LOU_CHUAN
    TIGER_CAVALRY_LINE            = 902, "Own Tiger Cavalry Line", "Tiger Cavalry Line", Age2UnitData.TIGER_CAVALRY
    XIANBEI_RAIDER_LINE           = 903, "Own Xianbei Raider Line", "Xianbei Raider Line", Age2UnitData.XIANBEI_RAIDER
    WHITE_FEATHER_GUARD_LINE      = 904, "Own White Feather Guard Line", "White Feather Guard Line", Age2UnitData.WHITE_FEATHER_GUARD
    WAR_CHARIOT_FOCUS_FIRE_LINE   = 905, "Own War Chariot Focus Fire Line", "War Chariot Focus Fire Line", Age2UnitData.WAR_CHARIOT_FOCUS_FIRE
    FIRE_ARCHER_LINE              = 906, "Own Fire Archer Line", "Fire Archer Line", Age2UnitData.FIRE_ARCHER
    JIAN_SWORDSMAN_LINE           = 907, "Own Jian Swordsman Line", "Jian Swordsman Line", Age2UnitData.JIAN_SWORDSMAN
    WAR_CHARIOT_BARRAGE_LINE      = 908, "Own War Chariot Barrage Line", "War Chariot Barrage Line", Age2UnitData.WAR_CHARIOT_BARRAGE
    IMMORTAL_MELEE_LINE           = 909, "Own Immortal Line", "Immortal Line", Age2UnitData.IMMORTAL_MELEE
    STRATEGOS_LINE                = 910, "Own Strategos Line", "Strategos Line", Age2UnitData.STRATEGOS
    HIPPEUS_LINE                  = 911, "Own Hippeus Line", "Hippeus Line", Age2UnitData.HIPPEUS
    HOPLITE_LINE                  = 912, "Own Hoplite Line", "Hoplite Line", Age2UnitData.HOPLITE
    LEMBOS_LINE                   = 913, "Own Lembos Line", "Lembos Line", Age2UnitData.LEMBOS
    MONOREME_LINE                 = 914, "Own Monoreme Line", "Monoreme Line", Age2UnitData.MONOREME
    GALLEY_ANTIQUITY_LINE         = 915, "Own Ancient Galley Line", "Ancient Galley Line", Age2UnitData.GALLEY_ANTIQUITY
    INCENDIARY_RAFT_LINE          = 916, "Own Incendiary Ship Line", "Incendiary Ship Line", Age2UnitData.INCENDIARY_RAFT
    CATAPULT_SHIP_LINE            = 917, "Own Catapult Ship Line", "Catapult Ship Line", Age2UnitData.CATAPULT_SHIP
    LEVIATHAN_LINE                = 918, "Own Leviathan Line", "Leviathan Line", Age2UnitData.LEVIATHAN
    TRANSPORT_SHIP_ANTIQUITY_LINE = 919, "Own Transport Ship Antiquity Line", "Transport Ship Antiquity Line", Age2UnitData.TRANSPORT_SHIP_ANTIQUITY
    MERCHANT_SHIP_LINE            = 920, "Own Merchant Ship Line", "Merchant Ship Line", Age2UnitData.MERCHANT_SHIP
    WAR_CHARIOT_ANTIQUITY_LINE    = 921, "Own War Chariot Line", "War Chariot Line", Age2UnitData.WAR_CHARIOT_ANTIQUITY
    CHAMPI_SCOUT_LINE             = 922, "Own Champi Line", "Champi Line", Age2UnitData.CHAMPI_SCOUT
    GUECHA_WARRIOR_LINE           = 923, "Own Guecha Warrior Line", "Guecha Warrior Line", Age2UnitData.GUECHA_WARRIOR
    KONA_LINE                     = 924, "Own Kona Line", "Kona Line", Age2UnitData.KONA
    BOLAS_RIDER_LINE              = 925, "Own Bolas Rider Line", "Bolas Rider Line", Age2UnitData.BOLAS_RIDER
    BLACKWOOD_ARCHER_LINE         = 926, "Own Blackwood Archer Line", "Blackwood Archer Line", Age2UnitData.BLACKWOOD_ARCHER
    IBIRAPEMA_WARRIOR_LINE        = 927, "Own Ibirapema Warrior Line", "Ibirapema Warrior Line", Age2UnitData.IBIRAPEMA_WARRIOR
    TEMPLE_GUARD_LINE             = 928, "Own Temple Guard Line", "Temple Guard Line", Age2UnitData.TEMPLE_GUARD
    CATAPULT_GALLEON_LINE         = 929, "Own Catapult Galleon Line", "Catapult Galleon Line", Age2UnitData.CATAPULT_GALLEON
    MOUNTED_CROSSBOWMAN_LINE      = 930, "Own Mounted Crossbowman Line", "Mounted Crossbowman Line", Age2UnitData.MOUNTED_CROSSBOWMAN
    VARANGIAN_GUARD_LINE          = 931, "Own Varangian Guard Line", "Varangian Guard Line", Age2UnitData.VARANGIAN_GUARD
    HEARTH_TROOP_LINE             = 932, "Own Hearth Troop Line", "Hearth Troop Line", Age2UnitData.HEARTH_TROOP
    JARL_LINE                     = 933, "Own Jarl Line", "Jarl Line", Age2UnitData.JARL
    JOMSVIKING_LINE               = 934, "Own Jomsviking Line", "Jomsviking Line", Age2UnitData.JOMSVIKING


NAME_TO_LINE: dict[str, Age2UnitLineData] = {line.line_name: line
                                             for line in Age2UnitLineData}
