from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Attila1StartingState(ScenarioStartingState):
    alternate_vils: Rule = HasAny(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name, Age2ItemData.AP_ATTILA_1_ROMAN_VILLAGERS.item_name)
    has_bledas_camp: Rule = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.rules = logic
        self.is_unlocked = Has("Attila the Hun Campaign")
        self.has_vils = self.has_bledas_camp | self.alternate_vils
        self.has_tc = self.has_bledas_camp | (logic.buildings.can_build_tc() & 
            self.alternate_vils)
        self.can_reach_age[Age2AgeData.FEUDAL] = self.has_bledas_camp | (logic.ages.can_reach_feudal() & self.alternate_vils)
        self.can_reach_age[Age2AgeData.CASTLE] = self.has_bledas_camp | (logic.ages.can_reach_castle() & self.alternate_vils)
        self.starts_with_building[Age2BuildingData.STABLE] = self.has_bledas_camp | Has(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name)
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)
        self.starts_with_building[Age2BuildingData.BARRACKS] = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)
        self.starts_with_building[Age2BuildingData.LUMBER_CAMP] = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)
        self.starts_with_building[Age2BuildingData.MILL] = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)
        self.starts_with_building[Age2BuildingData.MARKET] = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)