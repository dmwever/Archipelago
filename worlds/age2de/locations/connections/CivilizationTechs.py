
from ..Civilizations import Age2CivData
from ..Techs import Age2TechData, TechOption

Age2CivData.HUNS.included_techs = [
    Age2TechData.ELITE_TARKAN_HUNS,
    Age2TechData.ATHEISM_HUNS,
    Age2TechData.MARAUDERS_HUNS,
]
Age2CivData.FRANKS.included_techs = [
    Age2TechData.BEARDED_AXE_FRANKS,
    Age2TechData.ELITE_THROWING_AXEMAN_FRANKS,
    Age2TechData.CHIVALRY_FRANKS,
]

Age2CivData.HUNS.excluded_techs = [
    Age2TechData.CROP_ROTATION,
    Age2TechData.ARCHITECTURE,
    Age2TechData.TREADMILL_CRANE,
    Age2TechData.KEEP,
    Age2TechData.BOMBARD_TOWER_TECH,
    Age2TechData.PLATE_MAIL_ARMOR,
    Age2TechData.GUARD_TOWER,
    Age2TechData.FORTIFIED_WALL,
    Age2TechData.RING_ARCHER_ARMOR,
    Age2TechData.BLOCK_PRINTING,
    Age2TechData.ARBALESTER,
    Age2TechData.HEAVY_SCORPION,
    Age2TechData.ONAGER,
    Age2TechData.CHAMPION,
    Age2TechData.STONE_SHAFT_MINING,
    Age2TechData.REDEMPTION,
    Age2TechData.SIEGE_ONAGER,
    Age2TechData.SHIPWRIGHT,
    Age2TechData.ELITE_CANNON_GALLEON,
    Age2TechData.SIEGE_ENGINEERS,
    Age2TechData.HOARDINGS,
    Age2TechData.HEATED_SHOT,
    Age2TechData.THEOCRACY,
    Age2TechData.HERBAL_MEDICINE,
    Age2TechData.ARROWSLITS,
    Age2TechData.GAMBESONS,
    Age2TechData.SIPHONS,
    Age2TechData.INCENDIARIES,
]
Age2CivData.FRANKS.excluded_techs = [
    Age2TechData.GUILDS,
    Age2TechData.TREADMILL_CRANE,
    Age2TechData.KEEP,
    Age2TechData.BOMBARD_TOWER_TECH,
    Age2TechData.BRACER,
    Age2TechData.RING_ARCHER_ARMOR,
    Age2TechData.TWO_MAN_SAW,
    Age2TechData.ARBALESTER,
    Age2TechData.SIEGE_RAM,
    Age2TechData.STONE_SHAFT_MINING,
    Age2TechData.REDEMPTION,
    Age2TechData.ATONEMENT,
    Age2TechData.SIEGE_ONAGER,
    Age2TechData.SHIPWRIGHT,
    Age2TechData.ELITE_CANNON_GALLEON,
    Age2TechData.HEATED_SHOT,
    Age2TechData.HUSSAR,
    Age2TechData.BLOODLINES,
    Age2TechData.PARTHIAN_TACTICS,
    Age2TechData.THUMB_RING,
    Age2TechData.INCENDIARIES,
]


CIV_TO_TECHS: dict[Age2CivData, list[Age2TechData]] = {}

for civ in Age2CivData:
    included = set(civ.included_techs)
    excluded = set(civ.excluded_techs)
    researchable = []
    for tech in Age2TechData:
        if tech.item.type.is_unique or TechOption.regional in tech.tech_options:
            if tech in included:
                researchable.append(tech)
        elif tech not in excluded:
            researchable.append(tech)
    CIV_TO_TECHS[civ] = researchable

assert not [civ for civ in Age2CivData
            if set(civ.included_techs) & set(civ.excluded_techs)], "tech both included and excluded"
