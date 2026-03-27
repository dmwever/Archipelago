from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioRules import ScenarioStartingState


if TYPE_CHECKING:
    from .. import Age2World
    from ..Rules import Rules

class Attila1Rules(ScenarioStartingState):
    alternate_vils: Rule = Has(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name) | Has(Age2ItemData.AP_ATTILA_1_ROMAN_VILLAGERS.item_name)
    has_bledas_camp: Rule = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)

    def __init__(self, rules: 'Rules'):
        self.rules = rules
        self.has_vils = self.has_bledas_camp | self.alternate_vils
        self.has_tc = self.has_bledas_camp | (rules.age_rules.can_build_tc & 
            self.alternate_vils)
        self.has_ages[Age2AgeData.DARK] = True_()
        self.can_reach_age[Age2AgeData.FEUDAL] = self.has_bledas_camp | (rules.age_rules.can_reach_feudal & self.alternate_vils)
        self.can_reach_age[Age2AgeData.CASTLE] = self.has_bledas_camp | (rules.age_rules.can_reach_castle & self.alternate_vils)
        self.starts_with_building[Age2BuildingData.STABLE] = self.has_bledas_camp | Has(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name)
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)