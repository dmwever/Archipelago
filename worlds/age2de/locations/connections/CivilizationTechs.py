
from ..Civilizations import Age2CivData
from ..Techs import Age2TechData


# Technologies only some civilizations reach: unique technologies, and the
# regional lines a group of civilizations shares, such as Eagle Warrior. Both
# go here, so a technology is gated on a civilization owning it rather than on
# every other civilization excluding it.
Age2CivData.HUNS.included_techs = [
    Age2TechData.ELITE_TARKAN_HUNS,
    Age2TechData.MARAUDERS_HUNS,
    Age2TechData.ATHEISM_HUNS,
]
Age2CivData.FRANKS.included_techs = [
    Age2TechData.ELITE_THROWING_AXEMAN_FRANKS,
    Age2TechData.BEARDED_AXE_FRANKS,
    Age2TechData.CHIVALRY_FRANKS,
]

# Shared technologies this civilization's tech tree leaves out. Both lists are
# read off the in-game tech tree, where a greyed node is excluded and a node
# only some civilizations show at all is restricted, so it belongs above.
# Empty means the civilization researches everything, which is not yet true.
Age2CivData.HUNS.excluded_techs = []
Age2CivData.FRANKS.excluded_techs = []
