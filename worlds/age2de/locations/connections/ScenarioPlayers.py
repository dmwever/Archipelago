from ..Players import Age2PlayerData
from ..Scenarios import Age2ScenarioData

SCENARIO_TO_PLAYERS: dict[Age2ScenarioData, list[Age2PlayerData]] = {
    Age2ScenarioData.AP_ATTILA_1: [
        Age2PlayerData.ATT1_SCYTHIANS,
        Age2PlayerData.ATT1_PERSIANS,
        Age2PlayerData.ATT1_EASTERN_ROMAN_EMPIRE,
    ],
    Age2ScenarioData.AP_ATTILA_2: [
        Age2PlayerData.ATT2_SOFIA,
        Age2PlayerData.ATT2_NAISSUS,
        Age2PlayerData.ATT2_ADRIANOPLE,
        Age2PlayerData.ATT2_DYRRHACHIUM,
        Age2PlayerData.ATT2_THESSALONICA,
        Age2PlayerData.ATT2_EASTERN_ROMAN_EMPIRE,
    ],
    Age2ScenarioData.AP_ATTILA_3: [
        Age2PlayerData.ATT3_CONSTANTINOPLE,
        Age2PlayerData.ATT3_MARCIANOPOLIS,
        Age2PlayerData.ATT3_PHILIPPOPOLIS,
    ],
    Age2ScenarioData.AP_ATTILA_4: [
        Age2PlayerData.ATT4_BURGUNDY,
        Age2PlayerData.ATT4_METZ,
        Age2PlayerData.ATT4_ORLEANS,
        Age2PlayerData.ATT4_WESTERN_ROMAN_EMPIRE,
    ],
    Age2ScenarioData.AP_ATTILA_5: [
        Age2PlayerData.ATT5_OSTROGOTHS,
        Age2PlayerData.ATT5_WESTERN_ROMAN_EMPIRE,
        Age2PlayerData.ATT5_VISIGOTHS,
        Age2PlayerData.ATT5_ALANS,
    ],
    Age2ScenarioData.AP_ATTILA_6: [
        Age2PlayerData.ATT6_AQUILEIA,
        Age2PlayerData.ATT6_MEDIOLANUM,
        Age2PlayerData.ATT6_VERONA,
        Age2PlayerData.ATT6_PATAVIUM,
        Age2PlayerData.ATT6_WESTERN_ROMAN_EMPIRE,
    ],
    # Fixed force: no economy, so no one to trade with.
    Age2ScenarioData.AP_JOAN_1: [],
    Age2ScenarioData.AP_JOAN_2: [
        Age2PlayerData.JOAN2_BURGUNDY,
        Age2PlayerData.JOAN2_NORTHERN_ENGLISH,
        Age2PlayerData.JOAN2_ORLEANS,
        Age2PlayerData.JOAN2_BLOIS,
        Age2PlayerData.JOAN2_CHINON,
        Age2PlayerData.JOAN2_SOUTHERN_ENGLISH,
    ],
    Age2ScenarioData.AP_JOAN_3: [
        Age2PlayerData.JOAN3_BURGUNDY,
        Age2PlayerData.JOAN3_ENGLISH,
        Age2PlayerData.JOAN3_FASTOLF,
    ],
    Age2ScenarioData.AP_JOAN_4: [
        Age2PlayerData.JOAN4_TROYES,
        Age2PlayerData.JOAN4_CHALONS,
        Age2PlayerData.JOAN4_RHEIMS,
        Age2PlayerData.JOAN4_ENGLISH_GUARDS,
    ],
    # Fixed force: no economy, so no one to trade with.
    Age2ScenarioData.AP_JOAN_5: [],
    Age2ScenarioData.AP_JOAN_6: [
        Age2PlayerData.JOAN6_BURGUNDY,
        Age2PlayerData.JOAN6_ENGLISH,
        Age2PlayerData.JOAN6_SHREWSBURY,
    ],
    Age2ScenarioData.AP_GENGHIS_1: [
        Age2PlayerData.GEN1_GENGHIS_KHAN,
        Age2PlayerData.GEN1_KEREYIDS,
        Age2PlayerData.GEN1_TAYICHIUDS,
        Age2PlayerData.GEN1_UIGHURS,
        Age2PlayerData.GEN1_NAIMAN,
        Age2PlayerData.GEN1_UNGIRRADS,
    ],
    Age2ScenarioData.AP_GENGHIS_2: [
        Age2PlayerData.GEN2_KARA_KHITAI,
        Age2PlayerData.GEN2_KUSHLUK,
    ],
    Age2ScenarioData.AP_GENGHIS_3: [
        Age2PlayerData.GEN3_TANGUTS,
        Age2PlayerData.GEN3_XI_XIA,
        Age2PlayerData.GEN3_JIN,
        Age2PlayerData.GEN3_SONG,
    ],
    Age2ScenarioData.AP_GENGHIS_4: [
        Age2PlayerData.GEN4_KIPCHAKS,
        Age2PlayerData.GEN4_RUSSIANS,
        Age2PlayerData.GEN4_KHWARAZM,
    ],
    Age2ScenarioData.AP_GENGHIS_5: [
        Age2PlayerData.GEN5_POLISH,
        Age2PlayerData.GEN5_BOHEMIANS,
        Age2PlayerData.GEN5_GERMANS,
    ],
    Age2ScenarioData.AP_GENGHIS_6: [
        Age2PlayerData.GEN6_HUNGARY,
    ],
}

for _scenario, _players in SCENARIO_TO_PLAYERS.items():
    _scenario.players = _players
