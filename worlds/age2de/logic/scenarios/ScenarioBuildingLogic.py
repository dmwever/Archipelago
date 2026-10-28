from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Or, Rule

from ...items.Items import Age2ItemData, Resource

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ..custom_logic.ScenarioQuestions import ScenarioCanBuild

if TYPE_CHECKING:
    from ..building_logic import BuildingLogic
    from ..ScenarioLogic import ScenarioLogic


B = Age2BuildingData
GOLD_DROPSITES = [B.MINING_CAMP, B.TOWN_CENTER, B.MULE_CART]
STONE_DROPSITES = [B.MINING_CAMP, B.TOWN_CENTER, B.MULE_CART]
WOOD_DROPSITES = [B.LUMBER_CAMP, B.TOWN_CENTER, B.MULE_CART]
FOOD_DROPSITES = [B.MILL, B.TOWN_CENTER, B.FOLWARK]
HUNT_DROPSITES = FOOD_DROPSITES + [B.MULE_CART]
"""A mule cart takes meat, but no other food - not fish, not herdables."""
FISHERMAN_DROPSITES = FOOD_DROPSITES + [B.DOCK]
FISHING_BOAT_DROPSITES = [B.DOCK, B.HARBOR]
"""Where each kind of gatherer can drop off."""

STRONGPOINTS = [B.CASTLE, B.FORTIFIED_CHURCH, B.KREPOST, B.DONJON]
WALLS = [B.STONE_WALL, B.PALISADE_WALL]
TOWERS = [B.WATCH_TOWER, B.BOMBARD_TOWER]

class ScenarioBuildingLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self.buildings: BuildingLogic = scenario.logic.buildings

    def can_build_structurally(self, building: Age2BuildingData) -> Rule:
        if not self.scenario.civilization.can_build(building):
            return False_()   # not this civilisation's to put up, and that is free to answer
        if building in self.scenario.scenario.excluded_buildings:
            return False_()   # the scenario forbids it, whatever the civilisation allows
        return ScenarioCanBuild(scenario=self.scenario.scenario, building=building)

    def can_build(self, building: Age2BuildingData) -> Rule:
        return self.can_build_structurally(building) & self.can_pay_for(building)

    def can_pay_for(self, building: Age2BuildingData) -> Rule:
        if building is Age2BuildingData.TOWN_CENTER:
            return (Has(Age2ItemData.TOWN_CENTER_WOOD.item_name)
                    & Has(Age2ItemData.TOWN_CENTER_STONE.item_name))
        rule = (self.scenario.economy.can_pay(building.cost)
                & self.scenario.ages.can_advance(building.age))
        prerequisite = self.buildings.prerequisite(building)
        if prerequisite is not None:
            rule = rule & self.scenario.has_building(prerequisite)
        return rule

    def can_build_anything(self) -> Rule:
        return Or(*[self.can_build_structurally(building) & self.scenario.economy.can_pay_some(building.cost)
                    & self.scenario.ages.can_advance(building.age)
                    for building in Age2BuildingData
                    if self.scenario.civilization.can_build(building)])

    def can_build_tc(self) -> Rule:
        return self.buildings.can_build_tc() & self.scenario.has_builders()

    def can_build_base(self) -> Rule:
        if not self.scenario.civilization.can_build(Age2BuildingData.HOUSE):
            return self.can_build_tc()
        return self.can_build_tc() & self.can_build_structurally(Age2BuildingData.HOUSE)

    def can_build_tc_as_defence(self) -> Rule:
        return self.scenario.named(
            "can build a second Town Center as a defence",
            self._tc_as_defence(),
        )

    def _tc_as_defence(self) -> Rule:
        return (self._can_defend_with(B.TOWN_CENTER)
                & self.scenario.ages.has_reached(Age2AgeData.CASTLE)
                & self.scenario.ages.can_advance_in_economy(Age2AgeData.CASTLE))

    def can_build_tc_as_camp(self) -> Rule:
        return self.scenario.named(
            "can build a second Town Center as a camp",
            self._tc_as_camp(),
        )

    def _tc_as_camp(self) -> Rule:
        return (self.can_build_structurally(B.TOWN_CENTER)
                & self.scenario.ages.has_reached(Age2AgeData.CASTLE))

    def can_build_castle_of_some_stone(self) -> Rule:
        return self.scenario.named(
            "can build a Castle out of some stone",
            self._castle_of_some_stone(),
        )

    def _castle_of_some_stone(self) -> Rule:
        buildable = self.can_build_structurally(B.CASTLE)
        if isinstance(buildable, False_):
            return False_()
        return (buildable
                & self.scenario.economy.can_pay_some([Resource.STONE])
                & self.scenario.ages.can_advance_in_economy(Age2AgeData.CASTLE))

    def is_fortified(self) -> Rule:
        return self.scenario.named("has a built defence", self._fortified())

    def _fortified(self) -> Rule:
        strongpoint = self.can_build_tc_as_defence() | self._can_defend_with_any_of(STRONGPOINTS)
        return strongpoint | (self._can_defend_with_any_of(WALLS) & self._can_defend_with_any_of(TOWERS))

    def _can_defend_with_any_of(self, buildings: list[Age2BuildingData]) -> Rule:
        return Or(*[self._can_defend_with(building) for building in buildings])

    def _can_defend_with(self, building: Age2BuildingData) -> Rule:
        buildable = self.can_build_structurally(building)
        if isinstance(buildable, False_):
            return False_()
        advance = self.scenario.ages.can_advance_in_economy(building.age)
        if building is B.CASTLE:
            return (buildable
                    & self.scenario.economy.has_ungated_easy_source(Resource.STONE)
                    & advance)
        return buildable & self.scenario.economy.can_pay_some(building.cost) & advance

    def can_hold_a_shoreline(self) -> Rule:
        return ((self._has_mill_paid_for_some() & self.is_fortified())
                | self.can_build_tc_as_defence()
                | self._can_defend_with(Age2BuildingData.DOCK))

    def _has_mill_paid_for_some(self) -> Rule:
        return (self.scenario.starting_state.starts_with_building[B.MILL]
                | (self.can_build_structurally(B.MILL)
                   & self.scenario.economy.can_pay_some(B.MILL.cost)))

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

    def has_wood_camp(self) -> Rule:
        return self._camp_among(WOOD_DROPSITES)

    def has_gold_camp(self) -> Rule:
        return self._camp_among(GOLD_DROPSITES)

    def has_stone_camp(self) -> Rule:
        return self._camp_among(STONE_DROPSITES)

    def has_hunt_camp(self) -> Rule:
        return self._camp_among(HUNT_DROPSITES)

    def has_food_camp(self) -> Rule:
        return self._camp_among(FOOD_DROPSITES)

    def has_fisherman_camp(self) -> Rule:
        return self._camp_among(FISHERMAN_DROPSITES)

    def _camp_among(self, dropsites: list[Age2BuildingData]) -> Rule:
        return Or(*[
            self._camp(building) for building in dropsites
                if building is not B.TOWN_CENTER
        ])

    def _camp(self, building: Age2BuildingData) -> Rule:
        if not self.scenario.is_seeded(building):
            return self.scenario.has_building_structurally(building)
        return self.scenario.has_seeded_building(building)

    def has_standing_or_seeded(self, building: Age2BuildingData) -> Rule:
        if not self.scenario.is_seeded(building):
            return self.scenario.starting_state.starts_with_building[building]
        return self.scenario.has_seeded_building(building)

    def can_build_unseeded(self, building: Age2BuildingData) -> Rule:
        if self.scenario.is_seeded(building):
            return False_()
        return self.can_build_structurally(building)

    def _any_of(self, buildings: list[Age2BuildingData]) -> Rule:
        return Or(*[self.scenario.has_building_structurally(building) for building in buildings])

    def has_fishing_boat_dropsite(self) -> Rule:
        return self._any_of(FISHING_BOAT_DROPSITES)

    def has_fisherman_dropsite(self) -> Rule:
        return self._any_of(FISHERMAN_DROPSITES)
