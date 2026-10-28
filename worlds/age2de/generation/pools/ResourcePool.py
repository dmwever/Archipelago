from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING, Iterable

from ...items import Items
from ...items.Items import Age2ItemData, Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Players import Side, TradeAccess
from ...locations.Units import Age2UnitData
from ...Options import PartnerTrade

if TYPE_CHECKING:
    from ... import Age2World
    from ...locations.Scenarios import Age2ScenarioData
    from ...Options import Age2Options
    from .AgePool import AgePool


LARGEST = {
    Resource.WOOD: Age2ItemData.STARTING_WOOD_LARGE,
    Resource.FOOD: Age2ItemData.STARTING_FOOD_LARGE,
    Resource.GOLD: Age2ItemData.STARTING_GOLD_LARGE,
    Resource.STONE: Age2ItemData.STARTING_STONE_LARGE,
}

STARTING_WOOD = 1000

TARGETS = {
    Resource.FOOD: 850,
    Resource.GOLD: 750,
    Resource.STONE: 400,
}


MAX_ITEM_POOL_PERCENT = 0.5


class ResourcePool:
    def __init__(self, options: 'Age2Options', world: 'Age2World',
                 scenarios: Iterable['Age2ScenarioData'], ages: 'AgePool') -> None:
        self._world = world
        self.totals: dict[Resource, int] = {resource: 0 for resource in Resource}
        scenarios = list(scenarios)
        self.seeds: list[Age2ItemData] = [
            item for item in Items.CATEGORY_TO_ITEMS[Items.SeedResources]
            if self.is_economy_route_shuffled(item.type.seeds, options)
            and (item.type.seeds is not Age2AgeData.FEUDAL
                 or self.is_feudal_awaited(scenarios, ages, options))
        ]
        seed_wood = sum(
            item.type.amount for item in self.seeds
            if item.type.type is Resource.WOOD
        )
        self.targets: dict[Resource, int] = {Resource.WOOD: STARTING_WOOD - seed_wood, **TARGETS}

    @staticmethod
    def is_economy_route_shuffled(building: Age2BuildingData, options: 'Age2Options') -> bool:
        partner_trade = options.partner_trade.value != PartnerTrade.option_none
        if building is Age2BuildingData.DOCK:
            return partner_trade
        if building is Age2BuildingData.MARKET:
            return bool(options.market_trade) or partner_trade
        return True

    @classmethod
    def is_feudal_awaited(cls, scenarios: list['Age2ScenarioData'], ages: 'AgePool',
                          options: 'Age2Options') -> bool:
        return any(
            not scenario.fixed_force
            and (ages.dark_start or ages.starts_in(scenario) < Age2AgeData.FEUDAL)
            and (cls.can_trade_with_a_partner(scenario, options) or cls.can_work_fish_traps(scenario))
            for scenario in scenarios
        )

    @staticmethod
    def can_trade_with_a_partner(scenario: 'Age2ScenarioData', options: 'Age2Options') -> bool:
        partner_trade = options.partner_trade.value
        if partner_trade == PartnerTrade.option_none:
            return False
        partners = [
            player for player in scenario.players
            if player.side is Side.ALLY or partner_trade == PartnerTrade.option_allies_and_enemies
        ]
        carts = (Age2BuildingData.MARKET, Age2UnitData.TRADE_CART, True)
        cogs = (Age2BuildingData.DOCK, Age2UnitData.TRADE_COG, scenario.has_water_access)
        return any(
            on_water
            and scenario.civ.builds(building)
            and building not in scenario.excluded_buildings
            and unit not in scenario.excluded_units
            and any(player.trade_access(building) is not TradeAccess.CLOSED for player in partners)
            for building, unit, on_water in (carts, cogs)
        )

    @staticmethod
    def can_work_fish_traps(scenario: 'Age2ScenarioData') -> bool:
        fish_trap = Age2BuildingData.FISH_TRAP
        return (scenario.has_water_access
                and scenario.civ.builds(fish_trap)
                and fish_trap not in scenario.excluded_buildings
                and Age2UnitData.FISHING_SHIP not in scenario.excluded_units)

    def plan(self, locations_to_fill: int) -> list[Age2ItemData]:
        """The starting resources for this seed, out of at most its share of the open locations,
        tallied into totals."""
        items = self.build(int(locations_to_fill * MAX_ITEM_POOL_PERCENT))
        self._tally(items)
        return items

    def build(self, locations_to_fill: int) -> list[Age2ItemData]:
        """Random starting resources until every target is met, then stop: what is left of the
        locations is spare. A budget too small for the targets halves them and spends it all."""
        items: list[Age2ItemData] = []
        halved = False
        if locations_to_fill <= 0:
            return items

        amounts = dict(self.targets)
        choices = Items.CATEGORY_TO_ITEMS[Items.StartingResources]

        while locations_to_fill > 0:
            worst_case = {resource: ceil(amounts[resource] / LARGEST[resource].type.amount)
                          for resource in amounts}
            worst_case_sum = sum(worst_case.values())

            if worst_case_sum > locations_to_fill:
                amounts = {resource: amount // 2 for resource, amount in amounts.items()}
                halved = True
                continue

            if worst_case_sum == locations_to_fill:
                for resource, needed in worst_case.items():
                    for _ in range(needed):
                        items.append(LARGEST[resource])
                        locations_to_fill -= 1
                return items

            if worst_case_sum == 0 and not halved:
                return items   # every target met

            item_data = self._world.random.choice(choices)
            resource = item_data.type.type
            amounts[resource] = max(0, amounts[resource] - item_data.type.amount)
            items.append(item_data)
            locations_to_fill -= 1
        return items

    def _tally(self, items: list[Age2ItemData]) -> None:
        tallied = {resource: 0 for resource in Resource}
        precollected = [Items.NAME_TO_ITEM[item.name]
                        for item in self._world.multiworld.precollected_items[self._world.player]]
        pooled = items + self.seeds
        for item in pooled + precollected:
            payload = item.type
            if isinstance(payload, (Items.StartingResources, Items.SeedResources)):
                tallied[payload.type] += payload.amount
        self.totals.clear()
        self.totals.update(tallied)
