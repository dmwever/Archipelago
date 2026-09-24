from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAll, HasAny, Or, Rule, True_

from ..Options import Unitsanity, UnitsanityItems
from ..locations.Buildings import Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from ..locations.connections.UnitBuildings import BUILDING_TO_UNITS_ITEM

if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic
    from .ScenarioLogic import ScenarioLogic

HORSE_LINE = Age2UnitLineData.SCOUT_CAVALRY_LINE
"""What a civilisation has to be able to train for a horse to be a thing it owns."""

JOB_BUILDING = {
    "Farmer": Age2BuildingData.FARM,
    "Herder": Age2BuildingData.PASTURE
}
"""A job that cannot happen without a particular building. The rest need a resource on the map,
not something you can be given, so they are governed by the scenario instead - see
ScenarioStartingState.job_available. The builder is a case of its own: any building will do."""


class UnitLogic:

    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world
        self.pool = world.unit_pool

    # -- owning ------------------------------------------------------------------------------

    def can_own(self, unit: Age2UnitData) -> Rule:
        """Every way of coming by this exact tier.

        Exact, because a granted unit never climbs its line: an upgrade transforms what you own
        at the moment you research it, and anything handed over afterwards stays as it arrived.
        So being given a Heavy Cavalry Archer is no way at all to own a Cavalry Archer.
        """
        return self.can_train(unit) | self.is_granted(unit) | self.can_convert(unit)

    def can_own_line(self, line: Age2UnitLineData) -> Rule:
        """Owning any tier is owning the line."""
        return Or(*[self.can_own(unit) for unit in line.units if self.pool.includes(unit)])

    def can_convert(self, unit: Age2UnitData) -> Rule:
        """A placeholder, matching the conversion entrances. Monk logic and a per-scenario
        roster of what the enemy fields would both have to exist first."""
        return False_()

    def is_granted(self, target: Age2UnitData | Age2HeroData | Age2EscortUnitData) -> Rule:
        """Handed over by a scenario, at its start or by one of its triggers."""
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
        """Turning one out yourself, in some scenario that can still produce this tier.

        Scenario by scenario rather than once globally, because whether a tier can be trained at
        all depends on where that scenario starts - see upgraded_away.
        """
        if not self.pool.includes(unit) or not unit.buildings:
            return False_()
        somewhere = Or(*[scenario.is_unlocked() & self.can_train_in(scenario, unit)
                         for scenario in self.logic.scenarios])
        return self.has_unit_items(unit) & self.has_upgrade_tech(unit) & somewhere

    def can_train_in(self, scenario: 'ScenarioLogic', unit: Age2UnitData) -> Rule:
        if self.upgraded_away(scenario, unit):
            return False_()
        return Or(*[scenario.start_with_building(building) for building in unit.buildings
                    if self.world.civ_can_build(building)])

    def upgraded_away(self, scenario: 'ScenarioLogic', unit: Age2UnitData) -> bool:
        """Whether this scenario has already upgraded past this tier before you touch anything.

        A scenario auto-researches everything below the age it starts in, and an upgrade changes
        what the building turns out. So under vanilla technologies a Castle-Age scenario trains
        Crossbowmen and can never produce an Archer - the tier is not merely hard to get there,
        it does not exist.

        Static rather than a rule: which technologies a scenario starts with is settled by
        Existing Techs and the scenario's own age, neither of which an item can change.
        """
        for successor in unit.line.units:
            if successor.tier != unit.tier + 1:
                continue
            tech = successor.upgrade_tech
            if tech is None or self.world.tech_pool.locked_at_start(tech):
                continue  # withheld, so researching it is your choice and your timing
            if scenario.scenario.vanilla_age >= tech.age:
                return True
        return False

    def has_upgrade_tech(self, unit: Age2UnitData) -> Rule:
        """A tier above the base needs its own upgrade researched."""
        tech = unit.upgrade_tech
        if tech is None or not self.world.tech_pool.includes(tech):
            return True_()
        return self.logic.techs.can_research(tech)

    # -- items -------------------------------------------------------------------------------

    def has_unit_items(self, unit: Age2UnitData) -> Rule:
        """What Unitsanity Items asks for before this unit can be trained."""
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
        """A trade cart wants a horse to pull it, except where there are no horses. A
        meso-american civilisation trains no cavalry at all and still runs trade carts."""
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

    # -- villagers ---------------------------------------------------------------------------

    def can_do_job(self, job: Age2VillagerJobData) -> Rule:
        """A villager doing a particular piece of work.

        Most jobs need a resource on the map rather than anything you can be handed, so the
        scenario answers for them and says yes unless it is one of the few that cannot.
        """
        available = Or(*[scenario.is_unlocked() & scenario.job_available(job)
                         for scenario in self.logic.scenarios])
        return available & self.job_requirement(job)

    def job_requirement(self, job: Age2VillagerJobData) -> Rule:
        if job.job_name == "Builder":
            return self.logic.buildings.can_build_anything()
        building = JOB_BUILDING.get(job.job_name)
        if building is None:
            return True_()
        return self.logic.can_build_building(building)
