from ..Scenarios import Age2ScenarioData
from ..Units import Age2UnitData

SCENARIO_TO_CAVEMAN_EXEMPTIONS: dict[Age2ScenarioData, list[Age2UnitData]] = {
    Age2ScenarioData.AP_ATTILA_1: [],
    Age2ScenarioData.AP_ATTILA_2: [],
    Age2ScenarioData.AP_ATTILA_3: [],
    Age2ScenarioData.AP_ATTILA_4: [],
    Age2ScenarioData.AP_ATTILA_5: [],
    Age2ScenarioData.AP_ATTILA_6: [],
    Age2ScenarioData.AP_JOAN_1: [],
    Age2ScenarioData.AP_JOAN_2: [
        Age2UnitData.TRADE_CART,
    ],
    Age2ScenarioData.AP_JOAN_3: [],
    Age2ScenarioData.AP_JOAN_4: [],
    Age2ScenarioData.AP_JOAN_5: [],
    Age2ScenarioData.AP_JOAN_6: [],
    Age2ScenarioData.AP_GENGHIS_1: [],
    Age2ScenarioData.AP_GENGHIS_2: [],
    Age2ScenarioData.AP_GENGHIS_3: [],
    Age2ScenarioData.AP_GENGHIS_4: [
        Age2UnitData.TRADE_CART,
    ],
    Age2ScenarioData.AP_GENGHIS_5: [],
    Age2ScenarioData.AP_GENGHIS_6: [],
}


for _scenario, _units in SCENARIO_TO_CAVEMAN_EXEMPTIONS.items():
    _scenario.caveman_exempt_units = _units


assert not [scenario for scenario in Age2ScenarioData
            if scenario not in SCENARIO_TO_CAVEMAN_EXEMPTIONS], \
    "a scenario has no caveman exemption list, not even an empty one"
