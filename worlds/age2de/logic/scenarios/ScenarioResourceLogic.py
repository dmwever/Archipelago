from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Callable, Collection, Mapping

from rule_builder.rules import And, False_, Or, Rule, True_

from ...items.Items import Resource
from ...locations.Buildings import Age2BuildingData
from ...locations.connections import ScenarioResources
from ...locations.connections.ScenarioResources import Tier
from ...locations.Ages import Age2AgeData
from ...locations.Units import Age2UnitData
from ...locations.VillagerJobs import Age2VillagerJobData as Job
from ..custom_logic.EconomyRoutes import EconomyRoute, EconomyRoutes, EconomyRoutesYield, Strength
from ..custom_logic.ScenarioQuestions import ScenarioHasEconomyRoutes, ScenarioHasEasyResource, ScenarioHasSomeResource
from ..custom_logic.SufficientRawResources import SufficientRawResources

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

TRADE_SEED_GOLD = 100
TRADE_SEED_WOOD_AT_SEA = 400

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

    def tier_gates(self, kind: str = "land", boat_guard: Rule = False_()) -> dict[Tier, Rule]:
        return {
            Tier.BASE: True_(),
            Tier.OPEN: self._open_gate(kind, boat_guard),
            Tier.ALLY: False_(),
            Tier.ENEMY: self.scenario.starting_state.must_steal_base,
        }

    def herd_gates(self) -> dict[Tier, Rule]:
        return {
            Tier.BASE: True_(),
            Tier.OPEN: True_(),
            Tier.ALLY: False_(),
            Tier.ENEMY: self.scenario.starting_state.must_steal_base,
        }

    def _open_gate(self, kind: str, boat_guard: Rule) -> Rule:
        if kind == "afloat":
            return boat_guard
        if kind == "shoreline":
            return self.scenario.named("can hold a shoreline", self._hold_shoreline(boat_guard))
        return self.can_defend_resources()

    def _hold_shoreline(self, boat_guard: Rule) -> Rule:
        return self.scenario.buildings.can_hold_a_shoreline() | boat_guard

    def can_defend_resources(self) -> Rule:
        return self.scenario.named("can defend resources", self._defend_open_ground())

    def _defend_open_ground(self) -> Rule:
        return self.scenario.buildings._fortified()

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

    def can_mine_some(self) -> Rule:
        return self.scenario.named("can mine gold", self._mine_gold())

    def _mine_gold(self) -> Rule:
        if not self.counts.gold_count:
            return False_()
        return (self.scenario.buildings.has_gold_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.GOLD_MINER_MALE))

    def can_quarry_some(self) -> Rule:
        return self.scenario.named("can quarry stone", self._quarry_stone())

    def _quarry_stone(self) -> Rule:
        if not self.counts.stone_count:
            return False_()
        return (self.scenario.buildings.has_stone_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.STONE_MINER_MALE))

    def can_chop_some(self) -> Rule:
        return (self.scenario.buildings.has_wood_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.LUMBERJACK_MALE))

    def can_hunt(self) -> Rule:
        return self.scenario.named("can hunt", self._hunt())

    def _hunt(self) -> Rule:
        if not self.counts.hunt_count:
            return False_()
        return (self.scenario.buildings.has_hunt_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.HUNTER_MALE))

    def can_herd(self) -> Rule:
        return self.scenario.named("can herd sheep", self._herd())

    def _herd(self) -> Rule:
        if not self.counts.herd_count:
            return False_()
        return (self.scenario.buildings.has_food_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.SHEPHERD_MALE))

    def can_forage(self) -> Rule:
        return self.scenario.named("can forage berries", self._forage())

    def _forage(self) -> Rule:
        if not self.counts.bush_count:
            return False_()
        return (self.scenario.buildings.has_food_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.FORAGER_MALE))

    def can_fish_from_shore(self) -> Rule:
        return self.scenario.named("can fish from the shore", self._fish_from_shore())

    def _fish_from_shore(self) -> Rule:
        if not self.counts.shore_fish_count:
            return False_()
        return (self.scenario.buildings.has_fisherman_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.FISHERMAN_MALE))

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

    def can_gather_oysters_from_shore(self) -> Rule:
        return self.scenario.named("can gather oysters from the shore", self._oysters_from_shore())

    def _oysters_from_shore(self) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return (self.scenario.buildings.has_fisherman_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.OYSTER_GATHERER_MALE))

    def can_gather_oysters_by_boat(self) -> Rule:
        return self.scenario.named("can gather oysters by boat", self._oysters_by_boat())

    def _oysters_by_boat(self) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return self.scenario.buildings.has_fishing_boat_dropsite() & self.has_fishing_ships()

    def can_gather_oysters(self) -> Rule:
        return self.can_gather_oysters_from_shore() | self.can_gather_oysters_by_boat()

    def can_hunt_whales(self) -> Rule:
        return self.scenario.named("can hunt whales", self._hunt_whales())

    def _hunt_whales(self) -> Rule:
        if not self.counts.whale_count:
            return False_()
        return self.scenario.buildings.has_fishing_boat_dropsite() & self.has_fishing_ships()

    def can_collect_relics(self) -> Rule:
        return self.scenario.named("can collect relics", self._collect_relics())

    def _collect_relics(self) -> Rule:
        if not self.counts.relic_count:
            return False_()
        monk = Age2UnitData.MONK
        return (
            self.scenario.has_building_structurally(Age2BuildingData.MONASTERY)
            & (
                self.logic.units.has_unit_items(monk)
                | (self.scenario.obtains_unit(monk) & self.logic.units.survives_caveman(monk))
            )
            & self.scenario.ages.has_reached(Age2UnitData.MONK.age)
            & self._in_any_tier(self.tiered(True_(), "relic_count", self.tier_gates()))
        )

    # -- food that grows back -----------------------------------------------------------------

    def can_farm(self) -> Rule:
        return self.scenario.named("can farm", self._farm())

    def _farm(self) -> Rule:
        return (
            self.scenario.has_base()
            & Or(*[self.scenario.has_building_structurally(building) & self.has_job(job)
                   for building, job in RENEWABLE_FOOD])
            & self.scenario.buildings.has_food_dropsite()
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
        return self.scenario.has_building_structurally(Age2BuildingData.MARKET)

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
            & self.scenario.has_building_structurally(Age2BuildingData.MARKET)
            & self.logic.units.has_unit_items(Age2UnitData.TRADE_CART)
        )

    def can_run_trade_cogs(self) -> Rule:
        partner_dock = self.scenario.player_logic.can_reach_partner(Age2BuildingData.DOCK)
        if isinstance(partner_dock, False_):
            return False_()
        return (
            partner_dock
            & self.scenario.ages.has_reached(Age2AgeData.FEUDAL)
            & self.scenario.has_building_structurally(Age2BuildingData.DOCK)
            & self.logic.units.has_unit_items(Age2UnitData.TRADE_COG)
        )

    # -- economy routes -----------------------------------------------------------------------

    def economy_routes(self) -> EconomyRoutes:
        return EconomyRoutes(
            routes=(
                *self.own_routes(),
                *self.market_routes(),
                *self.scenario_routes(),
            ),
            label=self.scenario.scenario.scenario_name,
        )

    def own_routes(self) -> list[EconomyRoute]:
        return [
            *self.villager_routes_of_some(),
            *self.villager_routes_at_scale(),
            *self.boat_routes(),
            *self.trade_routes(),
            EconomyRoute(
                name="Relics",
                yields={Resource.GOLD: Strength.SOME},
                leaf=self.can_collect_relics(),
            ),
        ]

    def villager_routes_of_some(self) -> list[EconomyRoute]:
        land = self.tier_gates()
        return [
            EconomyRoute(
                name="Lumberjacks",
                yields={Resource.WOOD: Strength.SOME},
                leaf=self.can_chop_some(),
            ),
            EconomyRoute(
                name="Gold Miners",
                yields={Resource.GOLD: Strength.SOME},
                leaf=self._in_any_tier(self.tiered(self.can_mine_some(), "gold_count", land)),
            ),
            EconomyRoute(
                name="Stone Miners",
                yields={Resource.STONE: Strength.SOME},
                leaf=self._in_any_tier(self.tiered(self.can_quarry_some(), "stone_count", land)),
            ),
            EconomyRoute(
                name="Hunters",
                yields={Resource.FOOD: Strength.SOME},
                leaf=self._in_any_tier(self.tiered(self.can_hunt(), "hunt_count", land)),
            ),
            EconomyRoute(
                name="Shepherds",
                yields={Resource.FOOD: Strength.SOME},
                leaf=self._in_any_tier(
                    self.tiered(self.can_herd(), "herd_count", self.herd_gates()),
                ),
            ),
            EconomyRoute(
                name="Foragers",
                yields={Resource.FOOD: Strength.SOME},
                leaf=self._in_any_tier(self.tiered(self.can_forage(), "bush_count", land)),
            ),
            *self._guarded_routes(
                "Fishermen",
                {Resource.FOOD: Strength.SOME},
                lambda boat_guard: self._in_any_tier(self.tiered(
                    self.can_fish_from_shore(),
                    "shore_fish_count",
                    self.tier_gates("shoreline", boat_guard),
                )),
            ),
            *self._guarded_routes(
                "Oyster Gatherers",
                {Resource.GOLD: Strength.SOME},
                lambda boat_guard: self._in_any_tier(self.tiered(
                    self.can_gather_oysters_from_shore(),
                    "oyster_count",
                    self.tier_gates("shoreline", boat_guard),
                )),
            ),
        ]

    def villager_routes_at_scale(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="Lumberjacks with a Base",
                yields={Resource.WOOD: Strength.AT_SCALE},
                leaf=(
                    self.can_chop_some()
                    & self.scenario.has_base()
                    & self.scenario.buildings.has_wood_camp()
                ),
            ),
            *self._guarded_routes(
                "Villagers gathering food with a Base",
                {Resource.FOOD: Strength.AT_SCALE},
                lambda boat_guard: (
                    SufficientRawResources(
                        sources=self._villager_food(boat_guard),
                        needed=self.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
            ),
            *self._guarded_routes(
                "Villagers gathering gold with a Base",
                {Resource.GOLD: Strength.AT_SCALE},
                lambda boat_guard: (
                    SufficientRawResources(
                        sources=self._villager_gold(boat_guard),
                        needed=self.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
            ),
            EconomyRoute(
                name="Villagers gathering stone with a Base",
                yields={Resource.STONE: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self._villager_stone(),
                        needed=self.demand.stone,
                        resource="stone",
                    )
                    & self.scenario.has_base()
                ),
            ),
            EconomyRoute(
                name="Farmers",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=self.can_farm(),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
        ]

    def boat_routes(self) -> list[EconomyRoute]:
        wood_at_scale = {Resource.WOOD: Strength.AT_SCALE}
        return [
            *self._guarded_routes(
                "Fishing Ships gathering food",
                {Resource.FOOD: Strength.AT_SCALE},
                lambda boat_guard: SufficientRawResources(
                    sources=self._boat_food(boat_guard),
                    needed=self.demand.food,
                    resource="food",
                ),
                wood_at_scale,
            ),
            *self._guarded_routes(
                "Fishing Ships gathering gold",
                {Resource.GOLD: Strength.AT_SCALE},
                lambda boat_guard: SufficientRawResources(
                    sources=self._boat_gold(boat_guard),
                    needed=self.demand.gold,
                    resource="gold",
                ),
                wood_at_scale,
            ),
            *self._guarded_routes(
                "Villagers and Fishing Ships gathering food",
                {Resource.FOOD: Strength.AT_SCALE},
                lambda boat_guard: (
                    SufficientRawResources(
                        sources=self._villager_and_boat_food(boat_guard),
                        needed=self.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                wood_at_scale,
            ),
            *self._guarded_routes(
                "Villagers and Fishing Ships gathering gold",
                {Resource.GOLD: Strength.AT_SCALE},
                lambda boat_guard: (
                    SufficientRawResources(
                        sources=self._villager_and_boat_gold(boat_guard),
                        needed=self.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                wood_at_scale,
            ),
            EconomyRoute(
                name="Fish Traps",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=self.can_work_fish_traps(),
                needs=wood_at_scale,
            ),
        ]

    def trade_routes(self) -> list[EconomyRoute]:
        trade_seed_gold = self.logic.resources.has_amount(Resource.GOLD, TRADE_SEED_GOLD)
        trade_seed_wood = self.logic.resources.has_amount(Resource.WOOD, TRADE_SEED_WOOD_AT_SEA)
        return [
            *self._banked_routes(
                EconomyRoute(
                    name="Trade Cogs",
                    yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                    leaf=self.can_run_trade_cogs(),
                    needs={Resource.WOOD: Strength.SOME, Resource.GOLD: Strength.SOME},
                ),
                {Resource.WOOD: trade_seed_wood, Resource.GOLD: trade_seed_gold},
            ),
            *self._banked_routes(
                EconomyRoute(
                    name="Trade Carts",
                    yields={Resource.GOLD: Strength.AT_SCALE},
                    leaf=self.can_run_trade_carts(),
                    needs={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.SOME},
                ),
                {Resource.GOLD: trade_seed_gold},
            ),
        ]

    def market_routes(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="Market Trade",
                yields={resource: Strength.AT_SCALE for resource in Resource},
                leaf=self.can_trade_at_market(),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
        ]

    def scenario_routes(self) -> list[EconomyRoute]:
        starting_state = self.scenario.starting_state
        return [
            *[
                EconomyRoute(
                    name=f"its own {resource.name.lower()}",
                    yields={resource: Strength.AT_SCALE},
                    leaf=starting_state.easy_resource_sources[resource],
                )
                for resource in Resource
            ],
            *[
                EconomyRoute(
                    name=f"a little of its own {resource.name.lower()}",
                    yields={resource: Strength.SOME},
                    leaf=starting_state.some_resource_sources[resource],
                )
                for resource in Resource
            ],
        ]

    def _guarded_routes(
        self,
        name: str,
        yields: Mapping[Resource, Strength],
        gathers: Callable[[Rule], Rule],
        needs: Mapping[Resource, Strength] | None = None,
    ) -> list[EconomyRoute]:
        routes = [
            EconomyRoute(
                name=name,
                yields=yields,
                leaf=gathers(False_()),
                needs=needs or {},
            ),
        ]
        for costs, boat_guard in self.scenario.military.can_guard_boats().items():
            guarded_needs = dict(needs or {})
            for cost in costs:
                guarded_needs.setdefault(cost, Strength.SOME)
            routes.append(
                EconomyRoute(
                    name=f"{name} with Guarded Boats",
                    yields=yields,
                    leaf=gathers(boat_guard),
                    needs=guarded_needs,
                ),
            )
        return routes

    def _banked_routes(
        self,
        route: EconomyRoute,
        banks: Mapping[Resource, Rule],
    ) -> list[EconomyRoute]:
        routes = []
        for count in range(len(banks) + 1):
            for banked in itertools.combinations(banks, count):
                routes.append(
                    EconomyRoute(
                        name=route.name,
                        yields=route.yields,
                        leaf=And(route.leaf, *[banks[resource] for resource in banked]),
                        needs={
                            resource: strength for resource, strength in route.needs.items()
                            if resource not in banked
                        },
                    ),
                )
        return routes

    def _villager_food(self, boat_guard: Rule) -> tuple[Term, ...]:
        return (
            *self._land_food(),
            *self.tiered(
                self._fish_the_shore_from_a_camp(),
                "shore_fish_count",
                self.tier_gates("shoreline", boat_guard),
            ),
        )

    def _boat_food(self, boat_guard: Rule) -> tuple[Term, ...]:
        return (
            *self._deep_fish(boat_guard),
            *self.tiered(
                self.can_fish_the_shore_by_boat(),
                "shore_fish_count",
                self.tier_gates("shoreline", boat_guard),
            ),
        )

    def _villager_and_boat_food(self, boat_guard: Rule) -> tuple[Term, ...]:
        return (
            *self._land_food(),
            *self.tiered(
                self._fish_the_shore_from_a_camp() | self.can_fish_the_shore_by_boat(),
                "shore_fish_count",
                self.tier_gates("shoreline", boat_guard),
            ),
            *self._deep_fish(boat_guard),
        )

    def _land_food(self) -> tuple[Term, ...]:
        buildings = self.scenario.buildings
        land = self.tier_gates()
        return (
            *self.tiered(self.can_hunt() & buildings.has_hunt_camp(), "hunt_count", land),
            *self.tiered(self.can_herd(), "herd_count", self.herd_gates()),
            *self.tiered(self.can_forage() & buildings.has_food_camp(), "bush_count", land),
        )

    def _fish_the_shore_from_a_camp(self) -> Rule:
        return self.can_fish_from_shore() & self.scenario.buildings.has_fisherman_camp()

    def _deep_fish(self, boat_guard: Rule) -> tuple[Term, ...]:
        return self.tiered(
            self.can_fish_by_boat(),
            "deep_fish_count",
            self.tier_gates("afloat", boat_guard),
        )

    def _villager_gold(self, boat_guard: Rule) -> tuple[Term, ...]:
        return (
            *self._mined_gold(),
            *self.tiered(
                self._gather_shore_oysters_from_a_camp(),
                "oyster_count",
                self.tier_gates("shoreline", boat_guard),
            ),
        )

    def _boat_gold(self, boat_guard: Rule) -> tuple[Term, ...]:
        return (
            *self.tiered(
                self.can_gather_oysters_by_boat(),
                "oyster_count",
                self.tier_gates("shoreline", boat_guard),
            ),
            *self._whales(boat_guard),
        )

    def _villager_and_boat_gold(self, boat_guard: Rule) -> tuple[Term, ...]:
        return (
            *self._mined_gold(),
            *self.tiered(
                self._gather_shore_oysters_from_a_camp() | self.can_gather_oysters_by_boat(),
                "oyster_count",
                self.tier_gates("shoreline", boat_guard),
            ),
            *self._whales(boat_guard),
        )

    def _mined_gold(self) -> tuple[Term, ...]:
        return self.tiered(
            self.can_mine_some() & self.scenario.buildings.has_gold_camp(),
            "gold_count",
            self.tier_gates(),
        )

    def _gather_shore_oysters_from_a_camp(self) -> Rule:
        return self.can_gather_oysters_from_shore() & self.scenario.buildings.has_fisherman_camp()

    def _whales(self, boat_guard: Rule) -> tuple[Term, ...]:
        return self.tiered(
            self.can_hunt_whales(),
            "whale_count",
            self.tier_gates("afloat", boat_guard),
        )

    def _villager_stone(self) -> tuple[Term, ...]:
        return self.tiered(
            self.can_quarry_some() & self.scenario.buildings.has_stone_camp(),
            "stone_count",
            self.tier_gates(),
        )

    # -- aggregates ---------------------------------------------------------------------------
    def has_economy_routes(self) -> Rule:
        return ScenarioHasEconomyRoutes(scenario=self.scenario.scenario)

    def has_easy_source(self, resource: Resource) -> Rule:
        return ScenarioHasEasyResource(scenario=self.scenario.scenario, resource=resource)

    def has_some_source(self, resource: Resource) -> Rule:
        return ScenarioHasSomeResource(scenario=self.scenario.scenario, resource=resource)

    def has_own_easy_source(self, resource: Resource) -> Rule:
        return EconomyRoutesYield(
            economy=self.economy_routes(),
            resource=resource,
            strength=Strength.AT_SCALE,
            among=frozenset(route.name for route in self.own_routes()),
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
