from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

from rule_builder.rules import And, False_, Or, Rule, True_

from ...items.Items import Resource
from ...locations.Buildings import Age2BuildingData
from ...locations.Units import Age2UnitData
from ...locations.VillagerJobs import Age2VillagerJobData as Job
from ...rules.custom_rules.SufficientRawResources import SufficientRawResources
from ...rules.custom_rules.ScenarioQuestions import ScenarioHasResource

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic


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
        self.counts = scenario.scenario.resources
        self.demand = scenario.scenario.demand

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

    def can_fish_by_boat(self) -> Rule:
        if not self.counts.fish_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.scenario.units.can_train(Age2UnitData.FISHING_SHIP)
                & self.scenario.starting_state.starting_fish)

    def can_fish_some(self) -> Rule:
        return self.can_fish_from_shore() | self.can_fish_by_boat()

    def can_gather_oysters(self) -> Rule:
        if not self.counts.oyster_count:
            return False_()
        return (self.scenario.buildings.has_fisherman_dropsite() & self.scenario.has_vils()
                & self.has_job(Job.OYSTER_GATHERER_MALE)
                & self.scenario.starting_state.starting_oysters)

    def can_hunt_whales(self) -> Rule:
        if not self.counts.whale_count:
            return False_()
        return (self.scenario.buildings.has_fishing_boat_dropsite()
                & self.scenario.units.can_train(Age2UnitData.FISHING_SHIP)
                & self.scenario.starting_state.starting_whales)

    def can_collect_relics(self) -> Rule:
        if not self.counts.relic_count:
            return False_()
        return (self.scenario.units.can_train(Age2UnitData.MONK)
                & self.scenario.has_building(Age2BuildingData.MONASTERY)
                & self.scenario.starting_state.starting_relics)

    # -- food that grows back -----------------------------------------------------------------

    def has_infinite_food(self) -> Rule:
        return Or(*[self.scenario.has_building(building) & self.has_job(job)
                    for building, job in RENEWABLE_FOOD])

    def has_infinite_fish(self) -> Rule:
        return (self.scenario.units.can_train(Age2UnitData.FISHING_SHIP)
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
        return self.scenario.starting_state.trading_ally & (
            self.scenario.units.can_train(Age2UnitData.TRADE_CART)
            | self.scenario.units.can_train(Age2UnitData.TRADE_COG))

    def ally_trade_wood(self) -> Rule:
        if not ALLY_TRADE:
            return False_()
        return (self.scenario.starting_state.trading_ally
                & self.scenario.units.can_train(Age2UnitData.TRADE_COG))

    # -- aggregates ---------------------------------------------------------------------------

    def has_source(self, resource: Resource) -> Rule:
        return ScenarioHasResource(scenario=self.scenario.scenario, resource=resource)

    def has_easy_source(self, resource: Resource) -> Rule:
        return ScenarioHasResource(scenario=self.scenario.scenario, resource=resource, easy=True)

    # -- what units and techs ask -------------------------------------------------------------

    def can_afford(self, costs: Mapping[Resource, float]) -> Rule:
        # An empty And resolves to False_, not True_, so free asks for nothing explicitly.
        priced = [resource for resource, amount in costs.items() if amount > 0]
        if not priced:
            return True_()
        return And(*[self.logic.resources.has_amount(resource, costs[resource])
                     | self.has_source(resource) for resource in priced])

    def can_sustain(self, costs: Mapping[Resource, float]) -> Rule:
        priced = [resource for resource, amount in costs.items() if amount > 0]
        if not priced:
            return True_()
        return And(*[self.has_easy_source(resource) for resource in priced])

    # -- what ScenarioHasResource resolves to -------------------------------------------------

    def _can_get_food(self) -> Rule:
        """What ScenarioHasResource resolves to. Ask it through has_source, not directly: the
        question also folds in this scenario's declared sources, which this does not know."""
        return (self.can_hunt() | self.can_herd() | self.can_forage() | self.can_fish_some()
                | self.endless_food())

    def _can_get_gold(self) -> Rule:
        return (self.can_mine_some() | self.can_gather_oysters() | self.can_hunt_whales()
                | self.can_collect_relics() | self.ally_trade_gold())

    def _can_get_stone(self) -> Rule:
        return self.can_quarry_some()

    def _can_get_wood(self) -> Rule:
        return self.can_chop_some() | self.ally_trade_wood()

    def _can_get_food_easily(self) -> Rule:
        """Reached through has_easy_source, with one exception: endless_food and market_trades
        call the wood one directly, because going through the question would have the wood
        aggregate ask the market which asks the wood aggregate."""
        raw_food = (
            (self.can_hunt(), self.counts.hunt_count),
            (self.can_herd(), self.counts.herd_count),
            (self.can_forage(), self.counts.bush_count),
            (self.can_fish_from_shore(), self.counts.shore_fish_count),
            (self.can_fish_by_boat(), self.counts.deep_fish_count),
        )

        return self.endless_food() | SufficientRawResources(sources=raw_food,
                                                            needed=self.demand.food)

    def _can_get_gold_easily(self) -> Rule:
        raw_gold = (
            (self.can_mine_some(), self.counts.gold_count),
            (self.can_gather_oysters(), self.counts.oyster_count),
            (self.can_hunt_whales(), self.counts.whale_count),
        )

        return self.ally_trade_gold() | (
            SufficientRawResources(sources=raw_gold, needed=self.demand.gold)
            & self.scenario.has_base()
            & (self.scenario.buildings.can_build_building(Age2BuildingData.MINING_CAMP)
               | self.scenario.buildings.can_build_multiple_tc()))

    def _can_get_stone_easily(self) -> Rule:
        raw_stone = (
            (self.can_quarry_some(), self.counts.stone_count),
        )

        return (SufficientRawResources(sources=raw_stone, needed=self.demand.stone)
                & self.scenario.has_base()
                & (self.scenario.buildings.can_build_building(Age2BuildingData.MINING_CAMP)
                   | self.scenario.buildings.can_build_multiple_tc()))

    def _can_get_wood_easily(self) -> Rule:
        return self.ally_trade_wood() | (
            self.can_chop_some() & self.scenario.has_base()
            & (self.scenario.buildings.can_build_building(Age2BuildingData.LUMBER_CAMP)
               | self.scenario.buildings.can_build_multiple_tc()))
