
import enum
from worlds.age2de.locations.Campaigns import Age2CampaignData
from worlds.age2de.locations.Civilizations import Age2Civ


class Age2ScenarioData(enum.IntEnum):
    def __new__(cls, name: str, short_name: str, xsdat_read_name: str, xsdat_write_name: str, campaign: Age2CampaignData, chapter: int, civ: Age2Civ):
        value = campaign.value * 100 + chapter
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(
        self, name: str, short_name: str, xsdat_read_name: str, xsdat_write_name: str, campaign: Age2CampaignData, chapter: int, civ: Age2Civ
    ) -> None:
        self.id = self.value
        self.scenario_name = name
        self.short_name = short_name
        self.xsdat_read_name = xsdat_read_name
        self.xsdat_write_name = xsdat_write_name
        self.campaign = campaign
        self.chapter = chapter
        self.civ = civ
        
    GENERAL = "General", "age2", "AP.xsdat", "", Age2CampaignData.GENERAL, 0, Age2Civ.NONE

    AP_ATTILA_1 =           "The Scourge of God", "H1", "AP_Attila_1.xsdat", "ATT1.xsdat", Age2CampaignData.ATTILA, 1, Age2Civ.HUNS
    AP_ATTILA_2 =               "The Great Ride", "H2", "AP_Attila_2.xsdat", "ATT2.xsdat", Age2CampaignData.ATTILA, 2, Age2Civ.HUNS
    AP_ATTILA_3 =  "The Walls of Constantinople", "H3", "AP_Attila_3.xsdat", "ATT3.xsdat", Age2CampaignData.ATTILA, 3, Age2Civ.HUNS
    AP_ATTILA_4 =        "A Barbarian Betrothal", "H4", "AP_Attila_4.xsdat", "ATT4.xsdat", Age2CampaignData.ATTILA, 4, Age2Civ.HUNS
    AP_ATTILA_5 =        "The Catalunian Fields", "H5", "AP_Attila_5.xsdat", "ATT5.xsdat", Age2CampaignData.ATTILA, 5, Age2Civ.HUNS
    AP_ATTILA_6 =             "The Fall of Rome", "H6", "AP_Attila_6.xsdat", "ATT6.xsdat", Age2CampaignData.ATTILA, 6, Age2Civ.HUNS