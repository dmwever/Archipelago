from dataclasses import dataclass

from ..Scenarios import Age2ScenarioData


@dataclass(frozen=True)
class ScenarioResourceDemand:
    gold: int = 3000
    stone: int = 1000
    food: int = 10000


@dataclass(frozen=True)
class ScenarioBaseResourceCount:
    gold_count: int
    stone_count: int
    hunt_count: int
    herd_count: int
    bush_count: int
    shore_fish_count: int
    fish_count: int
    oyster_count: int
    whale_count: int
    relic_count: int


@dataclass(frozen=True)
class ScenarioOpenResourceCount:
    gold_count: int
    stone_count: int
    hunt_count: int
    herd_count: int
    bush_count: int
    shore_fish_count: int
    fish_count: int
    oyster_count: int
    whale_count: int
    relic_count: int


@dataclass(frozen=True)
class ScenarioAllyResourceCount:
    gold_count: int
    stone_count: int
    hunt_count: int
    herd_count: int
    bush_count: int
    shore_fish_count: int
    fish_count: int
    oyster_count: int
    whale_count: int
    relic_count: int


@dataclass(frozen=True)
class ScenarioEnemyResourceCount:
    gold_count: int
    stone_count: int
    hunt_count: int
    herd_count: int
    bush_count: int
    shore_fish_count: int
    fish_count: int
    oyster_count: int
    whale_count: int
    relic_count: int
    
    @property
    def deep_fish_count(self) -> int:
        """What only a fishing ship can reach."""
        return self.fish_count - self.shore_fish_count

    @property
    def food_count(self) -> int:
        """Every edible thing on the map, counting each shore fish once."""
        return self.hunt_count + self.herd_count + self.bush_count + self.fish_count

for _scenario in Age2ScenarioData:
    _scenario.demand = ScenarioResourceDemand()

Age2ScenarioData.AP_ATTILA_1.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_ATTILA_2.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_ATTILA_3.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_ATTILA_4.demand = ScenarioResourceDemand(gold=9000, stone=2000, food=25000)
Age2ScenarioData.AP_ATTILA_5.demand = ScenarioResourceDemand(gold=7500, stone=2000, food=20000)
Age2ScenarioData.AP_ATTILA_6.demand = ScenarioResourceDemand(gold=12000, stone=4000, food=40000)
Age2ScenarioData.AP_JOAN_1.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_JOAN_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)
Age2ScenarioData.AP_JOAN_3.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_JOAN_4.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)
Age2ScenarioData.AP_JOAN_5.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_JOAN_6.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)
# etc

