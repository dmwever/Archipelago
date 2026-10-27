"""The ways a location can be had, asking per scenario the same pieces its rule is built from."""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Callable

from rule_builder.rules import Has, Or, Rule, True_

from ..items.Items import Age2ItemData
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.Locations import Age2ScenarioLocationData
from ..locations.Techs import Age2TechData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from .Lookup import Explained

if TYPE_CHECKING:
    from .. import Age2World
    from ..logic.ScenarioLogic import ScenarioLogic


@dataclasses.dataclass(frozen=True)
class Way:
    """One way a scenario offers a route: what it asks of the scenario, less paying, and what it
    costs. None asks or costs nothing."""
    structural: Rule | None = None
    payment: Rule | None = None


@dataclasses.dataclass(frozen=True)
class Route:
    action: str
    """How the player gets it: "Trains it", "Starts with it"."""
    verb: str
    """What a scenario that offers it but can't yet is short of: "can't train"."""
    ways: Callable[[ScenarioLogic], list[Way]]
    """What a scenario offers on this route; none means it doesn't offer it."""
    requires: tuple[Rule, ...] = ()
    """What a scenario asks of the items when it is given nothing for free. Shown, never decides
    a chapter: a Barracks standing at the start, or a technology researched there, lets that
    scenario off, and its own check says so."""
    gates: tuple[Rule, ...] = ()
    """Item rules outside the per-scenario check that still decide every chapter: a villager
    job's profession."""
    at: tuple[Age2BuildingData, ...] = ()
    """The buildings it is made or researched at."""
    age: Age2AgeData | None = None
    """The age it is first had in."""
    upgrade: Age2TechData | None = None
    """The pooled tech whose item the route asks for, unless a scenario starts with it researched."""

    @property
    def label(self) -> str:
        """"Trains it at the Castle or Krepost in the Castle Age", as plain text."""
        at = f" at the {building_names(self.at)}" if self.at else ""
        age = f" in the {age_name(self.age)}" if self.age is not None else ""
        return f"{self.action}{at}{age}"


def routes_for(world: Age2World, data: Explained) -> list[Route]:
    if isinstance(data, Age2ScenarioLocationData):
        return [_objective(world, data)]
    if isinstance(data, Age2BuildingData):
        return [_building(world, data)]
    if isinstance(data, Age2TechData):
        return [_tech(world, data)]
    if isinstance(data, Age2AgeData):
        return [_age(world, data)]
    if isinstance(data, Age2VillagerJobData):
        return [_job(world, data)]
    if isinstance(data, (Age2HeroData, Age2EscortUnitData)):   # before the villager check, as
        return _granted(world, data, [data])                   # UnitRules.location_rule orders it
    if world.pool.units.is_villager_location(data):
        return [_villager(world)]
    tiers = ([unit for unit in data.units if world.pool.units.includes(unit)]
             if isinstance(data, Age2UnitLineData) else [data])
    return [*_trained(world, tiers), *_granted(world, data, tiers)]


# -- a scenario's own locations: its objectives and its victory ---------------------------------

def _objective(world: Age2World, objective: Age2ScenarioLocationData) -> Route:
    """Done in its own scenario only, by whatever its rule asks - nothing past the unlock where
    it has none."""
    rule = world.get_location(objective.global_name()).access_rule
    asks = rule if isinstance(rule, Rule.Resolved) else None
    return Route(
        "Completes it", "can't complete",
        lambda sl: [Way(asks)] if sl.scenario is objective.scenario else [],
    )


# -- buildings, techs, ages, jobs: one route each ------------------------------------------------

def _building(world: Age2World, building: Age2BuildingData) -> Route:
    logic = world.rules.logic
    prerequisite = BUILDING_PREREQUISITE.get(building)
    return Route(
        "Builds it", "can't build",
        lambda sl: [Way(sl.buildings.can_build_structurally(building),
                        sl.buildings.can_pay_for(building))],
        requires=(
            logic.buildings.has_building_item(building),
            logic.buildings.has_building_item(prerequisite) if prerequisite else True_(),
            logic.ages.has_age(building.age),
            logic.units.has_profession_item(Age2VillagerJobData.BUILDER_MALE),
        ),
        age=building.age,
    )


