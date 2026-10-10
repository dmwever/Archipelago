from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Or, Rule, True_

from ...locations.Ages import Age2AgeData
from ...locations.EscortUnits import Age2EscortUnitData
from ...locations.Heroes import Age2HeroData
from ...locations.UnitLines import Age2UnitLineData
from ...locations.Units import Age2UnitData
from ...locations.VillagerJobs import Age2VillagerJobData
from ...locations.connections.UnitBuildings import logic_buildings
from ..custom_logic.ScenarioQuestions import ScenarioCanTrain

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


VILLAGER_LINES = (Age2UnitLineData.VILLAGER_MALE_LINE, Age2UnitLineData.VILLAGER_FEMALE_LINE)

class ScenarioUnitLogic:
    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world

    # -- training ----------------------------------------------------------------------------

    def can_train_structurally(self, unit: Age2UnitData) -> Rule:
        """Everything training it asks for except paying for it."""
        if not logic_buildings(unit) or not self.scenario.civilization.trains(unit):
            return False_()   # this scenario's civilisation does not have it
        if self.upgraded_away(unit):
            return False_()
        return ScenarioCanTrain(scenario=self.scenario.scenario, unit=unit)

    def upgraded_away(self, unit: Age2UnitData) -> bool:
        for successor in unit.line.units:
            if successor.tier != unit.tier + 1:
                continue
            tech = successor.upgrade_tech
            if tech is None or not self.scenario.civilization.researches(tech):
                continue  # none, or not this civilisation's, so it never fires
            if self.scenario.techs.researched_at_start(tech):
                return True   # strictly below the opening age, and not withheld
        return False

    def has_upgrade_tech(self, unit: Age2UnitData) -> Rule:
        tech = unit.upgrade_tech
        if tech is None or not self.world.pool.techs.includes(tech):
            return True_()
        item = Has(tech.item.item_name)
        if self.scenario.techs.researched_at_start(tech):
            return True_()   # the scenario researched it for itself, so the tier is upgraded
        if tech.age < self.scenario.scenario.vanilla_age:
            return item
        return self.scenario.techs.has_tech(tech) & item

    # -- fielding ----------------------------------------------------------------------------

    def can_field(self, line: Age2UnitLineData, age: Age2AgeData | None = None) -> Rule:
        tiers = self.fieldable_tiers(line, age) if age is not None else self.starting_unit(line)
        if not tiers:
            return False_()
        sustained = {resource for unit in tiers
                     for resource, amount in unit.cost.items() if amount > 0}
        return (Or(*[self.can_train_structurally(unit) for unit in tiers])
                & self.scenario.has_base()
                & self.scenario.economy.can_sustain(sustained))

    def can_counter(self, target: Age2UnitLineData, age: Age2AgeData) -> Rule:
        return Or(*[self.can_field(line, age) for line in target.countered_by])

    def starting_unit(self, line: Age2UnitLineData) -> list[Age2UnitData]:
        for unit in sorted(line.units, key=lambda unit: unit.tier):
            if self.scenario.civilization.trains(unit) and not self.upgraded_away(unit):
                return [unit]
        return []

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
        if self.world.pool.units.startup_grants(data, target):
            ways.append(True_())   # it is standing there when the scenario opens
        if self.world.pool.units.trigger_grants(data, target):
            ways.append(self.scenario.obtains_unit(target))
        return Or(*ways)

    # -- villagers ---------------------------------------------------------------------------

    def can_do_job(self, job: Age2VillagerJobData) -> Rule:
        return self.scenario.job_available(job) & self.job_requirement(job)

    def job_requirement(self, job: Age2VillagerJobData) -> Rule:
        if job.job_name == "Builder":
            return self.scenario.buildings.can_build_anything()
        if job.building is None:
            return True_()
        return self.scenario.buildings.can_build_building(job.building)
