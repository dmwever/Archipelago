"""The kinds of location a unit can be, and how to get from an id back to one.

Vocabulary rather than seed shape: the client reads these at install time, when it has location
ids and slot data but no world and no pools.
"""

from .EscortUnits import Age2EscortUnitData
from .Heroes import Age2HeroData
from .UnitLines import Age2UnitLineData
from .Units import Age2UnitData
from .VillagerJobs import Age2VillagerJobData

type UnitLocation = (Age2UnitData | Age2UnitLineData | Age2VillagerJobData | Age2HeroData
                     | Age2EscortUnitData)

VILLAGER_LINES = (Age2UnitLineData.VILLAGER_MALE_LINE, Age2UnitLineData.VILLAGER_FEMALE_LINE)

UNIT_LOCATION_TYPES = (Age2UnitData, Age2UnitLineData, Age2VillagerJobData, Age2HeroData,
                       Age2EscortUnitData)


def unit_location(id: int) -> UnitLocation | None:
    for kind in UNIT_LOCATION_TYPES:
        if id in kind:
            return kind(id)
    return None
