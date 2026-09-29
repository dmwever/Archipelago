from dataclasses import dataclass

from ..Scenarios import Age2ScenarioData


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
Age2ScenarioData.AP_ATTILA_5.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_ATTILA_6.demand = ScenarioResourceDemand()
Age2ScenarioData.AP_JOAN_1.demand = ScenarioResourceDemand()
# etc

Age2ScenarioData.AP_ATTILA_1.resources = ScenarioResourceCount(
    gold_count=44000, stone_count=10150,
    hunt_count=6880, herd_count=0, bush_count=6375,
    shore_fish_count=11200, fish_count=20425,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_2.resources = ScenarioResourceCount(
    gold_count=37600, stone_count=4550,
    hunt_count=3500, herd_count=0, bush_count=250,
    shore_fish_count=2800, fish_count=3925,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_3.resources = ScenarioResourceCount(
    gold_count=4800, stone_count=8400,
    hunt_count=4340, herd_count=1100, bush_count=875,
    shore_fish_count=6800, fish_count=19275,
    oyster_count=0, whale_count=0, relic_count=2)

# The fish drought: five deep fish and seven shore fish, against eighty-five gold mines.
Age2ScenarioData.AP_ATTILA_4.resources = ScenarioResourceCount(
    gold_count=68000, stone_count=11550,
    hunt_count=6740, herd_count=1600, bush_count=1875,
    shore_fish_count=1400, fish_count=2525,
    oyster_count=0, whale_count=0, relic_count=4)

Age2ScenarioData.AP_ATTILA_5.resources = ScenarioResourceCount(
    gold_count=62400, stone_count=13650,
    hunt_count=6040, herd_count=4200, bush_count=3750,
    shore_fish_count=9200, fish_count=11225,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ATTILA_6.resources = ScenarioResourceCount(
    gold_count=52000, stone_count=11550,
    hunt_count=6660, herd_count=2100, bush_count=1625,
    shore_fish_count=2200, fish_count=14875,
    oyster_count=0, whale_count=0, relic_count=0)

# No gold and no stone anywhere on the map. Deliberate, and pinned by a test.
Age2ScenarioData.AP_JOAN_1.resources = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=4960, herd_count=0, bush_count=0,
    shore_fish_count=1200, fish_count=4975,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_2.resources = ScenarioResourceCount(
    gold_count=37600, stone_count=7350,
    hunt_count=680, herd_count=1500, bush_count=2125,
    shore_fish_count=400, fish_count=6725,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_3.resources = ScenarioResourceCount(
    gold_count=52800, stone_count=10500,
    hunt_count=2520, herd_count=1900, bush_count=3250,
    shore_fish_count=3400, fish_count=6950,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_4.resources = ScenarioResourceCount(
    gold_count=44000, stone_count=15400,
    hunt_count=0, herd_count=600, bush_count=6375,
    shore_fish_count=4400, fish_count=9200,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_5.resources = ScenarioResourceCount(
    gold_count=3200, stone_count=1750,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=7600, fish_count=11850,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_JOAN_6.resources = ScenarioResourceCount(
    gold_count=49600, stone_count=11900,
    hunt_count=0, herd_count=0, bush_count=2000,
    shore_fish_count=8800, fish_count=11425,
    oyster_count=0, whale_count=0, relic_count=0)


assert not [scenario for scenario in Age2ScenarioData if scenario.resources is None], \
    "a scenario has no resource count; re-scan the loose scenario files and add one"
