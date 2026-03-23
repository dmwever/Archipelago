from worlds.age2de.rules import BuildingRules

from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from rule_builder.rules import Rule, True_


can_reach_feudal: Rule = BuildingRules.two_from_dark_age & BuildingRules.can_build_tc

can_reach_castle: Rule = BuildingRules.two_from_feudal_age & BuildingRules.can_build_tc

can_reach_imperial: Rule = BuildingRules.two_from_castle_age & BuildingRules.can_build_tc

def building_age(building: Age2BuildingData) -> Rule:
    if building.age == Age2AgeData.FEUDAL:
        return can_reach_feudal
    elif building.age == Age2AgeData.CASTLE:
        return can_reach_castle
    elif building.age == Age2AgeData.IMPERIAL:
        return can_reach_imperial
    else:
        return True_()