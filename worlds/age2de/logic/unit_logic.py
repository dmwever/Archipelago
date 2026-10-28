from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.options import OptionFilter
from rule_builder.rules import False_, Has, HasAll, HasAny, Or, Rule, True_

from ..Options import (Caveman, ShuffleVillager, Unitsanity, UnitsanityItems,
                       upgrade_techs_shuffled)
from ..items.Items import Age2ItemData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from ..locations.UnitLocations import VILLAGER_LINES
from ..locations.connections.UnitBuildings import BUILDING_TO_UNITS_ITEM

NOT_CAVEMAN = OptionFilter(Caveman, Caveman.option_false)

if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

HORSE_LINE = Age2UnitLineData.SCOUT_CAVALRY_LINE


class UnitLogic:
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world

    # -- owning ------------------------------------------------------------------------------

    def can_own_anywhere(self, unit: Age2UnitData) -> Rule:
        granted = self.is_granted_anywhere(unit) & self.survives_caveman(unit)
        return self.can_train_anywhere(unit) | granted | self.can_convert(unit)

    def survives_caveman(self, unit: Age2UnitData) -> Rule:
        return NOT_CAVEMAN | self.can_restore(unit)

    def can_restore(self, unit: Age2UnitData) -> Rule:
        tech = unit.upgrade_tech
        if tech is None or not self.world.pool.techs.includes(tech):
            return self.has_unit_items(unit)
        return self.has_unit_items(unit) & Has(tech.item.item_name)

    def can_own_line_anywhere(self, line: Age2UnitLineData) -> Rule:
        return Or(*[self.can_own_anywhere(unit) for unit in line.units
                    if self.world.pool.units.includes(unit)])

    def can_convert(self, unit: Age2UnitData) -> Rule:
        return False_()

    def is_granted_anywhere(self, target: Age2UnitData | Age2HeroData | Age2EscortUnitData) -> Rule:
        rules: list[Rule] = []
        for scenario in self.logic.scenarios:
            answer = scenario.units.is_granted(target)
            if isinstance(answer, False_):
                continue
            rules.append(scenario.is_unlocked() & answer)
        return Or(*rules)

    # -- training ----------------------------------------------------------------------------

    def can_train_anywhere(self, unit: Age2UnitData) -> Rule:
        if not self.world.pool.units.is_trainable_unit(unit) or not unit.logic_buildings:
            return False_()
        rules: list[Rule] = []
        for scenario in self.logic.scenarios:
            answer = scenario.units.can_train(unit)
            if isinstance(answer, False_):
                continue
            rules.append(scenario.is_unlocked() & answer)
        return Or(*rules)

    def can_get_villager_anywhere(self) -> Rule:
        villager, food = Age2UnitData.VILLAGER_MALE, Age2ItemData.STARTING_VILLAGER_FOOD.type
        rules: list[Rule] = []
        for scenario in self.logic.scenarios:
            answer = scenario.units.can_train_structurally(villager)
            if isinstance(answer, False_):
                continue
            rules.append(scenario.is_unlocked() & answer
                         & scenario.economy.can_pay({food.type: food.amount}))
        return Or(*rules)


    def has_profession_item(self, job: Age2VillagerJobData) -> Rule:
        if self.world.options.shuffle_villager != ShuffleVillager.option_include_professions:
            return True_()
        return Has(job.item.item_name)

    def can_do_job_anywhere(self, job: Age2VillagerJobData) -> Rule:
        rules: list[Rule] = []
        for scenario in self.logic.scenarios:
            answer = scenario.units.can_do_job(job)
            if isinstance(answer, False_):
                continue
            if job.building is not None:
                answer = answer & scenario.economy.can_pay_some(job.building.cost)
            rules.append(scenario.is_unlocked() & answer)
        return Or(*rules) & self.has_profession_item(job)

    # -- items -------------------------------------------------------------------------------

    def has_unit_items(self, unit: Age2UnitData) -> Rule:
        if unit.line in VILLAGER_LINES:
            return self.has_villager_item()
        if self.world.options.unitsanity == Unitsanity.option_none:
            return True_()
        mode = self.world.options.unitsanity_items
        if mode == UnitsanityItems.option_unit_line:
            return self.has_line_item(unit.line)
        if mode == UnitsanityItems.option_upgrades:
            return self.has_upgrade_tokens(unit)
        return self.has_building_item(unit)

    def has_villager_item(self) -> Rule:
        if not self.world.unit_regions.shuffled_villager:
            return True_()
        return Has(Age2ItemData.UNIT_LINE_VILLAGER.item_name)

    def has_line_item(self, line: Age2UnitLineData) -> Rule:
        if line not in self.world.unit_regions.shuffled_lines:
            return True_()
        return Has(line.item.item_name)

    def has_upgrade_tokens(self, unit: Age2UnitData) -> Rule:
        gated_by = unit
        if unit.tier > 0 and not upgrade_techs_shuffled(self.world.options.techsanity):
            gated_by = unit.line.head
        tokens = [token for token in gated_by.upgrade_tokens if self.token_applies(unit, token)]
        if not tokens:
            return True_()
        return HasAll(*[token.item_name for token in tokens])

    def token_applies(self, unit: Age2UnitData, token) -> bool:
        if unit is not Age2UnitData.TRADE_CART or token is not Age2ItemData.UPGRADE_HORSE:
            return True
        return self.has_horses()

    def has_horses(self) -> bool:
        return any(self.world.pool.civs.any_trains(unit) for unit in HORSE_LINE.units)

    def has_building_item(self, unit: Age2UnitData) -> Rule:
        wanted = [BUILDING_TO_UNITS_ITEM[building].item_name for building in unit.logic_buildings
                  if building in self.world.unit_regions.shuffled_unit_building_items]
        if not wanted:
            return True_()
        return HasAny(*wanted)
