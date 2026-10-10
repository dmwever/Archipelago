import enum
from dataclasses import dataclass, fields

from ..Scenarios import Age2ScenarioData


class Tier(enum.Enum):
    BASE = "base"      # where you start, yours for the taking
    OPEN = "open"      # out on the map; you have to hold the ground
    ALLY = "ally"      # an ally's, and only theirs to give
    ENEMY = "enemy"    # inside a hostile base


@dataclass(frozen=True)
class ScenarioResourceDemand:
    gold: int = 3000
    stone: int = 1000
    food: int = 10000


@dataclass(frozen=True)
class ScenarioResourceCount:
    gold_count: int
    stone_count: int
    hunt_count: int
    herd_count: int
    bush_count: int
    shore_fish_count: int
    deep_fish_count: int
    oyster_count: int
    whale_count: int
    relic_count: int

    @property
    def food_count(self) -> int:
        """Every edible thing in this tier."""
        return (self.hunt_count + self.herd_count + self.bush_count
                + self.shore_fish_count + self.deep_fish_count)


COUNT_FIELDS = tuple(field.name for field in fields(ScenarioResourceCount))

EMPTY = ScenarioResourceCount(**{name: 0 for name in COUNT_FIELDS})

def total(scenario: Age2ScenarioData) -> ScenarioResourceCount:
    return ScenarioResourceCount(**{
        name: sum(getattr(counts, name) for counts in scenario.resources.values())
        for name in COUNT_FIELDS})


for _scenario in Age2ScenarioData:
    _scenario.demand = ScenarioResourceDemand()

Age2ScenarioData.AP_ATTILA_1.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_ATTILA_2.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_ATTILA_3.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_ATTILA_4.demand = ScenarioResourceDemand(gold=9000, stone=2000, food=25000)
Age2ScenarioData.AP_ATTILA_5.demand = ScenarioResourceDemand(gold=7500, stone=2000, food=20000)
Age2ScenarioData.AP_ATTILA_6.demand = ScenarioResourceDemand(gold=12000, stone=4000, food=40000)
Age2ScenarioData.AP_JOAN_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)
Age2ScenarioData.AP_JOAN_3.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_JOAN_4.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)
Age2ScenarioData.AP_JOAN_6.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)
# etc

Age2ScenarioData.AP_ATTILA_1.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=6400, stone_count=350,
    hunt_count=3900, herd_count=0, bush_count=1875,
    shore_fish_count=2225, deep_fish_count=450,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_1.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=8000, stone_count=1750,
    hunt_count=2860, herd_count=0, bush_count=1875,
    shore_fish_count=4025, deep_fish_count=2025,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_1.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=8000, stone_count=4900,
    hunt_count=0, herd_count=0, bush_count=2625,
    shore_fish_count=1650, deep_fish_count=1350,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_1.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=21600, stone_count=3150,
    hunt_count=420, herd_count=0, bush_count=0,
    shore_fish_count=4200, deep_fish_count=4500,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=5600, stone_count=0,
    hunt_count=840, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=19200, stone_count=4550,
    hunt_count=2660, herd_count=0, bush_count=0,
    shore_fish_count=2600, deep_fish_count=1325,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=12800, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=250,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=840, herd_count=900, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=4800, stone_count=4900,
    hunt_count=3500, herd_count=0, bush_count=0,
    shore_fish_count=5000, deep_fish_count=6000,
    oyster_count=0, whale_count=0, relic_count=2)

Age2ScenarioData.AP_ATTILA_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=3500,
    hunt_count=0, herd_count=200, bush_count=875,
    shore_fish_count=1600, deep_fish_count=6675,
    oyster_count=0, whale_count=0, relic_count=0)

# The fish drought: five deep fish and seven shore fish, against eighty-five gold mines.
Age2ScenarioData.AP_ATTILA_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=16000, stone_count=2450,
    hunt_count=2780, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=13600, stone_count=5950,
    hunt_count=1040, herd_count=400, bush_count=0,
    shore_fish_count=1625, deep_fish_count=900,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=38400, stone_count=3150,
    hunt_count=2920, herd_count=1200, bush_count=1875,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=4)