def _tech(world: Age2World, tech: Age2TechData) -> Route:
    # A technology's own item only applies its effect, it never gates the location.
    logic = world.rules.logic
    return Route(
        "Researches it", "can't research",
        lambda sl: [Way(sl.techs.can_research_structurally(tech), sl.techs.can_pay_for(tech))],
        requires=(any_building_item(world, tech.buildings), logic.ages.has_age(tech.age)),
        at=tuple(tech.buildings),
        age=tech.age,
    )


def _age(world: Age2World, age: Age2AgeData) -> Route:
    logic = world.rules.logic
    return Route(
        "Reaches it", "can't reach",
        lambda sl: [Way(sl.ages.can_research_structurally(age), sl.ages.can_research(age))],
        requires=(logic.ages.has_age(age),
                  logic.buildings.has_building_item(Age2BuildingData.TOWN_CENTER)),
    )


def _job(world: Age2World, job: Age2VillagerJobData) -> Route:
    logic = world.rules.logic
    profession = logic.units.has_profession_item(job)
    return Route(
        "Does the job", "can't do it",
        lambda sl: [Way(sl.units.can_do_job(job))],
        requires=(profession,
                  logic.buildings.has_building_item(job.building) if job.building else True_()),
        gates=(profession,),
    )


# -- units ----------------------------------------------------------------------------------------

def _villager(world: Age2World) -> Route:
    """Any villager location: one villager, priced at the food that staffs a base."""
    food = Age2ItemData.STARTING_VILLAGER_FOOD.type
    villager = Age2UnitData.VILLAGER_MALE
    buildings = villager.logic_buildings
    return Route(
        "Trains it", "can't train",
        lambda sl: [Way(sl.units.can_train_structurally(villager),
                        sl.economy.can_pay({food.type: food.amount}))],
        requires=(world.rules.logic.units.has_villager_item(), any_building_item(world, buildings)),
        at=tuple(buildings),
        age=villager.age,
    )


def _trained(world: Age2World, tiers: list[Age2UnitData]) -> list[Route]:
    trainable = [unit for unit in tiers
                 if world.pool.units.is_trainable_unit(unit) and unit.logic_buildings]
    if not trainable:
        return []
    first = min(trainable, key=lambda unit: unit.tier)
    buildings = list(dict.fromkeys(building for unit in trainable for building in unit.logic_buildings))
    logic = world.rules.logic
    tech = first.upgrade_tech
    return [Route(
        "Trains it", "can't train",
        lambda sl: [Way(sl.units.can_train_structurally(unit), sl.economy.can_pay(unit.cost))
                    for unit in trainable],
        requires=(
            logic.units.has_unit_items(first),
            any_building_item(world, buildings),
            Has(tech.item.item_name) if tech is not None and world.pool.techs.includes(tech) else True_(),
            logic.ages.has_age(first.age),
        ),
        at=tuple(buildings),
        age=first.age,
        upgrade=tech if tech is not None and world.pool.techs.includes(tech) else None,
    )]


def _granted(world: Age2World, target, grants: list) -> list[Route]:
    """Being handed it: standing there when the scenario opens, or given by a trigger."""
    units = world.pool.units
    # Under caveman a unit handed over has to be restored - its items, and its upgrade's.
    restore: Rule | None = None
    if world.options.caveman.value:
        restoring = [world.rules.logic.units.can_restore(unit) for unit in grants
                     if isinstance(unit, Age2UnitData)]
        restore = Or(*restoring) if restoring else None
    requires = (restore,) if restore is not None else ()

    def started(sl: ScenarioLogic) -> list[Way]:
        return [Way(restore)] if units.startup_grants(sl.scenario, target) else []

    def triggered(sl: ScenarioLogic) -> list[Way]:
        given = [sl.obtains_unit(grant) for grant in sl.scenario.trigger_units
                 if grant is target or getattr(grant, "line", None) is target]
        if not given:
            return []
        return [Way(Or(*given) & restore if restore is not None else Or(*given))]

    return [
        Route("Starts with it", "needs restoring", started, requires=requires),
        Route("Handed over during play", "not handed over yet", triggered, requires=requires),
    ]


# -- naming ---------------------------------------------------------------------------------------

def any_building_item(world: Age2World, buildings) -> Rule:
    if not buildings:
        return True_()
    return Or(*[world.rules.logic.buildings.has_building_item(building) for building in buildings])


def building_names(buildings) -> str:
    """"Barracks", "Castle or Krepost"."""
    return " or ".join(building.building_name for building in buildings)


def age_name(age: Age2AgeData) -> str:
    return age.location_name.removeprefix("Reach ")
