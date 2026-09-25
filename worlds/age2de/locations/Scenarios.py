
import enum
from typing import TYPE_CHECKING

from .Ages import Age2AgeData
from .Campaigns import Age2CampaignData
from .Civilizations import Age2CivData
from .EscortUnits import Age2EscortUnitData
from .Heroes import Age2HeroData
from .Units import Age2UnitData
type ScenarioUnit = Age2UnitData | Age2HeroData | Age2EscortUnitData

if TYPE_CHECKING:
    from ..rules.ScenarioRules import ScenarioRules
    from ..logic.ScenarioLogic import ScenarioStartingState

class Age2ScenarioData(enum.IntEnum):
    def __new__(cls, name: str, file_stem: str, xsdat_write_name: str, campaign: Age2CampaignData, chapter: int, civ: Age2CivData,
                vanilla_age: Age2AgeData):
        value = campaign.value * 100 + chapter
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(
        self, name: str, file_stem: str, xsdat_write_name: str, campaign: Age2CampaignData, chapter: int, civ: Age2CivData,
        vanilla_age: Age2AgeData
    ) -> None:
        self.id = self.value
        self.scenario_name = name
        self.file_stem = file_stem
        self.xsdat_write_name = xsdat_write_name
        self.campaign = campaign
        self.chapter = chapter
        self.civ = civ
        self.vanilla_age = vanilla_age
        self.rules: 'ScenarioRules' = None
        self.logic: 'ScenarioStartingState' = None
        self.startup_units: list[ScenarioUnit] = []
        self.trigger_units: list[ScenarioUnit] = []
    
    AP_ATTILA_1 =           "The Scourge of God", "AP_Attila_1", "ATT1.xsdat", Age2CampaignData.ATTILA, 1, Age2CivData.HUNS, Age2AgeData.DARK
    AP_ATTILA_2 =               "The Great Ride", "AP_Attila_2", "ATT2.xsdat", Age2CampaignData.ATTILA, 2, Age2CivData.HUNS, Age2AgeData.CASTLE
    AP_ATTILA_3 =  "The Walls of Constantinople", "AP_Attila_3", "ATT3.xsdat", Age2CampaignData.ATTILA, 3, Age2CivData.HUNS, Age2AgeData.CASTLE
    AP_ATTILA_4 =        "A Barbarian Betrothal", "AP_Attila_4", "ATT4.xsdat", Age2CampaignData.ATTILA, 4, Age2CivData.HUNS, Age2AgeData.CASTLE
    AP_ATTILA_5 =        "The Catalunian Fields", "AP_Attila_5", "ATT5.xsdat", Age2CampaignData.ATTILA, 5, Age2CivData.HUNS, Age2AgeData.CASTLE
    AP_ATTILA_6 =             "The Fall of Rome", "AP_Attila_6", "ATT6.xsdat", Age2CampaignData.ATTILA, 6, Age2CivData.HUNS, Age2AgeData.IMPERIAL
    
    AP_JOAN_1 =          "An Unlikely Messiah", "AP_Joan_1", "JOAN1.xsdat", Age2CampaignData.JOAN, 1, Age2CivData.FRANKS, Age2AgeData.CASTLE
    AP_JOAN_2 =          "The Maid of Orleans", "AP_Joan_2", "JOAN2.xsdat", Age2CampaignData.JOAN, 2, Age2CivData.FRANKS, Age2AgeData.FEUDAL
    AP_JOAN_3 =   "The Cleansing of the Loire", "AP_Joan_3", "JOAN3.xsdat", Age2CampaignData.JOAN, 3, Age2CivData.FRANKS, Age2AgeData.FEUDAL
    AP_JOAN_4 =                   "The Rising", "AP_Joan_4", "JOAN4.xsdat", Age2CampaignData.JOAN, 4, Age2CivData.FRANKS, Age2AgeData.CASTLE
    AP_JOAN_5 =           "The Siege of Paris", "AP_Joan_5", "JOAN5.xsdat", Age2CampaignData.JOAN, 5, Age2CivData.FRANKS, Age2AgeData.IMPERIAL
    AP_JOAN_6 =             "A Perfect Martyr", "AP_Joan_6", "JOAN6.xsdat", Age2CampaignData.JOAN, 6, Age2CivData.FRANKS, Age2AgeData.CASTLE
    
scenario_from_id = {_scenario.id: _scenario for _scenario in Age2ScenarioData}
scenario_names: list[Age2ScenarioData] = [scn.scenario_name for scn in Age2ScenarioData]
CAMPAIGN_TO_SCENARIOS: dict[Age2CampaignData, list[Age2ScenarioData]] = {_campaign: [] for _campaign in Age2CampaignData}
for _scenario in Age2ScenarioData:
    CAMPAIGN_TO_SCENARIOS[_scenario.campaign].append(_scenario)