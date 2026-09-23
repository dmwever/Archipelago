from ..Heroes import Age2HeroData
from ..Scenarios import Age2ScenarioData, ScenarioUnit
from ..Units import Age2UnitData

SCENARIO_TO_STARTUP_UNITS: dict[Age2ScenarioData, list[ScenarioUnit]] = {
    # Attila arrives by trigger here, not on the map - see ScenarioTriggerUnits.
    Age2ScenarioData.AP_ATTILA_1: [],
    Age2ScenarioData.AP_ATTILA_2: [
        Age2UnitData.CAVALRY_ARCHER,
        Age2UnitData.TARKAN,
    ],
    Age2ScenarioData.AP_ATTILA_3: [
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
        Age2UnitData.MONK,
        Age2UnitData.TARKAN,
    ],
    Age2ScenarioData.AP_ATTILA_4: [
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
        Age2UnitData.SCOUT_CAVALRY,
    ],
    Age2ScenarioData.AP_ATTILA_5: [
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
        Age2UnitData.SCOUT_CAVALRY,
        Age2UnitData.TARKAN,
    ],
    Age2ScenarioData.AP_ATTILA_6: [
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
        Age2UnitData.TREBUCHET_PACKED,
        Age2UnitData.HEAVY_CAVALRY_ARCHER,
        Age2UnitData.TARKAN,
        Age2HeroData.ATTILA_THE_HUN,
    ],
    # Joan starts with her escort and nothing else - every soldier arrives by trigger.
    Age2ScenarioData.AP_JOAN_1: [
        Age2HeroData.JOAN_THE_MAID,
        Age2HeroData.SIEUR_DE_METZ,
        Age2HeroData.SIEUR_BERTRAND,
    ],
    Age2ScenarioData.AP_JOAN_2: [
        Age2UnitData.KNIGHT,
        Age2UnitData.TWO_HANDED_SWORDSMAN,
        Age2UnitData.SCOUT_CAVALRY,
        Age2HeroData.JOAN_OF_ARC,
        Age2HeroData.DUKE_D_ALENCON,
    ],
    Age2ScenarioData.AP_JOAN_3: [
        Age2UnitData.CROSSBOWMAN,
        Age2UnitData.KNIGHT,
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.PIKEMAN,
        Age2UnitData.SCOUT_CAVALRY,
        Age2HeroData.JOAN_OF_ARC,
        Age2HeroData.LA_HIRE,
    ],
    Age2ScenarioData.AP_JOAN_4: [
        Age2UnitData.CROSSBOWMAN,
        Age2UnitData.KNIGHT,
        Age2UnitData.MAN_AT_ARMS,
        Age2UnitData.MONK,
        Age2UnitData.SCOUT_CAVALRY,
        Age2HeroData.JOAN_OF_ARC,
    ],
    Age2ScenarioData.AP_JOAN_5: [
        Age2UnitData.CROSSBOWMAN,
        Age2UnitData.BOMBARD_CANNON,
        Age2UnitData.CAVALIER,
        Age2UnitData.PALADIN,
        Age2UnitData.TREBUCHET_PACKED,
        Age2UnitData.PIKEMAN,
        Age2UnitData.SCOUT_CAVALRY,
        Age2HeroData.JOAN_OF_ARC,
        Age2HeroData.LORD_DE_GRAVILLE,
        Age2HeroData.JEAN_DE_LORRAIN,
    ],
    Age2ScenarioData.AP_JOAN_6: [
        Age2UnitData.CART,
        Age2HeroData.GUY_JOSSELYNE,
    ],
}


for _scenario, _units in SCENARIO_TO_STARTUP_UNITS.items():
    _scenario.startup_units = _units


assert not [scenario for scenario in Age2ScenarioData
            if scenario not in SCENARIO_TO_STARTUP_UNITS], \
    "a scenario has no startup unit list, not even an empty one"
