from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAll, HasAny, Or, Rule, True_

from ..Options import Unitsanity, UnitsanityItems
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from ..locations.connections.UnitBuildings import BUILDING_TO_UNITS_ITEM

if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic

HORSE_LINE = Age2UnitLineData.SCOUT_CAVALRY_LINE


class UnitLogic:
    """Whether a unit can be had **somewhere**, which is what its global location asks.

    Every question that depends on where you are standing belongs to ScenarioUnitLogic, and the
    answers here are an Or over the scenarios that can be reached. What is left is the item half:
    an item is global by nature, so holding the Archer Line holds it everywhere.
    """

    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
        self.pool = world.unit_pool

    # -- owning ------------------------------------------------------------------------------

    def can_own_anywhere(self, unit: Age2UnitData) -> Rule:
        return (self.can_train_anywhere(unit) | self.is_granted_anywhere(unit)
                | self.can_convert(unit))

    def can_own_line_anywhere(self, line: Age2UnitLineData) -> Rule:
        """Owning any tier is owning the line."""
        return Or(*[self.can_own_anywhere(unit) for unit in line.units
                    if self.pool.includes(unit)])

    def can_convert(self, unit: Age2UnitData) -> Rule:
        return False_()

    def is_granted_anywhere(self, target: Age2UnitData | Age2HeroData | Age2EscortUnitData) -> Rule:
        ways: list[Rule] = []
        for scenario in self.logic.scenarios:
            answer = scenario.units.is_granted(target)
            if isinstance(answer, False_):
                continue
            ways.append(scenario.is_unlocked() & answer)
        return Or(*ways)

    # -- training ----------------------------------------------------------------------------

    def can_train_anywhere(self, unit: Age2UnitData) -> Rule:
        if not self.pool.is_trainable_unit(unit) or not unit.buildings:
            return False_()
        ways: list[Rule] = []
        for scenario in self.logic.scenarios:
            answer = scenario.units.can_train(unit)
            if isinstance(answer, False_):
                continue
            ways.append(scenario.is_unlocked() & answer)
        return Or(*ways)

    # -- villagers ---------------------------------------------------------------------------

    def can_do_job_anywhere(self, job: Age2VillagerJobData) -> Rule:
        ways: list[Rule] = []
        for scenario in self.logic.scenarios:
            answer = scenario.units.can_do_job(job)
            if isinstance(answer, False_):
                continue
            ways.append(scenario.is_unlocked() & answer)
        return Or(*ways)

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
        """A meso-american civilisation trains a trade cart and has nothing to pull it."""
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
