from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Or, Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ..custom_logic.ScenarioQuestions import ScenarioCanBuild

if TYPE_CHECKING:
    from ..building_logic import BuildingLogic
    from ..ScenarioLogic import ScenarioLogic


B = Age2BuildingData
GOLD_DROPSITES = (B.MINING_CAMP, B.TOWN_CENTER, B.MULE_CART)
STONE_DROPSITES = (B.MINING_CAMP, B.TOWN_CENTER, B.MULE_CART)
WOOD_DROPSITES = (B.LUMBER_CAMP, B.TOWN_CENTER, B.MULE_CART)
FOOD_DROPSITES = (B.MILL, B.TOWN_CENTER, B.FOLWARK)
HUNT_DROPSITES = FOOD_DROPSITES + (B.MULE_CART,)
"""A mule cart takes meat, but no other food - not fish, not herdables."""
FISHERMAN_DROPSITES = FOOD_DROPSITES + (B.DOCK,)
FISHING_BOAT_DROPSITES = (B.DOCK, B.HARBOR)
"""Where each kind of gatherer can drop off, here and in the budget's seeds."""


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

    def can_build_anything(self) -> Rule:
        return Or(*[self.can_build_building(building) for building in Age2BuildingData
                    if self.scenario.civilization.can_build(building)])

    def can_build_tc(self) -> Rule:
        return self.buildings.can_build_tc() & self.scenario.has_vils()

    def has_tc(self) -> Rule:
        """A Town Centre to work from. One standing on the map counts, and costs nothing - the
        villagers are asked on the built path only, where they are the ones putting it up."""
        standing = self.scenario.starting_state.starts_with_building[Age2BuildingData.TOWN_CENTER]
        return standing | self.can_build_tc()

    def can_build_base(self) -> Rule:
        if not self.scenario.civilization.can_build(Age2BuildingData.HOUSE):
            return self.can_build_tc()
        return self.can_build_tc() & self.can_build_building(Age2BuildingData.HOUSE)

    def can_build_multiple_tc(self) -> Rule:
        return self.can_build_tc() & self.scenario.ages.has_reached(Age2AgeData.CASTLE)

    def is_fortified(self) -> Rule:
        strongpoint = Or(*[self.scenario.has_building(building) for building in
                           (Age2BuildingData.TOWN_CENTER, Age2BuildingData.CASTLE,
                            Age2BuildingData.FORTIFIED_CHURCH, Age2BuildingData.KREPOST,
                            Age2BuildingData.DONJON)
                           if self.scenario.civilization.can_build(building)])
        wall = Or(*[self.scenario.has_building(building) for building in
                    (Age2BuildingData.STONE_WALL, Age2BuildingData.PALISADE_WALL)
                    if self.scenario.civilization.can_build(building)])
        tower = Or(*[self.scenario.has_building(building) for building in
                     (Age2BuildingData.WATCH_TOWER, Age2BuildingData.BOMBARD_TOWER)
                     if self.scenario.civilization.can_build(building)])
        return strongpoint | (wall & tower)

    def can_hold_a_shoreline(self) -> Rule:
        return ((self.scenario.has_building(Age2BuildingData.MILL) & self.is_fortified())
                | self.can_build_multiple_tc()
                | self.scenario.has_building(Age2BuildingData.DOCK))

    def has_gold_dropsite(self) -> Rule:
        return self._any_of(GOLD_DROPSITES)

    def has_stone_dropsite(self) -> Rule:
        return self._any_of(STONE_DROPSITES)

    def has_wood_dropsite(self) -> Rule:
        return self._any_of(WOOD_DROPSITES)

    def has_food_dropsite(self) -> Rule:
        return self._any_of(FOOD_DROPSITES)

    def has_hunt_dropsite(self) -> Rule:
        return self._any_of(HUNT_DROPSITES)

    def _any_of(self, buildings: tuple[Age2BuildingData, ...]) -> Rule:
        return Or(*[self.scenario.has_building(building) for building in buildings])

    def has_fishing_boat_dropsite(self) -> Rule:
        return self._any_of(FISHING_BOAT_DROPSITES)

    def has_fisherman_dropsite(self) -> Rule:
        return self._any_of(FISHERMAN_DROPSITES)
