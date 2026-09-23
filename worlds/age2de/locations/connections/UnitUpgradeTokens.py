from ...items.Items import Age2ItemData
from ..Units import Age2UnitData
from .CivilizationUnits import UNTRAINABLE


UNIT_TO_UPGRADE_TOKENS: dict[Age2UnitData, list[Age2ItemData]] = {
    # Archer Line
    Age2UnitData.ARCHER: [Age2ItemData.UPGRADE_BOW],
    Age2UnitData.CROSSBOWMAN: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOLT],
    Age2UnitData.ARBALESTER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOLT],
    # Hand Cannoneer Line
    Age2UnitData.HAND_CANNONEER: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_GUNPOWDER],
    # Skirmisher Line
    Age2UnitData.SKIRMISHER: [Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.ELITE_SKIRMISHER: [Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.IMPERIAL_SKIRMISHER: [Age2ItemData.UPGRADE_SPEAR],
    # Longbowman Line
    Age2UnitData.LONGBOWMAN: [Age2ItemData.UPGRADE_BOW],
    Age2UnitData.ELITE_LONGBOWMAN: [Age2ItemData.UPGRADE_BOW],
    # Mangudai Line
    Age2UnitData.MANGUDAI: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_MANGUDAI: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE],
    # Fishing Ship Line
    Age2UnitData.FISHING_SHIP: [Age2ItemData.UPGRADE_BOAT],
    # Trade Cog Line
    Age2UnitData.TRADE_COG: [Age2ItemData.UPGRADE_BOAT],
    # Teutonic Knight Line
    Age2UnitData.TEUTONIC_KNIGHT: [Age2ItemData.UPGRADE_SWORD],
    Age2UnitData.ELITE_TEUTONIC_KNIGHT: [Age2ItemData.UPGRADE_SWORD],
    # Bombard Cannon Line
    Age2UnitData.BOMBARD_CANNON: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CANNON],
    Age2UnitData.HOUFNICE: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CANNON],
    # Knight Line
    Age2UnitData.KNIGHT: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.CAVALIER: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.PALADIN: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.SAVAR: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE],
    # Cavalry Archer Line
    Age2UnitData.CAVALRY_ARCHER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.HEAVY_CAVALRY_ARCHER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE],
    # Cataphract Line
    Age2UnitData.CATAPHRACT: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_CATAPHRACT: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE],
    # Huskarl Line
    Age2UnitData.HUSKARL: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    Age2UnitData.ELITE_HUSKARL: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    # Janissary Line
    Age2UnitData.JANISSARY: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_GUNPOWDER],
    Age2UnitData.ELITE_JANISSARY: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_GUNPOWDER],
    # Chu Ko Nu Line
    Age2UnitData.CHU_KO_NU: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOLT],
    Age2UnitData.ELITE_CHU_KO_NU: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOLT],
    # Militia Line
    Age2UnitData.MILITIA: [Age2ItemData.UPGRADE_CLUB],
    Age2UnitData.MAN_AT_ARMS: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    Age2UnitData.LONG_SWORDSMAN: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    Age2UnitData.TWO_HANDED_SWORDSMAN: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    Age2UnitData.LEGIONARY: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    Age2UnitData.CHAMPION: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    # Spearman Line
    Age2UnitData.SPEARMAN: [Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.PIKEMAN: [Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.HALBERDIER: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_AXE],
    # Monk Line
    Age2UnitData.MONK: [Age2ItemData.UPGRADE_BIBLE],
    # Trade Cart Line
    # The horse is a civilisation-dependent requirement rather than a flat one: a
    # meso-american civilisation has no horses and still trains trade carts. The table
    # states the general case and Phase 7's can_train_unit is where the exception belongs,
    # the same way CIV_TO_UNITS rather than this file decides what a civilisation may train.
    Age2UnitData.TRADE_CART: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_CART],
    # Slinger Line
    Age2UnitData.SLINGER: [Age2ItemData.UPGRADE_SLING],
    # Woad Raider Line
    Age2UnitData.WOAD_RAIDER: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_WOAD_RAIDER: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_AXE],
    # War Elephant Line
    Age2UnitData.WAR_ELEPHANT: [Age2ItemData.UPGRADE_ELEPHANT],
    Age2UnitData.ELITE_WAR_ELEPHANT: [Age2ItemData.UPGRADE_ELEPHANT],
    # Longboat Line
    Age2UnitData.LONGBOAT: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.ELITE_LONGBOAT: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOAT],
    # Scorpion Line
    Age2UnitData.SCORPION: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_BOLT],
    Age2UnitData.HEAVY_SCORPION: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_BOLT],
    # Mangonel Line
    Age2UnitData.MANGONEL: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_STONE],
    Age2UnitData.ONAGER: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_STONE],
    Age2UnitData.SIEGE_ONAGER: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_STONE],
    # Throwing Axeman Line
    Age2UnitData.THROWING_AXEMAN: [Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_THROWING_AXEMAN: [Age2ItemData.UPGRADE_AXE],
    # Mameluke Line
    Age2UnitData.MAMELUKE: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_CAMEL],
    Age2UnitData.ELITE_MAMELUKE: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_CAMEL],
    # Samurai Line
    Age2UnitData.SAMURAI: [Age2ItemData.UPGRADE_SWORD],
    Age2UnitData.ELITE_SAMURAI: [Age2ItemData.UPGRADE_SWORD],
    # Trebuchet Line
    Age2UnitData.TREBUCHET_PACKED: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_STONE],
    # Cannon Galleon Line
    Age2UnitData.CANNON_GALLEON: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CANNON, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.ELITE_CANNON_GALLEON: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CANNON, Age2ItemData.UPGRADE_BOAT],
    # Petard Line
    Age2UnitData.PETARD: [Age2ItemData.UPGRADE_GUNPOWDER],
    # Scout Cavalry Line
    Age2UnitData.SCOUT_CAVALRY: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.LIGHT_CAVALRY: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.HUSSAR: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.WINGED_HUSSAR: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_HORSE],
    # War Galley Line
    Age2UnitData.GALLEY: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.WAR_GALLEY: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.GALLEON: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_BOAT],
    # Transport Ship Line
    Age2UnitData.TRANSPORT_SHIP: [Age2ItemData.UPGRADE_BOAT],
    # Berserk Line
    Age2UnitData.BERSERK: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_BERSERK: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_AXE],
    # Jaguar Warrior Line
    Age2UnitData.JAGUAR_WARRIOR: [Age2ItemData.UPGRADE_CLUB],
    Age2UnitData.ELITE_JAGUAR_WARRIOR: [Age2ItemData.UPGRADE_CLUB],
    # Eagle Warrior Line
    Age2UnitData.EAGLE_SCOUT: [Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.EAGLE_WARRIOR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.ELITE_EAGLE_WARRIOR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    # Tarkan Line
    Age2UnitData.TARKAN: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_TORCH],
    Age2UnitData.ELITE_TARKAN: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_TORCH],
    # Plumed Archer Line
    Age2UnitData.PLUMED_ARCHER: [Age2ItemData.UPGRADE_BOW],
    Age2UnitData.ELITE_PLUMED_ARCHER: [Age2ItemData.UPGRADE_BOW],
    # Conquistador Line
    Age2UnitData.CONQUISTADOR: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_GUNPOWDER],
    Age2UnitData.ELITE_CONQUISTADOR: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_GUNPOWDER],
    # Missionary Line
    Age2UnitData.MISSIONARY: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_BIBLE],
    # War Wagon Line
    Age2UnitData.WAR_WAGON: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_CART],
    Age2UnitData.ELITE_WAR_WAGON: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_CART],
    # Turtle Ship Line
    Age2UnitData.TURTLE_SHIP: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CANNON, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.ELITE_TURTLE_SHIP: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CANNON, Age2ItemData.UPGRADE_BOAT],
    # Genoese Crossbowman Line
    Age2UnitData.GENOESE_CROSSBOWMAN: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOLT],
    Age2UnitData.ELITE_GENOESE_CROSSBOWMAN: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_BOLT],
    # Magyar Huszar Line
    Age2UnitData.MAGYAR_HUSZAR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_MAGYAR_HUSZAR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Elephant Archer Line
    Age2UnitData.ELEPHANT_ARCHER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_ELEPHANT],
    Age2UnitData.ELITE_ELEPHANT_ARCHER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_ELEPHANT],
    # Boyar Line
    Age2UnitData.BOYAR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_BOYAR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_AXE],
    # Kamayuk Line
    Age2UnitData.KAMAYUK: [Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.ELITE_KAMAYUK: [Age2ItemData.UPGRADE_SPEAR],
    # Condottiero Line
    Age2UnitData.CONDOTTIERO: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    # Organ Gun Line
    Age2UnitData.ORGAN_GUN: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_GUNPOWDER],
    Age2UnitData.ELITE_ORGAN_GUN: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_GUNPOWDER],
    # Caravel Line
    Age2UnitData.CARAVEL: [Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.ELITE_CARAVEL: [Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_BOAT],
    # Camel Archer Line
    Age2UnitData.CAMEL_ARCHER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_CAMEL],
    Age2UnitData.ELITE_CAMEL_ARCHER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_CAMEL],
    # Genitour Line
    Age2UnitData.GENITOUR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_GENITOUR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Gbeto Line
    Age2UnitData.GBETO: [Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_GBETO: [Age2ItemData.UPGRADE_AXE],
    # Shotel Warrior Line
    Age2UnitData.SHOTEL_WARRIOR: [Age2ItemData.UPGRADE_SWORD],
    Age2UnitData.ELITE_SHOTEL_WARRIOR: [Age2ItemData.UPGRADE_SWORD],
    # Fire Ship Line
    Age2UnitData.FIRE_GALLEY: [Age2ItemData.UPGRADE_TORCH, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.FIRE_SHIP: [Age2ItemData.UPGRADE_TORCH, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.FAST_FIRE_SHIP: [Age2ItemData.UPGRADE_TORCH, Age2ItemData.UPGRADE_BOAT],
    # Demolition Ship Line
    Age2UnitData.DEMOLITION_RAFT: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.DEMOLITION_SHIP: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_BOAT],
    Age2UnitData.HEAVY_DEMOLITION_SHIP: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_BOAT],
    # Siege Tower Line
    Age2UnitData.SIEGE_TOWER: [Age2ItemData.UPGRADE_SIEGEWORKS],
    # Ballista Elephant Line
    Age2UnitData.BALLISTA_ELEPHANT: [Age2ItemData.UPGRADE_ELEPHANT, Age2ItemData.UPGRADE_BOLT],
    Age2UnitData.ELITE_BALLISTA_ELEPHANT: [Age2ItemData.UPGRADE_ELEPHANT, Age2ItemData.UPGRADE_BOLT],
    # Karambit Warrior Line
    Age2UnitData.KARAMBIT_WARRIOR: [Age2ItemData.UPGRADE_SWORD],
    Age2UnitData.ELITE_KARAMBIT_WARRIOR: [Age2ItemData.UPGRADE_SWORD],
    # Arambai Line
    Age2UnitData.ARAMBAI: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_DART],
    Age2UnitData.ELITE_ARAMBAI: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_DART],
    # Rattan Archer Line
    Age2UnitData.RATTAN_ARCHER: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_BOW],
    Age2UnitData.ELITE_RATTAN_ARCHER: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_BOW],
    # Battle Elephant Line
    Age2UnitData.BATTLE_ELEPHANT: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_ELEPHANT],
    Age2UnitData.ELITE_BATTLE_ELEPHANT: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_ELEPHANT],
    # Konnik Line
    Age2UnitData.KONNIK: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_MACE],
    Age2UnitData.ELITE_KONNIK: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_MACE],
    # Keshik Line
    Age2UnitData.KESHIK: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_KESHIK: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Kipchak Line
    Age2UnitData.KIPCHAK: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_KIPCHAK: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE],
    # Leitis Line
    Age2UnitData.LEITIS: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_LEITIS: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Battering Ram Line
    Age2UnitData.BATTERING_RAM: [Age2ItemData.UPGRADE_SIEGEWORKS],
    Age2UnitData.CAPPED_RAM: [Age2ItemData.UPGRADE_SIEGEWORKS],
    Age2UnitData.SIEGE_RAM: [Age2ItemData.UPGRADE_SIEGEWORKS],
    # Flaming Camel Line
    Age2UnitData.FLAMING_CAMEL: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CAMEL, Age2ItemData.UPGRADE_TORCH],
    # Dragon Ship Line
    Age2UnitData.DRAGON_SHIP: [Age2ItemData.UPGRADE_TORCH, Age2ItemData.UPGRADE_BOAT],
    # Steppe Lancer Line
    Age2UnitData.STEPPE_LANCER: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_STEPPE_LANCER: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Coustillier Line
    Age2UnitData.COUSTILLIER: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_COUSTILLIER: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Serjeant Line
    Age2UnitData.SERJEANT: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_SERJEANT: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_AXE],
    # Flemish Militia Line
    Age2UnitData.FLEMISH_MILITIA: [Age2ItemData.UPGRADE_SPEAR],
    # Obuch Line
    Age2UnitData.OBUCH: [Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_OBUCH: [Age2ItemData.UPGRADE_AXE],
    # Hussite Wagon Line
    Age2UnitData.HUSSITE_WAGON: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CART],
    Age2UnitData.ELITE_HUSSITE_WAGON: [Age2ItemData.UPGRADE_GUN, Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_CART],
    # Urumi Swordsman Line
    Age2UnitData.URUMI_SWORDSMAN: [Age2ItemData.UPGRADE_WHIP],
    Age2UnitData.ELITE_URUMI_SWORDSMAN: [Age2ItemData.UPGRADE_WHIP],
    # Chakram Thrower Line
    Age2UnitData.CHAKRAM_THROWER: [Age2ItemData.UPGRADE_CHAKRAM],
    Age2UnitData.ELITE_CHAKRAM_THROWER: [Age2ItemData.UPGRADE_CHAKRAM],
    # Armored Elephant Line
    Age2UnitData.ARMORED_ELEPHANT: [Age2ItemData.UPGRADE_ELEPHANT, Age2ItemData.UPGRADE_SIEGEWORKS],
    Age2UnitData.SIEGE_ELEPHANT: [Age2ItemData.UPGRADE_ELEPHANT, Age2ItemData.UPGRADE_SIEGEWORKS],
    # Ghulam Line
    Age2UnitData.GHULAM: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.ELITE_GHULAM: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    # Thirisadai Line
    Age2UnitData.THIRISADAI: [Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_BOAT],
    # Shrivamsha Rider Line
    Age2UnitData.SHRIVAMSHA_RIDER: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_SHRIVAMSHA_RIDER: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_AXE],
    # Camel Line
    Age2UnitData.CAMEL_SCOUT: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_CAMEL],
    Age2UnitData.CAMEL_RIDER: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_CAMEL],
    Age2UnitData.HEAVY_CAMEL_RIDER: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_CAMEL],
    Age2UnitData.IMPERIAL_CAMEL_RIDER: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_CAMEL],
    # Ratha Line
    Age2UnitData.RATHA: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_CART],
    Age2UnitData.ELITE_RATHA: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_CART],
    # Centurion Line
    Age2UnitData.CENTURION: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_CENTURION: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE],
    # Dromon Line
    Age2UnitData.DROMON: [Age2ItemData.UPGRADE_TORCH, Age2ItemData.UPGRADE_STONE, Age2ItemData.UPGRADE_BOAT],
    # Composite Bowman Line
    Age2UnitData.COMPOSITE_BOWMAN: [Age2ItemData.UPGRADE_BOW],
    Age2UnitData.ELITE_COMPOSITE_BOWMAN: [Age2ItemData.UPGRADE_BOW],
    # Monaspa Line
    Age2UnitData.MONASPA: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_MONASPA: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Warrior Priest Line
    Age2UnitData.WARRIOR_PRIEST: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_AXE],
    # Fire Lancer Line
    Age2UnitData.FIRE_LANCER: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_ROCKET, Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_FIRE_LANCER: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_ROCKET, Age2ItemData.UPGRADE_AXE],
    # Rocket Cart Line
    Age2UnitData.ROCKET_CART: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_ROCKET],
    # Heavy Rocket Cart Line
    Age2UnitData.HEAVY_ROCKET_CART: [Age2ItemData.UPGRADE_GUNPOWDER, Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_ROCKET],
    # Iron Pagoda Line
    Age2UnitData.IRON_PAGODA: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_IRON_PAGODA: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Grenadier Line
    Age2UnitData.GRENADIER: [Age2ItemData.UPGRADE_GUNPOWDER],
    # Liao Dao Line
    Age2UnitData.LIAO_DAO: [Age2ItemData.UPGRADE_SWORD],
    Age2UnitData.ELITE_LIAO_DAO: [Age2ItemData.UPGRADE_SWORD],
    # Mounted Trebuchet Line
    Age2UnitData.MOUNTED_TREBUCHET: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_STONE],
    # Traction Trebuchet Line
    Age2UnitData.TRACTION_TREBUCHET: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_STONE],
    # Hei Guang Cavalry Line
    Age2UnitData.HEI_GUANG_CAVALRY: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.HEAVY_HEI_GUANG_CAVALRY: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_HORSE],
    # Lou Chuan Line
    Age2UnitData.LOU_CHUAN: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_STONE, Age2ItemData.UPGRADE_BOAT],
    # Tiger Cavalry Line
    Age2UnitData.TIGER_CAVALRY: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_TIGER_CAVALRY: [Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Xianbei Raider Line
    Age2UnitData.XIANBEI_RAIDER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE],
    # White Feather Guard Line
    Age2UnitData.WHITE_FEATHER_GUARD: [Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.ELITE_WHITE_FEATHER_GUARD: [Age2ItemData.UPGRADE_SPEAR],
    # War Chariot Line
    Age2UnitData.WAR_CHARIOT_FOCUS_FIRE: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_CART],
    Age2UnitData.WAR_CHARIOT_BARRAGE: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_BOLT, Age2ItemData.UPGRADE_CART],
    # Fire Archer Line
    Age2UnitData.FIRE_ARCHER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_TORCH],
    Age2UnitData.ELITE_FIRE_ARCHER: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_TORCH],
    # Jian Swordsman Line
    Age2UnitData.JIAN_SWORDSMAN: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD],
    # Champi Line
    Age2UnitData.CHAMPI_SCOUT: [Age2ItemData.UPGRADE_CLUB],
    Age2UnitData.CHAMPI_RUNNER: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SHIELD],
    Age2UnitData.CHAMPI_WARRIOR: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SHIELD],
    Age2UnitData.ELITE_CHAMPI_WARRIOR: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SHIELD],
    # Guecha Warrior Line
    Age2UnitData.GUECHA_WARRIOR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.ELITE_GUECHA_WARRIOR: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    # Kona Line
    Age2UnitData.KONA: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    Age2UnitData.ELITE_KONA: [Age2ItemData.UPGRADE_CLUB, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_HORSE],
    # Bolas Rider Line
    Age2UnitData.BOLAS_RIDER: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_BOLAS],
    Age2UnitData.ELITE_BOLAS_RIDER: [Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_BOLAS],
    # Blackwood Archer Line
    Age2UnitData.BLACKWOOD_ARCHER: [Age2ItemData.UPGRADE_BOW],
    Age2UnitData.ELITE_BLACKWOOD_ARCHER: [Age2ItemData.UPGRADE_BOW],
    # Ibirapema Warrior Line
    Age2UnitData.IBIRAPEMA_WARRIOR: [Age2ItemData.UPGRADE_CLUB],
    Age2UnitData.ELITE_IBIRAPEMA_WARRIOR: [Age2ItemData.UPGRADE_CLUB],
    # Temple Guard Line
    Age2UnitData.TEMPLE_GUARD: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    # Catapult Galleon Line
    Age2UnitData.CATAPULT_GALLEON: [Age2ItemData.UPGRADE_SIEGEWORKS, Age2ItemData.UPGRADE_STONE, Age2ItemData.UPGRADE_BOAT],
    # Mounted Crossbowman Line
    Age2UnitData.MOUNTED_CROSSBOWMAN: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_BOLT],
    Age2UnitData.HEAVY_MOUNTED_CROSSBOWMAN: [Age2ItemData.UPGRADE_BOW, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_BOLT],
    # Varangian Guard Line
    Age2UnitData.VARANGIAN_GUARD: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_VARANGIAN_GUARD: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_AXE],
    # Hearth Troop Line
    Age2UnitData.HEARTH_TROOP: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    Age2UnitData.ELITE_HEARTH_TROOP: [Age2ItemData.UPGRADE_SWORD, Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR],
    # Jarl Line
    Age2UnitData.JARL: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_AXE],
    Age2UnitData.ELITE_JARL: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_HORSE, Age2ItemData.UPGRADE_AXE],
    # Jomsviking Line
    Age2UnitData.JOMSVIKING: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_TORCH],
    Age2UnitData.ELITE_JOMSVIKING: [Age2ItemData.UPGRADE_SHIELD, Age2ItemData.UPGRADE_SPEAR, Age2ItemData.UPGRADE_TORCH],
}


for unit in Age2UnitData:
    unit.upgrade_tokens = UNIT_TO_UPGRADE_TOKENS.get(unit, [])


# A trainable unit with no equipment would be free under unitsanity_items: upgrades, which
# is only ever correct for the villager. Anything else reaching this is a missing row.
assert not [unit for unit in Age2UnitData
            if not unit.upgrade_tokens
            and unit not in UNTRAINABLE
            and unit.line is not Age2UnitData.VILLAGER_MALE.line], \
    "trainable unit with no upgrade tokens"
