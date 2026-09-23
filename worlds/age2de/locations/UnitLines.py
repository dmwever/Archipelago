import enum

from .Units import Age2UnitData

from ..items.Items import Age2ItemData


@enum.unique
class Age2UnitLineData(enum.IntEnum):

    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str, line_name: str,
                 head: Age2UnitData, item: Age2ItemData) -> None:
        self.id = id
        self.location_name = location_name
        self.line_name = line_name
        self.head = head
        self.item = item

    @property
    def units(self) -> list[Age2UnitData]:
        """Every tier in this line, lowest first."""
        from .connections.UnitLineUnits import LINE_TO_UNITS
        return LINE_TO_UNITS[self]

    # 800 - 999 = Unit lines. Names come from the game's own unitlines.json.
    ARCHER_LINE                   = 800, "Own Archer Line", "Archer Line", Age2UnitData.ARCHER, Age2ItemData.UNIT_LINE_ARCHER
    HAND_CANNONEER_LINE           = 801, "Own Hand Cannoneer Line", "Hand Cannoneer Line", Age2UnitData.HAND_CANNONEER, Age2ItemData.UNIT_LINE_HAND_CANNONEER
    SKIRMISHER_LINE               = 802, "Own Skirmisher Line", "Skirmisher Line", Age2UnitData.SKIRMISHER, Age2ItemData.UNIT_LINE_SKIRMISHER
    LONGBOWMAN_LINE               = 803, "Own Longbowman Line", "Longbowman Line", Age2UnitData.LONGBOWMAN, Age2ItemData.UNIT_LINE_LONGBOWMAN
    MANGUDAI_LINE                 = 804, "Own Mangudai Line", "Mangudai Line", Age2UnitData.MANGUDAI, Age2ItemData.UNIT_LINE_MANGUDAI
    FISHING_SHIP_LINE             = 805, "Own Fishing Ship Line", "Fishing Ship Line", Age2UnitData.FISHING_SHIP, Age2ItemData.UNIT_LINE_FISHING_SHIP
    TRADE_COG_LINE                = 806, "Own Trade Cog Line", "Trade Cog Line", Age2UnitData.TRADE_COG, Age2ItemData.UNIT_LINE_TRADE_COG
    TEUTONIC_KNIGHT_LINE          = 807, "Own Teutonic Knight Line", "Teutonic Knight Line", Age2UnitData.TEUTONIC_KNIGHT, Age2ItemData.UNIT_LINE_TEUTONIC_KNIGHT
    BOMBARD_CANNON_LINE           = 808, "Own Bombard Cannon Line", "Bombard Cannon Line", Age2UnitData.BOMBARD_CANNON, Age2ItemData.UNIT_LINE_BOMBARD_CANNON
    KNIGHT_LINE                   = 809, "Own Knight Line", "Knight Line", Age2UnitData.KNIGHT, Age2ItemData.UNIT_LINE_KNIGHT
    CAVALRY_ARCHER_LINE           = 810, "Own Cavalry Archer Line", "Cavalry Archer Line", Age2UnitData.CAVALRY_ARCHER, Age2ItemData.UNIT_LINE_CAVALRY_ARCHER
    CATAPHRACT_LINE               = 811, "Own Cataphract Line", "Cataphract Line", Age2UnitData.CATAPHRACT, Age2ItemData.UNIT_LINE_CATAPHRACT
    HUSKARL_LINE                  = 812, "Own Huskarl Line", "Huskarl Line", Age2UnitData.HUSKARL, Age2ItemData.UNIT_LINE_HUSKARL
    JANISSARY_LINE                = 813, "Own Janissary Line", "Janissary Line", Age2UnitData.JANISSARY, Age2ItemData.UNIT_LINE_JANISSARY
    CHU_KO_NU_LINE                = 814, "Own Chu Ko Nu Line", "Chu Ko Nu Line", Age2UnitData.CHU_KO_NU, Age2ItemData.UNIT_LINE_CHU_KO_NU
    MILITIA_LINE                  = 815, "Own Militia Line", "Militia Line", Age2UnitData.MILITIA, Age2ItemData.UNIT_LINE_MILITIA
    VILLAGER_LINE                 = 816, "Own Villager Line", "Villager Line", Age2UnitData.VILLAGER_MALE, Age2ItemData.UNIT_LINE_VILLAGER
    SPEARMAN_LINE                 = 817, "Own Spearman Line", "Spearman Line", Age2UnitData.SPEARMAN, Age2ItemData.UNIT_LINE_SPEARMAN
    MONK_LINE                     = 818, "Own Monk Line", "Monk Line", Age2UnitData.MONK, Age2ItemData.UNIT_LINE_MONK
    TRADE_CART_LINE               = 819, "Own Trade Cart Line", "Trade Cart Line", Age2UnitData.TRADE_CART, Age2ItemData.UNIT_LINE_TRADE_CART
    SLINGER_LINE                  = 820, "Own Slinger Line", "Slinger Line", Age2UnitData.SLINGER, Age2ItemData.UNIT_LINE_SLINGER
    WOAD_RAIDER_LINE              = 821, "Own Woad Raider Line", "Woad Raider Line", Age2UnitData.WOAD_RAIDER, Age2ItemData.UNIT_LINE_WOAD_RAIDER
    WAR_ELEPHANT_LINE             = 822, "Own War Elephant Line", "War Elephant Line", Age2UnitData.WAR_ELEPHANT, Age2ItemData.UNIT_LINE_WAR_ELEPHANT
    LONGBOAT_LINE                 = 823, "Own Longboat Line", "Longboat Line", Age2UnitData.LONGBOAT, Age2ItemData.UNIT_LINE_LONGBOAT
    SCORPION_LINE                 = 824, "Own Scorpion Line", "Scorpion Line", Age2UnitData.SCORPION, Age2ItemData.UNIT_LINE_SCORPION
    MANGONEL_LINE                 = 825, "Own Mangonel Line", "Mangonel Line", Age2UnitData.MANGONEL, Age2ItemData.UNIT_LINE_MANGONEL
    THROWING_AXEMAN_LINE          = 826, "Own Throwing Axeman Line", "Throwing Axeman Line", Age2UnitData.THROWING_AXEMAN, Age2ItemData.UNIT_LINE_THROWING_AXEMAN
    MAMELUKE_LINE                 = 827, "Own Mameluke Line", "Mameluke Line", Age2UnitData.MAMELUKE, Age2ItemData.UNIT_LINE_MAMELUKE
    SAMURAI_LINE                  = 828, "Own Samurai Line", "Samurai Line", Age2UnitData.SAMURAI, Age2ItemData.UNIT_LINE_SAMURAI
    TREBUCHET_LINE                = 829, "Own Trebuchet Line", "Trebuchet Line", Age2UnitData.TREBUCHET_PACKED, Age2ItemData.UNIT_LINE_TREBUCHET
    CANNON_GALLEON_LINE           = 830, "Own Cannon Galleon Line", "Cannon Galleon Line", Age2UnitData.CANNON_GALLEON, Age2ItemData.UNIT_LINE_CANNON_GALLEON
    PETARD_LINE                   = 831, "Own Petard Line", "Petard Line", Age2UnitData.PETARD, Age2ItemData.UNIT_LINE_PETARD
    SCOUT_CAVALRY_LINE            = 832, "Own Scout Cavalry Line", "Scout Cavalry Line", Age2UnitData.SCOUT_CAVALRY, Age2ItemData.UNIT_LINE_SCOUT_CAVALRY
    GALLEY_LINE                   = 833, "Own War Galley Line", "War Galley Line", Age2UnitData.GALLEY, Age2ItemData.UNIT_LINE_GALLEY
    TRANSPORT_SHIP_LINE           = 834, "Own Transport Ship Line", "Transport Ship Line", Age2UnitData.TRANSPORT_SHIP, Age2ItemData.UNIT_LINE_TRANSPORT_SHIP
    JEAN_BUREAU_LINE              = 835, "Own Jean Bureau Line", "Jean Bureau Line", Age2UnitData.JEAN_BUREAU, Age2ItemData.UNIT_LINE_JEAN_BUREAU
    BERSERK_LINE                  = 836, "Own Berserk Line", "Berserk Line", Age2UnitData.BERSERK, Age2ItemData.UNIT_LINE_BERSERK
    JAGUAR_WARRIOR_LINE           = 837, "Own Jaguar Warrior Line", "Jaguar Warrior Line", Age2UnitData.JAGUAR_WARRIOR, Age2ItemData.UNIT_LINE_JAGUAR_WARRIOR
    EAGLE_SCOUT_LINE              = 838, "Own Eagle Warrior Line", "Eagle Warrior Line", Age2UnitData.EAGLE_SCOUT, Age2ItemData.UNIT_LINE_EAGLE_SCOUT
    TARKAN_LINE                   = 839, "Own Tarkan Line", "Tarkan Line", Age2UnitData.TARKAN, Age2ItemData.UNIT_LINE_TARKAN
    PLUMED_ARCHER_LINE            = 840, "Own Plumed Archer Line", "Plumed Archer Line", Age2UnitData.PLUMED_ARCHER, Age2ItemData.UNIT_LINE_PLUMED_ARCHER
    CONQUISTADOR_LINE             = 841, "Own Conquistador Line", "Conquistador Line", Age2UnitData.CONQUISTADOR, Age2ItemData.UNIT_LINE_CONQUISTADOR
    MISSIONARY_LINE               = 842, "Own Missionary Line", "Missionary Line", Age2UnitData.MISSIONARY, Age2ItemData.UNIT_LINE_MISSIONARY
    WAR_WAGON_LINE                = 843, "Own War Wagon Line", "War Wagon Line", Age2UnitData.WAR_WAGON, Age2ItemData.UNIT_LINE_WAR_WAGON
    TURTLE_SHIP_LINE              = 844, "Own Turtle Ship Line", "Turtle Ship Line", Age2UnitData.TURTLE_SHIP, Age2ItemData.UNIT_LINE_TURTLE_SHIP
    GENOESE_CROSSBOWMAN_LINE      = 845, "Own Genoese Crossbowman Line", "Genoese Crossbowman Line", Age2UnitData.GENOESE_CROSSBOWMAN, Age2ItemData.UNIT_LINE_GENOESE_CROSSBOWMAN
    MAGYAR_HUSZAR_LINE            = 846, "Own Magyar Huszar Line", "Magyar Huszar Line", Age2UnitData.MAGYAR_HUSZAR, Age2ItemData.UNIT_LINE_MAGYAR_HUSZAR
    ELEPHANT_ARCHER_LINE          = 847, "Own Elephant Archer Line", "Elephant Archer Line", Age2UnitData.ELEPHANT_ARCHER, Age2ItemData.UNIT_LINE_ELEPHANT_ARCHER
    BOYAR_LINE                    = 848, "Own Boyar Line", "Boyar Line", Age2UnitData.BOYAR, Age2ItemData.UNIT_LINE_BOYAR
    KAMAYUK_LINE                  = 849, "Own Kamayuk Line", "Kamayuk Line", Age2UnitData.KAMAYUK, Age2ItemData.UNIT_LINE_KAMAYUK
    CONDOTTIERO_LINE              = 850, "Own Condottiero Line", "Condottiero Line", Age2UnitData.CONDOTTIERO, Age2ItemData.UNIT_LINE_CONDOTTIERO
    ORGAN_GUN_LINE                = 851, "Own Organ Gun Line", "Organ Gun Line", Age2UnitData.ORGAN_GUN, Age2ItemData.UNIT_LINE_ORGAN_GUN
    CARAVEL_LINE                  = 852, "Own Caravel Line", "Caravel Line", Age2UnitData.CARAVEL, Age2ItemData.UNIT_LINE_CARAVEL
    CAMEL_ARCHER_LINE             = 853, "Own Camel Archer Line", "Camel Archer Line", Age2UnitData.CAMEL_ARCHER, Age2ItemData.UNIT_LINE_CAMEL_ARCHER
    GENITOUR_LINE                 = 854, "Own Genitour Line", "Genitour Line", Age2UnitData.GENITOUR, Age2ItemData.UNIT_LINE_GENITOUR
    GBETO_LINE                    = 855, "Own Gbeto Line", "Gbeto Line", Age2UnitData.GBETO, Age2ItemData.UNIT_LINE_GBETO
    SHOTEL_WARRIOR_LINE           = 856, "Own Shotel Warrior Line", "Shotel Warrior Line", Age2UnitData.SHOTEL_WARRIOR, Age2ItemData.UNIT_LINE_SHOTEL_WARRIOR
    FIRE_GALLEY_LINE              = 857, "Own Fire Ship Line", "Fire Ship Line", Age2UnitData.FIRE_GALLEY, Age2ItemData.UNIT_LINE_FIRE_GALLEY
    DEMOLITION_RAFT_LINE          = 858, "Own Demolition Ship Line", "Demolition Ship Line", Age2UnitData.DEMOLITION_RAFT, Age2ItemData.UNIT_LINE_DEMOLITION_RAFT
    SIEGE_TOWER_LINE              = 859, "Own Siege Tower Line", "Siege Tower Line", Age2UnitData.SIEGE_TOWER, Age2ItemData.UNIT_LINE_SIEGE_TOWER
    BALLISTA_ELEPHANT_LINE        = 860, "Own Ballista Elephant Line", "Ballista Elephant Line", Age2UnitData.BALLISTA_ELEPHANT, Age2ItemData.UNIT_LINE_BALLISTA_ELEPHANT
    KARAMBIT_WARRIOR_LINE         = 861, "Own Karambit Warrior Line", "Karambit Warrior Line", Age2UnitData.KARAMBIT_WARRIOR, Age2ItemData.UNIT_LINE_KARAMBIT_WARRIOR
    ARAMBAI_LINE                  = 862, "Own Arambai Line", "Arambai Line", Age2UnitData.ARAMBAI, Age2ItemData.UNIT_LINE_ARAMBAI
    RATTAN_ARCHER_LINE            = 863, "Own Rattan Archer Line", "Rattan Archer Line", Age2UnitData.RATTAN_ARCHER, Age2ItemData.UNIT_LINE_RATTAN_ARCHER
    BATTLE_ELEPHANT_LINE          = 864, "Own Battle Elephant Line", "Battle Elephant Line", Age2UnitData.BATTLE_ELEPHANT, Age2ItemData.UNIT_LINE_BATTLE_ELEPHANT
    KONNIK_LINE                   = 865, "Own Konnik Line", "Konnik Line", Age2UnitData.KONNIK, Age2ItemData.UNIT_LINE_KONNIK
    KESHIK_LINE                   = 866, "Own Keshik Line", "Keshik Line", Age2UnitData.KESHIK, Age2ItemData.UNIT_LINE_KESHIK
    KIPCHAK_LINE                  = 867, "Own Kipchak Line", "Kipchak Line", Age2UnitData.KIPCHAK, Age2ItemData.UNIT_LINE_KIPCHAK
    LEITIS_LINE                   = 868, "Own Leitis Line", "Leitis Line", Age2UnitData.LEITIS, Age2ItemData.UNIT_LINE_LEITIS
    BATTERING_RAM_LINE            = 869, "Own Battering Ram Line", "Battering Ram Line", Age2UnitData.BATTERING_RAM, Age2ItemData.UNIT_LINE_BATTERING_RAM
    FLAMING_CAMEL_LINE            = 870, "Own Flaming Camel Line", "Flaming Camel Line", Age2UnitData.FLAMING_CAMEL, Age2ItemData.UNIT_LINE_FLAMING_CAMEL
    DRAGON_SHIP_LINE              = 871, "Own Dragon Ship Line", "Dragon Ship Line", Age2UnitData.DRAGON_SHIP, Age2ItemData.UNIT_LINE_DRAGON_SHIP
    STEPPE_LANCER_LINE            = 872, "Own Steppe Lancer Line", "Steppe Lancer Line", Age2UnitData.STEPPE_LANCER, Age2ItemData.UNIT_LINE_STEPPE_LANCER
    COUSTILLIER_LINE              = 873, "Own Coustillier Line", "Coustillier Line", Age2UnitData.COUSTILLIER, Age2ItemData.UNIT_LINE_COUSTILLIER
    SERJEANT_LINE                 = 874, "Own Serjeant Line", "Serjeant Line", Age2UnitData.SERJEANT, Age2ItemData.UNIT_LINE_SERJEANT
    FLEMISH_MILITIA_LINE          = 875, "Own Flemish Militia Line", "Flemish Militia Line", Age2UnitData.FLEMISH_MILITIA, Age2ItemData.UNIT_LINE_FLEMISH_MILITIA
    OBUCH_LINE                    = 876, "Own Obuch Line", "Obuch Line", Age2UnitData.OBUCH, Age2ItemData.UNIT_LINE_OBUCH
    HUSSITE_WAGON_LINE            = 877, "Own Hussite Wagon Line", "Hussite Wagon Line", Age2UnitData.HUSSITE_WAGON, Age2ItemData.UNIT_LINE_HUSSITE_WAGON
    URUMI_SWORDSMAN_LINE          = 878, "Own Urumi Swordsman Line", "Urumi Swordsman Line", Age2UnitData.URUMI_SWORDSMAN, Age2ItemData.UNIT_LINE_URUMI_SWORDSMAN
    CHAKRAM_THROWER_LINE          = 879, "Own Chakram Thrower Line", "Chakram Thrower Line", Age2UnitData.CHAKRAM_THROWER, Age2ItemData.UNIT_LINE_CHAKRAM_THROWER
    ARMORED_ELEPHANT_LINE         = 880, "Own Armored Elephant Line", "Armored Elephant Line", Age2UnitData.ARMORED_ELEPHANT, Age2ItemData.UNIT_LINE_ARMORED_ELEPHANT
    GHULAM_LINE                   = 881, "Own Ghulam Line", "Ghulam Line", Age2UnitData.GHULAM, Age2ItemData.UNIT_LINE_GHULAM
    THIRISADAI_LINE               = 882, "Own Thirisadai Line", "Thirisadai Line", Age2UnitData.THIRISADAI, Age2ItemData.UNIT_LINE_THIRISADAI
    SHRIVAMSHA_RIDER_LINE         = 883, "Own Shrivamsha Rider Line", "Shrivamsha Rider Line", Age2UnitData.SHRIVAMSHA_RIDER, Age2ItemData.UNIT_LINE_SHRIVAMSHA_RIDER
    CAMEL_SCOUT_LINE              = 884, "Own Camel Line", "Camel Line", Age2UnitData.CAMEL_SCOUT, Age2ItemData.UNIT_LINE_CAMEL_SCOUT
    RATHA_LINE                    = 885, "Own Ratha Line", "Ratha Line", Age2UnitData.RATHA, Age2ItemData.UNIT_LINE_RATHA
    CENTURION_LINE                = 886, "Own Centurion Line", "Centurion Line", Age2UnitData.CENTURION, Age2ItemData.UNIT_LINE_CENTURION
    DROMON_LINE                   = 887, "Own Dromon Line", "Dromon Line", Age2UnitData.DROMON, Age2ItemData.UNIT_LINE_DROMON
    COMPOSITE_BOWMAN_LINE         = 888, "Own Composite Bowman Line", "Composite Bowman Line", Age2UnitData.COMPOSITE_BOWMAN, Age2ItemData.UNIT_LINE_COMPOSITE_BOWMAN
    MONASPA_LINE                  = 889, "Own Monaspa Line", "Monaspa Line", Age2UnitData.MONASPA, Age2ItemData.UNIT_LINE_MONASPA
    WARRIOR_PRIEST_LINE           = 890, "Own Warrior Priest Line", "Warrior Priest Line", Age2UnitData.WARRIOR_PRIEST, Age2ItemData.UNIT_LINE_WARRIOR_PRIEST
    FIRE_LANCER_LINE              = 891, "Own Fire Lancer Line", "Fire Lancer Line", Age2UnitData.FIRE_LANCER, Age2ItemData.UNIT_LINE_FIRE_LANCER
    ROCKET_CART_LINE              = 892, "Own Rocket Cart Line", "Rocket Cart Line", Age2UnitData.ROCKET_CART, Age2ItemData.UNIT_LINE_ROCKET_CART
    HEAVY_ROCKET_CART_LINE        = 893, "Own Heavy Rocket Cart Line", "Heavy Rocket Cart Line", Age2UnitData.HEAVY_ROCKET_CART, Age2ItemData.UNIT_LINE_HEAVY_ROCKET_CART
    IRON_PAGODA_LINE              = 894, "Own Iron Pagoda Line", "Iron Pagoda Line", Age2UnitData.IRON_PAGODA, Age2ItemData.UNIT_LINE_IRON_PAGODA
    GRENADIER_LINE                = 895, "Own Grenadier Line", "Grenadier Line", Age2UnitData.GRENADIER, Age2ItemData.UNIT_LINE_GRENADIER
    LIAO_DAO_LINE                 = 896, "Own Liao Dao Line", "Liao Dao Line", Age2UnitData.LIAO_DAO, Age2ItemData.UNIT_LINE_LIAO_DAO
    MOUNTED_TREBUCHET_LINE        = 897, "Own Mounted Trebuchet Line", "Mounted Trebuchet Line", Age2UnitData.MOUNTED_TREBUCHET, Age2ItemData.UNIT_LINE_MOUNTED_TREBUCHET
    TRACTION_TREBUCHET_LINE       = 898, "Own Traction Trebuchet Line", "Traction Trebuchet Line", Age2UnitData.TRACTION_TREBUCHET, Age2ItemData.UNIT_LINE_TRACTION_TREBUCHET
    HEI_GUANG_CAVALRY_LINE        = 899, "Own Hei Guang Cavalry Line", "Hei Guang Cavalry Line", Age2UnitData.HEI_GUANG_CAVALRY, Age2ItemData.UNIT_LINE_HEI_GUANG_CAVALRY
    LOU_CHUAN_LINE                = 900, "Own Lou Chuan Line", "Lou Chuan Line", Age2UnitData.LOU_CHUAN, Age2ItemData.UNIT_LINE_LOU_CHUAN
    TIGER_CAVALRY_LINE            = 901, "Own Tiger Cavalry Line", "Tiger Cavalry Line", Age2UnitData.TIGER_CAVALRY, Age2ItemData.UNIT_LINE_TIGER_CAVALRY
    XIANBEI_RAIDER_LINE           = 902, "Own Xianbei Raider Line", "Xianbei Raider Line", Age2UnitData.XIANBEI_RAIDER, Age2ItemData.UNIT_LINE_XIANBEI_RAIDER
    WHITE_FEATHER_GUARD_LINE      = 903, "Own White Feather Guard Line", "White Feather Guard Line", Age2UnitData.WHITE_FEATHER_GUARD, Age2ItemData.UNIT_LINE_WHITE_FEATHER_GUARD
    WAR_CHARIOT_LINE              = 904, "Own War Chariot Line", "War Chariot Line", Age2UnitData.WAR_CHARIOT_FOCUS_FIRE, Age2ItemData.UNIT_LINE_WAR_CHARIOT
    FIRE_ARCHER_LINE              = 905, "Own Fire Archer Line", "Fire Archer Line", Age2UnitData.FIRE_ARCHER, Age2ItemData.UNIT_LINE_FIRE_ARCHER
    JIAN_SWORDSMAN_LINE           = 906, "Own Jian Swordsman Line", "Jian Swordsman Line", Age2UnitData.JIAN_SWORDSMAN, Age2ItemData.UNIT_LINE_JIAN_SWORDSMAN
    IMMORTAL_MELEE_LINE           = 907, "Own Immortal Line", "Immortal Line", Age2UnitData.IMMORTAL_MELEE, Age2ItemData.UNIT_LINE_IMMORTAL_MELEE
    STRATEGOS_LINE                = 908, "Own Strategos Line", "Strategos Line", Age2UnitData.STRATEGOS, Age2ItemData.UNIT_LINE_STRATEGOS
    HIPPEUS_LINE                  = 909, "Own Hippeus Line", "Hippeus Line", Age2UnitData.HIPPEUS, Age2ItemData.UNIT_LINE_HIPPEUS
    HOPLITE_LINE                  = 910, "Own Hoplite Line", "Hoplite Line", Age2UnitData.HOPLITE, Age2ItemData.UNIT_LINE_HOPLITE
    LEMBOS_LINE                   = 911, "Own Lembos Line", "Lembos Line", Age2UnitData.LEMBOS, Age2ItemData.UNIT_LINE_LEMBOS
    MONOREME_LINE                 = 912, "Own Monoreme Line", "Monoreme Line", Age2UnitData.MONOREME, Age2ItemData.UNIT_LINE_MONOREME
    GALLEY_ANTIQUITY_LINE         = 913, "Own Ancient Galley Line", "Ancient Galley Line", Age2UnitData.GALLEY_ANTIQUITY, Age2ItemData.UNIT_LINE_GALLEY_ANTIQUITY
    INCENDIARY_RAFT_LINE          = 914, "Own Incendiary Ship Line", "Incendiary Ship Line", Age2UnitData.INCENDIARY_RAFT, Age2ItemData.UNIT_LINE_INCENDIARY_RAFT
    CATAPULT_SHIP_LINE            = 915, "Own Catapult Ship Line", "Catapult Ship Line", Age2UnitData.CATAPULT_SHIP, Age2ItemData.UNIT_LINE_CATAPULT_SHIP
    LEVIATHAN_LINE                = 916, "Own Leviathan Line", "Leviathan Line", Age2UnitData.LEVIATHAN, Age2ItemData.UNIT_LINE_LEVIATHAN
    TRANSPORT_SHIP_ANTIQUITY_LINE = 917, "Own Transport Ship Antiquity Line", "Transport Ship Antiquity Line", Age2UnitData.TRANSPORT_SHIP_ANTIQUITY, Age2ItemData.UNIT_LINE_TRANSPORT_SHIP_ANTIQUITY
    MERCHANT_SHIP_LINE            = 918, "Own Merchant Ship Line", "Merchant Ship Line", Age2UnitData.MERCHANT_SHIP, Age2ItemData.UNIT_LINE_MERCHANT_SHIP
    WAR_CHARIOT_ANTIQUITY_LINE    = 919, "Own War Chariot (Antiquity) Line", "War Chariot (Antiquity) Line", Age2UnitData.WAR_CHARIOT_ANTIQUITY, Age2ItemData.UNIT_LINE_WAR_CHARIOT_ANTIQUITY
    CHAMPI_SCOUT_LINE             = 920, "Own Champi Line", "Champi Line", Age2UnitData.CHAMPI_SCOUT, Age2ItemData.UNIT_LINE_CHAMPI_SCOUT
    GUECHA_WARRIOR_LINE           = 921, "Own Guecha Warrior Line", "Guecha Warrior Line", Age2UnitData.GUECHA_WARRIOR, Age2ItemData.UNIT_LINE_GUECHA_WARRIOR
    KONA_LINE                     = 922, "Own Kona Line", "Kona Line", Age2UnitData.KONA, Age2ItemData.UNIT_LINE_KONA
    BOLAS_RIDER_LINE              = 923, "Own Bolas Rider Line", "Bolas Rider Line", Age2UnitData.BOLAS_RIDER, Age2ItemData.UNIT_LINE_BOLAS_RIDER
    BLACKWOOD_ARCHER_LINE         = 924, "Own Blackwood Archer Line", "Blackwood Archer Line", Age2UnitData.BLACKWOOD_ARCHER, Age2ItemData.UNIT_LINE_BLACKWOOD_ARCHER
    IBIRAPEMA_WARRIOR_LINE        = 925, "Own Ibirapema Warrior Line", "Ibirapema Warrior Line", Age2UnitData.IBIRAPEMA_WARRIOR, Age2ItemData.UNIT_LINE_IBIRAPEMA_WARRIOR
    TEMPLE_GUARD_LINE             = 926, "Own Temple Guard Line", "Temple Guard Line", Age2UnitData.TEMPLE_GUARD, Age2ItemData.UNIT_LINE_TEMPLE_GUARD
    CATAPULT_GALLEON_LINE         = 927, "Own Catapult Galleon Line", "Catapult Galleon Line", Age2UnitData.CATAPULT_GALLEON, Age2ItemData.UNIT_LINE_CATAPULT_GALLEON
    MOUNTED_CROSSBOWMAN_LINE      = 928, "Own Mounted Crossbowman Line", "Mounted Crossbowman Line", Age2UnitData.MOUNTED_CROSSBOWMAN, Age2ItemData.UNIT_LINE_MOUNTED_CROSSBOWMAN
    VARANGIAN_GUARD_LINE          = 929, "Own Varangian Guard Line", "Varangian Guard Line", Age2UnitData.VARANGIAN_GUARD, Age2ItemData.UNIT_LINE_VARANGIAN_GUARD
    HEARTH_TROOP_LINE             = 930, "Own Hearth Troop Line", "Hearth Troop Line", Age2UnitData.HEARTH_TROOP, Age2ItemData.UNIT_LINE_HEARTH_TROOP
    JARL_LINE                     = 931, "Own Jarl Line", "Jarl Line", Age2UnitData.JARL, Age2ItemData.UNIT_LINE_JARL
    JOMSVIKING_LINE               = 932, "Own Jomsviking Line", "Jomsviking Line", Age2UnitData.JOMSVIKING, Age2ItemData.UNIT_LINE_JOMSVIKING


NAME_TO_LINE: dict[str, Age2UnitLineData] = {line.line_name: line
                                             for line in Age2UnitLineData}
