"""What each scenario forbids, over and above what its civilisation cannot do.

A campaign scenario is not a skirmish: it often withholds a building, a unit or a technology
the civilisation would otherwise have. The civilisation lists live beside this one in
CivilizationBuildings, CivilizationUnits and CivilizationTechs, and are asked first; these are
asked second, and either one answering yes puts the thing out of reach.

Nothing is derived. Forbidding the siege workshop does not forbid the ram - the units and the
techs are listed in their own right, because a scenario that leaves a building standing while
withholding only some of what it makes is just as ordinary.
"""

from ..Buildings import Age2BuildingData
from ..Scenarios import Age2ScenarioData
from ..Techs import Age2TechData
from ..Units import Age2UnitData

# Attila 1 and 2 withhold nothing of their own: what they gate is the base itself, and
# has_vils carries that. The houses the Huns cannot build, and the fast fire ships they
# cannot launch, belong to the civilisation and are already in CivilizationUnits.

Age2ScenarioData.AP_ATTILA_4.has_water_access = False
Age2ScenarioData.AP_GENGHIS_2.has_water_access = False

Age2ScenarioData.AP_ATTILA_3.excluded_buildings = [
    Age2BuildingData.MARKET,
]
Age2ScenarioData.AP_ATTILA_3.excluded_units = [
    Age2UnitData.TRADE_CART,
]
Age2ScenarioData.AP_ATTILA_3.excluded_techs = [
    Age2TechData.CARAVAN,
    Age2TechData.COINAGE,
]

# Joan 1 and 5 are fixed forces. Joan 2 and 3 withhold nothing; the mill technologies their
# sheets mention are handed to the Franks, not kept from them.

Age2ScenarioData.AP_JOAN_4.excluded_units = [
    Age2UnitData.HAND_CANNONEER,
    Age2UnitData.BOMBARD_CANNON,
    Age2UnitData.CANNON_GALLEON,
]
Age2ScenarioData.AP_JOAN_4.excluded_techs = [
    Age2TechData.SAPPERS,
]

Age2ScenarioData.AP_JOAN_6.excluded_techs = [
    Age2TechData.SAPPERS,
]

# Genghis 1 is a fixed force: no economy at all, which fixed_force already says.

Age2ScenarioData.AP_GENGHIS_2.excluded_buildings = [
    Age2BuildingData.SIEGE_WORKSHOP,
]
Age2ScenarioData.AP_GENGHIS_2.excluded_units = [
    Age2UnitData.BATTERING_RAM,
    Age2UnitData.MANGONEL,
    Age2UnitData.SCORPION,
    Age2UnitData.SIEGE_TOWER,
    Age2UnitData.PETARD,
]
Age2ScenarioData.AP_GENGHIS_2.excluded_techs = [
    Age2TechData.CAREENING,
    Age2TechData.CLINKER_CONSTRUCTION,
    Age2TechData.SIPHONS,
    Age2TechData.SHIPWRIGHT,
]

Age2ScenarioData.AP_GENGHIS_3.excluded_buildings = [
    Age2BuildingData.WONDER,
]

Age2ScenarioData.AP_GENGHIS_4.excluded_units = [
    Age2UnitData.TRADE_CART,
]

Age2ScenarioData.AP_GENGHIS_5.excluded_techs = [
    Age2TechData.CAREENING,
    Age2TechData.CLINKER_CONSTRUCTION,
    Age2TechData.SIPHONS,
    Age2TechData.CARVEL_HULL,
    Age2TechData.SHIPWRIGHT,
]

Age2ScenarioData.AP_GENGHIS_6.excluded_buildings = [
    Age2BuildingData.DOCK,
    Age2BuildingData.FISH_TRAP,
]
Age2ScenarioData.AP_GENGHIS_6.excluded_units = [
    Age2UnitData.FIRE_SHIP,
    Age2UnitData.FAST_FIRE_SHIP,
    Age2UnitData.WAR_GALLEY,
    Age2UnitData.GALLEON,
    Age2UnitData.WAR_HULK,
    Age2UnitData.DEMOLITION_SHIP,
    Age2UnitData.HEAVY_DEMOLITION_SHIP,
    Age2UnitData.TRADE_COG,
    Age2UnitData.FISHING_SHIP,
    Age2UnitData.TRANSPORT_SHIP,
]
Age2ScenarioData.AP_GENGHIS_6.excluded_techs = [
    Age2TechData.CARVEL_HULL,
    Age2TechData.SHIPWRIGHT,
    Age2TechData.HEAVY_WARSHIPS,
]
