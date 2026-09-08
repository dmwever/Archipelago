import enum

class Age2CampaignData(enum.Enum):
    def __new__(cls, id: int, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = id
        return obj

    def __init__(self, id: int, name: str, file_stem: str) -> None:
        self.id = id
        self.campaign_name = name
        self.file_stem = file_stem
    
    ATTILA  =       1, "Attila the Hun", "AP Attila the Hun"
    JOAN  =         2, "Joan of Arc", "AP Joan of Arc"