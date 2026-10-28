from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Mapping

from rule_builder.rules import And, False_, Or, Rule, True_

from ...items.Items import Resource
from ...locations.Buildings import Age2BuildingData
from ...locations.connections import ScenarioResources
from ...locations.connections.ScenarioResources import Tier
from ...locations.Ages import Age2AgeData
from ...locations.Units import Age2UnitData
from ...locations.VillagerJobs import Age2VillagerJobData as Job
from ..custom_logic.EconomyRoutes import EconomyRoutesYield, Strength
from ..custom_logic.ScenarioQuestions import (
    ScenarioHasEasyResource,
    ScenarioHasEconomyRoutes,
    ScenarioHasSomeResource,
    ScenarioHasUngatedRoutes,
)
from .ScenarioBuildingLogic import (
    FISHERMAN_DROPSITES,
    FOOD_DROPSITES,
    GOLD_DROPSITES,
    HUNT_DROPSITES,
    STONE_DROPSITES,
)

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

RENEWABLE_FOOD: tuple[tuple[Age2BuildingData, Job], ...] = (
    (Age2BuildingData.FARM, Job.FARMER_MALE),
    (Age2BuildingData.PASTURE, Job.HERDER_MALE),
)

Term = tuple[Rule, int, str, str]


class ScenarioResourceLogic:

    def __init__(self, scenario: 'ScenarioLogic') -> None:
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self.counts = ScenarioResources.total(scenario.scenario)
        self.demand = scenario.scenario.demand

    # -- what each tier costs to reach ---------------------------------------------------------

    def tier_gates(self, kind: str = "land") -> dict[Tier, Rule]:
        return {
            Tier.BASE: True_(),
            Tier.OPEN: self._open_gate(kind),
            Tier.ALLY: False_(),
            Tier.ENEMY: self.scenario.starting_state.must_steal_base,
        }

    def open_resource_gates(self) -> dict[Tier, Rule]:
        return {
            Tier.BASE: True_(),
            Tier.OPEN: True_(),
            Tier.ALLY: False_(),
            Tier.ENEMY: self.scenario.starting_state.must_steal_base,
        }

    def _open_gate(self, kind: str) -> Rule:
        if kind == "afloat":
            return self.scenario.military.can_guard_boats()
        if kind == "shoreline":
            return self.scenario.named("can hold a shoreline", self._hold_shoreline())
        return self.can_defend_resources()

    def _hold_shoreline(self) -> Rule:
        return (self.scenario.buildings.can_hold_a_shoreline()
                | self.scenario.military.can_guard_boats())

    def can_defend_resources(self) -> Rule:
        return self.scenario.named("can defend resources", self._defend_open_ground())

    def _defend_open_ground(self) -> Rule:
        return (self.scenario.buildings.is_fortified()
                | self.scenario.military.can_hold_open_ground())

    def tiered(self, gathers: Rule, field: str,
               gates: Mapping[Tier, Rule]) -> tuple[Term, ...]:
        """Each map area holding some of the source: gathering it there, how much, the area, and
        which count it is - the last two for the explanation only."""
        return tuple((gathers & gates[tier], getattr(counts, field), tier.value, field)
                     for tier, counts in self.scenario.scenario.resources.items()
                     if getattr(counts, field))

    def _in_any_tier(self, terms: tuple[Term, ...]) -> Rule:
        if not terms:
            return False_()
        return Or(*[term[0] for term in terms])

    # -- can gather ---------------------------------------------------------------------------

    def has_job(self, job: Job) -> Rule:
        return self.scenario.units.can_do_job(job) & self.logic.units.has_profession_item(job)

    def can_mine_some(self, dropsite: Rule) -> Rule:
        return self.scenario.named("can mine gold", self._mine_gold(dropsite))

    def _mine_gold(self, dropsite: Rule) -> Rule:
        if not self.counts.gold_count:
            return False_()
        return dropsite & self.scenario.has_vils() & self.has_job(Job.GOLD_MINER_MALE)

    def can_quarry_some(self, dropsite: Rule) -> Rule:
        return self.scenario.named("can quarry stone", self._quarry_stone(dropsite))

    def _quarry_stone(self, dropsite: Rule) -> Rule:
        if not self.counts.stone_count:
            return False_()
        return dropsite & self.scenario.has_vils() & self.has_job(Job.STONE_MINER_MALE)

    def can_hunt(self, dropsite: Rule) -> Rule:
        return self.scenario.named("can hunt", self._hunt(dropsite))

    def _hunt(self, dropsite: Rule) -> Rule:
        if not self.counts.hunt_count:
            return False_()
        return dropsite & self.scenario.has_vils() & self.has_job(Job.HUNTER_MALE)

    def can_herd(self) -> Rule:
        return self.scenario.named("can herd sheep", self._herd())

    def _herd(self) -> Rule:
        if not self.counts.herd_count:
            return False_()
        return (self.scenario.buildings.has_food_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.SHEPHERD_MALE))

    def can_forage(self, dropsite: Rule) -> Rule:
        return self.scenario.named("can forage berries", self._forage(dropsite))

    def _forage(self, dropsite: Rule) -> Rule:
        if not self.counts.bush_count:
            return False_()
        return dropsite & self.scenario.has_vils() & self.has_job(Job.FORAGER_MALE)

    def can_fish_from_shore(self, dropsite: Rule) -> Rule:
        return self.scenario.named("can fish from the shore", self._fish_from_shore(dropsite))

    def _fish_from_shore(self, dropsite: Rule) -> Rule:
        if not self.counts.shore_fish_count:
            return False_()
        return dropsite & self.scenario.has_vils() & self.has_job(Job.FISHERMAN_MALE)

    def has_fishing_ships(self) -> Rule:
        """Fishing Ships to put to sea, less paying for one."""
        return self.logic.units.has_unit_items(Age2UnitData.FISHING_SHIP)

    def can_fish_by_boat(self) -> Rule:
        return self.scenario.named("can fish by boat", self._fish_by_boat())

    def _fish_by_boat(self) -> Rule:
        if not self.counts.deep_fish_count:
            return False_()
        return self.scenario.buildings.has_fishing_boat_dropsite() & self.has_fishing_ships()

    def can_fish_the_shore_by_boat(self) -> Rule:
        return self.scenario.named("can fish the shore by boat", self._fish_the_shore_by_boat())

    def _fish_the_shore_by_boat(self) -> Rule:
        if not self.counts.shore_fish_count:
            return False_()
        return self.scenario.buildings.has_fishing_boat_dropsite() & self.has_fishing_ships()

    def can_gather_oysters_from_shore(self, dropsite: Rule) -> Rule:
        return self.scenario.named("can gather oysters from the shore",
                                   self._oysters_from_shore(dropsite))

    def _oysters_from_shore(self, dropsite: Rule) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return dropsite & self.scenario.has_vils() & self.has_job(Job.OYSTER_GATHERER_MALE)

    def can_gather_oysters_by_boat(self) -> Rule:
        return self.scenario.named("can gather oysters by boat", self._oysters_by_boat())

    def _oysters_by_boat(self) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return self.scenario.buildings.has_fishing_boat_dropsite() & self.has_fishing_ships()

    def can_gather_oysters(self) -> Rule:
        return (self.can_gather_oysters_from_shore(self.scenario.buildings.has_fisherman_dropsite())
                | self.can_gather_oysters_by_boat())

    def can_hunt_whales(self) -> Rule:
        return self.scenario.named("can hunt whales", self._hunt_whales())

    def _hunt_whales(self) -> Rule:
        if not self.counts.whale_count:
            return False_()
        return self.scenario.buildings.has_fishing_boat_dropsite() & self.has_fishing_ships()

    def chops_some_at(self, dropsite: Rule) -> Rule:
        return dropsite & self.scenario.has_vils() & self.has_job(Job.LUMBERJACK_MALE)

    def gathers_some_at(self, dropsite: Rule, job: Job, field: str) -> Rule:
        if not getattr(self.counts, field):
            return False_()
        gathers = dropsite & self.scenario.has_vils() & self.has_job(job)
        return self._in_any_tier(self.tiered(gathers, field, self.open_resource_gates()))

    def can_collect_relics(self, monastery: Rule | None = None) -> Rule:
        return self.scenario.named("can collect relics", self._collect_relics(monastery))

    def _collect_relics(self, monastery: Rule | None = None) -> Rule:
        if not self.counts.relic_count:
            return False_()
        monk = Age2UnitData.MONK
        if monastery is None:
            monastery = self.scenario.has_building_structurally(Age2BuildingData.MONASTERY)
        return (
            monastery
            & (
                self.logic.units.has_unit_items(monk)
                | (self.scenario.obtains_unit(monk) & self.logic.units.survives_caveman(monk))
            )
            & self.scenario.ages.has_reached(Age2UnitData.MONK.age)
            & self._in_any_tier(
                self.tiered(True_(), "relic_count", self.open_resource_gates()),
            )
        )

    # -- food that grows back -----------------------------------------------------------------

    def can_farm(self) -> Rule:
        return self.scenario.named("can farm", self._farm())

    def _farm(self) -> Rule:
        return (
            self.scenario.has_base()
            & Or(*[self.scenario.has_building_structurally(building) & self.has_job(job)
                   for building, job in RENEWABLE_FOOD])
        )

    def can_work_fish_traps(self) -> Rule:
        return self.scenario.named("can work fish traps", self._work_fish_traps())

    def _work_fish_traps(self) -> Rule:
        return (
            self.has_fishing_ships()
            & self.scenario.buildings.has_fishing_boat_dropsite()
            & self.scenario.has_building_structurally(Age2BuildingData.FISH_TRAP)
        )

    # -- trade --------------------------------------------------------------------------------

    def can_trade_at_market(self) -> Rule:
        if not self.world.options.market_trade:
            return False_()
        return self.scenario.has_seeded_building(Age2BuildingData.MARKET)

    def can_earn_gold_by_partner_trade(self) -> Rule:
        """Trade carts to a trade partner's market, or trade cogs to its dock."""
        return self.can_run_trade_carts() | self.can_run_trade_cogs()

    def can_earn_wood_by_partner_trade(self) -> Rule:
        """Trade cogs to a trade partner's dock: a sea route brings wood home, a cart does not."""
        return self.can_run_trade_cogs()

    def can_run_trade_carts(self) -> Rule:
        partner_market = self.scenario.player_logic.can_reach_partner(Age2BuildingData.MARKET)
        if isinstance(partner_market, False_):
            return False_()
        return (
            partner_market
            & self.scenario.ages.has_reached(Age2AgeData.FEUDAL)
            & self.scenario.has_seeded_building(Age2BuildingData.MARKET)
            & self.logic.units.has_unit_items(Age2UnitData.TRADE_CART)
        )

    def can_run_trade_cogs(self) -> Rule:
        partner_dock = self.scenario.player_logic.can_reach_partner(Age2BuildingData.DOCK)
        if isinstance(partner_dock, False_):
            return False_()
        return (
            partner_dock
            & self.scenario.ages.has_reached(Age2AgeData.FEUDAL)
            & self.scenario.has_seeded_building(Age2BuildingData.DOCK)
            & self.logic.units.has_unit_items(Age2UnitData.TRADE_COG)
        )

    # -- what a route at scale adds up --------------------------------------------------------

    def villager_food(self, camp: Age2BuildingData, dropsite: Rule) -> tuple[Term, ...]:
        sources: list[Term] = [
            *self.tiered(self.can_herd(), "herd_count", self.open_resource_gates()),
        ]
        if camp in HUNT_DROPSITES:
            sources.extend(self.tiered(self.can_hunt(dropsite), "hunt_count", self.tier_gates()))
        if camp in FOOD_DROPSITES:
            sources.extend(self.tiered(self.can_forage(dropsite), "bush_count", self.tier_gates()))
        if camp in FISHERMAN_DROPSITES:
            sources.extend(self.tiered(
                self._fish_the_shore_from_a_camp(dropsite),
                "shore_fish_count",
                self.tier_gates("shoreline"),
            ))
        return tuple(sources)

    def boat_food(self) -> tuple[Term, ...]:
        return (
            *self._deep_fish(),
            *self.tiered(
                self.can_fish_the_shore_by_boat(),
                "shore_fish_count",
                self.tier_gates("shoreline"),
            ),
        )

    def villager_and_boat_food(self) -> tuple[Term, ...]:
        buildings = self.scenario.buildings
        return (
            *self.tiered(self.can_hunt(buildings.has_hunt_camp()), "hunt_count", self.tier_gates()),
            *self.tiered(self.can_herd(), "herd_count", self.open_resource_gates()),
            *self.tiered(
                self.can_forage(buildings.has_food_camp()),
                "bush_count",
                self.tier_gates(),
            ),
            *self.tiered(
                self._fish_the_shore_from_a_camp(buildings.has_fisherman_camp())
                | self.can_fish_the_shore_by_boat(),
                "shore_fish_count",
                self.tier_gates("shoreline"),
            ),
            *self._deep_fish(),
        )

    def villager_and_boat_food_at_a_second_town_center(self) -> tuple[Term, ...]:
        town_center = self.scenario.buildings.can_build_tc_as_camp()
        return (
            *self.tiered(self.can_hunt(town_center), "hunt_count", self.tier_gates()),
            *self.tiered(self.can_herd(), "herd_count", self.open_resource_gates()),
            *self.tiered(self.can_forage(town_center), "bush_count", self.tier_gates()),
            *self.tiered(
                self._fish_the_shore_from_a_camp(town_center)
                | self.can_fish_the_shore_by_boat(),
                "shore_fish_count",
                self.tier_gates("shoreline"),
            ),
            *self._deep_fish(),
        )

    def _fish_the_shore_from_a_camp(self, fisherman_camp: Rule) -> Rule:
        return self.can_fish_from_shore(fisherman_camp)

    def _deep_fish(self) -> tuple[Term, ...]:
        return self.tiered(
            self.can_fish_by_boat(),
            "deep_fish_count",
            self.tier_gates("afloat"),
        )

    def villager_gold(self, camp: Age2BuildingData, dropsite: Rule) -> tuple[Term, ...]:
        sources: list[Term] = []
        if camp in GOLD_DROPSITES:
            sources.extend(self._mined_gold(dropsite))
        if camp in FISHERMAN_DROPSITES:
            sources.extend(self.tiered(
                self._gather_shore_oysters_from_a_camp(dropsite),
                "oyster_count",
                self.tier_gates("shoreline"),
            ))
        return tuple(sources)

    def boat_gold(self) -> tuple[Term, ...]:
        return (
            *self.tiered(
                self.can_gather_oysters_by_boat(),
                "oyster_count",
                self.tier_gates("shoreline"),
            ),
            *self._whales(),
        )

    def villager_and_boat_gold(self) -> tuple[Term, ...]:
        buildings = self.scenario.buildings
        return (
            *self._mined_gold(buildings.has_gold_camp()),
            *self.tiered(
                self._gather_shore_oysters_from_a_camp(buildings.has_fisherman_camp())
                | self.can_gather_oysters_by_boat(),
                "oyster_count",
                self.tier_gates("shoreline"),
            ),
            *self._whales(),
        )

    def villager_and_boat_gold_at_a_second_town_center(self) -> tuple[Term, ...]:
        town_center = self.scenario.buildings.can_build_tc_as_camp()
        return (
            *self._mined_gold(town_center),
            *self.tiered(
                self._gather_shore_oysters_from_a_camp(town_center)
                | self.can_gather_oysters_by_boat(),
                "oyster_count",
                self.tier_gates("shoreline"),
            ),
            *self._whales(),
        )

    def _mined_gold(self, gold_camp: Rule) -> tuple[Term, ...]:
        return self.tiered(
            self.can_mine_some(gold_camp),
            "gold_count",
            self.tier_gates(),
        )

    def _gather_shore_oysters_from_a_camp(self, fisherman_camp: Rule) -> Rule:
        return self.can_gather_oysters_from_shore(fisherman_camp)

    def _whales(self) -> tuple[Term, ...]:
        return self.tiered(
            self.can_hunt_whales(),
            "whale_count",
            self.tier_gates("afloat"),
        )

    def villager_stone(self, camp: Age2BuildingData, dropsite: Rule) -> tuple[Term, ...]:
        if camp not in STONE_DROPSITES:
            return ()
        return self.tiered(
            self.can_quarry_some(dropsite),
            "stone_count",
            self._stone_gates(),
        )

    def _stone_gates(self) -> dict[Tier, Rule]:
        gates = self.tier_gates()
        return {
            **gates,
            Tier.OPEN: gates[Tier.OPEN] | self.scenario.buildings.can_build_castle_of_some_stone(),
        }

    # -- aggregates ---------------------------------------------------------------------------
    def has_economy_routes(self) -> Rule:
        return ScenarioHasEconomyRoutes(scenario=self.scenario.scenario)

    def has_ungated_routes(self) -> Rule:
        return ScenarioHasUngatedRoutes(scenario=self.scenario.scenario)

    def has_easy_source(self, resource: Resource) -> Rule:
        return ScenarioHasEasyResource(scenario=self.scenario.scenario, resource=resource)

    def has_some_source(self, resource: Resource) -> Rule:
        return ScenarioHasSomeResource(scenario=self.scenario.scenario, resource=resource)

    def has_ungated_easy_source(self, resource: Resource) -> Rule:
        return EconomyRoutesYield(
            economy=self.has_ungated_routes(),
            resource=resource,
            strength=Strength.AT_SCALE,
        )

    def has_own_easy_source(self, resource: Resource) -> Rule:
        return EconomyRoutesYield(
            economy=self.scenario.routes.economy_routes(),
            resource=resource,
            strength=Strength.AT_SCALE,
            among=frozenset(route.name for route in self.scenario.routes.scenario_specific_routes()),
        )

    # -- what units and techs ask -------------------------------------------------------------

    def can_sustain(self, resources: Collection[Resource]) -> Rule:
        if not resources:
            return True_()
        return And(*[self.has_easy_source(resource) for resource in resources])

    def can_pay(self, costs: Mapping[Resource, float]) -> Rule:
        """What a location asks of its price: an easy source of everything it costs. Nothing at
        all if it is free."""
        return self.can_sustain([resource for resource, amount in costs.items() if amount > 0])

    def can_pay_some(self, costs: Collection[Resource]) -> Rule:
        if not costs:
            return True_()
        return And(*[self.has_some_source(resource) for resource in costs])
