from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAll, HasAny, Or, Rule, True_

from ..Options import Unitsanity, UnitsanityItems
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from ..locations.connections.CivilizationTechs import CIV_TO_TECHS
from ..locations.connections.UnitBuildings import BUILDING_TO_UNITS_ITEM

if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic
    from .ScenarioLogic import ScenarioLogic

HORSE_LINE = Age2UnitLineData.SCOUT_CAVALRY_LINE

JOB_BUILDING = {
    "Farmer": Age2BuildingData.FARM,
    "Herder": Age2BuildingData.PASTURE
}


class UnitLogic:

    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
        self.pool = world.unit_pool

    # -- owning ------------------------------------------------------------------------------

    def can_own(self, unit: Age2UnitData) -> Rule:
        return self.can_train(unit) | self.is_granted(unit) | self.can_convert(unit)

    def can_own_line(self, line: Age2UnitLineData) -> Rule:
        """Owning any tier is owning the line."""
        return Or(*[self.can_own(unit) for unit in line.units if self.pool.includes(unit)])

    def can_convert(self, unit: Age2UnitData) -> Rule:
        return False_()

    def is_granted(self, target: Age2UnitData | Age2HeroData | Age2EscortUnitData) -> Rule:
        ways: list[Rule] = []
        for scenario in self.logic.scenarios:
            data = scenario.scenario
            if self.pool.startup_grants(data, target):
                ways.append(scenario.is_unlocked())
            if self.pool.trigger_grants(data, target):
                ways.append(scenario.is_unlocked() & scenario.obtains_unit(target))
        return Or(*ways)

    # -- training ----------------------------------------------------------------------------

    def can_train(self, unit: Age2UnitData) -> Rule:
        if not self.pool.is_trainable_unit(unit) or not unit.buildings:
            return False_()
        somewhere = Or(*[scenario.is_unlocked()
                         & self.has_upgrade_tech(scenario, unit)
                         & self.can_train_in(scenario, unit)
                         for scenario in self.logic.scenarios])
        return self.has_unit_items(unit) & somewhere

    def can_train_in(self, scenario: 'ScenarioLogic', unit: Age2UnitData) -> Rule:
        if not self.pool.civ_trains(scenario.scenario.civ, unit):
            return False_()   # this scenario's civilisation does not have it
        if self.upgraded_away(scenario, unit):
            return False_()
        return Or(*[scenario.start_with_building(building) for building in unit.buildings
                    if self.world.civ_can_build(building)])

    def upgraded_away(self, scenario: 'ScenarioLogic', unit: Age2UnitData) -> bool:
        for successor in unit.line.units:
            if successor.tier != unit.tier + 1:
                continue
            tech = successor.upgrade_tech
            if tech is None or self.world.tech_pool.locked_at_start(tech):
                continue  # withheld, so researching it is your choice and your timing
            if tech not in CIV_TO_TECHS[scenario.scenario.civ]:
                continue
            if scenario.scenario.vanilla_age >= tech.age:
                return True
        return False

    def has_upgrade_tech(self, scenario: 'ScenarioLogic', unit: Age2UnitData) -> Rule:
        tech = unit.upgrade_tech
        if tech is None or not self.world.tech_pool.includes(tech):
            return True_()
        return scenario.techs.has_tech(tech)

    # -- items -------------------------------------------------------------------------------

    def has_unit_items(self, unit: Age2UnitData) -> Rule:
        if self.world.options.unitsanity == Unitsanity.option_none:
            return True_()
        mode = self.world.options.unitsanity_items
        if mode == UnitsanityItems.option_unit_line:
            return self.has_line_item(unit.line)
        if mode == UnitsanityItems.option_upgrades:
            return self.has_upgrade_tokens(unit)
        return self.has_building_item(unit)

    def has_line_item(self, line: Age2UnitLineData) -> Rule:
        if line not in self.world.unit_regions.shuffled_lines:
            return True_()
        return Has(line.item.item_name)

    def has_upgrade_tokens(self, unit: Age2UnitData) -> Rule:
        tokens = [token for token in unit.upgrade_tokens if self.token_applies(unit, token)]
        if not tokens:
            return True_()
        return HasAll(*[token.item_name for token in tokens])

    def token_applies(self, unit: Age2UnitData, token) -> bool:
        from ..items.Items import Age2ItemData
        if unit is not Age2UnitData.TRADE_CART or token is not Age2ItemData.UPGRADE_HORSE:
            return True
        return self.has_horses()

    def has_horses(self) -> bool:
        from ..locations.connections.CivilizationUnits import CIV_TO_UNITS
        return any(unit in CIV_TO_UNITS[civ]
                   for civ in self.world.included_civs
                   for unit in HORSE_LINE.units)

    def has_building_item(self, unit: Age2UnitData) -> Rule:
        wanted = [BUILDING_TO_UNITS_ITEM[building].item_name for building in unit.buildings
                  if building in self.world.unit_regions.shuffled_unit_building_items]
        if not wanted:
            return True_()
        return HasAny(*wanted)

    # -- counters ----------------------------------------------------------------------------

    def tiers_from_age(self, line: Age2UnitLineData, age: Age2AgeData) -> list[Age2UnitData]:
        return [unit for unit in line.units if unit.age >= age]

    def can_counter(self, target: Age2UnitLineData, age: Age2AgeData,
                    scenario: 'ScenarioLogic') -> Rule:
        ways = []
        civ = scenario.scenario.civ
        for line in target.countered_by:
            for unit in self.counter_tiers(line, age, civ):
                ways.append(self.has_unit_items(unit)
                            & self.has_upgrade_tech(scenario, unit)
                            & self.can_train_in(scenario, unit))
        return Or(*ways)

    def counter_tiers(self, line: Age2UnitLineData, age: Age2AgeData,
                      civ) -> list[Age2UnitData]:
        theirs = [unit for unit in line.units if self.pool.civ_trains(civ, unit)]
        good_enough = [unit for unit in theirs if unit.age >= age]
        if good_enough:
            return good_enough
        return [max(theirs, key=lambda unit: unit.tier)] if theirs else []

    # -- villagers ---------------------------------------------------------------------------

    def can_do_job(self, job: Age2VillagerJobData) -> Rule:
        available = Or(*[scenario.is_unlocked() & scenario.job_available(job)
                         for scenario in self.logic.scenarios])
        return available & self.job_requirement(job)

    def job_requirement(self, job: Age2VillagerJobData) -> Rule:
        if job.job_name == "Builder":
            return self.logic.can_build_anything()
        building = JOB_BUILDING.get(job.job_name)
        if building is None:
            return True_()
        return self.logic.can_build_building(building)
