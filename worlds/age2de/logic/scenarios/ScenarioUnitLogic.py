from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Or, Rule, True_

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.EscortUnits import Age2EscortUnitData
from ...locations.Heroes import Age2HeroData
from ...locations.UnitLines import Age2UnitLineData
from ...locations.Units import Age2UnitData
from ...locations.VillagerJobs import Age2VillagerJobData

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


JOB_BUILDING = {
    "Farmer": Age2BuildingData.FARM,
    "Herder": Age2BuildingData.PASTURE,
}


class ScenarioUnitLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self.pool = scenario.logic.world.unit_pool

    # -- training ----------------------------------------------------------------------------

    def can_train(self, unit: Age2UnitData) -> Rule:
        if not unit.buildings or not self.scenario.civilization.trains(unit):
            return False_()   # this scenario's civilisation does not have it
        if self.upgraded_away(unit):
            return False_()
        somewhere = Or(*[self.scenario.has_building(building)
                         for building in unit.buildings
                         if self.scenario.civilization.can_build(building)])
        return (self.logic.units.has_unit_items(unit) & self.has_upgrade_tech(unit)
                & somewhere & self.scenario.can_play_age(unit.age))

    def upgraded_away(self, unit: Age2UnitData) -> bool:
        for successor in unit.line.units:
            if successor.tier != unit.tier + 1:
                continue
            tech = successor.upgrade_tech
            if tech is None or self.world.tech_pool.locked_at_start(tech):
                continue  # withheld, so researching it is your choice and your timing
            if not self.scenario.civilization.researches(tech):
                continue  # not this civilisation's, so it never fires
            if self.scenario.scenario.vanilla_age >= tech.age:
                return True
        return False

    def has_upgrade_tech(self, unit: Age2UnitData) -> Rule:
        tech = unit.upgrade_tech
        if tech is None or not self.world.tech_pool.includes(tech):
            return True_()
        return self.scenario.techs.has_tech(tech)

    # -- fielding ----------------------------------------------------------------------------

    def can_field(self, line: Age2UnitLineData, age: Age2AgeData) -> Rule:
        tiers = self.fieldable_tiers(line, age)
        if not tiers:
            return False_()
        return Or(*[self.can_train(unit) for unit in tiers])

    def can_counter(self, target: Age2UnitLineData, age: Age2AgeData) -> Rule:
        return Or(*[self.can_field(line, age) for line in target.countered_by])

    def fieldable_tiers(self, line: Age2UnitLineData,
                        age: Age2AgeData) -> list[Age2UnitData]:
        theirs = [unit for unit in line.units
                  if self.scenario.civilization.trains(unit)]
        good_enough = [unit for unit in theirs if unit.age >= age]
        if good_enough:
            return good_enough
        return [max(theirs, key=lambda unit: unit.tier)] if theirs else []

    # -- being handed one --------------------------------------------------------------------

    def is_granted(self, target: Age2UnitData | Age2HeroData | Age2EscortUnitData) -> Rule:
        ways: list[Rule] = []
        data = self.scenario.scenario
        if self.pool.startup_grants(data, target):
            ways.append(True_())   # it is standing there when the scenario opens
        if self.pool.trigger_grants(data, target):
            ways.append(self.scenario.obtains_unit(target))
        return Or(*ways)

    # -- villagers ---------------------------------------------------------------------------

    def can_do_job(self, job: Age2VillagerJobData) -> Rule:
        return self.scenario.job_available(job) & self.job_requirement(job)

    def job_requirement(self, job: Age2VillagerJobData) -> Rule:
        if job.job_name == "Builder":
            return self.scenario.buildings.can_build_anything()
        building = JOB_BUILDING.get(job.job_name)
        if building is None:
            return True_()
        return self.scenario.buildings.can_build_building(building)
