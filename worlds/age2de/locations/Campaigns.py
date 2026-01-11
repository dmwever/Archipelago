
import enum


class Age2CampaignData(enum.Enum):
    def __new__(cls, id: int, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = id
        return obj

    def __init__(self, id: int, mnemonic: str, civ: str, name: str) -> None:
        self.id = id
        self.mnemonic = mnemonic
        self.civ = civ
        self.campaign_name = name
        
    ATTILA  =     1, "H", "Huns", "Attila the Hun"