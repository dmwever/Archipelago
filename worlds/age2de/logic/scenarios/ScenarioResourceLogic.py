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
from ..custom_logic.ScenarioQuestions import ScenarioHasEasyResource

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
        self._gates: dict[str, dict[Tier, Rule]] = {}
        self.demand = scenario.scenario.demand

    # -- what each tier costs to reach ---------------------------------------------------------

    def tier_gates(self, kind: str = "land") -> dict[Tier, Rule]:
        gates = self._gates.get(kind)
        if gates is None:
            gates = self._gates[kind] = {
                Tier.BASE: True_(),
                Tier.OPEN: self._open_gate(kind),
                Tier.ALLY: False_(),
                Tier.ENEMY: self.scenario.starting_state.must_steal_base,
            }
        return gates

    def _open_gate(self, kind: str) -> Rule:
        """What working a source out in the open asks: a navy at sea, a held shoreline, or on land
        somewhere to fall back to - each a shared question, as every source of that kind asks it."""
        if kind == "afloat":
            return self.scenario.military.can_protect_boats()
        if kind == "shoreline":
            return self.scenario.named("can hold a shoreline", self._hold_shoreline())
        return self.can_defend_resources()

    def _hold_shoreline(self) -> Rule:
        return (self.scenario.buildings.can_hold_a_shoreline()
                | self.scenario.military.can_protect_boats())

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
                & self.has_job(Job.GOLD_MINER_MALE)
                & self.scenario.starting_state.starting_gold_mine)

    def can_quarry_some(self) -> Rule:
        return self.scenario.named("can quarry stone", self._quarry_stone())

    def _quarry_stone(self) -> Rule:
        if not self.counts.stone_count:
            return False_()
        return (self.scenario.buildings.has_stone_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.STONE_MINER_MALE)
                & self.scenario.starting_state.starting_stone_mine)

    def can_chop_some(self) -> Rule:
        return (self.scenario.buildings.has_wood_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.LUMBERJACK_MALE)
                & self.scenario.starting_state.starting_trees)

    def can_hunt(self) -> Rule:
        return self.scenario.named("can hunt", self._hunt())

    def _hunt(self) -> Rule:
        if not self.counts.hunt_count:
            return False_()
        return (self.scenario.buildings.has_hunt_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.HUNTER_MALE)
                & self.scenario.starting_state.starting_hunting)

    def can_herd(self) -> Rule:
        return self.scenario.named("can herd sheep", self._herd())

    def _herd(self) -> Rule:
        if not self.counts.herd_count:
            return False_()
        return (self.scenario.buildings.has_food_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.SHEPHERD_MALE)
                & self.scenario.starting_state.starting_sheep)

    def can_forage(self) -> Rule:
        return self.scenario.named("can forage berries", self._forage())

    def _forage(self) -> Rule:
        if not self.counts.bush_count:
            return False_()
        return (self.scenario.buildings.has_food_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.FORAGER_MALE)
                & self.scenario.starting_state.starting_bushes)

    def can_fish_from_shore(self) -> Rule:
        return self.scenario.named("can fish from the shore", self._fish_from_shore())

    def _fish_from_shore(self) -> Rule:
        if not self.counts.shore_fish_count:
            return False_()
        return (self.scenario.buildings.has_fisherman_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.FISHERMAN_MALE)
                & self.scenario.starting_state.starting_fish)

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
                & self.can_crew_fishing_ships()
                & self.scenario.starting_state.starting_fish)

    def can_fish_some(self) -> Rule:
        return self.can_fish_from_shore() | self.can_fish_by_boat()

    def can_gather_oysters_from_shore(self) -> Rule:
        return self.scenario.named("can gather oysters from the shore", self._oysters_from_shore())

    def _oysters_from_shore(self) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return (self.scenario.buildings.has_fisherman_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.OYSTER_GATHERER_MALE)
                & self.scenario.starting_state.starting_oysters)

    def can_gather_oysters_by_boat(self) -> Rule:
        return self.scenario.named("can gather oysters by boat", self._oysters_by_boat())

    def _oysters_by_boat(self) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.can_crew_fishing_ships()
                & self.scenario.starting_state.starting_oysters)

    def can_gather_oysters(self) -> Rule:
        return self.can_gather_oysters_from_shore() | self.can_gather_oysters_by_boat()

    def can_hunt_whales(self) -> Rule:
        return self.scenario.named("can hunt whales", self._hunt_whales())

    def _hunt_whales(self) -> Rule:
        if not self.counts.whale_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.can_crew_fishing_ships()
                & self.scenario.starting_state.starting_whales)

    def can_collect_relics(self) -> Rule:
        return self.scenario.named("can collect relics", self._collect_relics())

    def _collect_relics(self) -> Rule:
        if not self.counts.relic_count:
            return False_()
        monk = Age2UnitData.MONK
        return (
            self.scenario.has_building(Age2BuildingData.MONASTERY)
            & (
                self.logic.units.has_unit_items(Age2UnitData.MONK)
                | self.scenario.obtains_unit(monk)
            )
            & self.scenario.ages.has_reached(Age2UnitData.MONK.age)
            & self.can_mine_some()
        ) & self.scenario.starting_state.starting_relics

    def can_gather_gold(self) -> Rule:
        return (self.can_mine_some() | self.can_gather_oysters() | self.can_hunt_whales()
                | self.can_collect_relics())

    def can_gather_wood(self) -> Rule:
        return self.scenario.named("can chop wood", self._chop_wood())

    def _chop_wood(self) -> Rule:
        return (self.can_chop_some() & self.scenario.has_base()
                & (self.scenario.buildings.can_build_building(Age2BuildingData.LUMBER_CAMP)
                   | self.scenario.buildings.can_build_multiple_tc()))

    # -- food that grows back -----------------------------------------------------------------

    def has_infinite_food(self) -> Rule:
        return self.scenario.named("can farm", self._farm())

    def _farm(self) -> Rule:
        return Or(*[self.scenario.has_building(building) & self.has_job(job)
                    for building, job in RENEWABLE_FOOD])

    def has_infinite_fish(self) -> Rule:
        return self.scenario.named("can work fish traps", self._work_fish_traps())

    def _work_fish_traps(self) -> Rule:
        return (self.can_crew_fishing_ships()
                & self.scenario.has_building(Age2BuildingData.FISH_TRAP))

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
        return (self.scenario.has_building(Age2BuildingData.MARKET)
                & (self._can_get_wood_easily() | self.endless_food()))

    def can_earn_gold_by_partner_trade(self) -> Rule:
        """Trade carts to a trade partner's market, or trade cogs to its dock."""
        partner_market = self.scenario.players.can_reach_partner(Age2BuildingData.MARKET)
        partner_dock = self.scenario.players.can_reach_partner(Age2BuildingData.DOCK)
        if isinstance(partner_market, False_) and isinstance(partner_dock, False_):
            return False_()
        resources = self.logic.resources

        seed_gold = (self.can_gather_gold()
                     | resources.has_amount(Resource.GOLD, TRADE_SEED_GOLD))

        by_cart = (
            partner_market
            & self.scenario.has_building(Age2BuildingData.MARKET)
            & self.logic.units.has_unit_items(Age2UnitData.TRADE_CART)
            & self.can_gather_wood()
        )

        by_cog = (
            partner_dock
            & self.scenario.has_building(Age2BuildingData.DOCK)
            & self.logic.units.has_unit_items(Age2UnitData.TRADE_COG)
            & (
                self.can_gather_wood()
                | resources.has_amount(Resource.WOOD, TRADE_SEED_WOOD_AT_SEA)
            )
        )

        return (self.scenario.ages.has_reached(Age2AgeData.FEUDAL)
                & seed_gold & (by_cart | by_cog))

    def can_earn_wood_by_partner_trade(self) -> Rule:
        """Trade cogs to a trade partner's dock: a sea route brings wood home, a cart does not."""
        partner_dock = self.scenario.players.can_reach_partner(Age2BuildingData.DOCK)
        if isinstance(partner_dock, False_):
            return False_()
        resources = self.logic.resources
        return (
            partner_dock
            & self.scenario.ages.has_reached(Age2AgeData.FEUDAL)
            & self.scenario.has_building(Age2BuildingData.DOCK)
            & self.logic.units.has_unit_items(Age2UnitData.TRADE_COG)
            & (
                resources.has_amount(Resource.WOOD, TRADE_SEED_WOOD_AT_SEA)
                | self.can_gather_wood()
            )
            & (
                resources.has_amount(Resource.GOLD, TRADE_SEED_GOLD)
                | self.can_gather_gold()
            )
        )

    # -- aggregates ---------------------------------------------------------------------------

    def has_easy_source(self, resource: Resource) -> Rule:
        return ScenarioHasEasyResource(scenario=self.scenario.scenario, resource=resource)

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