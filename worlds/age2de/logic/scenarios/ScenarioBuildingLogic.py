from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Or, Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...rules.custom_rules.ScenarioQuestions import ScenarioCanBuild

if TYPE_CHECKING:
    from ..building_logic import BuildingLogic
    from ..ScenarioLogic import ScenarioLogic


WATER_BUILDINGS: frozenset[Age2BuildingData] = frozenset({
    Age2BuildingData.DOCK,
    Age2BuildingData.HARBOR,
    Age2BuildingData.FISH_TRAP,
})
"""Buildings that need a shoreline. The fish trap is in here rather than leaning on its dock
prerequisite, which is answered by the global has_building and never sees the scenario."""


class ScenarioBuildingLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self.buildings: BuildingLogic = scenario.logic.buildings

    def can_build_building(self, building: Age2BuildingData) -> Rule:
        if not self.scenario.civilization.can_build(building):
            return False_()   # not this civilisation's to put up, and that is free to answer
        return ScenarioCanBuild(scenario=self.scenario.scenario, building=building)

    def build_rule(self, building: Age2BuildingData) -> Rule:
        """What ScenarioCanBuild resolves to. Call it through that, not directly."""
        rule = (self.buildings.has_building(building)
                & self.buildings.has_prerequisites(building)
                & self.scenario.has_vils()
                & self.scenario.ages.has_reached(building.age))
        if building in WATER_BUILDINGS:
            rule = rule & self.scenario.has_water_access()
        return rule

    def can_build_anything(self) -> Rule:
        return Or(*[self.can_build_building(building) for building in Age2BuildingData
                    if self.scenario.civilization.can_build(building)])

    def can_build_tc(self) -> Rule:
        return self.buildings.can_build_tc() & self.scenario.has_vils()

    def can_build_base(self) -> Rule:
        if not self.scenario.civilization.can_build(Age2BuildingData.HOUSE):
            return self.can_build_tc()
        return self.can_build_tc() & self.can_build_building(Age2BuildingData.HOUSE)

    def can_build_multiple_tc(self) -> Rule:
        return self.can_build_tc() & self.scenario.ages.has_reached(Age2AgeData.CASTLE)

    def has_gold_dropsite(self) -> Rule:
        return Or(*[self.scenario.has_building(building) for building in
                    (Age2BuildingData.MINING_CAMP, Age2BuildingData.TOWN_CENTER,
                     Age2BuildingData.MULE_CART)])

    def has_stone_dropsite(self) -> Rule:
        return Or(*[self.scenario.has_building(building) for building in
                    (Age2BuildingData.MINING_CAMP, Age2BuildingData.TOWN_CENTER,
                     Age2BuildingData.MULE_CART)])

    def has_wood_dropsite(self) -> Rule:
        return Or(*[self.scenario.has_building(building) for building in
                    (Age2BuildingData.LUMBER_CAMP, Age2BuildingData.TOWN_CENTER,
                     Age2BuildingData.MULE_CART)])

    def has_food_dropsite(self) -> Rule:
        return Or(*[self.scenario.has_building(building) for building in
                    (Age2BuildingData.MILL, Age2BuildingData.TOWN_CENTER,
                     Age2BuildingData.FOLWARK)])

    def has_hunt_dropsite(self) -> Rule:
        """A mule cart takes meat, but no other food - not fish, not herdables."""
        return self.has_food_dropsite() | self.scenario.has_building(Age2BuildingData.MULE_CART)

    def has_fishing_boat_dropsite(self) -> Rule:
        return (self.scenario.has_building(Age2BuildingData.DOCK)
                | self.scenario.has_building(Age2BuildingData.HARBOR))

    def has_fisherman_dropsite(self) -> Rule:
        return self.has_food_dropsite() | self.scenario.has_building(Age2BuildingData.DOCK)
