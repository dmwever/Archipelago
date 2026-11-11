"""Barbarossa map yields, scanned ahead of the campaign itself.

NOT IMPORTED, and deliberately so. The Barbarossa campaign is not connected: there is no
Age2CampaignData.BARBAROSSA, no Age2ScenarioData.AP_BARBAROSSA_*, no locations, no rules, no logic
and no campaign bundle. Declaring the enums to make this data compile breaks the tests that walk the
campaign, scenario and civilisation enums directly - they ask things like "every campaign has
exactly one campaign item", which a placeholder cannot answer.

So the data waits here instead of rotting in a branch. When the campaign is connected, move the
demand and resource statements into ScenarioResources.py; they are in the same form as every other
scenario and need no translation beyond whatever tier restructuring has happened since.

MARKET_AND_DOCK_FLAGS keeps PR 19's market and dock flags, one set per scenario. They record judged
usability, not building existence: never "correct" one from a scenario scan. Connected scenarios do
not store these flags; they derive them from per-player records. So when the campaign is connected,
these flags must be rescanned per player - which player owns or builds each market and dock, on
which side, and whether it is usable - and written as player records. Do not move this table into
the connected data.

AP_BARBAROSSA_5 has no demand and no counts.
"""

from ..Scenarios import Age2ScenarioData
from .ScenarioResources import ScenarioResourceCount, ScenarioResourceDemand, Tier

Age2ScenarioData.AP_BARBAROSSA_1.demand = ScenarioResourceDemand(gold=9000, stone=3000, food=30000)

Age2ScenarioData.AP_BARBAROSSA_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_BARBAROSSA_3.demand = ScenarioResourceDemand(gold=6000, stone=3000, food=20000)

Age2ScenarioData.AP_BARBAROSSA_4.demand = ScenarioResourceDemand(gold=9000, stone=3000, food=30000)

Age2ScenarioData.AP_BARBAROSSA_6.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_BARBAROSSA_1.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=9600, stone_count=3500,
    hunt_count=680, herd_count=1000, bush_count=1000,
    shore_fish_count=0, deep_fish_count=4300,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_1.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=24000, stone_count=7350,
    hunt_count=2040, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=1350,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_1.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_1.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=67200, stone_count=18200,
    hunt_count=9360, herd_count=4800, bush_count=4500,
    shore_fish_count=600, deep_fish_count=2200,
    oyster_count=0, whale_count=0, relic_count=6)

Age2ScenarioData.AP_BARBAROSSA_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=1680, herd_count=0, bush_count=875,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=2600, deep_fish_count=900,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=19200, stone_count=5950,
    hunt_count=1120, herd_count=0, bush_count=1500,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=6300, herd_count=0, bush_count=0,
    shore_fish_count=6200, deep_fish_count=1350,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=6400, stone_count=3150,
    hunt_count=2100, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=1400, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=12800, stone_count=1400,
    hunt_count=1380, herd_count=900, bush_count=750,
    shore_fish_count=4000, deep_fish_count=1050,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_BARBAROSSA_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=4800, stone_count=700,
    hunt_count=1400, herd_count=0, bush_count=0,
    shore_fish_count=1400, deep_fish_count=2675,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=28000, stone_count=7000,
    hunt_count=1940, herd_count=1200, bush_count=750,
    shore_fish_count=6200, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_BARBAROSSA_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=9600, stone_count=3500,
    hunt_count=680, herd_count=400, bush_count=1250,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=22400, stone_count=7350,
    hunt_count=3440, herd_count=800, bush_count=1500,
    # Please just use Scenario parsing to source the total and subtract it from what I've got for
    # the enemies, it's too much to count manually, for both deep_ and shore_fish
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=31200, stone_count=5950,
    hunt_count=0, herd_count=1200, bush_count=750,
    shore_fish_count=3400, deep_fish_count=4750,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=8800, stone_count=1050,
    hunt_count=1020, herd_count=1500, bush_count=0,
    shore_fish_count=800, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=15200, stone_count=1400,
    hunt_count=1240, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_BARBAROSSA_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=4000, stone_count=1400,
    hunt_count=1020, herd_count=1200, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=22400, stone_count=6650,
    hunt_count=1960, herd_count=1000, bush_count=3750,
    shore_fish_count=1000, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

MARKET_AND_DOCK_FLAGS = {
    Age2ScenarioData.AP_BARBAROSSA_1: {
        "ally_market": False,
        "enemy_market": True,
        "ally_dock": False,
        "enemy_dock": False,
    },
    Age2ScenarioData.AP_BARBAROSSA_2: {
        "ally_market": True,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": True,
    },
    Age2ScenarioData.AP_BARBAROSSA_3: {
        "ally_market": True,
        "enemy_market": True,
        "ally_dock": True,
        "enemy_dock": False,
    },
    Age2ScenarioData.AP_BARBAROSSA_4: {
        "ally_market": False,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": True,
    },
    Age2ScenarioData.AP_BARBAROSSA_6: {
        "ally_market": True,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": False,
    },
}
