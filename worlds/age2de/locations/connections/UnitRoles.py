from ..UnitLines import Age2UnitLineData

# The tables below run to fifty-odd rows; the alias is what keeps them readable.
L = Age2UnitLineData


class UnitRole:
    military = "military"                    # a land army unit
    building_counter = "building_counter"    # brings a building down in reasonable time
    siege = "siege"                          # a dedicated building breaker
    long_range_siege = "long_range_siege"    # outranges the fortification it is shooting
    navy = "navy"                            # a warship
    naval_bombardment = "naval_bombardment"  # shoots buildings from the water


SHIP_LINES = (
    L.FISHING_SHIP_LINE, L.TRADE_COG_LINE, L.TRANSPORT_SHIP_LINE, L.LONGBOAT_LINE,
    L.CANNON_GALLEON_LINE, L.GALLEY_LINE, L.TURTLE_SHIP_LINE, L.CARAVEL_LINE,
    L.FIRE_GALLEY_LINE, L.DEMOLITION_RAFT_LINE, L.DRAGON_SHIP_LINE, L.THIRISADAI_LINE,
    L.DROMON_LINE, L.LOU_CHUAN_LINE, L.CATAPULT_GALLEON_LINE,
    L.LEMBOS_LINE, L.MONOREME_LINE, L.GALLEY_ANTIQUITY_LINE, L.INCENDIARY_RAFT_LINE,
    L.CATAPULT_SHIP_LINE, L.LEVIATHAN_LINE, L.TRANSPORT_SHIP_ANTIQUITY_LINE,
    L.MERCHANT_SHIP_LINE,
)

CIVILIAN_LINES = (
    L.VILLAGER_LINE, L.TRADE_CART_LINE, L.TRADE_COG_LINE, L.FISHING_SHIP_LINE,
    L.TRANSPORT_SHIP_LINE, L.MERCHANT_SHIP_LINE, L.TRANSPORT_SHIP_ANTIQUITY_LINE,
)

FAITH_LINES = (L.MONK_LINE, L.MISSIONARY_LINE)

ANTI_BUILDING = (
    # Barracks
    L.MILITIA_LINE, L.SPEARMAN_LINE, L.EAGLE_SCOUT_LINE, L.CONDOTTIERO_LINE,
    L.FLEMISH_MILITIA_LINE, L.FIRE_LANCER_LINE, L.JIAN_SWORDSMAN_LINE, L.HOPLITE_LINE,
    L.CHAMPI_SCOUT_LINE, L.IBIRAPEMA_WARRIOR_LINE, L.TEMPLE_GUARD_LINE,
    L.VARANGIAN_GUARD_LINE, L.HUSKARL_LINE,
    # Stable
    L.KNIGHT_LINE, L.SCOUT_CAVALRY_LINE, L.BATTLE_ELEPHANT_LINE, L.STEPPE_LANCER_LINE,
    L.SHRIVAMSHA_RIDER_LINE, L.CAMEL_SCOUT_LINE, L.HEI_GUANG_CAVALRY_LINE,
    # Castle
    L.TEUTONIC_KNIGHT_LINE, L.WOAD_RAIDER_LINE, L.SAMURAI_LINE, L.BERSERK_LINE,
    L.JAGUAR_WARRIOR_LINE, L.KAMAYUK_LINE, L.SHOTEL_WARRIOR_LINE, L.KARAMBIT_WARRIOR_LINE,
    L.SERJEANT_LINE, L.OBUCH_LINE, L.URUMI_SWORDSMAN_LINE, L.GHULAM_LINE, L.LIAO_DAO_LINE,
    L.WHITE_FEATHER_GUARD_LINE, L.GUECHA_WARRIOR_LINE, L.HEARTH_TROOP_LINE,
    L.JOMSVIKING_LINE, L.IMMORTAL_MELEE_LINE, L.STRATEGOS_LINE,
    L.THROWING_AXEMAN_LINE, L.GBETO_LINE, L.CHAKRAM_THROWER_LINE,
    L.CATAPHRACT_LINE, L.WAR_ELEPHANT_LINE, L.MAMELUKE_LINE, L.MAGYAR_HUSZAR_LINE,
    L.BOYAR_LINE, L.KONNIK_LINE, L.KESHIK_LINE, L.LEITIS_LINE, L.COUSTILLIER_LINE,
    L.RATHA_LINE, L.CENTURION_LINE, L.MONASPA_LINE, L.IRON_PAGODA_LINE,
    L.TIGER_CAVALRY_LINE, L.TARKAN_LINE, L.KONA_LINE, L.JARL_LINE, L.HIPPEUS_LINE,
    L.ARAMBAI_LINE, L.JANISSARY_LINE, L.CONQUISTADOR_LINE, L.HUSSITE_WAGON_LINE,
    # Monastery
    L.WARRIOR_PRIEST_LINE,
    # Archery Range
    L.GRENADIER_LINE, L.HAND_CANNONEER_LINE,
    # Siege Workshop
    L.MANGONEL_LINE, L.ROCKET_CART_LINE, L.HEAVY_ROCKET_CART_LINE, L.FLAMING_CAMEL_LINE,
)

SIEGE = (
    L.BATTERING_RAM_LINE,
    L.ARMORED_ELEPHANT_LINE,   # the ram of the civilisations that have elephants
    L.TREBUCHET_LINE,
    L.TRACTION_TREBUCHET_LINE,
    L.MOUNTED_TREBUCHET_LINE,
    L.BOMBARD_CANNON_LINE,     # the Houfnice is its Imperial tier
    L.PETARD_LINE,
    L.FIRE_ARCHER_LINE,        # shoots buildings alight, so it counts as siege
)

LONG_RANGE_SIEGE = (
    L.TREBUCHET_LINE, L.TRACTION_TREBUCHET_LINE, L.MOUNTED_TREBUCHET_LINE,
    L.BOMBARD_CANNON_LINE,
)

NAVAL_BOMBARDMENT = (
    L.CANNON_GALLEON_LINE,
    L.CATAPULT_GALLEON_LINE,
    L.DROMON_LINE,             # the Huns' only one - they have no Cannon Galleon
    L.LOU_CHUAN_LINE,
)

NAVY = tuple(line for line in SHIP_LINES if line not in CIVILIAN_LINES)
MILITARY = tuple(line for line in L if line not in CIVILIAN_LINES + SHIP_LINES
                       + FAITH_LINES)

BUILDING_COUNTER = tuple(line for line in L if line in ANTI_BUILDING
                               or line in SIEGE)


ROLE_TO_LINES: dict[str, tuple[Age2UnitLineData, ...]] = {
    UnitRole.military: MILITARY,
    UnitRole.building_counter: BUILDING_COUNTER,
    UnitRole.siege: SIEGE,
    UnitRole.long_range_siege: LONG_RANGE_SIEGE,
    UnitRole.navy: NAVY,
    UnitRole.naval_bombardment: NAVAL_BOMBARDMENT,
}


assert not set(LONG_RANGE_SIEGE) - set(SIEGE), \
    "a long range siege line that is not siege"
assert not set(NAVAL_BOMBARDMENT) - set(NAVY), \
    "a naval bombardment line that is not a warship"
assert not set(BUILDING_COUNTER) & set(SHIP_LINES),     "a ship counting as a building counter - it is a land role, and naval bombardment is its own"
assert not [role for role, lines in ROLE_TO_LINES.items() if not lines], \
    "a role no line fills"