Age2ScenarioData.AP_ATTILA_5.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=12000, stone_count=2800,
    hunt_count=680, herd_count=1400, bush_count=750,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_5.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=4800, stone_count=1400,
    hunt_count=420, herd_count=1600, bush_count=0,
    shore_fish_count=9200, deep_fish_count=2025,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_5.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=8800, stone_count=1750,
    hunt_count=1100, herd_count=500, bush_count=750,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_5.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=36800, stone_count=7700,
    hunt_count=3840, herd_count=2100, bush_count=2250,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=3060, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=23200, stone_count=7000,
    hunt_count=2340, herd_count=500, bush_count=1625,
    shore_fish_count=2000, deep_fish_count=9050,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=28800, stone_count=4550,
    hunt_count=1260, herd_count=1600, bush_count=0,
    shore_fish_count=200, deep_fish_count=3275,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=13600, stone_count=3500,
    hunt_count=680, herd_count=0, bush_count=0,
    shore_fish_count=425, deep_fish_count=6975,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=24000, stone_count=3850,
    hunt_count=0, herd_count=1500, bush_count=2125,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=5600, stone_count=1050,
    hunt_count=0, herd_count=500, bush_count=625,
    shore_fish_count=1800, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=4000, stone_count=3500,
    hunt_count=0, herd_count=900, bush_count=1250,
    shore_fish_count=1800, deep_fish_count=3350,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=43200, stone_count=5950,
    hunt_count=2520, herd_count=500, bush_count=1375,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=4000, stone_count=1400,
    hunt_count=0, herd_count=600, bush_count=1750,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=6400, stone_count=1400,
    hunt_count=0, herd_count=0, bush_count=625,
    shore_fish_count=1425, deep_fish_count=3950,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=33600, stone_count=12600,
    hunt_count=0, herd_count=0, bush_count=4000,
    shore_fish_count=3000, deep_fish_count=825,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=8000, stone_count=3150,
    hunt_count=0, herd_count=0, bush_count=750,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=3200, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=3000, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=38400, stone_count=8750,
    hunt_count=0, herd_count=0, bush_count=1250,
    shore_fish_count=5400, deep_fish_count=3025,
    oyster_count=0, whale_count=0, relic_count=0)

# A fixed force has no villagers, so there is nothing to gather whatever the map holds.

# Genghis Khan. Scanned from the maps; chapter 1 is a fixed force and is set to EMPTY below.
#
# TODO: five tier assignments are still outstanding. Counting every Gold Mine (800) and Stone
# Mine (350) object on each map and comparing with the totals declared here - the convention
# every Attila and Joan scenario already follows exactly - leaves these unaccounted for:
#     chapter 3   6 gold mines     (4800 gold)
#     chapter 4   6 stone quarries (2100 stone) and 11 gold mines (8800 gold)
#     chapter 5   4 stone quarries (1400 stone) declared that the map does not hold
#     chapter 6   5 stone quarries (1750 stone)
# The counts are known; which tier each pile belongs to is a judgement about map regions.

Age2ScenarioData.AP_GENGHIS_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_GENGHIS_3.demand = ScenarioResourceDemand(gold=12000, stone=4000, food=40000)

Age2ScenarioData.AP_GENGHIS_4.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_GENGHIS_5.demand = ScenarioResourceDemand(gold=4500, stone=4000, food=15000)

Age2ScenarioData.AP_GENGHIS_6.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_GENGHIS_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=8000, stone_count=1050,
    hunt_count=1400, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=7200, stone_count=1050,
    hunt_count=5040, herd_count=300, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=12000, stone_count=2450,
    hunt_count=1120, herd_count=0, bush_count=2500,
    shore_fish_count=800, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=3200, stone_count=3500,
    hunt_count=340, herd_count=300, bush_count=1500,
    shore_fish_count=800, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

# stone was 10050, which is not a whole number of quarries. The map holds 83 at 350
# each = 29050, and BASE 3500 + ENEMY 15750 leaves exactly 9800 here.
Age2ScenarioData.AP_GENGHIS_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=16800, stone_count=9800,
    hunt_count=1660, herd_count=200, bush_count=0,
    shore_fish_count=2275, deep_fish_count=575,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=40800, stone_count=15750,
    hunt_count=2980, herd_count=600, bush_count=5750,
    shore_fish_count=5050, deep_fish_count=12875,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=8000, stone_count=1750,
    hunt_count=1660, herd_count=1000, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=12000, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=625,
    shore_fish_count=3600, deep_fish_count=2475,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=28800, stone_count=5250,
    hunt_count=980, herd_count=0, bush_count=1500,
    shore_fish_count=800, deep_fish_count=400,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_5.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=3200, stone_count=2100,
    hunt_count=840, herd_count=0, bush_count=0,
    shore_fish_count=1000, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_5.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=4000, stone_count=6650,
    hunt_count=1120, herd_count=0, bush_count=0,
    shore_fish_count=1000, deep_fish_count=425,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_GENGHIS_5.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_5.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=17600, stone_count=1750,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=1000, deep_fish_count=425,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=8000, stone_count=4550,
    hunt_count=980, herd_count=1000, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=8000, stone_count=4200,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=16000, stone_count=5950,
    hunt_count=1660, herd_count=900, bush_count=875,
    shore_fish_count=425, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

# Chapter 1 has no villagers and the map holds no gold or stone at all.
Age2ScenarioData.AP_GENGHIS_1.resources = {tier: EMPTY for tier in Tier}

Age2ScenarioData.AP_JOAN_1.resources = {tier: EMPTY for tier in Tier}
Age2ScenarioData.AP_JOAN_5.resources = {tier: EMPTY for tier in Tier}

assert not [scenario for scenario in Age2ScenarioData
            if set(scenario.resources) != set(Tier)], \
    "a scenario is missing a resource tier; re-scan the loose scenario files and add one"
