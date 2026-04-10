from __future__ import annotations

from typing import TYPE_CHECKING
from rule_builder.rules import Has, HasAll, Rule, True_
from ..locations.Ages import Age2AgeData
from ..items.Items import Age2ItemData

from ..locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

class MilitaryLogic:
    
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
    
    # Troop requirements
    
    def has_siege(self) -> Rule:
        return self.logic.buildings.has_siege()
    
    def has_long_range_siege(self) -> Rule:
        return self.logic.buildings.has_siege() & self.logic.ages.can_reach_imperial()
    
    def has_military(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.logic.buildings.has_military() & self.logic.ages.has_age(age)
    
    def has_navy(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.logic.buildings.has_building(Age2BuildingData.DOCK) & self.logic.ages.has_age(age)
    
    def has_naval_bombardment(self) -> Rule:
        return self.logic.buildings.has_building(Age2BuildingData.DOCK) & self.logic.ages.can_reach_imperial()
    
    # Counters
    
    def counters_building(self) -> Rule:
        return self.logic.buildings.contains_building_counter()
    
    def counters_militia(self, age: Age2AgeData = Age2AgeData.DARK) -> Rule:
        return self.logic.buildings.contains_milita_counter() & self.logic.ages.has_age(age)
    
    def counters_spear(self, age: Age2AgeData = Age2AgeData.FEUDAL) -> Rule:
        return self.logic.buildings.contains_spear_counter() & self.logic.ages.has_age(age)
    
    def counters_scout(self, age: Age2AgeData = Age2AgeData.FEUDAL) -> Rule:
        return self.logic.buildings.contains_scout_counter() & self.logic.ages.has_age(age)
    
    def counters_knight(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_knight_counter() & self.logic.ages.has_age(age)
    
    def counters_skirm(self, age: Age2AgeData = Age2AgeData.FEUDAL) -> Rule:
        return self.logic.buildings.contains_skirmisher_counter() & self.logic.ages.has_age(age)
    
    def counters_archer(self, age: Age2AgeData = Age2AgeData.FEUDAL) -> Rule:
        return self.logic.buildings.contains_archer_counter() & self.logic.ages.has_age(age)
    
    def counters_cav_archer(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_cav_archer_counter() & self.logic.ages.has_age(age)
    
    def counters_ram(self) -> Rule:
        return self.logic.buildings.contains_ram_counter()
    
    def counters_scorpion(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_scorpion_counter() & self.logic.ages.has_age(age)
    
    def counters_mangonel(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_mangonel_counter() & self.logic.ages.has_age(age)
    
    def counters_monk(self) -> Rule:
        return self.logic.buildings.contains_monk_counter()
    
    def counters_trebuchet(self) -> Rule:
        return self.logic.buildings.contains_trebuchet_counter()
    
    # Unique Counters
    
    def counters_centurion(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_centurion_counter() & self.logic.ages.has_age(age)
    
    def counters_huskarl(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_huskarl_counter() & self.logic.ages.has_age(age)
    
    def counters_legionary(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_legionary_counter() & self.logic.ages.has_age(age)
    
    def counters_longbowman(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_longbowman_counter() & self.logic.ages.has_age(age)
    
    def counters_mangudai(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_mangudai_counter() & self.logic.ages.has_age(age)
    
    def counters_throwing_axeman(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_throwing_axeman_counter() & self.logic.ages.has_age(age)
    
    def counters_war_elephant(self, age: Age2AgeData = Age2AgeData.CASTLE) -> Rule:
        return self.logic.buildings.contains_war_elephant_counter() & self.logic.ages.has_age(age)