from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.options import OptionFilter
from rule_builder.rules import False_, Has, Or, Rule, True_

from ...Options import MonksCanCounter, SiegeCanCounter
from ...items.Items import Resource

from ...locations.Ages import Age2AgeData
from ...locations.EscortUnits import Age2EscortUnitData
from ...locations.Heroes import Age2HeroData
from ...locations.UnitLines import Age2UnitLineData
from ...locations.Units import Age2UnitData
from ...locations.VillagerJobs import Age2VillagerJobData
from ...locations.connections.UnitCounters import RAM_COUNTER_TARGETS
from ...locations.connections.UnitRoles import (
    ANTI_UNIT_SIEGE,
    FAITH_LINES,
    MONKS_ALWAYS_COUNTER,
    RAM_LINES,
    ROLE_TO_LINES,
    SIEGE_ALWAYS_COUNTERS,
    UnitRole,
)
from ...locations.connections.VillagerJobResources import scenario_has_job_resource
from ..custom_logic.ScenarioQuestions import ScenarioCanTrain

MONKS_CAN_COUNTER = OptionFilter(MonksCanCounter, MonksCanCounter.option_true)
SIEGE_CAN_COUNTER = OptionFilter(SiegeCanCounter, SiegeCanCounter.option_true)

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
        if not unit.logic_buildings or not self.scenario.civilization.trains(unit):
            return False_()   # this scenario's civilisation does not have it
        if unit in self.scenario.scenario.excluded_units:
            return False_()   # the scenario forbids it
        if self.upgraded_away(unit):
            return False_()
        return ScenarioCanTrain(scenario=self.scenario.scenario, unit=unit)

    def upgraded_away(self, unit: Age2UnitData) -> bool:
        for successor in unit.line.units:
            if successor.tier != unit.tier + 1:
                continue
            tech = successor.upgrade_tech
            if (tech is None or not self.scenario.civilization.researches(tech)
                    or tech in self.scenario.scenario.excluded_techs):
                continue  # none, not this civilisation's, or forbidden - it never fires
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
        rule = self._field(line, age, paid=True)
        if isinstance(rule, False_):
            return rule   # kept bare: the roles drop a line no tier of which is trained here
        when = f" in the {age.location_name.removeprefix('Reach ')}" if age not in (None, Age2AgeData.DARK) else ""
        return self.scenario.named(f"can field the {line.line_name}{when}", rule)

    def can_field_structurally(self, line: Age2UnitLineData,
                               age: Age2AgeData | None = None) -> Rule:
        return self._field(line, age, paid=False)

    def _field(self, line: Age2UnitLineData, age: Age2AgeData | None, paid: bool) -> Rule:
        tiers = self._fielded_tiers(line, age)
        if not tiers:
            return False_()
        if not paid:
            return Or(*[self.can_train_structurally(unit) for unit in tiers])
        trained = [
            self.can_train_structurally(unit) & self.scenario.ages.can_pay_for(unit.age)
            & self.can_pay_for_training_building(unit)
            for unit in tiers
        ]
        sustained = self.resources_to_sustain(line, age)
        return Or(*trained) & self.scenario.economy.can_sustain(sustained)

    def resources_to_sustain(
        self,
        line: Age2UnitLineData,
        age: Age2AgeData | None = None,
    ) -> set[Resource]:
        return {
            resource for unit in self._fielded_tiers(line, age)
            for resource, amount in unit.cost.items()
            if amount > 0
        }

    def _fielded_tiers(
        self,
        line: Age2UnitLineData,
        age: Age2AgeData | None,
    ) -> list[Age2UnitData]:
        if age is None:
            return self.starting_unit(line)
        return self.fieldable_tiers(line, age)

    def can_pay_for_training_building(self, unit: Age2UnitData) -> Rule:
        return Or(*[self.scenario.has_building(building)
                    for building in unit.logic_buildings
                    if self.scenario.civilization.can_build(building)])

    def can_counter(self, target: Age2UnitLineData, age: Age2AgeData) -> Rule:
        return self._counter(target, age, paid=True)

    def can_counter_structurally(self, target: Age2UnitLineData, age: Age2AgeData) -> Rule:
        return self._counter(target, age, paid=False)

    def _counter(self, target: Age2UnitLineData, age: Age2AgeData, paid: bool) -> Rule:
        field = self.can_field if paid else self.can_field_structurally
        researched = (self.scenario.techs.has_researched if paid
                      else self.scenario.techs.has_researched_structurally)
        ways: list[Rule] = []
        for line in target.countered_by:
            way = field(line, age)
            if line in target.counter_techs:
                way = way & researched(target.counter_techs[line])
            ways.append(self._with_counter_options(way, line, target))
        if target in RAM_COUNTER_TARGETS:
            ways.append(self._sponge(age, paid))
        return Or(*ways)

    def _with_counter_options(
        self,
        way: Rule,
        line: Age2UnitLineData,
        target: Age2UnitLineData,
    ) -> Rule:
        if line in FAITH_LINES and target not in MONKS_ALWAYS_COUNTER:
            return way & MONKS_CAN_COUNTER
        if line in ANTI_UNIT_SIEGE and target not in SIEGE_ALWAYS_COUNTERS:
            return way & SIEGE_CAN_COUNTER
        return way

    def can_sponge_for_military(self, age: Age2AgeData) -> Rule:
        return self._sponge(age, paid=True)

    def _sponge(self, age: Age2AgeData, paid: bool) -> Rule:
        field = self.can_field if paid else self.can_field_structurally
        rams = [field(line, age) for line in RAM_LINES]
        escorts: list[Rule] = []
        for line in ROLE_TO_LINES[UnitRole.military]:
            escort = field(line, age)
            if isinstance(escort, False_):
                continue
            escorts.append(self._with_escort_options(escort, line))
        return Or(*rams) & Or(*escorts)

    def _with_escort_options(self, escort: Rule, line: Age2UnitLineData) -> Rule:
        if line in ANTI_UNIT_SIEGE:
            return escort & SIEGE_CAN_COUNTER
        return escort

    def starting_unit(self, line: Age2UnitLineData) -> list[Age2UnitData]:
        for unit in sorted(line.units, key=lambda unit: unit.tier):
            if (self.scenario.civilization.trains(unit) and unit not in self.scenario.scenario.excluded_units
                    and not self.upgraded_away(unit)):
                return [unit]
        return []

    def fieldable_tiers(self, line: Age2UnitLineData,
                        age: Age2AgeData) -> list[Age2UnitData]:
        theirs = [unit for unit in line.units
                  if self.scenario.civilization.trains(unit) and unit not in self.scenario.scenario.excluded_units]
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
        if job.building is not None:
            return self.scenario.buildings.can_build_structurally(job.building)
        if not scenario_has_job_resource(self.scenario.scenario, job):
            return False_()   # nothing on this map for the job to work
        if job.job_name == "Repairer":
            return self.scenario.has_vils() & self.has_something_to_mend()
        return self.scenario.has_vils()

    def has_something_to_mend(self) -> Rule:
        return (self.scenario.starts_with_any_building()
                | self.scenario.buildings.can_build_anything())