Age2ScenarioData.AP_ATTILA_1.resources = ScenarioBaseResourceCount(
    gold_count=6400, stone_count=350,
    hunt_count=3900, herd_count=0, bush_count=1875,
    shore_fish_count=2250, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_1.resources = ScenarioOpenResourceCount(
    gold_count=8000, stone_count=1750,
    hunt_count=2860, herd_count=0, bush_count=1875,
    shore_fish_count=2625, fish_count=2025,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_1.resources = ScenarioAllyResourceCount(
    gold_count=8000, stone_count=4900,
    hunt_count=0, herd_count=0, bush_count=2625,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_1.resources = ScenarioEnemyResourceCount(
    gold_count=21600, stone_count=3150,
    hunt_count=420, herd_count=0, bush_count=0,
    shore_fish_count=4000, fish_count=5625,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources = ScenarioBaseResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources = ScenarioOpenResourceCount(
    gold_count=16800, stone_count=4550,
    hunt_count=3500, herd_count=0, bush_count=0,
    shore_fish_count=1200, fish_count=1125,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources = ScenarioEnemyResourceCount(
    gold_count=12800, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=250,
    shore_fish_count=800, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_3.resources = ScenarioBaseResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=840, herd_count=900, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)
Age2ScenarioData.AP_ATTILA_3.resources = ScenarioOpenResourceCount(
    gold_count=4800, stone_count=4900,
    hunt_count=3500, herd_count=0, bush_count=0,
    shore_fish_count=3400, fish_count=5750,
    oyster_count=0, whale_count=0, relic_count=0)
Age2ScenarioData.AP_ATTILA_3.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)
Age2ScenarioData.AP_ATTILA_3.resources = ScenarioEnemyResourceCount(
    gold_count=0, stone_count=3500,
    hunt_count=0, herd_count=200, bush_count=875,
    shore_fish_count=2000, fish_count=6650,
    oyster_count=0, whale_count=0, relic_count=1)

# The fish drought: five deep fish and seven shore fish, against eighty-five gold mines.
Age2ScenarioData.AP_ATTILA_4.resources = ScenarioBaseResourceCount(
    gold_count=16000, stone_count=2450,
    hunt_count=2780, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_4.resources = ScenarioOpenResourceCount(
    gold_count=13600, stone_count=5950,
    hunt_count=1040, herd_count=100, bush_count=0,
    shore_fish_count=1400, fish_count=1125,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_4.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_4.resources = ScenarioEnemyResourceCount(
    gold_count=39200, stone_count=3150,
    hunt_count=2290, herd_count=1200, bush_count=1875,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=4)

Age2ScenarioData.AP_ATTILA_5.resources = ScenarioBaseResourceCount(
    gold_count=1200, stone_count=2800,
    hunt_count=680, herd_count=1400, bush_count=750,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_5.resources = ScenarioOpenResourceCount(
    gold_count=4800, stone_count=1400,
    hunt_count=420, herd_count=200, bush_count=0,
    shore_fish_count=9200, fish_count=11225,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_5.resources = ScenarioAllyResourceCount(
    gold_count=8800, stone_count=1750,
    hunt_count=1100, herd_count=500, bush_count=750,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_5.resources = ScenarioEnemyResourceCount(
    gold_count=30400, stone_count=6300,
    hunt_count=3840, herd_count=2100, bush_count=2250,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources = ScenarioBaseResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=2720, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources = ScenarioOpenResourceCount(
    gold_count=24800, stone_count=7000,
    hunt_count=2340, herd_count=500, bush_count=1625,
    shore_fish_count=1600, fish_count=12325,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=4550,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources = ScenarioEnemyResourceCount(
    gold_count=25600, stone_count=0,
    hunt_count=1260, herd_count=1600, bush_count=0,
    shore_fish_count=0, fish_count=1800,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources = ScenarioBaseResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources = ScenarioOpenResourceCount(
    gold_count=13600, stone_count=3500,
    hunt_count=680, herd_count=0, bush_count=0,
    shore_fish_count=625, fish_count=6325,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources = ScenarioEnemyResourceCount(
    gold_count=24000, stone_count=3850,
    hunt_count=0, herd_count=1500, bush_count=2125,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources = ScenarioBaseResourceCount(
    gold_count=5600, stone_count=1050,
    hunt_count=0, herd_count=500, bush_count=500,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources = ScenarioOpenResourceCount(
    gold_count=4000, stone_count=1050,
    hunt_count=0, herd_count=900, bush_count=625,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=2400, fish_count=3550,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources = ScenarioEnemyResourceCount(
    gold_count=43200, stone_count=4900,
    hunt_count=2520, herd_count=500, bush_count=1375,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources = ScenarioBaseResourceCount(
    gold_count=4000, stone_count=1400,
    hunt_count=0, herd_count=600, bush_count=1750,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources = ScenarioOpenResourceCount(
    gold_count=6400, stone_count=1400,
    hunt_count=0, herd_count=0, bush_count=625,
    shore_fish_count=2000, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources = ScenarioEnemyResourceCount(
    gold_count=33600, stone_count=12250,
    hunt_count=0, herd_count=0, bush_count=3750,
    shore_fish_count=2000, fish_count=4800,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources = ScenarioBaseResourceCount(
    gold_count=8000, stone_count=3150,
    hunt_count=0, herd_count=0, bush_count=750,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources = ScenarioOpenResourceCount(
    gold_count=3200, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=5400, fish_count=875,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources = ScenarioEnemyResourceCount(
    gold_count=38400, stone_count=8750,
    hunt_count=0, herd_count=0, bush_count=1250,
    shore_fish_count=1825, fish_count=1300,
    oyster_count=0, whale_count=0, relic_count=0)


assert not [scenario for scenario in Age2ScenarioData if scenario.resources is None], \
    "a scenario has no resource count; re-scan the loose scenario files and add one"
