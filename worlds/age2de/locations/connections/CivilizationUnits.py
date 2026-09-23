"""Which units each civilisation can train.

Read from the game's own civilisation tech trees. Two kinds of restriction, mirroring
CivilizationTechs: a unique or regional unit is available only to the civilisations that list
it, and a generic unit is available to everyone except the civilisations that lack it.

Imported for its side effect: populates Age2CivData.included_units and .excluded_units.
"""

from ..Civilizations import Age2CivData
from ..Units import Age2UnitData, UnitType


# Return of Rome and Chronicles units. Those modes run on their own civilisation rosters, so
# no Age of Empires II civilisation trains any of these - but no single civilisation excludes
# them either, which is why they need naming here rather than in a per-civ list.
#
# Derived by asking which units only an antiquity civilisation's tech tree lists, where
# antiquity is the era civilizations.json gives the six Return of Rome and Chronicles civs:
# Achaemenids, Athenians, Macedonians, Puru, Spartans, Thracians. Reading that field rather
# than naming the civs by hand matters - a hand-written list here wrongly held the Three
# Kingdoms and American civilisations, whose units are ordinary Age of Empires II content.
OTHER_GAME_MODE_UNITS: frozenset[Age2UnitData] = frozenset({
    Age2UnitData.IMMORTAL_MELEE,
    Age2UnitData.ELITE_IMMORTAL_MELEE,
    Age2UnitData.STRATEGOS,
    Age2UnitData.ELITE_STRATEGOS,
    Age2UnitData.HIPPEUS,
    Age2UnitData.ELITE_HIPPEUS,
    Age2UnitData.HOPLITE,
    Age2UnitData.ELITE_HOPLITE,
    Age2UnitData.LEMBOS,
    Age2UnitData.WAR_LEMBOS,
    Age2UnitData.HEAVY_LEMBOS,
    Age2UnitData.ELITE_LEMBOS,
    Age2UnitData.MONOREME,
    Age2UnitData.BIREME,
    Age2UnitData.TRIREME,
    Age2UnitData.GALLEY_ANTIQUITY,
    Age2UnitData.WAR_GALLEY_ANTIQUITY,
    Age2UnitData.ELITE_GALLEY,
    Age2UnitData.INCENDIARY_RAFT,
    Age2UnitData.INCENDIARY_SHIP,
    Age2UnitData.HEAVY_INCENDIARY_SHIP,
    Age2UnitData.CATAPULT_SHIP,
    Age2UnitData.ONAGER_SHIP,
    Age2UnitData.LEVIATHAN,
    Age2UnitData.TRANSPORT_SHIP_ANTIQUITY,
    Age2UnitData.MERCHANT_SHIP,
    Age2UnitData.WAR_CHARIOT_ANTIQUITY,
    Age2UnitData.ELITE_WAR_CHARIOT_ANTIQUITY,
})


# Units no tech tree lists at all. Villager (Female) is a variant of the male villager, carried
# because mercenary items name her. War Chariot Barrage is a Three Kingdoms firing mode rather
# than a unit anyone trains. Heroes are not here at all - they live in Age2HeroData.
UNLISTED_UNITS: frozenset[Age2UnitData] = frozenset({
    Age2UnitData.VILLAGER_FEMALE,
    Age2UnitData.WAR_CHARIOT_BARRAGE,
})


UNTRAINABLE: frozenset[Age2UnitData] = OTHER_GAME_MODE_UNITS | UNLISTED_UNITS


Age2CivData.HUNS.included_units = [
    Age2UnitData.TARKAN,
    Age2UnitData.ELITE_TARKAN,
    Age2UnitData.DROMON,
]
Age2CivData.FRANKS.included_units = [
    Age2UnitData.THROWING_AXEMAN,
    Age2UnitData.ELITE_THROWING_AXEMAN,
    Age2UnitData.MOUNTED_CROSSBOWMAN,
    Age2UnitData.HEAVY_MOUNTED_CROSSBOWMAN,
]

Age2CivData.HUNS.excluded_units = [
    Age2UnitData.HAND_CANNONEER,
    Age2UnitData.BOMBARD_CANNON,
    Age2UnitData.CANNON_GALLEON,
    Age2UnitData.ARBALESTER,
    Age2UnitData.FAST_FIRE_SHIP,
    Age2UnitData.HEAVY_SCORPION,
    Age2UnitData.ONAGER,
    Age2UnitData.CHAMPION,
    Age2UnitData.SIEGE_ONAGER,
    Age2UnitData.ELITE_CANNON_GALLEON,
]
Age2CivData.FRANKS.excluded_units = [
    Age2UnitData.CAVALRY_ARCHER,
    Age2UnitData.HUSSAR,
    Age2UnitData.HEAVY_CAVALRY_ARCHER,
    Age2UnitData.ARBALESTER,
    Age2UnitData.SIEGE_RAM,
    Age2UnitData.SIEGE_ONAGER,
    Age2UnitData.ELITE_CANNON_GALLEON,
]


CIV_TO_UNITS: dict[Age2CivData, list[Age2UnitData]] = {}

for civ in Age2CivData:
    included = set(civ.included_units)
    excluded = set(civ.excluded_units)
    trainable = []
    for unit in Age2UnitData:
        if unit in UNTRAINABLE:
            continue
        if unit.unit_type in (UnitType.unique_unit, UnitType.regional_unit):
            if unit in included:
                trainable.append(unit)
        elif unit not in excluded:
            trainable.append(unit)
    CIV_TO_UNITS[civ] = trainable


assert not [civ for civ in Age2CivData
            if set(civ.included_units) & set(civ.excluded_units)], \
    "unit both included and excluded"
assert not (OTHER_GAME_MODE_UNITS & UNLISTED_UNITS), \
    "a unit cannot be both another mode's and unlisted"
assert not [civ for civ in Age2CivData
            if set(civ.included_units) & UNTRAINABLE
            or set(civ.excluded_units) & UNTRAINABLE], \
    "a civilisation names a unit the world holds untrainable"
