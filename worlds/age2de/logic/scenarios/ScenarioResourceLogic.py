from __future__ import annotations

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
               gates: Mapping[Tier, Rule]) -> tuple[tuple[Rule, int, str, str], ...]:
        """Each map area holding some of the source: gathering it there, how much, the area, and
        which count it is - the last two for the explanation only."""
        return tuple((gathers & gates[tier], getattr(counts, field), tier.value, field)
                     for tier, counts in self.scenario.scenario.resources.items()
                     if getattr(counts, field))

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
        ship = Age2UnitData.FISHING_SHIP
        return self.logic.units.has_unit_items(ship) & self.scenario.ages.has_reached(ship.age)

    def can_crew_fishing_ships(self) -> Rule:
        return self.scenario.named("can crew Fishing Ships", self._crew_fishing_ships())

    def _crew_fishing_ships(self) -> Rule:
        """Fishing Ships, and the wood for one: banked, or chopped."""
        ship = Age2UnitData.FISHING_SHIP
        return (self.has_fishing_ships()
                & (self.can_gather_wood()
                   | self.logic.resources.has_amount(Resource.WOOD,
                                                     ship.cost.get(Resource.WOOD, 0))))

    def can_fish_by_boat(self) -> Rule:
        return self.scenario.named("can fish by boat", self._fish_by_boat())

    def _fish_by_boat(self) -> Rule:
        if not self.counts.deep_fish_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.can_crew_fishing_ships())

    def can_fish_some(self) -> Rule:
        return self.can_fish_from_shore() | self.can_fish_by_boat()

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
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.can_crew_fishing_ships())

    def can_gather_oysters(self) -> Rule:
        return self.can_gather_oysters_from_shore() | self.can_gather_oysters_by_boat()

    def can_hunt_whales(self) -> Rule:
        return self.scenario.named("can hunt whales", self._hunt_whales())

    def _hunt_whales(self) -> Rule:
        if not self.counts.whale_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.can_crew_fishing_ships())

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
            & self.can_mine_some()
        )

    def can_gather_gold(self) -> Rule:
        return (self.can_mine_some() | self.can_gather_oysters() | self.can_hunt_whales()
                | self.can_collect_relics())

    def can_gather_wood(self) -> Rule:
        return self.scenario.named("can chop wood", self._chop_wood())

    def _chop_wood(self) -> Rule:
        return (self.can_chop_some() & self.scenario.has_base()
                & (self.scenario.buildings.can_build_structurally(Age2BuildingData.LUMBER_CAMP)
                   | self.scenario.buildings.can_build_multiple_tc()))

    # -- food that grows back -----------------------------------------------------------------

    def has_infinite_food(self) -> Rule:
        return self.scenario.named("can farm", self._farm())

    def _farm(self) -> Rule:
        return Or(*[self.scenario.has_building_structurally(building) & self.has_job(job)
                    for building, job in RENEWABLE_FOOD])

    def has_infinite_fish(self) -> Rule:
        return self.scenario.named("can work fish traps", self._work_fish_traps())

    def _work_fish_traps(self) -> Rule:
        return (self.can_crew_fishing_ships()
                & self.scenario.has_building_structurally(Age2BuildingData.FISH_TRAP))

    def endless_food(self) -> Rule:
        return self.scenario.named("has endless food", self._endless_food())

    def _endless_food(self) -> Rule:
        return (self.endless_farming() | self.endless_fish_traps()) & self._can_get_wood_easily()

    def endless_farming(self) -> Rule:
        return self.scenario.named("can farm endlessly", self._endless_farming())

    def _endless_farming(self) -> Rule:
        return self.has_infinite_food() & self.scenario.buildings.has_food_dropsite()

    def endless_fish_traps(self) -> Rule:
        return self.scenario.named("can fish endlessly with traps", self._endless_fish_traps())

    def _endless_fish_traps(self) -> Rule:
        return self.has_infinite_fish() & self.scenario.buildings.has_fishing_boat_dropsite()

    # -- trade --------------------------------------------------------------------------------

    def can_trade_at_market(self) -> Rule:
        if not self.world.options.market_trade:
            return False_()
        # Leaf gatherers only. has_easy_source asks the market, and easy food outside the base
        # asks for an army, which asks gold and wood, which ask the market again.
        return (self.scenario.has_building_structurally(Age2BuildingData.MARKET)
                & (self._can_get_wood_easily() | self.endless_food()))

    def can_earn_gold_by_partner_trade(self) -> Rule:
        """Trade carts to a trade partner's market, or trade cogs to its dock."""
        by_cart = self.can_run_trade_carts()
        by_cog = self.can_run_trade_cogs()
        if isinstance(by_cart, False_) and isinstance(by_cog, False_):
            return False_()
        return self._can_seed_trade_gold() & (by_cart | by_cog)

    def can_earn_wood_by_partner_trade(self) -> Rule:
        """Trade cogs to a trade partner's dock: a sea route brings wood home, a cart does not."""
        by_cog = self.can_run_trade_cogs()
        if isinstance(by_cog, False_):
            return False_()
        return self._can_seed_trade_gold() & by_cog

    def _can_seed_trade_gold(self) -> Rule:
        return (
            self.can_gather_gold()
            | self.logic.resources.has_amount(Resource.GOLD, TRADE_SEED_GOLD)
        )

    def can_run_trade_carts(self) -> Rule:
        partner_market = self.scenario.player_logic.can_reach_partner(Age2BuildingData.MARKET)
        if isinstance(partner_market, False_):
            return False_()
        return (
            partner_market
            & self.scenario.ages.has_reached(Age2AgeData.FEUDAL)
            & self.scenario.has_building_structurally(Age2BuildingData.MARKET)
            & self.logic.units.has_unit_items(Age2UnitData.TRADE_CART)
            & self.can_gather_wood()
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
            & (
                self.can_gather_wood()
                | self.logic.resources.has_amount(Resource.WOOD, TRADE_SEED_WOOD_AT_SEA)
            )
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
            EconomyRoute(
                name="Lumberjacks",
                yields={Resource.WOOD: Strength.AT_SCALE},
                leaf=self.can_gather_wood(),
            ),
            EconomyRoute(
                name="Trade Cogs",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=self.can_earn_wood_by_partner_trade(),
            ),
            EconomyRoute(
                name="Trade Carts",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=self._can_seed_trade_gold() & self.can_run_trade_carts(),
            ),
            EconomyRoute(
                name="Farms and Fish Traps",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=self.endless_food(),
            ),
            *self._guarded_routes("Food Gatherers", Resource.FOOD, self._can_gather_food_at_scale),
            *self._guarded_routes("Gold Miners", Resource.GOLD, self._can_mine_gold_at_scale),
            EconomyRoute(
                name="Stone Miners",
                yields={Resource.STONE: Strength.AT_SCALE},
                leaf=self._can_quarry_stone_at_scale(),
            ),
        ]

    def market_routes(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="Market Trade",
                yields={resource: Strength.AT_SCALE for resource in Resource},
                leaf=self.can_trade_at_market(),
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
        resource: Resource,
        gathers: Callable[[Rule], Rule],
    ) -> list[EconomyRoute]:
        routes = [
            EconomyRoute(
                name=name,
                yields={resource: Strength.AT_SCALE},
                leaf=gathers(False_()),
            ),
        ]
        for costs, boat_guard in self.scenario.military.can_guard_boats().items():
            routes.append(
                EconomyRoute(
                    name=f"{name} with Guarded Boats",
                    yields={resource: Strength.AT_SCALE},
                    leaf=gathers(boat_guard),
                    needs={cost: Strength.AT_SCALE for cost in costs},
                ),
            )
        return routes

    def _can_gather_food_at_scale(self, boat_guard: Rule) -> Rule:
        land = self.tier_gates()
        raw_food = (
            *self.tiered(self.can_hunt(), "hunt_count", land),
            *self.tiered(self.can_herd(), "herd_count", land),
            *self.tiered(self.can_forage(), "bush_count", land),
            *self.tiered(
                self.can_fish_some(),
                "shore_fish_count",
                self.tier_gates("shoreline", boat_guard),
            ),
            *self.tiered(
                self.can_fish_by_boat(),
                "deep_fish_count",
                self.tier_gates("afloat", boat_guard),
            ),
        )
        return (
            SufficientRawResources(sources=raw_food, needed=self.demand.food, resource="food")
            & self.scenario.has_base()
        )

    def _can_mine_gold_at_scale(self, boat_guard: Rule) -> Rule:
        raw_gold = (
            *self.tiered(self.can_mine_some(), "gold_count", self.tier_gates()),
            *self.tiered(
                self.can_gather_oysters(),
                "oyster_count",
                self.tier_gates("shoreline", boat_guard),
            ),
            *self.tiered(
                self.can_hunt_whales(),
                "whale_count",
                self.tier_gates("afloat", boat_guard),
            ),
        )
        return (
            SufficientRawResources(sources=raw_gold, needed=self.demand.gold, resource="gold")
            & self.scenario.has_base()
            & self._can_work_at_scale(Age2BuildingData.MINING_CAMP)
        )

    def _can_quarry_stone_at_scale(self) -> Rule:
        raw_stone = self.tiered(self.can_quarry_some(), "stone_count", self.tier_gates())
        return (
            SufficientRawResources(sources=raw_stone, needed=self.demand.stone, resource="stone")
            & self.scenario.has_base()
            & self._can_work_at_scale(Age2BuildingData.MINING_CAMP)
        )

    def _can_work_at_scale(self, camp: Age2BuildingData) -> Rule:
        return (
            self.scenario.buildings.can_build_structurally(camp)
            | self.scenario.buildings.can_build_multiple_tc()
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

    # -- private methods -------------------------------------------------------------

    def _can_get_wood_easily(self) -> Rule:
        return self.can_earn_wood_by_partner_trade() | self.can_gather_wood()