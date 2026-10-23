from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Units import Age2UnitData as U
from ...locations.EscortUnits import Age2EscortUnitData as E
from ...locations.Heroes import Age2HeroData as H
from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Attila1StartingState(ScenarioStartingState):
    alternate_vils: Rule = HasAny(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name, Age2ItemData.AP_ATTILA_1_ROMAN_VILLAGERS.item_name)
    has_bledas_camp: Rule = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has("Attila the Hun Campaign")
        self.has_vils = self.has_bledas_camp | self.alternate_vils
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = self.has_bledas_camp
        self.starts_with_building[Age2BuildingData.STABLE] = self.has_bledas_camp | Has(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name)
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = self.has_bledas_camp
        self.starts_with_building[Age2BuildingData.BARRACKS] = self.has_bledas_camp
        self.starts_with_building[Age2BuildingData.LUMBER_CAMP] = self.has_bledas_camp
        self.starts_with_building[Age2BuildingData.MILL] = self.has_bledas_camp
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = self.has_bledas_camp
        self.starts_with_building[Age2BuildingData.MARKET] = self.has_bledas_camp

        self.obtains_unit[U.TARKAN] = True_()
        self.obtains_unit[U.SCOUT_CAVALRY] = self.has_bledas_camp
        self.obtains_unit[U.VILLAGER_MALE] = self.has_bledas_camp | self.alternate_vils
        self.obtains_unit[U.VILLAGER_FEMALE] = self.has_bledas_camp | self.alternate_vils
        self.obtains_unit[H.ATTILA_THE_HUN] = True_()
        self.obtains_unit[E.HORSE] = True_()

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            Age2PlayerData.ATT1_EASTERN_ROMAN_EMPIRE: (
                scenario_logic.ages.can_reach(Age2AgeData.FEUDAL) &
                scenario_logic.has_base() &
                military.has_military()
            ),
            Age2PlayerData.ATT1_PERSIANS: (
                scenario_logic.ages.can_reach(Age2AgeData.CASTLE) &
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.WAR_ELEPHANT_LINE, Age2AgeData.CASTLE)
            ),
            Age2PlayerData.ATT1_SCYTHIANS: (
                scenario_logic.ages.can_reach(Age2AgeData.CASTLE) &
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MANGUDAI_LINE, Age2AgeData.CASTLE)
            ),
        }
