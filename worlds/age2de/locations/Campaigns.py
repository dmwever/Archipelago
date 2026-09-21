import enum

class Age2CampaignData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        obj = int.__new__(cls, id)
        obj._value_ = id
        return obj

    def __init__(self, id: int, name: str, file_stem: str) -> None:
        self.id = id
        self.campaign_name = name
        self.file_stem = file_stem
    
    ATTILA  =       1, "Attila the Hun", "AP Attila the Hun"
    JOAN  =         2, "Joan of Arc", "AP Joan of Arc"

NAME_TO_CAMPAIGN = {campaign.campaign_name: campaign for campaign in Age2CampaignData}