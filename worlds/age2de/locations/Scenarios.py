
import enum
from .Campaigns import Age2CampaignData
from .Civilizations import Age2CivData


class Age2ScenarioData(enum.IntEnum):
    def __new__(cls, name: str, short_name: str, xsdat_read_name: str, xsdat_write_name: str, campaign: Age2CampaignData, chapter: int, civ: Age2CivData, completion_bit: int):
        value = campaign.value * 100 + chapter
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(
        self, name: str, short_name: str, xsdat_read_name: str, xsdat_write_name: str, campaign: Age2CampaignData, chapter: int, civ: Age2CivData, completion_bit: int
    ) -> None:
        self.id = self.value
        self.scenario_name = name
        self.short_name = short_name
        self.xsdat_read_name = xsdat_read_name
        self.xsdat_write_name = xsdat_write_name
        self.campaign = campaign
        self.chapter = chapter
        self.civ = civ
        self.completion_bit = completion_bit
    
    AP_ATTILA_1 =           "The Scourge of God", "AP_Attila_1.xsdat", "ATT1.xsdat", Age2CampaignData.ATTILA, 1, Age2CivData.HUNS, 0
    AP_ATTILA_2 =               "The Great Ride", "AP_Attila_2.xsdat", "ATT2.xsdat", Age2CampaignData.ATTILA, 2, Age2CivData.HUNS, 1
    AP_ATTILA_3 =  "The Walls of Constantinople", "AP_Attila_3.xsdat", "ATT3.xsdat", Age2CampaignData.ATTILA, 3, Age2CivData.HUNS, 2
    AP_ATTILA_4 =        "A Barbarian Betrothal", "AP_Attila_4.xsdat", "ATT4.xsdat", Age2CampaignData.ATTILA, 4, Age2CivData.HUNS, 3
    AP_ATTILA_5 =        "The Catalunian Fields", "AP_Attila_5.xsdat", "ATT5.xsdat", Age2CampaignData.ATTILA, 5, Age2CivData.HUNS, 4
    AP_ATTILA_6 =             "The Fall of Rome", "AP_Attila_6.xsdat", "ATT6.xsdat", Age2CampaignData.ATTILA, 6, Age2CivData.HUNS, 5
    
    AP_JOAN_1 =          "An Unlikely Messiah", "AP_Joan_1.xsdat", "JOAN1.xsdat", Age2CampaignData.JOAN, 1, Age2CivData.FRANKS, 6
    AP_JOAN_2 =          "The Maid of Orleans", "AP_Joan_2.xsdat", "JOAN2.xsdat", Age2CampaignData.JOAN, 2, Age2CivData.FRANKS, 7
    AP_JOAN_3 =   "The Cleansing of the Loire", "AP_Joan_3.xsdat", "JOAN3.xsdat", Age2CampaignData.JOAN, 3, Age2CivData.FRANKS, 8
    AP_JOAN_4 =                   "The Rising", "AP_Joan_4.xsdat", "JOAN4.xsdat", Age2CampaignData.JOAN, 4, Age2CivData.FRANKS, 9
    AP_JOAN_5 =           "The Siege of Paris", "AP_Joan_5.xsdat", "JOAN5.xsdat", Age2CampaignData.JOAN, 5, Age2CivData.FRANKS, 10
    AP_JOAN_6 =             "A Perfect Martyr", "AP_Joan_6.xsdat", "JOAN6.xsdat", Age2CampaignData.JOAN, 6, Age2CivData.FRANKS, 11
    
scenario_from_id = {_scenario.id: _scenario for _scenario in Age2ScenarioData}
scenario_names: list[Age2ScenarioData] = [scn.scenario_name for scn in Age2ScenarioData]
CAMPAIGN_TO_SCENARIOS: dict[Age2CampaignData, list[Age2ScenarioData]] = {_campaign: [] for _campaign in Age2CampaignData}
for _scenario in Age2ScenarioData:
    CAMPAIGN_TO_SCENARIOS[_scenario.campaign].append(_scenario)