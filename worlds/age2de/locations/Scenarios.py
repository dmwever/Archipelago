
import enum
from worlds.age2de.locations.Campaigns import Age2CampaignData
from worlds.age2de.locations.Civilizations import Age2Civ


class Age2ScenarioData(enum.IntEnum):
    def __new__(cls, name: str, short_name: str, campaign: Age2CampaignData, chapter: int, civ: Age2Civ):
        value = campaign.value * 100 + chapter
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(
        self, name: str, short_name: str, campaign: Age2CampaignData, chapter: int, civ: Age2Civ
    ) -> None:
        self.id = self.value
        self.scenario_name = name
        self.short_name = short_name
        self.campaign = campaign
        self.chapter = chapter
        self.civ = civ
        
    GENERAL = "General", "wc3", Age2CampaignData.GENERAL, 0, Age2Civ.NONE

    C1_ATTILA_1 =           "The Scourge of God", "H1", Age2CampaignData.ATTILA, 1, Age2Civ.HUNS
    C1_ATTILA_2 =               "The Great Ride", "H2", Age2CampaignData.ATTILA, 1, Age2Civ.HUNS
    C1_ATTILA_3 =  "The Walls of Constantinople", "H3", Age2CampaignData.ATTILA, 1, Age2Civ.HUNS
    C1_ATTILA_4 =        "A Barbarian Betrothal", "H4", Age2CampaignData.ATTILA, 1, Age2Civ.HUNS
    C1_ATTILA_5 =        "The Catalunian Fields", "H5", Age2CampaignData.ATTILA, 1, Age2Civ.HUNS
    C1_ATTILA_6 =             "The Fall of Rome", "H6", Age2CampaignData.ATTILA, 1, Age2Civ.HUNS