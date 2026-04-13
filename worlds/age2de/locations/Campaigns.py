import enum

class Age2CampaignData(enum.Enum):
    def __new__(cls, id: int, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = id
        return obj

    def __init__(self, id: int, name: str, xsdat_read_name) -> None:
        self.id = id
        self.campaign_name = name
        self.xsdat_read_name = xsdat_read_name
    
    ATTILA  =       1, "Attila the Hun", "AP Attila the Hun.xsdat"