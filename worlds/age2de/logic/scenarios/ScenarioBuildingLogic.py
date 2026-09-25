from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Or, Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData

if TYPE_CHECKING:
    from ..building_logic import BuildingLogic
    from ..ScenarioLogic import ScenarioLogic


class ScenarioBuildingLogic:
    """What can go up in one scenario.

    BuildingLogic answers about items, which are global - holding the Barracks item holds it
    everywhere. Everything that also needs villagers or an age is a question about a particular
    scenario, and asking it globally is how a Castle became buildable in a scenario that has
    neither: `has_vils()` and `can_reach_age()` were each an Or across every scenario, so one
    could be satisfied by Attila 1 and the other by Joan 5.
    """

    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self.buildings: BuildingLogic = scenario.logic.buildings

    def can_build_building(self, building: Age2BuildingData) -> Rule:
        return (self.buildings.has_building(building)
                & self.buildings.has_prerequisites(building)
                & self.scenario.has_vils()
                & self.scenario.can_play_age(building.age))

    def can_build_anything(self) -> Rule:
        return Or(*[self.can_build_building(building) for building in Age2BuildingData
                    if self.world.civ_can_build(building)])

    def can_build_tc(self) -> Rule:
        return self.buildings.can_build_tc() & self.scenario.has_vils()

    def can_build_base(self) -> Rule:
        return self.can_build_tc() & self.can_build_building(Age2BuildingData.HOUSE)

    def has_siege(self) -> Rule:
        return (self.can_build_building(Age2BuildingData.CASTLE)
                | self.can_build_building(Age2BuildingData.SIEGE_WORKSHOP))

    def has_military(self) -> Rule:
        return (self.can_build_building(Age2BuildingData.BARRACKS)
                | self.can_build_building(Age2BuildingData.ARCHERY_RANGE)
                | self.can_build_building(Age2BuildingData.STABLE)
                | self.has_siege())

    def can_build_multiple_tc(self) -> Rule:
        return self.can_build_tc() & self.scenario.can_play_age(Age2AgeData.CASTLE)

    def can_mine(self) -> Rule:
        """Gold and stone need somewhere to drop off, unless a second town centre covers it."""
        return (self.can_build_multiple_tc()
                | self.can_build_building(Age2BuildingData.MINING_CAMP))

    def contains_building_counter(self) -> Rule:
        """Something here that can knock a building down.

        Not a unit matchup - the nineteen per-unit contains_*_counter methods this used to sit
        beside are gone, because which line beats which is data now in
        connections/UnitCounters.py and the rule asks whether the unit can be trained.
        """
        return (self.can_build_building(Age2BuildingData.BARRACKS)
                | self.can_build_building(Age2BuildingData.STABLE)
                | self.has_siege())
