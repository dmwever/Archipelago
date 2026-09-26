from ...items.Items import Mercenary, SCENARIO_TO_ITEMS
from ..Heroes import Age2HeroData
from ..Scenarios import Age2ScenarioData, ScenarioUnit
from ..Units import Age2UnitData
AUTHORED_TRIGGER_UNITS: dict[Age2ScenarioData, list[ScenarioUnit]] = {
    Age2ScenarioData.AP_ATTILA_1: [
        Age2UnitData.TARKAN,
        Age2UnitData.SCOUT_CAVALRY,
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
        Age2HeroData.ATTILA_THE_HUN,
    ],
    Age2ScenarioData.AP_ATTILA_2: [
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
    ],
    Age2ScenarioData.AP_ATTILA_3: [],
    Age2ScenarioData.AP_ATTILA_4: [],
    Age2ScenarioData.AP_ATTILA_5: [],
    Age2ScenarioData.AP_ATTILA_6: [],
    Age2ScenarioData.AP_JOAN_1: [
        Age2UnitData.TRANSPORT_SHIP,
    ],
    Age2ScenarioData.AP_JOAN_2: [
        Age2UnitData.TRANSPORT_SHIP,
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
        Age2UnitData.CROSSBOWMAN,
        Age2UnitData.KNIGHT,
        Age2UnitData.TRADE_CART,
    ],
    Age2ScenarioData.AP_JOAN_3: [
        Age2UnitData.TRANSPORT_SHIP,
        Age2UnitData.DEMOLITION_SHIP,
    ],
    Age2ScenarioData.AP_JOAN_4: [
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
        Age2UnitData.CROSSBOWMAN,
    ],
    Age2ScenarioData.AP_JOAN_5: [
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
    ],
    Age2ScenarioData.AP_JOAN_6: [
        Age2UnitData.ARCHER,
        Age2UnitData.MILITIA,
        Age2UnitData.SCOUT_CAVALRY,
        Age2UnitData.KNIGHT,
        Age2UnitData.TREBUCHET_PACKED,
        Age2UnitData.VILLAGER_MALE,
        Age2UnitData.VILLAGER_FEMALE,
        Age2HeroData.LA_HIRE,
        Age2HeroData.CONSTABLE_RICHEMONT,
    ],
}


def _mercenary_units(scenario: Age2ScenarioData) -> list[ScenarioUnit]:
    """What this scenario's own mercenary musters spawn."""
    return [soldier.unit
            for item in SCENARIO_TO_ITEMS[scenario] if item.type_data is Mercenary
            for soldier in item.type.units]


SCENARIO_TO_TRIGGER_UNITS: dict[Age2ScenarioData, list[ScenarioUnit]] = {}

for _scenario in Age2ScenarioData:
    _granted: list[ScenarioUnit] = list(AUTHORED_TRIGGER_UNITS.get(_scenario, []))
    for _unit in _mercenary_units(_scenario):
        if _unit not in _granted:
            _granted.append(_unit)
    SCENARIO_TO_TRIGGER_UNITS[_scenario] = _granted
    _scenario.trigger_units = _granted


assert not [scenario for scenario in Age2ScenarioData
            if scenario not in AUTHORED_TRIGGER_UNITS], \
    "a scenario has no authored trigger list, not even an empty one"
