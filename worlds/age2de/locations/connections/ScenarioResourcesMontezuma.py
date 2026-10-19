"""MONTEZUMA map yields, scanned ahead of the campaign itself.

NOT IMPORTED, and deliberately so. These five scenarios do not exist yet: there is no
Age2CampaignData.MONTEZUMA, no Age2ScenarioData.AP_MONTEZUMA_*, no Mongols civilisation, no locations,
no rules, no logic and no campaign bundle. Declaring the enums to make this data compile breaks
fourteen test methods that walk the campaign, scenario and civilisation enums directly - they ask
things like "every campaign has exactly one campaign item", which a placeholder cannot answer.

So the data waits here instead of rotting in a branch. When the campaign is really added, move
these statements back into ScenarioResources.py; they are in the same form as every other scenario
and need no translation beyond whatever tier restructuring has happened since.

Note AP_MONTEZUMA_5 has no counts - the scan starts at chapter 2.
"""

from ..Scenarios import Age2ScenarioData
from .ScenarioResources import ScenarioResourceCount, ScenarioResourceDemand, Tier

Age2ScenarioData.AP_MONTEZUMA_1.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_MONTEZUMA_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_MONTEZUMA_3.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_MONTEZUMA_4.demand = ScenarioResourceDemand(gold=4500, stone=1000, food=15000) #This one can also be solved without any Resources whatsoever with the Speedrun strat, which is easier than the normal way, but requires at least one batch of troops.

Age2ScenarioData.AP_MONTEZUMA_5.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000) #Almost every fish is reachable for Villagers, but I figured I'd judge by walking distance from shore.

Age2ScenarioData.AP_MONTEZUMA_6.demand = ScenarioResourceDemand(gold=9000, stone=3000, food=30000)

Age2ScenarioData.AP_MONTEZUMA_1.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=9600, stone_count=3150,
    hunt_count=600, herd_count=800, bush_count=750,
    shore_fish_count=200, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=true,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_MONTEZUMA_1.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=9600, stone_count=0,
    hunt_count=2080, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=2)

Age2ScenarioData.AP_MONTEZUMA_1.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_1.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=25600, stone_count=6300,
    hunt_count=7100, herd_count=2000, bush_count=2000,
    shore_fish_count=4800, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=2)

Age2ScenarioData.AP_MONTEZUMA_2.resources[Tier.BASE] = ScenarioResourceCount(   """Gonna have to assume a slightly larger Base area here, otherwise we'd never have both food AND stone in it."""
    gold_count=8000, stone_count=1750,
    hunt_count=0, herd_count=0, bush_count=875,
    shore_fish_count=1400, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=true, enemy_market=true,
    ally_dock=true, enemy_dock=true)

Age2ScenarioData.AP_MONTEZUMA_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=8000, stone_count=2800,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=9250, deep_fish_count=3700,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=25600, stone_count=5950,
    hunt_count=0, herd_count=100, bush_count=1625,
    shore_fish_count=15425, deep_fish_count=3375,
    oyster_count=0, whale_count=0, relic_count=3)

Age2ScenarioData.AP_MONTEZUMA_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=30400, stone_count=2800,
    hunt_count=280, herd_count=200, bush_count=625,
    shore_fish_count=16200, deep_fish_count=600,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_MONTEZUMA_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=2400, stone_count=2100,
    hunt_count=0, herd_count=0, bush_count=1000,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=false,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_MONTEZUMA_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=4000, stone_count=1750,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=1000, deep_fish_count=2700,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=3200, stone_count=0,
    hunt_count=0, herd_count=2200, bush_count=1375,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=40800, stone_count=5600,
    hunt_count=0, herd_count=500, bush_count=2625,
    shore_fish_count=3600, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=17600, stone_count=4200,
    hunt_count=0, herd_count=1000, bush_count=2125,
    shore_fish_count=200, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=false,
    ally_dock=false, enemy_dock=true)

Age2ScenarioData.AP_MONTEZUMA_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=8800, stone_count=0,
    hunt_count=900, herd_count=0, bush_count=0,
    shore_fish_count=2200, deep_fish_count=10300,   
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=20800, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=4600, deep_fish_count=3125,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_5.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=3000, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=false,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_MONTEZUMA_5.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=20800, stone_count=3500,
    hunt_count=1200, herd_count=0, bush_count=750,
    shore_fish_count=4075, deep_fish_count=3700,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_5.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_5.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=16800, stone_count=4900,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=3150, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_MONTEZUMA_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=12800, stone_count=5250,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=4600, deep_fish_count=3400,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=false,
    ally_dock=false, enemy_dock=true)

Age2ScenarioData.AP_MONTEZUMA_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=4800, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=4525,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=41600, stone_count=3150,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=5200, deep_fish_count=4400,
    oyster_count=0, whale_count=0, relic_count=0)
