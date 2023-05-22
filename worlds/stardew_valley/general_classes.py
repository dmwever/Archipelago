from enum import IntFlag
from typing import Optional, List
from dataclasses import dataclass, field

connector_keyword = " to "


class RandomizationFlag(IntFlag):
    NOT_RANDOMIZED = 0b0
    PELICAN_TOWN = 0b11111
    NON_PROGRESSION = 0b11110
    BUILDINGS = 0b11100
    EVERYTHING = 0b11000
    CHAOS = 0b10000
    GINGER_ISLAND = 0b0100000
    LEAD_TO_OPEN_AREA = 0b1000000


@dataclass(frozen=True)
class RegionData:
    name: str
    exits: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ConnectionData:
    name: str
    destination: str
    origin: Optional[str] = None
    reverse: Optional[str] = None
    flag: RandomizationFlag = RandomizationFlag.NOT_RANDOMIZED

    def __post_init__(self):
        if connector_keyword in self.name:
            origin, destination = self.name.split(connector_keyword)
            if self.reverse is None:
                super().__setattr__("reverse", f"{destination}{connector_keyword}{origin}")


@dataclass(frozen=True)
class ModData:
    mod_name: str
    regions: List[RegionData]
    connections: List[ConnectionData]

