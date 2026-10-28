from __future__ import annotations

from typing import TYPE_CHECKING

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.VillagerJobs import Age2VillagerJobData as Job
from ..custom_logic.EconomyRoutes import EconomyRoute, EconomyRoutes, Strength
from ..custom_logic.SufficientRawResources import SufficientRawResources

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

TRADE_SEED_GOLD = 100
TRADE_SEED_WOOD_AT_SEA = 400


class ScenarioRoutesLogic:

    def __init__(self, scenario: 'ScenarioLogic') -> None:
        self.scenario = scenario
        self.logic = scenario.logic
        self.economy = scenario.economy

    def economy_routes(self) -> EconomyRoutes:
        return EconomyRoutes(
            routes=(*self.ungated_routes(), *self.gated_routes()),
            label=self.scenario.scenario.scenario_name,
        )

    def ungated_economy_routes(self) -> EconomyRoutes:
        """The ungated routes worked out on their own. A gate asks this and never the whole
        economy, which would be the gate asking itself (ADR-0003)."""
        return EconomyRoutes(
            routes=tuple(self.ungated_routes()),
            label=f"{self.scenario.scenario.scenario_name}, ungated",
        )

    def ungated_routes(self) -> list[EconomyRoute]:
        """Every route whose leaf reads no gate, and so the layer a defence is paid out of.
        Moving a route between here and `gated_routes` is the whole edit for regrouping one;
        `test_defence_pays.py` is what catches one filed in the wrong group."""
        return [
            *self.villager_routes_of_some(),
            *self.lumberjack_routes_at_scale(),
            *self.relic_routes(),
            *self.renewable_routes(),
            *self.trade_routes(),
            *self.market_routes(),
            *self.scenario_routes(),
        ]

    def gated_routes(self) -> list[EconomyRoute]:
        """The routes that work the map at scale, and so have to hold the ground they work."""
        return [
            *self.villager_routes_at_scale(),
            *self.boat_routes(),
        ]

    def scenario_specific_routes(self) -> list[EconomyRoute]:
        """What the scenario brings in by itself: not P1's own market, and not what it is
        handed."""
        return [
            *self.villager_routes_of_some(),
            *self.lumberjack_routes_at_scale(),
            *self.relic_routes(),
            *self.renewable_routes(),
            *self.trade_routes(),
            *self.gated_routes(),
        ]

    def relic_routes(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="Relics at a standing Monastery, started in Castle",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.can_collect_relics(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MONASTERY],
                    )
                    & self.scenario.ages.has_started_in(Age2AgeData.CASTLE)
                ),
            ),
            EconomyRoute(
                name="Relics at a standing Monastery, advanced to Castle",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.can_collect_relics(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MONASTERY],
                    )
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Relics at a built Monastery, started in Castle",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.can_collect_relics(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MONASTERY),
                    )
                    & self.scenario.ages.has_started_in(Age2AgeData.CASTLE)
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Relics at a built Monastery, advanced to Castle",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.can_collect_relics(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MONASTERY),
                    )
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                },
            ),
        ]

    def villager_routes_of_some(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="Lumberjacks at a Town Center",
                yields={Resource.WOOD: Strength.SOME},
                leaf=(
                    self.economy.chops_some_at(
                        self.scenario.has_building(Age2BuildingData.TOWN_CENTER),
                    )
                ),
            ),
            EconomyRoute(
                name="Lumberjacks at a Lumber Camp",
                yields={Resource.WOOD: Strength.SOME},
                leaf=(
                    self.economy.chops_some_at(
                        self.scenario.has_seeded_building(Age2BuildingData.LUMBER_CAMP),
                    )
                ),
            ),
            EconomyRoute(
                name="Lumberjacks at a Mule Cart",
                yields={Resource.WOOD: Strength.SOME},
                leaf=(
                    self.economy.chops_some_at(
                        self.scenario.has_seeded_building(Age2BuildingData.MULE_CART),
                    )
                ),
            ),
            EconomyRoute(
                name="Gold Miners at a Town Center",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_building(Age2BuildingData.TOWN_CENTER),
                        Job.GOLD_MINER_MALE,
                        "gold_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Gold Miners at a standing Mining Camp",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MINING_CAMP],
                        Job.GOLD_MINER_MALE,
                        "gold_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Gold Miners at a built Mining Camp",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MINING_CAMP),
                        Job.GOLD_MINER_MALE,
                        "gold_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Gold Miners at a Mule Cart",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_seeded_building(Age2BuildingData.MULE_CART),
                        Job.GOLD_MINER_MALE,
                        "gold_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Stone Miners at a Town Center",
                yields={Resource.STONE: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_building(Age2BuildingData.TOWN_CENTER),
                        Job.STONE_MINER_MALE,
                        "stone_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Stone Miners at a standing Mining Camp",
                yields={Resource.STONE: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MINING_CAMP],
                        Job.STONE_MINER_MALE,
                        "stone_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Stone Miners at a built Mining Camp",
                yields={Resource.STONE: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MINING_CAMP),
                        Job.STONE_MINER_MALE,
                        "stone_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Stone Miners at a Mule Cart",
                yields={Resource.STONE: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_seeded_building(Age2BuildingData.MULE_CART),
                        Job.STONE_MINER_MALE,
                        "stone_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Hunters at a Town Center",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_building(Age2BuildingData.TOWN_CENTER),
                        Job.HUNTER_MALE,
                        "hunt_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Hunters at a standing Mill",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MILL],
                        Job.HUNTER_MALE,
                        "hunt_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Hunters at a built Mill",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MILL),
                        Job.HUNTER_MALE,
                        "hunt_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Hunters at a standing Folwark",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.FOLWARK],
                        Job.HUNTER_MALE,
                        "hunt_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Hunters at a built Folwark",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.FOLWARK),
                        Job.HUNTER_MALE,
                        "hunt_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Hunters at a Mule Cart",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_seeded_building(Age2BuildingData.MULE_CART),
                        Job.HUNTER_MALE,
                        "hunt_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Shepherds at a Town Center",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_building(Age2BuildingData.TOWN_CENTER),
                        Job.SHEPHERD_MALE,
                        "herd_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Shepherds at a standing Mill",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MILL],
                        Job.SHEPHERD_MALE,
                        "herd_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Shepherds at a built Mill",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MILL),
                        Job.SHEPHERD_MALE,
                        "herd_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Shepherds at a standing Folwark",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.FOLWARK],
                        Job.SHEPHERD_MALE,
                        "herd_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Shepherds at a built Folwark",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.FOLWARK),
                        Job.SHEPHERD_MALE,
                        "herd_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Foragers at a Town Center",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_building(Age2BuildingData.TOWN_CENTER),
                        Job.FORAGER_MALE,
                        "bush_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Foragers at a standing Mill",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MILL],
                        Job.FORAGER_MALE,
                        "bush_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Foragers at a built Mill",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MILL),
                        Job.FORAGER_MALE,
                        "bush_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Foragers at a standing Folwark",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.FOLWARK],
                        Job.FORAGER_MALE,
                        "bush_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Foragers at a built Folwark",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.FOLWARK),
                        Job.FORAGER_MALE,
                        "bush_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Fishermen at a Town Center",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_building(Age2BuildingData.TOWN_CENTER),
                        Job.FISHERMAN_MALE,
                        "shore_fish_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Fishermen at a standing Mill",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MILL],
                        Job.FISHERMAN_MALE,
                        "shore_fish_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Fishermen at a built Mill",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MILL),
                        Job.FISHERMAN_MALE,
                        "shore_fish_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Fishermen at a standing Folwark",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.FOLWARK],
                        Job.FISHERMAN_MALE,
                        "shore_fish_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Fishermen at a built Folwark",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.FOLWARK),
                        Job.FISHERMAN_MALE,
                        "shore_fish_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Fishermen at a Dock",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.has_standing_or_seeded(Age2BuildingData.DOCK),
                        Job.FISHERMAN_MALE,
                        "shore_fish_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Fishermen at a built Dock",
                yields={Resource.FOOD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_unseeded(Age2BuildingData.DOCK),
                        Job.FISHERMAN_MALE,
                        "shore_fish_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Oyster Gatherers at a Town Center",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.has_building(Age2BuildingData.TOWN_CENTER),
                        Job.OYSTER_GATHERER_MALE,
                        "oyster_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Oyster Gatherers at a standing Mill",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.MILL],
                        Job.OYSTER_GATHERER_MALE,
                        "oyster_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Oyster Gatherers at a built Mill",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.MILL),
                        Job.OYSTER_GATHERER_MALE,
                        "oyster_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Oyster Gatherers at a standing Folwark",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.starting_state.starts_with_building[Age2BuildingData.FOLWARK],
                        Job.OYSTER_GATHERER_MALE,
                        "oyster_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Oyster Gatherers at a built Folwark",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_structurally(Age2BuildingData.FOLWARK),
                        Job.OYSTER_GATHERER_MALE,
                        "oyster_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Oyster Gatherers at a Dock",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.has_standing_or_seeded(Age2BuildingData.DOCK),
                        Job.OYSTER_GATHERER_MALE,
                        "oyster_count",
                    )
                ),
            ),
            EconomyRoute(
                name="Oyster Gatherers at a built Dock",
                yields={Resource.GOLD: Strength.SOME},
                leaf=(
                    self.economy.gathers_some_at(
                        self.scenario.buildings.can_build_unseeded(Age2BuildingData.DOCK),
                        Job.OYSTER_GATHERER_MALE,
                        "oyster_count",
                    )
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
        ]

    def lumberjack_routes_at_scale(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="Lumberjacks with a Base",
                yields={Resource.WOOD: Strength.AT_SCALE},
                leaf=(
                    self.scenario.has_vils()
                    & self.economy.has_job(Job.LUMBERJACK_MALE)
                    & self.scenario.has_base()
                    & self.scenario.buildings.has_wood_camp()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Lumberjacks with a Base at a second Town Center, started in Castle",
                yields={Resource.WOOD: Strength.AT_SCALE},
                leaf=(
                    self.scenario.has_vils()
                    & self.economy.has_job(Job.LUMBERJACK_MALE)
                    & self.scenario.has_base()
                    & self.scenario.buildings.can_build_tc_as_camp()
                    & self.scenario.ages.has_started_in(Age2AgeData.CASTLE)
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Lumberjacks with a Base at a second Town Center, advanced to Castle",
                yields={Resource.WOOD: Strength.AT_SCALE},
                leaf=(
                    self.scenario.has_vils()
                    & self.economy.has_job(Job.LUMBERJACK_MALE)
                    & self.scenario.has_base()
                    & self.scenario.buildings.can_build_tc_as_camp()
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
        ]

    def villager_routes_at_scale(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="Villagers gathering food with a Base at a second Town Center, started in Castle",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.TOWN_CENTER,
                            self.scenario.buildings.can_build_tc_as_camp(),
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                    & self.scenario.ages.has_started_in(Age2AgeData.CASTLE)
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers gathering food with a Base at a second Town Center, advanced to Castle",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.TOWN_CENTER,
                            self.scenario.buildings.can_build_tc_as_camp(),
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers gathering food with a Base at a standing Mill",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.MILL,
                            self.scenario.starting_state.starts_with_building[Age2BuildingData.MILL],
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering food with a Base at a built Mill",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.MILL,
                            self.scenario.buildings.can_build_structurally(Age2BuildingData.MILL),
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering food with a Base at a standing Folwark",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.FOLWARK,
                            self.scenario.starting_state.starts_with_building[Age2BuildingData.FOLWARK],
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering food with a Base at a built Folwark",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.FOLWARK,
                            self.scenario.buildings.can_build_structurally(Age2BuildingData.FOLWARK),
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering food with a Base at a Mule Cart",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.MULE_CART,
                            self.scenario.has_seeded_building(Age2BuildingData.MULE_CART),
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering food with a Base at a Dock",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.DOCK,
                            self.scenario.buildings.has_standing_or_seeded(Age2BuildingData.DOCK),
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering food with a Base at a built Dock",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_food(
                            Age2BuildingData.DOCK,
                            self.scenario.buildings.can_build_unseeded(Age2BuildingData.DOCK),
                        ),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a second Town Center, started in Castle",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.TOWN_CENTER,
                            self.scenario.buildings.can_build_tc_as_camp(),
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                    & self.scenario.ages.has_started_in(Age2AgeData.CASTLE)
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a second Town Center, advanced to Castle",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.TOWN_CENTER,
                            self.scenario.buildings.can_build_tc_as_camp(),
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a standing Mining Camp",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.MINING_CAMP,
                            self.scenario.starting_state.starts_with_building[Age2BuildingData.MINING_CAMP],
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a built Mining Camp",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.MINING_CAMP,
                            self.scenario.buildings.can_build_structurally(Age2BuildingData.MINING_CAMP),
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a Mule Cart",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.MULE_CART,
                            self.scenario.has_seeded_building(Age2BuildingData.MULE_CART),
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a standing Mill",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.MILL,
                            self.scenario.starting_state.starts_with_building[Age2BuildingData.MILL],
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a built Mill",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.MILL,
                            self.scenario.buildings.can_build_structurally(Age2BuildingData.MILL),
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a standing Folwark",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.FOLWARK,
                            self.scenario.starting_state.starts_with_building[Age2BuildingData.FOLWARK],
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a built Folwark",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.FOLWARK,
                            self.scenario.buildings.can_build_structurally(Age2BuildingData.FOLWARK),
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a Dock",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.DOCK,
                            self.scenario.buildings.has_standing_or_seeded(Age2BuildingData.DOCK),
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering gold with a Base at a built Dock",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_gold(
                            Age2BuildingData.DOCK,
                            self.scenario.buildings.can_build_unseeded(Age2BuildingData.DOCK),
                        ),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering stone with a Base at a second Town Center, started in Castle",
                yields={Resource.STONE: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_stone(
                            Age2BuildingData.TOWN_CENTER,
                            self.scenario.buildings.can_build_tc_as_camp(),
                        ),
                        needed=self.economy.demand.stone,
                        resource="stone",
                    )
                    & self.scenario.has_base()
                    & self.scenario.ages.has_started_in(Age2AgeData.CASTLE)
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers gathering stone with a Base at a second Town Center, advanced to Castle",
                yields={Resource.STONE: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_stone(
                            Age2BuildingData.TOWN_CENTER,
                            self.scenario.buildings.can_build_tc_as_camp(),
                        ),
                        needed=self.economy.demand.stone,
                        resource="stone",
                    )
                    & self.scenario.has_base()
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers gathering stone with a Base at a standing Mining Camp",
                yields={Resource.STONE: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_stone(
                            Age2BuildingData.MINING_CAMP,
                            self.scenario.starting_state.starts_with_building[Age2BuildingData.MINING_CAMP],
                        ),
                        needed=self.economy.demand.stone,
                        resource="stone",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering stone with a Base at a built Mining Camp",
                yields={Resource.STONE: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_stone(
                            Age2BuildingData.MINING_CAMP,
                            self.scenario.buildings.can_build_structurally(Age2BuildingData.MINING_CAMP),
                        ),
                        needed=self.economy.demand.stone,
                        resource="stone",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers gathering stone with a Base at a Mule Cart",
                yields={Resource.STONE: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_stone(
                            Age2BuildingData.MULE_CART,
                            self.scenario.has_seeded_building(Age2BuildingData.MULE_CART),
                        ),
                        needed=self.economy.demand.stone,
                        resource="stone",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.FOOD: Strength.SOME},
            ),
        ]

    def boat_routes(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="Fishing Ships gathering food",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.boat_food(),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                ),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
            EconomyRoute(
                name="Fishing Ships gathering gold",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.boat_gold(),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                ),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
            EconomyRoute(
                name="Villagers and Fishing Ships gathering food",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_and_boat_food(),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.AT_SCALE, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers and Fishing Ships gathering food at a second Town Center, started in Castle",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_and_boat_food_at_a_second_town_center(),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                    & self.scenario.ages.has_started_in(Age2AgeData.CASTLE)
                ),
                needs={
                    Resource.WOOD: Strength.AT_SCALE,
                    Resource.FOOD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers and Fishing Ships gathering food at a second Town Center, advanced to Castle",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_and_boat_food_at_a_second_town_center(),
                        needed=self.economy.demand.food,
                        resource="food",
                    )
                    & self.scenario.has_base()
                ),
                needs={
                    Resource.WOOD: Strength.AT_SCALE,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers and Fishing Ships gathering gold",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_and_boat_gold(),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={Resource.WOOD: Strength.AT_SCALE, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Villagers and Fishing Ships gathering gold at a second Town Center, started in Castle",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_and_boat_gold_at_a_second_town_center(),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                    & self.scenario.ages.has_started_in(Age2AgeData.CASTLE)
                ),
                needs={
                    Resource.WOOD: Strength.AT_SCALE,
                    Resource.FOOD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Villagers and Fishing Ships gathering gold at a second Town Center, advanced to Castle",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    SufficientRawResources(
                        sources=self.economy.villager_and_boat_gold_at_a_second_town_center(),
                        needed=self.economy.demand.gold,
                        resource="gold",
                    )
                    & self.scenario.has_base()
                ),
                needs={
                    Resource.WOOD: Strength.AT_SCALE,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                    Resource.STONE: Strength.SOME,
                },
            ),
        ]

    def renewable_routes(self) -> list[EconomyRoute]:
        """Food that grows back. Neither works ground the map holds, so neither reads a gate."""
        return [
            EconomyRoute(
                name="Farmers",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=self.economy.can_farm(),
                needs={Resource.WOOD: Strength.AT_SCALE, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Fish Traps, started in Feudal",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    self.economy.can_work_fish_traps()
                    & self.scenario.ages.has_started_in(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
            EconomyRoute(
                name="Fish Traps, advanced to Feudal",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    self.economy.can_work_fish_traps()
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Fish Traps, on Feudal Age Food",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=(
                    self.economy.can_work_fish_traps()
                    & self.scenario.ages.has_seed_item(Age2AgeData.FEUDAL)
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                    & self.scenario.ages.has_standing_or_seeded_age_up_buildings(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
        ]

    def trade_routes(self) -> list[EconomyRoute]:
        dock_seed = frozenset({Age2BuildingData.DOCK.seed_item.item_name})
        banked_gold = self.logic.resources.has_amount(Resource.GOLD, TRADE_SEED_GOLD)
        banked_wood = self.logic.resources.has_amount(
            Resource.WOOD,
            TRADE_SEED_WOOD_AT_SEA,
            excluding=dock_seed,
        )
        cogs = self.economy.can_run_trade_cogs()
        carts = self.economy.can_run_trade_carts()
        return [
            EconomyRoute(
                name="Trade Cogs, started in Feudal",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & self.scenario.ages.has_started_in(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.GOLD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Cogs, advanced to Feudal",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.SOME,
                    Resource.GOLD: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Trade Cogs, on Feudal Age Food",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & self.scenario.ages.has_seed_item(Age2AgeData.FEUDAL)
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                    & self.scenario.ages.has_standing_or_seeded_age_up_buildings(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.GOLD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Cogs on banked wood, started in Feudal",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_wood
                    & self.scenario.ages.has_started_in(Age2AgeData.FEUDAL)
                ),
                needs={Resource.GOLD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Cogs on banked wood, advanced to Feudal",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_wood
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.SOME,
                    Resource.GOLD: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Trade Cogs on banked wood, on Feudal Age Food",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_wood
                    & self.scenario.ages.has_seed_item(Age2AgeData.FEUDAL)
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                    & self.scenario.ages.has_standing_or_seeded_age_up_buildings(Age2AgeData.FEUDAL)
                ),
                needs={Resource.GOLD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Cogs on banked gold, started in Feudal",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_gold
                    & self.scenario.ages.has_started_in(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Cogs on banked gold, advanced to Feudal",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_gold
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Cogs on banked gold, on Feudal Age Food",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_gold
                    & self.scenario.ages.has_seed_item(Age2AgeData.FEUDAL)
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                    & self.scenario.ages.has_standing_or_seeded_age_up_buildings(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Cogs on banked wood and gold, started in Feudal",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_wood
                    & banked_gold
                    & self.scenario.ages.has_started_in(Age2AgeData.FEUDAL)
                ),
            ),
            EconomyRoute(
                name="Trade Cogs on banked wood and gold, advanced to Feudal",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_wood
                    & banked_gold
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={Resource.WOOD: Strength.SOME, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Cogs on banked wood and gold, on Feudal Age Food",
                yields={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    cogs
                    & banked_wood
                    & banked_gold
                    & self.scenario.ages.has_seed_item(Age2AgeData.FEUDAL)
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                    & self.scenario.ages.has_standing_or_seeded_age_up_buildings(Age2AgeData.FEUDAL)
                ),
            ),
            EconomyRoute(
                name="Trade Carts, started in Feudal",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    carts
                    & self.scenario.ages.has_started_in(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Carts, advanced to Feudal",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    carts
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={
                    Resource.WOOD: Strength.AT_SCALE,
                    Resource.FOOD: Strength.SOME,
                    Resource.GOLD: Strength.SOME,
                },
            ),
            EconomyRoute(
                name="Trade Carts, on Feudal Age Food",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    carts
                    & self.scenario.ages.has_seed_item(Age2AgeData.FEUDAL)
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                    & self.scenario.ages.has_standing_or_seeded_age_up_buildings(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE, Resource.GOLD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Carts on banked gold, started in Feudal",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    carts
                    & banked_gold
                    & self.scenario.ages.has_started_in(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
            EconomyRoute(
                name="Trade Carts on banked gold, advanced to Feudal",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    carts
                    & banked_gold
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Trade Carts on banked gold, on Feudal Age Food",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=(
                    carts
                    & banked_gold
                    & self.scenario.ages.has_seed_item(Age2AgeData.FEUDAL)
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                    & self.scenario.ages.has_standing_or_seeded_age_up_buildings(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
        ]

    def market_routes(self) -> list[EconomyRoute]:
        every_resource_at_scale = {
            Resource.WOOD: Strength.AT_SCALE,
            Resource.FOOD: Strength.AT_SCALE,
            Resource.GOLD: Strength.AT_SCALE,
            Resource.STONE: Strength.AT_SCALE,
        }
        market = self.economy.can_trade_at_market()
        return [
            EconomyRoute(
                name="Market Trade, started in Feudal",
                yields=every_resource_at_scale,
                leaf=(
                    market
                    & self.scenario.ages.has_started_in(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
            EconomyRoute(
                name="Market Trade, advanced to Feudal",
                yields=every_resource_at_scale,
                leaf=(
                    market
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE, Resource.FOOD: Strength.SOME},
            ),
            EconomyRoute(
                name="Market Trade, on Feudal Age Food",
                yields=every_resource_at_scale,
                leaf=(
                    market
                    & self.scenario.ages.has_seed_item(Age2AgeData.FEUDAL)
                    & self.scenario.has_building(Age2BuildingData.TOWN_CENTER)
                    & self.scenario.ages.has_standing_or_seeded_age_up_buildings(Age2AgeData.FEUDAL)
                ),
                needs={Resource.WOOD: Strength.AT_SCALE},
            ),
        ]

    def scenario_routes(self) -> list[EconomyRoute]:
        return [
            EconomyRoute(
                name="its own wood",
                yields={Resource.WOOD: Strength.AT_SCALE},
                leaf=self.scenario.starting_state.easy_resource_sources[Resource.WOOD],
            ),
            EconomyRoute(
                name="its own food",
                yields={Resource.FOOD: Strength.AT_SCALE},
                leaf=self.scenario.starting_state.easy_resource_sources[Resource.FOOD],
            ),
            EconomyRoute(
                name="its own gold",
                yields={Resource.GOLD: Strength.AT_SCALE},
                leaf=self.scenario.starting_state.easy_resource_sources[Resource.GOLD],
            ),
            EconomyRoute(
                name="its own stone",
                yields={Resource.STONE: Strength.AT_SCALE},
                leaf=self.scenario.starting_state.easy_resource_sources[Resource.STONE],
            ),
            EconomyRoute(
                name="a little of its own wood",
                yields={Resource.WOOD: Strength.SOME},
                leaf=self.scenario.starting_state.some_resource_sources[Resource.WOOD],
            ),
            EconomyRoute(
                name="a little of its own food",
                yields={Resource.FOOD: Strength.SOME},
                leaf=self.scenario.starting_state.some_resource_sources[Resource.FOOD],
            ),
            EconomyRoute(
                name="a little of its own gold",
                yields={Resource.GOLD: Strength.SOME},
                leaf=self.scenario.starting_state.some_resource_sources[Resource.GOLD],
            ),
            EconomyRoute(
                name="a little of its own stone",
                yields={Resource.STONE: Strength.SOME},
                leaf=self.scenario.starting_state.some_resource_sources[Resource.STONE],
            ),
        ]
