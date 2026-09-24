from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Rule
from ..locations.Ages import Age2AgeData

from ..locations.Buildings import Age2BuildingData
from ..locations.UnitLines import Age2UnitLineData

if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic
    from .ScenarioLogic import ScenarioLogic

class MilitaryLogic:

    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world

    # Troop requirements

    def has_siege(self) -> Rule:
        return self.logic.buildings.has_siege()

    def has_long_range_siege(self) -> Rule:
        return self.logic.buildings.has_siege() & self.logic.can_reach_age(Age2AgeData.IMPERIAL)

    def has_military(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.logic.buildings.has_military() & self.logic.can_reach_age(age)

    def has_navy(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.logic.buildings.has_building(Age2BuildingData.DOCK) & self.logic.can_reach_age(age)

    def has_naval_bombardment(self) -> Rule:
        return self.logic.buildings.has_building(Age2BuildingData.DOCK) & self.logic.can_reach_age(Age2AgeData.IMPERIAL)

    # Counters
    def counters(self, target: Age2UnitLineData, age: Age2AgeData,
                 scenario: 'ScenarioLogic') -> Rule:
        return self.logic.units.can_counter(target, age, scenario)

    def counters_building(self, scenario: 'ScenarioLogic') -> Rule:
        """Not a unit matchup: anything that can knock a building down."""
        return self.logic.buildings.contains_building_counter()

    def counters_militia(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.MILITIA_LINE, age, scenario)

    def counters_spear(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.SPEARMAN_LINE, age, scenario)

    def counters_scout(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, age, scenario)

    def counters_knight(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.KNIGHT_LINE, age, scenario)

    def counters_skirm(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.SKIRMISHER_LINE, age, scenario)

    def counters_archer(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.ARCHER_LINE, age, scenario)

    def counters_cav_archer(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, age, scenario)

    def counters_ram(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.BATTERING_RAM_LINE, age, scenario)

    def counters_scorpion(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.SCORPION_LINE, age, scenario)

    def counters_mangonel(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.MANGONEL_LINE, age, scenario)

    def counters_monk(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.MONK_LINE, age, scenario)

    def counters_trebuchet(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.TREBUCHET_LINE, age, scenario)

    # Unique Counters

    def counters_centurion(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.CENTURION_LINE, age, scenario)

    def counters_huskarl(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.HUSKARL_LINE, age, scenario)

    def counters_legionary(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        """The Legionary is a Roman tier of the Militia line, and both sources treat it so."""
        return self.counters(Age2UnitLineData.MILITIA_LINE, age, scenario)

    def counters_longbowman(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.LONGBOWMAN_LINE, age, scenario)

    def counters_mangudai(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.MANGUDAI_LINE, age, scenario)

    def counters_throwing_axeman(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.THROWING_AXEMAN_LINE, age, scenario)

    def counters_war_elephant(self, age: Age2AgeData, scenario: 'ScenarioLogic') -> Rule:
        return self.counters(Age2UnitLineData.WAR_ELEPHANT_LINE, age, scenario)
