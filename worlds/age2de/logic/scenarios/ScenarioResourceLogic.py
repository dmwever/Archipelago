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
from ..budget.BudgetItem import PricedLocation
from ..budget.BudgetTotal import BudgetTotal
from ..custom_logic.ScenarioQuestions import ScenarioHasEasyResource

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

TRADE_SEED_GOLD = 100
TRADE_SEED_WOOD_AT_SEA = 400

MARKET_ECONOMY = False
"""Buying and selling at a market is a higher-difficulty expectation. The rule is real and
tested; flipping this is what turns it on."""

ALLY_TRADE = False
"""A trade cart is gold, but only against an ally who keeps a market standing. No scenario
declares a trading ally yet."""

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
        if kind == "afloat":
            return self.scenario.military.has_navy()
        if kind == "shoreline":
            return (self.scenario.buildings.can_hold_a_shoreline()
                    | self.scenario.military.has_navy())
        return self.scenario.buildings.is_fortified()

    def tiered(self, gathers: Rule, field: str,
               gates: Mapping[Tier, Rule]) -> tuple[tuple[Rule, int], ...]:
        return tuple((gathers & gates[tier], getattr(counts, field))
                     for tier, counts in self.scenario.scenario.resources.items()
                     if getattr(counts, field))

    # -- can gather ---------------------------------------------------------------------------

    def has_job(self, job: Job) -> Rule:
        return self.scenario.units.can_do_job(job) & self.logic.units.has_profession_item(job)

    def can_mine_some(self) -> Rule:
        if not self.counts.gold_count:
            return False_()
        return (self.scenario.buildings.has_gold_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.GOLD_MINER_MALE)
                & self.scenario.starting_state.starting_gold_mine)

    def can_quarry_some(self) -> Rule:
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
        if not self.counts.hunt_count:
            return False_()
        return (self.scenario.buildings.has_hunt_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.HUNTER_MALE)
                & self.scenario.starting_state.starting_hunting)

    def can_herd(self) -> Rule:
        if not self.counts.herd_count:
            return False_()
        return (self.scenario.buildings.has_food_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.SHEPHERD_MALE)
                & self.scenario.starting_state.starting_sheep)

    def can_forage(self) -> Rule:
        if not self.counts.bush_count:
            return False_()
        return (self.scenario.buildings.has_food_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.FORAGER_MALE)
                & self.scenario.starting_state.starting_bushes)

    def can_fish_from_shore(self) -> Rule:
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
        """Fishing Ships, and the wood for one: banked, or chopped."""
        ship = Age2UnitData.FISHING_SHIP
        return (self.has_fishing_ships()
                & (self.can_gather_wood()
                   | self.logic.resources.has_amount(Resource.WOOD,
                                                     ship.cost.get(Resource.WOOD, 0))))

    def can_fish_by_boat(self) -> Rule:
        if not self.counts.deep_fish_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.can_crew_fishing_ships()
                & self.scenario.starting_state.starting_fish)

    def can_fish_some(self) -> Rule:
        return self.can_fish_from_shore() | self.can_fish_by_boat()

    def can_gather_oysters_from_shore(self) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return (self.scenario.buildings.has_fisherman_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.OYSTER_GATHERER_MALE)
                & self.scenario.starting_state.starting_oysters)

    def can_gather_oysters_by_boat(self) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.can_crew_fishing_ships()
                & self.scenario.starting_state.starting_oysters)

    def can_gather_oysters(self) -> Rule:
        return self.can_gather_oysters_from_shore() | self.can_gather_oysters_by_boat()

    def can_hunt_whales(self) -> Rule:
        if not self.counts.whale_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.can_crew_fishing_ships()
                & self.scenario.starting_state.starting_whales)

    def can_collect_relics(self) -> Rule:
        if not self.counts.relic_count:
            return False_()
        monk = Age2UnitData.MONK
        rule = (self.scenario.has_building(Age2BuildingData.MONASTERY)
                & self.logic.units.has_unit_items(monk)
                & self.scenario.ages.has_reached(monk.age)
                & self.scenario.starting_state.starting_relics)
        return rule & self.logic.resources.has_amount(Resource.GOLD, monk.cost.get(Resource.GOLD, 0))

    def can_gather_gold(self) -> Rule:
        return (self.can_mine_some() | self.can_gather_oysters() | self.can_hunt_whales()
                | self.can_collect_relics())

    def can_gather_wood(self) -> Rule:
        return (self.can_chop_some() & self.scenario.has_base()
                & (self.scenario.buildings.can_build_building(Age2BuildingData.LUMBER_CAMP)
                   | self.scenario.buildings.can_build_multiple_tc()))

    # -- food that grows back -----------------------------------------------------------------

    def has_infinite_food(self) -> Rule:
        return Or(*[self.scenario.has_building(building) & self.has_job(job)
                    for building, job in RENEWABLE_FOOD])

    def has_infinite_fish(self) -> Rule:
        return (self.can_crew_fishing_ships()
                & self.scenario.has_building(Age2BuildingData.FISH_TRAP))

    def endless_food(self) -> Rule:
        farms = self.has_infinite_food() & self.scenario.buildings.has_food_dropsite()
        traps = self.has_infinite_fish() & self.scenario.buildings.has_fishing_boat_dropsite()
        return (farms | traps) & self._can_get_wood_easily()

    # -- the higher-difficulty stubs ----------------------------------------------------------

    def market_trades(self) -> Rule:
        if not MARKET_ECONOMY:
            return False_()
        return (self.scenario.has_building(Age2BuildingData.MARKET)
                & (self._can_get_wood_easily() | self.endless_food()))

    def ally_trade_gold(self) -> Rule:
        if not ALLY_TRADE:
            return False_()
        resources = self.logic.resources

        seed_gold = (self.can_gather_gold()
                     | resources.has_amount(Resource.GOLD, TRADE_SEED_GOLD))
        
        wood_by_land = (self.scenario.has_building(Age2BuildingData.MARKET)
                   & self.logic.units.has_unit_items(Age2UnitData.TRADE_CART)
                   & self.can_gather_wood())
        
        wood_by_sea = (self.scenario.has_building(Age2BuildingData.DOCK)
                  & self.logic.units.has_unit_items(Age2UnitData.TRADE_COG)
                  & (self.can_gather_wood()
                     | resources.has_amount(Resource.WOOD, TRADE_SEED_WOOD_AT_SEA)))
        
        return (self.scenario.starting_state.trading_ally
                & self.scenario.ages.has_reached(Age2AgeData.FEUDAL)
                & seed_gold & (wood_by_land | wood_by_sea))

    def ally_trade_wood(self) -> Rule:
        if not ALLY_TRADE:
            return False_()
        resources = self.logic.resources
        return (
                    self.scenario.starting_state.trading_ally
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

    def can_pay(self, costs: Mapping[Resource, float], location: PricedLocation) -> Rule:
        """What a location asks of its price: an easy source of everything it costs, or its place
        in this scenario's budget order. Nothing at all if it is free."""
        priced = [resource for resource, amount in costs.items() if amount > 0]
        if not priced:
            return True_()
        return self.can_sustain(priced) | BudgetTotal(scenario=self.scenario.scenario,
                                                      location=location)

    # -- private methods -------------------------------------------------------------

    def _can_get_wood_easily(self) -> Rule:
        return self.ally_trade_wood() | self.can_gather_wood()